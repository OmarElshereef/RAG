from .BaseDataModel import BaseDataModel
from .db_schemas import Asset
from .enums.DataBaseEnums import DataBaseEnums
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from typing import List, Optional


class AssetModel(BaseDataModel):
    def __init__(self, db_client: sessionmaker):
        super().__init__(db_client)

    @classmethod
    async def create_instance(cls, db_client: sessionmaker):
        instance = cls(db_client)
        return instance

    async def create_asset(self, asset: Asset):
        async with self.db_client() as session:
            async with session.begin():
                session.add(asset)
            await session.commit()
            await session.refresh(asset)
        return asset

    async def get_all_project_assets(
        self, project_id: int, asset_type: str
    ) -> List[Asset]:
        async with self.db_client() as session:
            async with session.begin():
                query = select(Asset).where(
                    Asset.project_id == project_id, Asset.type == asset_type
                )
                result = await session.execute(query)
                records = result.scalars().all()

        return records

    async def get_asset_by_file_id(
        self, file_id: str, project_id: int
    ) -> Optional[Asset]:
        async with self.db_client() as session:
            async with session.begin():
                query = select(Asset).where(
                    Asset.name == file_id, Asset.project_id == project_id
                )
                result = await session.execute(query)
                asset = result.scalar_one_or_none()

        return asset
