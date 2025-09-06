from .BaseController import BaseController
from .ProjectController import ProjectController
from src.models import ProcessingEnum
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from typing import List
import os

from dataclasses import dataclass


@dataclass
class Document:
    page_content: str
    metadata: dict


class ProcessController(BaseController):
    def __init__(self, project_id: int):
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(self.project_id)

    def get_file_extension(self, file_id: str) -> str:
        return os.path.splitext(file_id)[-1]

    def get_file_loader(self, file_id: str):
        file_extension = self.get_file_extension(file_id)
        file_path = os.path.join(self.project_path, file_id)

        if not os.path.exists(file_path):
            return None

        if file_extension == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding="utf-8")

        elif file_extension == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)

        else:
            return None

    def get_file_content(self, file_id: str):
        loader = self.get_file_loader(file_id)
        if loader:
            documents = loader.load()
            return documents
        else:
            return None

    def process_file_content(
        self,
        file_content: list,
        file_id: str,
        chunk_size: int = 100,
        overlap_size: int = 20,
    ):

        file_content_texts = [rec.page_content for rec in file_content]

        file_content_metadata = [rec.metadata for rec in file_content]

        """ chunks = text_splitter.create_documents(
            file_content_texts, metadatas=file_content_metadata
        ) """

        chunks = self.process_simpler_splitter(
            file_content_texts, file_content_metadata, chunk_size
        )

        return chunks

    def process_simpler_splitter(
        self,
        texts: List[str],
        metadatas: List[dict],
        chunk_size: int,
        splitter_tag: str = "\n",
    ):
        full_text = " ".join(texts)

        lines = [
            doc.strip() for doc in full_text.split(splitter_tag) if doc.strip() != ""
        ]

        chunks = []
        current_chunk = ""

        for line in lines:
            current_chunk += line + splitter_tag
            if len(current_chunk) >= chunk_size:
                chunks.append(Document(page_content=current_chunk.strip(), metadata={}))
                current_chunk = ""

        if len(current_chunk) > 0:
            chunks.append(Document(page_content=current_chunk.strip(), metadata={}))
            current_chunk = ""

        return chunks
