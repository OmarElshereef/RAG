from ..VectorDBInterface import VectorDBInterface
from src.models.db_schemas.retrieved_document import RetrievedDocument
from ..VectorDBEnums import (
    PgVectorDistanceMethodEnums,
    PgVecotrTableSchemeEnums,
    PgVectorIndexTypeEnums,
    DistanceMethodEnums,
)
import logging
from typing import List
from sqlalchemy.sql import text as sql_text
import json


class PgVectorProvider(VectorDBInterface):
    def __init__(
        self,
        db_client,
        default_vector_size: int = 384,
        distance_method: str = None,
        index_threshold: int = 100,
    ):
        self.db_client = db_client
        self.default_vector_size = default_vector_size
        self.index_threshold = index_threshold

        self.pgvector_table_prefix = PgVecotrTableSchemeEnums._PREFIX.value

        self.logger = logging.getLogger("uvicorn")

        self.default_index_name = (
            lambda collection_name: f"{collection_name}_vector_idx"
        )

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = PgVectorDistanceMethodEnums.COSINE.value

    async def connect(self):
        async with self.db_client() as session:
            async with session.begin():
                await session.execute(
                    sql_text("CREATE EXTENSION IF NOT EXISTS vector;")
                )
            await session.commit()

    async def disconnect(self) -> None:
        pass

    async def collection_exists(self, collection_name: str) -> bool:

        record = None
        async with self.db_client() as session:
            async with session.begin():
                list_tbl = sql_text(
                    f"SELECT * from pg_tables WHERE tablename=:collection_name"
                )
                result = await session.execute(
                    list_tbl, {"collection_name": collection_name}
                )
                record = result.scalar_one_or_none()

        return record is not None

    async def list_all_collections(self) -> List:
        records = []
        async with self.db_client() as session:
            async with session.begin():
                list_tbl = sql_text(
                    "SELECT tablename from pg_tables WHERE tablename LIKE :prefix"
                )
                result = await session.execute(
                    list_tbl,
                    {"prefix": self.pgvector_table_prefix},
                )
                records = result.scalars().all()

        return records

    async def get_collection_info(self, collection_name: str) -> dict:
        async with self.db_client() as session:
            async with session.begin():
                table_info_sql = sql_text(
                    f"""
                    SELECT schemaname, tablename, tableowner, tablespace, hasindexes
                    FROM pg_tables
                    WHERE tablename = :collection_name
                    """
                )
                count_sql = sql_text(f'SELECT count(*) from "{collection_name}"')

                table_info_result = await session.execute(
                    table_info_sql, {"collection_name": collection_name}
                )

                table_info = table_info_result.fetchone()

                if not table_info:
                    return None

                count_result = await session.execute(
                    count_sql,
                )

                return {
                    "table_info": dict(table_info._mapping),
                    "record_count": count_result.scalar_one(),
                }

    async def delete_collection(self, collection_name: str):
        async with self.db_client() as session:
            async with session.begin():
                delete_sql = sql_text(f'DROP TABLE IF EXISTS "{collection_name}";')
                await session.execute(delete_sql)
            await session.commit()
        self.logger.info("Deleted collection %s", collection_name)
        return True

    async def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ) -> bool:
        if do_reset:
            await self.delete_collection(collection_name)

        collection_exists = await self.collection_exists(collection_name)

        if not collection_exists:
            self.logger.info("Creating collection %s", collection_name)
            async with self.db_client() as session:
                async with session.begin():
                    create_sql = sql_text(
                        f"""
                    CREATE TABLE "{collection_name}" (
                        {PgVecotrTableSchemeEnums.ID.value} bigserial PRIMARY KEY,
                        {PgVecotrTableSchemeEnums.TEXT.value} TEXT,
                        {PgVecotrTableSchemeEnums.VECTOR.value} VECTOR({embedding_size}),
                        {PgVecotrTableSchemeEnums.METADATA.value} JSONB DEFAULT '{{}}',
                        {PgVecotrTableSchemeEnums.CHUNK_ID.value} INTEGER
                            REFERENCES chunks(id)
                    );
                    """
                    )
                    await session.execute(create_sql)

                    await session.commit()
            return True

    async def index_exists(self, collection_name: str) -> bool:
        index_name = self.default_index_name(collection_name)
        async with self.db_client() as session:
            async with session.begin():
                check_sql = sql_text(
                    """
                    SELECT 1 
                    FROM pg_indexes 
                    WHERE tablename = :collection_name
                    AND indexname = :index_name
                    """
                )

                result = await session.execute(
                    check_sql,
                    {"collection_name": collection_name, "index_name": index_name},
                )

                record = result.scalar_one_or_none()
        return record is not None

    async def create_index(
        self, collection_name: str, index_type: str = PgVectorIndexTypeEnums.HNSW.value
    ):
        index_exists = await self.index_exists(collection_name)
        if index_exists:
            self.logger.info("Index on collection %s already exists", collection_name)
            return False

        async with self.db_client() as session:
            async with session.begin():
                count_sql = sql_text(f'SELECT COUNT(*) FROM "{collection_name}"')
                result = await session.execute(count_sql)
                record_count = result.scalar_one()
                if record_count < self.index_threshold:
                    self.logger.info(
                        "Collection %s has %d records, below threshold %d, skipping index creation",
                        collection_name,
                        record_count,
                        self.index_threshold,
                    )
                    return False
                self.logger.info(
                    "Creating index on collection %s with %d records",
                    collection_name,
                    record_count,
                )
                index_name = self.default_index_name(collection_name)

                create_index_sql = sql_text(
                    f"CREATE INDEX {index_name} ON {collection_name} "
                    f"USING {index_type} ({PgVecotrTableSchemeEnums.VECTOR.value} "
                    f"{self.distance_method}) ;"
                )
                await session.execute(create_index_sql)
            await session.commit()
            self.logger.info("finish creating index %s", index_name)
        return True

    async def reset_vector_index(self, collection_name: str):

        async with self.db_client() as session:
            async with session.begin():
                index_name = self.default_index_name(collection_name)
                drop_index_sql = sql_text(f"DROP INDEX IF EXISTS {index_name};")
                await session.execute(drop_index_sql)
            await session.commit()
            self.logger.info("Dropped index %s", index_name)

        created = await self.create_index(collection_name)
        if created:
            self.logger.info("Recreated index on collection %s", collection_name)
            return True
        else:
            self.logger.info(
                "Failed to recreate index on collection %s", collection_name
            )
            return False

    async def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list,
        metadata: dict = None,
        record_id: int = None,
    ):
        collection_exists = await self.collection_exists(collection_name)
        if not collection_exists:
            self.logger.error("Collection %s does not exist", collection_name)
            return False

        if not record_id:
            self.logger.error("record_id must be provided for insert_one")
            return False

        async with self.db_client() as session:
            async with session.begin():
                insert_sql = sql_text(
                    f"INSERT INTO {collection_name} "
                    f"({PgVecotrTableSchemeEnums.TEXT.value}, "
                    f"{PgVecotrTableSchemeEnums.VECTOR.value}, "
                    f"{PgVecotrTableSchemeEnums.METADATA.value}, "
                    f"{PgVecotrTableSchemeEnums.CHUNK_ID.value}) "
                    f"VALUES (:text, :vector, :metadata, :chunk_id)"
                )

                await session.execute(
                    insert_sql,
                    {
                        "text": text,
                        "vector": "[" + ",".join([str(i) for i in vector]) + "]",
                        "metadata": json.dumps(metadata) if metadata else "{}",
                        "chunk_id": record_id,
                    },
                )
            await session.commit()
            await self.create_index(collection_name)

        self.logger.info("Inserted one record into collection %s", collection_name)
        return True

    async def insert_many(
        self,
        collection_name: str,
        texts: List[str],
        vectors: List[list],
        metadatas: List[dict] = None,
        record_ids: List[int] = None,
        batch_size: int = 50,
    ):
        collection_exists = await self.collection_exists(collection_name)
        if not collection_exists:
            self.logger.error("Collection %s does not exist", collection_name)
            return False

        if len(vectors) != len(record_ids):
            self.logger.error("Length of vectors and record_ids must match")
            return False

        if not metadatas or len(metadatas) == 0:
            metadatas = [None] * len(texts)
        try:
            async with self.db_client() as session:
                async with session.begin():
                    for i in range(0, len(texts), batch_size):
                        batch_texts = texts[i : i + batch_size]
                        batch_vectors = vectors[i : i + batch_size]
                        batch_metadatas = metadatas[i : i + batch_size]
                        batch_record_ids = record_ids[i : i + batch_size]

                        values = []

                        for _text, _vector, _metadata, _record_id in zip(
                            batch_texts,
                            batch_vectors,
                            batch_metadatas,
                            batch_record_ids,
                        ):
                            values.append(
                                {
                                    "text": _text,
                                    "vector": "["
                                    + ",".join([str(i) for i in _vector])
                                    + "]",
                                    "metadata": json.dumps(_metadata),
                                    "chunk_id": _record_id,
                                }
                            )

                            batch_insert_sql = sql_text(
                                f"INSERT INTO {collection_name} "
                                f"({PgVecotrTableSchemeEnums.TEXT.value}, "
                                f"{PgVecotrTableSchemeEnums.VECTOR.value}, "
                                f"{PgVecotrTableSchemeEnums.METADATA.value}, "
                                f"{PgVecotrTableSchemeEnums.CHUNK_ID.value}) "
                                f"VALUES (:text, :vector, :metadata, :chunk_id)"
                            )

                        await session.execute(batch_insert_sql, values)
                    await session.commit()
            await self.create_index(collection_name)
        except Exception as e:
            self.logger.error("Error inserting records: %s", e)
            return False

        return True

    async def search_by_vector(
        self, collection_name: str, vector: list, limit: int
    ) -> List[RetrievedDocument]:

        collection_exists = await self.collection_exists(collection_name)
        if not collection_exists:
            self.logger.error("Collection %s does not exist", collection_name)
            return []

        vector = "[" + ",".join([str(i) for i in vector]) + "]"

        async with self.db_client() as session:
            async with session.begin():
                search_sql = sql_text(
                    f"select {PgVecotrTableSchemeEnums.TEXT.value} as text,"
                    f" 1 - ({PgVecotrTableSchemeEnums.VECTOR.value} <=> :vector ) as score "
                    f"from {collection_name} "
                    f"order by score desc "
                    f"limit {limit}"
                )

                result = await session.execute(search_sql, {"vector": vector})
                records = result.fetchall()
                documents = [
                    RetrievedDocument(text=record.text, score=record.score)
                    for record in records
                ]
        return documents
