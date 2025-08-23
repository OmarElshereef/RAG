from fastapi import HTTPException, status
from models.course import CourseCreate,CourseInsertion, Course
from database.mongo_client import MongoDBClient
from bson import ObjectId

db = MongoDBClient.get_client()


users_collection = db["users"]
courses_collection = db["courses"]

async def create_course_controller(course: CourseCreate, professor_id: str):
    
    prof = await users_collection.find_one({"_id": ObjectId(professor_id), "role": "professor"})
    if not prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professor not found"
        )

    
    existing_course = await courses_collection.find_one({"code": course.code})
    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Course with this code already exists"
        )

    
    course_data = course.model_dump()
    course_insertion = CourseInsertion(
        **course_data,
        professor_id=professor_id
    )

    
    insert_result = await courses_collection.insert_one(course_insertion.model_dump())

    if not insert_result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create course"
        )

    
    created_course = await courses_collection.find_one({"_id": insert_result.inserted_id})
    print(f"Created course: {created_course}")
    return Course(** created_course)



async def get_all_courses_controller():

    result = await courses_collection.find().to_list(length=None)
    if not result:
        return []
    courses = [Course(**course) for course in result]
    return courses




async def get_course_controller(course_id: str):
    try:
        if not ObjectId.is_valid(course_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid course ID"
            )

        course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        return Course(**course)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch course: {str(e)}"
        )