from fastapi import HTTPException, status, Response, UploadFile
from typing import List

from models.user import StudentCreate, UserLogin, UserReturn,User, StudentInsert

from utils.auth import create_access_token,hash_password, verify_password
from utils.multer import upload_to_supabase_storage
from database.supabase_client import SupabaseClient
from database.mongo_client import MongoDBClient
from datetime import datetime
from bson import ObjectId



db = MongoDBClient.get_client()
supabase = SupabaseClient().get_client()



users_collection = db["users"]

async def signup_student_logic(student: StudentCreate, response: Response):
    
    existing = await users_collection.find_one({"email": student.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    
    student.password = hash_password(student.password)
    insertion = StudentInsert(
        **student.model_dump(),
        created_at=datetime.now())

    user_doc = insertion.to_user_doc()

    
    result = await users_collection.insert_one(user_doc)
    if not result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

    
    token = create_access_token({"user_id": str(result.inserted_id), "role": "student"})

    
    return_user = UserReturn(
        id=str(result.inserted_id),
        name=insertion.name,
        email=insertion.email,
        role="student",
        created_at=insertion.created_at,
        profile=user_doc["profile"],
        token=token
    )

    return return_user

async def login_student_logic(student: UserLogin, response: Response):
    
    
    
    user = await users_collection.find_one({"email": student.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    if user.get("role") != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not a student account"
        )

    if not verify_password(student.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )

    token = create_access_token({
        "user_id": str(user["_id"]), 
        "role": "student"
    })


    return_user = UserReturn(
        **user,
        token=token
    )

    return return_user


async def get_all_students_logic():
    result = await users_collection.find({"role": "student"}).to_list(length=None)


    if not result:
        return []
    students = [User(**student) for student in result]
    return students

async def get_student_logic(student_id: str):
    student = await users_collection.find_one({"_id": ObjectId(student_id), "role": "student"})
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Student not found"
        )

    return User(**student)

async def upload_image_logic(student_id :int , file: UploadFile):
    return None

async def get_student_images_logic(student_id: int):
    return None
