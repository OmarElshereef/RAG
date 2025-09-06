from fastapi import FastAPI
from src.routers import base, data, NLP
from src.helpers.config import get_settings, Settings
from src.stores.LLM.LLMProviderFactory import LLMProviderFactory
from src.stores.vectorDB.VectorDBProviderFactory import VectorDBProviderFactory
from src.stores.LLM.templates.template_parser import TemplateParser
from src.utils.metrics import setup_metrics
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

app = FastAPI()

setup_metrics(app)


async def startup_span():
    settings: Settings = get_settings()

    postgres_url = f"postgresql+asyncpg://{settings.POSGRES_USERNAME}:{settings.POSGRES_PASSWORD}@{settings.POSGRES_HOST}:{settings.POSGRES_PORT}/{settings.POSGRES_MAIN_DB}"

    app.db_engine = create_async_engine(postgres_url)

    app.db_client = sessionmaker(
        app.db_engine, class_=AsyncSession, expire_on_commit=False
    )
    print("Connected to the PostgreSQL database!")

    llm_provider_factory = LLMProviderFactory(settings)
    vector_db_provider_factory = VectorDBProviderFactory(
        settings, db_client=app.db_client
    )

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

    await app.vector_db_client.connect()

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANGUAGE, default_language=settings.DEFAULT_LANGUAGE
    )


async def shutdown_span():
    await app.db_engine.dispose()
    print("PostgreSQL connection closed!")
    await app.vector_db_client.disconnect()


app.add_event_handler("startup", startup_span)
app.add_event_handler("shutdown", shutdown_span)


app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(NLP.nlp_router)

# contextual chunking
