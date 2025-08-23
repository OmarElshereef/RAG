from pydantic import BaseModel, EmailStr, HttpUrl
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime
from typing import List



class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int

class EnrollmentInsertion(EnrollmentCreate):
    enrolled_at: datetime = Field(default_factory=datetime.now())  


class Enrollment(BaseModel):
    id: int
    student_id: int
    course_id: int
    enrolled_at: datetime

