from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .py_objectId import PyObjectId, MongoModel
from bson import ObjectId


class CourseCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    max_students: int = 50
    current_enrollment: int = 0


class CourseInsertion(CourseCreate, MongoModel):
    professor_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.now)


class Course(MongoModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    code: str
    description: Optional[str]
    professor_id: PyObjectId
    max_students: int
    current_enrollment: int
    created_at: datetime
