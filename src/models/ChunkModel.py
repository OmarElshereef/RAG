from .BaseDataModel import BaseDataModel
from .db_schemas import DataChunk
from .enums.DataBaseEnums import DataBaseEnums
from bson import ObjectId
from pymongo import InsertOne
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import func, delete
from typing import List


class ChunkModel(BaseDataModel):
    def __init__(self, db_client: sessionmaker):
        super().__init__(db_client)

    @classmethod
    async def create_instance(cls, db_client: sessionmaker):
        instance = cls(db_client)
        return instance

    async def create_chunk(self, chunk: DataChunk):
        async with self.db_client() as session:
            async with session.begin():
                session.add(chunk)
            await session.commit()
            await session.refresh(chunk)
        return chunk

    async def get_chunk(self, chunk_id: id):
        async with self.db_client() as session:
            async with session.begin():
                query = select(DataChunk).where(DataChunk.id == chunk_id)
                result = await session.execute(query)
                chunk = result.scalar_one_or_none()

        return chunk

    async def insert_many_chunks(self, chunks: List[DataChunk], batch_size: int = 100):

        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(chunks), batch_size):
                    batch = chunks[i : i + batch_size]
                    session.add_all(batch)

            await session.commit()
        return len(chunks)

    async def delete_chunks_by_project(self, project_id: int):
        async with self.db_client() as session:
            async with session.begin():
                query = delete(DataChunk).where(DataChunk.project_id == project_id)
                result = await session.execute(query)
                await session.commit()
        return result.rowcount

    async def get_chunks_by_project(
        self, project_id: int, page: int = 1, page_size: int = 50
    ):
        async with self.db_client() as session:
            async with session.begin():
                query = (
                    select(DataChunk)
                    .where(DataChunk.project_id == project_id)
                    .offset((page - 1) * page_size)
                    .limit(page_size)
                )
                result = await session.execute(query)
                records = result.scalars().all()
        return records
