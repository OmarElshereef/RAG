from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import studentsRoutes, professorRoutes, coursesRoutes, enrollmentRoutes

app = FastAPI(title="Student Management API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(studentsRoutes.router, prefix="/students", tags=["Students"])
app.include_router(professorRoutes.router, prefix="/professors", tags=["Professors"])
app.include_router(coursesRoutes.router, prefix="/courses", tags=["Courses"])
app.include_router(enrollmentRoutes.router, prefix="/enrollments", tags=["Enrollments"])







@app.get("/")
async def root():
    return {"message": "Student Management API", "version": "1.0.0"}


"""
sqlmodel
docker
vector db
"""