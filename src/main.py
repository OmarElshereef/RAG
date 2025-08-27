from fastapi import FastAPI
from src.routers import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from src.helpers.config import get_settings, Settings

app = FastAPI()


@app.on_event("startup")
async def startup_db_client():
    settings: Settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGO_URI)
    app.db_client = app.mongo_conn[settings.MONGO_DB_NAME]
    print("Connected to the MongoDB database!")


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_conn.close()
    print("MongoDB connection closed!")


app.include_router(base.base_router)
app.include_router(data.data_router)


# contextual chunking
