from fastapi import APIRouter, HTTPException, status,Depends,Request
from database.supabase_client import SupabaseClient
from models.course import Course, CourseCreate
from typing import List
from controllers import courseController as controller 
from middlewares.authetication import verify_professor, verify_token
router = APIRouter()

supabase = SupabaseClient().get_client()





# Course endpoints
#create_course
@router.post("/courses", response_model=Course, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_professor)])
async def create_course(course: CourseCreate,request: Request):
    professor_id = request.state.user_id
    return await controller.create_course_controller(course,professor_id)

#get_all_courses
@router.get("/courses", response_model=List[Course], dependencies=[Depends(verify_token)])
async def get_all_courses():
    return await controller.get_all_courses_controller()

#get_course
@router.get("/courses/{course_id}", response_model=Course, dependencies=[Depends(verify_token)])
async def get_course(course_id: int):
    return await controller.get_course_controller(course_id)

