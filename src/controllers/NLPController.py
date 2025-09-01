from .BaseController import BaseController
from src.models.db_schemas import DataChunk, Project
from src.stores.vectorDB.VectorDBInterface import VectorDBInterface
from src.stores.LLM.LLMInterface import LLMInterface
from src.stores.LLM.LLMEnums import DocumentTypeEnums
from src.stores.LLM.templates.template_parser import TemplateParser
from typing import List
import json


class NLPController(BaseController):
    def __init__(
        self,
        vector_db_client: VectorDBInterface,
        embedding_client: LLMInterface,
        generation_client: LLMInterface,
        template_parser: TemplateParser,
    ):
        super().__init__()

        self.vector_db_client = vector_db_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str) -> str:
        return f"collection_{project_id}".strip()

    def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(str(project.project_id))
        return self.vector_db_client.delete_collection(collection_name)

    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(str(project.project_id))
        return self.vector_db_client.get_collection_info(collection_name)

    def index_into_vector_db(
        self,
        project: Project,
        chunks: List[DataChunk],
        do_reset: bool = False,
    ):
        collection_name = self.create_collection_name(str(project.project_id))

        texts = [chunk.text for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        vectors = [
            self.embedding_client.embed_text(text, DocumentTypeEnums.DOCUMENT.value)
            for text in texts
        ]

        _ = self.vector_db_client.create_collection(
            collection_name, self.embedding_client.embedding_size, do_reset
        )

        record_ids = list(range(len(chunks)))

        _ = self.vector_db_client.insert_many(
            collection_name,
            texts,
            vectors,
            metadatas,
            record_ids=record_ids,
            batch_size=100,
        )

        return True

    def search_vector_db_collection(self, project: Project, text: str, limit: int = 5):
        collection_name = self.create_collection_name(str(project.project_id))

        vector = self.embedding_client.embed_text(text, DocumentTypeEnums.QUERY.value)

        if not vector:
            return False

        results = self.vector_db_client.search_by_vector(
            collection_name, vector, limit=limit
        )
        if not results:
            return False

        return results

    def answer_rag_question(self, project: Project, query: str, limit: int = 5):

        retrieved_docs = self.search_vector_db_collection(project, query, limit)
        if not retrieved_docs:
            return None, None, None

        system_prompt = self.template_parser.get("rag", "system_prompt", {})

        """ document_prompt = []
        for idx, doc in enumerate(retrieved_docs):
            document_prompt.append(
                self.template_parser.get(
                    "rag",
                    "document_prompt",
                    {"doc_num": idx + 1, "content": doc.text},
                )
            ) """

        document_prompt = "\n".join(
            [
                self.template_parser.get(
                    "rag",
                    "document_prompt",
                    {"doc_num": idx + 1, "content": doc.text},
                )
                for idx, doc in enumerate(retrieved_docs)
            ]
        )

        footer_prompt = self.template_parser.get("rag", "footer_prompt", {})

        chat_history = [
            self.generation_client.construct_prompt(
                system_prompt, role=self.generation_client.enums.SYSTEM.value
            )
        ]

        full_prompt = "\n\n".join({document_prompt, footer_prompt})

        answer = self.generation_client.generate_text(
            full_prompt, chat_history, 512, 0.1
        )

        return answer, full_prompt, chat_history
