from fastapi import APIRouter, HTTPException, status, UploadFile, File
from utils.multer import upload_to_supabase_storage
from database.supabase_client import SupabaseClient
from models.enrollment import  EnrollmentCreate, Enrollment
from models.student import Student
from models.course import Course
from typing import List

supabase = SupabaseClient().get_client()


async def enroll_student_controller(enrollment: EnrollmentCreate):
    try:
        student_result = supabase.table("students").select("id").eq("id", enrollment.student_id).execute()
        if not student_result.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        
        
        course_result = supabase.table("courses").select("*").eq("id", enrollment.course_id).execute()
        if not course_result.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        
        
        course = course_result.data[0]
        if course["current_enrollment"] >= course["max_students"]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Course is full")
        
        
        existing_enrollment = supabase.table("enrollments").select("*").eq("student_id", enrollment.student_id).eq("course_id", enrollment.course_id).execute()
        if existing_enrollment.data:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student already enrolled in this course")
        
        
        result = supabase.table("enrollments").insert(enrollment.model_dump()).execute()
        
        if not result.data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to enroll student")
        
        

        new_count = course["current_enrollment"] + 1
        update_result = supabase.table("courses").update({
            "current_enrollment": new_count
        }).eq("id", enrollment.course_id).execute()
        
        if not update_result.data:
            
            supabase.table("enrollments").delete().eq("student_id", enrollment.student_id).eq("course_id", enrollment.course_id).execute()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update enrollment count")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_student_courses_controller(student_id: int):
    try:
        
        student_check = supabase.table("students").select("id").eq("id", student_id).execute()
        if not student_check.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        
        
        enrollments = supabase.table("enrollments").select("course_id").eq("student_id", student_id).execute()
        
        if not enrollments.data:
            return []
        
        course_ids = [e["course_id"] for e in enrollments.data]
        
       
        courses = supabase.table("courses").select("*").in_("id", course_ids).execute()
        
        return courses.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_course_students_controller(course_id: int):
    try:
        
        course_check = supabase.table("courses").select("id").eq("id", course_id).execute()
        if not course_check.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        
        
        enrollments = supabase.table("enrollments").select("student_id").eq("course_id", course_id).execute()
        
        if not enrollments.data:
            return []
        
        student_ids = [e["student_id"] for e in enrollments.data]
        
        
        students = supabase.table("students").select("*").in_("id", student_ids).execute()
        
        return students.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def unenroll_self(student_id: int, course_id: int):
    try:
        
        enrollment = supabase.table("enrollments").select("*").eq("student_id", student_id).eq("course_id", course_id).execute()
        if not enrollment.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
        
        
        delete_result = supabase.table("enrollments").delete().eq("student_id", student_id).eq("course_id", course_id).execute()
        
        if not delete_result.data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete enrollment")
        
        
        course_result = supabase.table("courses").select("*").eq("id", course_id).execute()  
        if not course_result.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
            
        course = course_result.data[0]
        new_count = max(0, course["current_enrollment"] - 1)  
        update_result = supabase.table("courses").update({
            "current_enrollment": new_count
        }).eq("id", course_id).execute()  
        
        if not update_result.data:
            
            supabase.table("enrollments").insert({
                "student_id": student_id,
                "course_id": course_id
            }).execute()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update enrollment count")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



async def unenroll_student_as_professor(student_id: int, course_id: int, professor_id: int):
    try:
        
        course_check = supabase.table("courses").select("*").eq("id", course_id).execute()
        if not course_check.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

        if not course_check.data[0]["professor_id"] == professor_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to unenroll students from this course")
        
        enrollment = supabase.table("enrollments").select("*").eq("student_id", student_id).eq("course_id", course_id).execute()
        if not enrollment.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
        
        
        delete_result = supabase.table("enrollments").delete().eq("student_id", student_id).eq("course_id", course_id).execute()
        
        if not delete_result.data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete enrollment")
        
        
        course = course_check.data[0]
        new_count = max(0, course["current_enrollment"] - 1)  
        update_result = supabase.table("courses").update({
            "current_enrollment": new_count
        }).eq("id", course_id).execute()  
        
        if not update_result.data:
            
            supabase.table("enrollments").insert({
                "student_id": student_id,
                "course_id": course_id
            }).execute()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update enrollment count")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))