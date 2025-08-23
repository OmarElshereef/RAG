from pydantic import BaseModel, EmailStr, HttpUrl
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, Literal
from datetime import datetime
from typing import List
from .py_objectId import PyObjectId, MongoModel



class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    year: Optional[int] = None
    major: Optional[str] = None
    
class ProfessorCreate(BaseModel):
    name: str
    email: EmailStr
    department: str
    password: str


class StudentProfile(BaseModel):
    year: Optional[int] = None
    major: Optional[str] = None


class ProfessorProfile(BaseModel):
    department: str

# ---------- BASE USER ----------

class UserBase(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Literal["student", "professor"]
    created_at: datetime = Field(default_factory=datetime.now)
    


class StudentInsert(UserBase, MongoModel,StudentProfile):
    role: Literal["student"] = "student"

    def to_user_doc(self):
        return {
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "role": self.role,
            "created_at": self.created_at,
            "profile": StudentProfile(
                year=self.year,
                major=self.major,
            ).model_dump()
        }


class ProfessorInsert(UserBase, MongoModel, ProfessorProfile):
    role: Literal["professor"] = "professor"

    def to_user_doc(self):
        return {
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "role": self.role,
            "created_at": self.created_at,
            "profile": ProfessorProfile(
                department=self.department
            ).model_dump()
        }


class User(MongoModel):
    name: str
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr
    role: Literal["student", "professor"]
    created_at: datetime
    profile: StudentProfile | ProfessorProfile

# ---------- AUTH / UTILITY MODELS ----------

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserReturn(User):
    token: str