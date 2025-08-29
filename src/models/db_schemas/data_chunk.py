from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId


class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    project_id: ObjectId
    asset_id: ObjectId
    text: str = Field(..., min_length=1)
    metadata: dict
    order: int = Field(..., gt=0)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("project_id", 1)],
                "name": "chunk_project_id_index",
                "unique": False,
            }
        ]
