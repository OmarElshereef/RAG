from fastapi import APIRouter, Response, status, UploadFile, File, Depends,Request
from typing import List
from middlewares.authetication import verify_student,verify_professor
from models.user import StudentCreate, UserLogin, UserReturn,User
from controllers import studentsController as controller

router = APIRouter()

@router.post("/signup", response_model=UserReturn, status_code=status.HTTP_201_CREATED)
async def signup_student(student: StudentCreate, response: Response):
    return await controller.signup_student_logic(student, response)

@router.post("/login", response_model=UserReturn, status_code=status.HTTP_200_OK)
async def login_student(student: UserLogin, response: Response):
    return await controller.login_student_logic(student, response)

@router.get("/", response_model=List[User],  dependencies=[Depends(verify_professor)])
async def get_all_students():
    return await controller.get_all_students_logic()


@router.get("/me", response_model=User, dependencies=[Depends(verify_student)])
async def get_my_student(request: Request):
    student_id = request.state.user_id
    return await controller.get_student_logic(student_id)


@router.get("/{student_id}", response_model=User, dependencies=[Depends(verify_professor)])
async def get_student(student_id: int):
    return await controller.get_student_logic(student_id)

@router.post("/images", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_student)])
async def upload_image(request:Request, file: UploadFile = File(...)):
    student_id = request.state.user_id
    return await controller.upload_image_logic(student_id, file)

@router.get("/images", dependencies=[Depends(verify_student)])
async def get_student_images(request: Request):
    student_id = request.state.user_id
    return await controller.get_student_images_logic(student_id)
