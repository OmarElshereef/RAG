from .BaseDataModel import BaseDataModel
from .db_schemas import DataChunk
from .enums.DataBaseEnums import DataBaseEnums
from bson import ObjectId
from pymongo import InsertOne


class ChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnums.COLLECTION_CHUNK_NAME.value]

    async def create_chunk(self, chunk: DataChunk):
        result = await self.collection.insert_one(
            chunk.model_dump(by_alias=True, exclude_unset=True)
        )
        chunk._id = result.inserted_id
        return chunk

    async def get_chunk(self, chunk_id: str):
        record = await self.collection.find_one({"_id": ObjectId(chunk_id)})
        if record:
            return DataChunk(**record)
        return None

    async def insert_many_chunks(self, chunks: list, batch_size: int = 100):

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            operations = [
                InsertOne(chunk.model_dump(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]
            if operations:
                await self.collection.bulk_write(operations)

        return len(chunks)

    async def delete_chunks_by_project(self, project_id: ObjectId):
        result = await self.collection.delete_many({"project_id": project_id})
        return result.deleted_count
