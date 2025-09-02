from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
from qdrant_client import QdrantClient, models
import logging
from typing import List
from src.models.db_schemas import RetrievedDocument


class QdrantDBProvider(VectorDBInterface):

    def __init__(
        self,
        db_client,
        default_vector_size: int = 384,
        distance_method: str = None,
        index_threshold: int = 100,
    ):

        self.db_client = db_client
        self.client = None

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT
        else:
            self.distance_method = models.Distance.COSINE

        self.logger = logging.getLogger("uvicorn")

    async def connect(self) -> None:
        self.client = QdrantClient(path=self.db_client)
        self.logger.info("Connected to QdrantDB at %s", self.db_client)

    async def disconnect(self) -> None:
        self.client = None
        self.logger.info("Disconnected from QdrantDB")

    async def collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name)

    async def list_all_collections(self) -> List:
        return self.client.get_collections()

    async def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name).model_dump()

    async def delete_collection(self, collection_name: str):
        if self.collection_exists(collection_name):
            return self.client.delete_collection(collection_name)

        return None

    async def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ) -> bool:
        if do_reset:
            self.delete_collection(collection_name)

        if not self.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size, distance=self.distance_method
                ),
            )
            self.logger.info("Created collection on Qdrant %s", collection_name)
            return True
        else:
            self.logger.info("Collection %s already exists", collection_name)
            return False

    async def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list,
        metadata: dict = None,
        record_id: str = None,
    ):
        if not self.collection_exists(collection_name):
            self.logger.error("Collection %s does not exist", collection_name)
            return False

        try:
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id=record_id,
                        vector=vector,
                        payload={"text": text, "metadata": metadata},
                    )
                ],
            )
        except Exception as e:
            self.logger.error("Error inserting record: %s", e)
            return False
        return True

    async def insert_many(
        self,
        collection_name: str,
        texts: List[str],
        vectors: List[list],
        metadatas: List[dict] = None,
        record_ids: List[str] = None,
        batch_size: int = 50,
    ):
        if not self.collection_exists(collection_name):
            self.logger.error("Collection %s does not exist", collection_name)
            return False

        if metadatas is None:
            metadatas = [None] * len(texts)

        if record_ids is None:
            record_ids = [None] * len(texts)

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]
            batch_vectors = vectors[i : i + batch_size]
            batch_metadatas = metadatas[i : i + batch_size]
            batch_record_ids = record_ids[i : i + batch_size]

            records = [
                models.Record(
                    id=batch_record_ids[j],
                    vector=batch_vectors[j],
                    payload={"text": batch_texts[j], "metadata": batch_metadatas[j]},
                )
                for j in range(len(batch_texts))
            ]
            try:
                _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=records,
                )
            except Exception as e:
                self.logger.error("Error inserting batch: %s", e)
                return False

        return True

    async def search_by_vector(
        self, collection_name: str, vector: list, limit: int
    ) -> List[RetrievedDocument]:
        results = self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit,
        )

        if not results or len(results) == 0:
            return None

        return [
            RetrievedDocument(**{"score": record.score, "text": record.payload["text"]})
            for record in results
        ]
