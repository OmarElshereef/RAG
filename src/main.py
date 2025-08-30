from fastapi import FastAPI
from src.routers import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from src.helpers.config import get_settings, Settings
from src.stores.LLM.LLMProviderFactory import LLMProviderFactory

app = FastAPI()


async def startup_db_client():
    settings: Settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGO_URI)
    app.db_client = app.mongo_conn[settings.MONGO_DB_NAME]
    print("Connected to the MongoDB database!")

    llm_provider_factory = LLMProviderFactory(settings)

    app.generation_client = llm_provider_factory.create(settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)

    app.embedding_client = llm_provider_factory.create(settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(
        settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_MODEL_SIZE
    )


async def shutdown_db_client():
    app.mongo_conn.close()
    print("MongoDB connection closed!")


app.add_event_handler("startup", startup_db_client)
app.add_event_handler("shutdown", shutdown_db_client)


app.include_router(base.base_router)
app.include_router(data.data_router)


# contextual chunking
