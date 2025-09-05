from abc import ABC, abstractmethod
from typing import List
from src.models.db_schemas import RetrievedDocument


class VectorDBInterface(ABC):

    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def collection_exists(self, collection_name: str) -> bool:
        pass

    @abstractmethod
    def list_all_collections(self) -> List:
        pass

    @abstractmethod
    def get_collection_info(self, collection_name: str) -> dict:
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str):
        pass

    @abstractmethod
    def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ) -> bool:
        pass

    @abstractmethod
    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list,
        metadata: dict = None,
        record_id: int = None,
    ):
        pass

    @abstractmethod
    def insert_many(
        self,
        collection_name: str,
        texts: List[str],
        vectors: List[list],
        metadatas: List[dict] = None,
        record_ids: List[int] = None,
        batch_size: int = 50,
    ):
        pass

    @abstractmethod
    def search_by_vector(
        self, collection_name: str, vector: list, limit: int
    ) -> List[RetrievedDocument]:
        pass
