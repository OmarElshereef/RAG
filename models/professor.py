from pydantic import BaseModel, EmailStr, HttpUrl
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime
from typing import List





class ProfessorCreate(BaseModel):
    name: str
    email: EmailStr
    department: str
    password: str

class ProfessorInsertion(BaseModel):
    name: str
    id: int
    department: str


class Professor(BaseModel):
    id: int
    name: str
    email: EmailStr
    department: str
    created_at: datetime

    @classmethod
    def from_supabase(cls, data: dict):
        flat_data = {**data, **data.get("users", {})}
        return cls(**flat_data)
    

class ProfessorLogin(BaseModel):
    email: EmailStr
    password: str

class ProfessorUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None



class ProfessorReturn(Professor):
    token:str