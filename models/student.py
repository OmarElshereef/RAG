from pydantic import BaseModel, EmailStr, HttpUrl
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime
from typing import List



class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class StudentInsertion(BaseModel):
    name: str
    id: int

class Student(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    @classmethod
    def from_supabase(cls, data: dict):
        flat_data = {**data, **data.get("users", {})}
        return cls(**flat_data)

class StudentLogin(BaseModel):
    email:EmailStr
    password:str

class StudentUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class StudentReturn(Student):
    token: str


class StudentImageUpload(BaseModel):
    student_id: int
    image_URL: HttpUrl
