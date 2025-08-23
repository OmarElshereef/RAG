from fastapi import APIRouter, HTTPException, status, UploadFile, File,Depends, Request
from utils.multer import upload_to_supabase_storage
from database.supabase_client import SupabaseClient
from models.enrollment import  EnrollmentCreate, Enrollment
from models.student import Student
from models.course import Course
from typing import List
from controllers import enrollmentController as controller
from middlewares.authetication import verify_professor, verify_student
router = APIRouter()

supabase = SupabaseClient().get_client()



# Enrollment endpoints
#enroll_student
@router.post("/{course_id}", response_model=Enrollment, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_student)])
async def enroll_student(course_id: int, request: Request):
   student_id = request.state.user_id
   return await controller.enroll_student_controller(EnrollmentCreate(course_id=course_id, student_id=student_id))


# Get student courses
@router.get("/students/{student_id}/courses", response_model=List[Course],dependencies=[Depends(verify_professor)])
async def get_student_courses(student_id: int):
    return await controller.get_student_courses_controller(student_id)

# Get course students
#test
@router.get("/courses/{course_id}/students", response_model=List[Student], dependencies=[Depends(verify_professor)])
async def get_course_students(course_id: int):
    return await controller.get_course_students_controller(course_id)

# Unenroll student from course
# Professor removes a student from a course
@router.delete("/enrollments/{student_id}/{course_id}",status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_professor)]) 
async def unenroll_student_as_professor(student_id: int, course_id: int,request: Request):
    professor_id = request.state.user_id
    return await controller.unenroll_student_as_professor(student_id, course_id,professor_id)


# Student removes themselves from a course
@router.delete("/enrollments/{course_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_student)])
async def unenroll_self_from_course(course_id: int, request: Request):
    student_id = request.state.user_id
    return await controller.unenroll_self(student_id, course_id)