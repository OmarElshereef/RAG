from .BaseDataModel import BaseDataModel
from .db_schemas import Asset
from .enums.DataBaseEnums import DataBaseEnums
from bson import ObjectId


class AssetModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnums.COLLECTION_ASSET_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnums.COLLECTION_ASSET_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnums.COLLECTION_ASSET_NAME.value]
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"], name=index["name"], unique=index["unique"]
                )

    async def create_asset(self, asset: Asset):
        result = await self.collection.insert_one(
            asset.model_dump(by_alias=True, exclude_unset=True)
        )
        asset.id = result.inserted_id
        return asset

    async def get_all_project_assets(self, project_id: ObjectId, asset_type: str):
        assets = await self.collection.find(
            {
                "project_id": project_id,
                "type": asset_type,
            }
        ).to_list(length=None)

        return [Asset(**asset) for asset in assets]

    async def get_asset_by_file_id(self, file_id: str, project_id: ObjectId):
        record = await self.collection.find_one(
            {
                "name": file_id,
                "project_id": project_id,
            }
        )
        if record:
            return Asset(**record)
        return None
