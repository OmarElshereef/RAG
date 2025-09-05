from .providers import QdrantDBProvider, PgVectorProvider
from .VectorDBEnums import VectorDBEnums
from src.controllers.BaseController import BaseController
from sqlalchemy.orm import sessionmaker
from src.helpers.config import Settings


class VectorDBProviderFactory:
    def __init__(self, config: dict, db_client: sessionmaker):
        self.config = config
        self.db_client = db_client

    def create(self, provider: str):
        if provider == VectorDBEnums.QDRANT.value:
            qdrant_db_client = BaseController().get_database_path(
                self.config.VECTOR_DB_PATH
            )
            return QdrantDBProvider(
                db_client=qdrant_db_client,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
                default_vector_size=self.config.EMBEDDING_MODEL_SIZE,
                index_threshold=self.config.VECTOR_DB_PGVEC_INDEX_THRSHOLD,
            )
        elif provider == VectorDBEnums.PGVECTOR.value:
            return PgVectorProvider(
                db_client=self.db_client,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
                default_vector_size=self.config.EMBEDDING_MODEL_SIZE,
                index_threshold=self.config.VECTOR_DB_PGVEC_INDEX_THRSHOLD,
            )

        return None
