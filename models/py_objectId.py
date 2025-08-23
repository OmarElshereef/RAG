from pydantic import BaseModel, Field
from pydantic import field_validator
from bson import ObjectId
from typing import Any
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    """Custom ObjectId field that works with Pydantic v2"""
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler
    ) -> core_schema.CoreSchema:
        """
        Return a Pydantic CoreSchema that behaves like an ObjectId field.
        """
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, value: Any) -> ObjectId:
        """Validate and convert input into an ObjectId."""
        if isinstance(value, ObjectId):
            return value
        if isinstance(value, str):
            if ObjectId.is_valid(value):
                return ObjectId(value)
        raise ValueError(f"Invalid ObjectId: {value}")

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler
    ) -> JsonSchemaValue:
        """Return JSON schema for ObjectId as string."""
        json_schema = handler(core_schema)
        json_schema.update(
            type="string",
            pattern="^[0-9a-fA-F]{24}$",
            example="507f1f77bcf86cd799439011"
        )
        return json_schema


class MongoModel(BaseModel):
    """Base model with ObjectId + JSON encoding support."""
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
    }

