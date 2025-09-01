from fastapi import FastAPI
from src.routers import base, data, NLP
from motor.motor_asyncio import AsyncIOMotorClient
from src.helpers.config import get_settings, Settings
from src.stores.LLM.LLMProviderFactory import LLMProviderFactory
from src.stores.vectorDB.VectorDBProviderFactory import VectorDBProviderFactory
from src.stores.LLM.templates.template_parser import TemplateParser

app = FastAPI()


async def startup_span():
    settings: Settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGO_URI)
    app.db_client = app.mongo_conn[settings.MONGO_DB_NAME]
    print("Connected to the MongoDB database!")

    llm_provider_factory = LLMProviderFactory(settings)
    vector_db_provider_factory = VectorDBProviderFactory(settings)

    app.generation_client = llm_provider_factory.create(settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)

    app.embedding_client = llm_provider_factory.create(settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(
        settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_MODEL_SIZE
    )

    # vector db client
    app.vector_db_client = vector_db_provider_factory.create(settings.VECTOR_DB_BACKEND)
    # print(app.vetcor_db_client)
    print("Vector DB Client created!" + settings.VECTOR_DB_BACKEND)

    app.vector_db_client.connect()

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANGUAGE, default_language=settings.DEFAULT_LANGUAGE
    )


async def shutdown_span():
    app.mongo_conn.close()
    print("MongoDB connection closed!")
    app.vector_db_client.disconnect()


app.add_event_handler("startup", startup_span)
app.add_event_handler("shutdown", shutdown_span)


app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(NLP.nlp_router)

# contextual chunking
