from fastapi import HTTPException, status, Response
from models.user import (ProfessorCreate, ProfessorInsert, User, UserBase, UserReturn, UserLogin)
from database.mongo_client import MongoDBClient
from utils.auth import create_access_token, hash_password, verify_password
from datetime import datetime
from bson import ObjectId

db = MongoDBClient.get_client()
users_collection = db["users"]

async def create_professor_logic(professor: ProfessorCreate):
    
    existing = await users_collection.find_one({"email": professor.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    professor.password = hash_password(professor.password)
    
    
    insertion = ProfessorInsert(
        **professor.model_dump(),
        created_at=datetime.now()
    )

    
    user_doc = insertion.to_user_doc()

    # Insert into MongoDB users collection
    result = await users_collection.insert_one(user_doc)
    if not result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

    # Create access token
    token = create_access_token({
        "user_id": str(result.inserted_id), 
        "role": "professor"
    })

    # Return user data
    return_user = UserReturn(
        id=str(result.inserted_id),
        name=insertion.name,
        email=insertion.email,
        role="professor",
        created_at=insertion.created_at,
        profile=user_doc["profile"],
        token=token
    )

    return return_user

async def login_professor_logic(professor: UserLogin):
    
    user = await users_collection.find_one({"email": professor.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    
    if user.get("role") != "professor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not a professor account"
        )

    if not verify_password(professor.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )

    token = create_access_token({
        "user_id": str(user["_id"]), 
        "role": "professor"
    })

    return_user = UserReturn(
        **user,
        token=token
    )

    return return_user

async def get_all_professors_logic():
    # Find all users with professor role
    result = await users_collection.find({"role": "professor"}).to_list(length=None)
    if not result:
        return []
    professors = [User(**professor) for professor in result]
    
    return professors


async def get_professor_logic(professor_id: str):
    try:
        
        if not ObjectId.is_valid(professor_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid professor ID format"
            )
        
        professor = await users_collection.find_one({
            "_id": ObjectId(professor_id),
            "role": "professor"
        })
        
        if not professor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Professor not found"
            )
        
        return User(**professor)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve professor: {str(e)}"
        )