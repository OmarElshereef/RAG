from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime


class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    project_id: ObjectId
    type: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    size: Optional[int] = Field(gte=0, default=None)
    config: dict = Field(default=None)
    pushed_at: datetime = Field(default=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("project_id", 1)],
                "name": "asset_project_id_index",
                "unique": False,
            },
            {
                "key": [("project_id", 1), ("name", 1)],
                "name": "asset_project_id_name_index",
                "unique": True,
            },
        ]
