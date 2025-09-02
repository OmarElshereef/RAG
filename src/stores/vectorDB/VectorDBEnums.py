from enum import Enum


class VectorDBEnums(Enum):
    QDRANT = "QDRANT"
    PGVECTOR = "PGVECTOR"


class DistanceMethodEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"


class PgVectorDistanceMethodEnums(Enum):
    COSINE = "vector_cosine_ops"
    DOT = "vector_12_ops"


class PgVecotrTableSchemeEnums(Enum):
    ID = "id"
    TEXT = "text"
    METADATA = "metadata"
    VECTOR = "vector"
    CHUNK_ID = "chunk_id"
    _PREFIX = "pgvector"


class PgVectorIndexTypeEnums(Enum):
    IVFFLAT = "ivfflat"
    HNSW = "hnsw"
    BRUTEFORCE = "bruteforce"
