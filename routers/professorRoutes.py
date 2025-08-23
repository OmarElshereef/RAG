from fastapi import APIRouter, status, Depends
from typing import List
from models.user import ProfessorCreate, User, UserReturn,UserLogin,UserBase
from controllers import professorController as controller
from middlewares.authetication import verify_professor


router = APIRouter()




@router.post("/signup", response_model=UserReturn, status_code=status.HTTP_201_CREATED)
async def create_professor(professor: ProfessorCreate):
    return await controller.create_professor_logic(professor)


@router.post("/login", response_model=UserReturn, status_code=status.HTTP_200_OK)
async def login_professor(professor: UserLogin):
    return await controller.login_professor_logic(professor)

@router.get("/", response_model=List[User], dependencies=[Depends(verify_professor)])
async def get_all_professors():
    return await controller.get_all_professors_logic()
