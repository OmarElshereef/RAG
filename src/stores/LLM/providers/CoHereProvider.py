from ..LLMInterface import LLMInterface
from ..LLMEnums import CohereEnums, DocumentTypeEnums
from cohere import Client
import logging
from typing import List, Union


class CoHereProvider(LLMInterface):

    def __init__(
        self,
        api_key: str,
        default_input_max_characters: int = 1000,
        default_output_max_tokens: int = 1000,
        default_temperature: float = 0.1,
    ):
        self.api_key = api_key
        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_tokens = default_output_max_tokens
        self.default_temperature = default_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = Client(api_key=self.api_key)

        self.logger = logging.getLogger(__name__)

        self.enums = CohereEnums

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        text = text.strip()
        if len(text) > self.default_input_max_characters:
            text = text[: self.default_input_max_characters]
        return text

    def generate_text(
        self,
        prompt: str,
        chat_history: list,
        max_output_token: int,
        temperature: float,
    ):
        if not self.client:
            self.logger.error("Cohere client is not initialized properly.")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model ID is not set.")
            return None

        max_output_token = (
            max_output_token
            if max_output_token is not None
            else self.default_output_max_tokens
        )
        temperature = (
            temperature if temperature is not None else self.default_temperature
        )

        response = self.client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            message=self.process_text(prompt),
            max_tokens=max_output_token,
            temperature=temperature,
        )

        if not response or not response.text:
            self.logger.error("No response from Cohere API.")
            return None

        return response.text

    def embed_text(self, text: Union[List[str], str], document_type: str):
        if not self.client:
            self.logger.error("Cohere client is not initialized properly.")
            return None

        if isinstance(text, str):
            text = [text]

        if not self.embedding_model_id:
            self.logger.error("Embedding model ID is not set.")
            return None

        input_type = (
            self.enums.DOCUMENT.value
            if document_type == DocumentTypeEnums.DOCUMENT.value
            else self.enums.QUERY.value
        )

        response = self.client.embed(
            model=self.embedding_model_id,
            texts=[self.process_text(t) for t in text],
            input_type=input_type,
            embedding_types=["float"],
        )

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("No embedding returned from Cohere API.")
            return None
        return [f for f in response.embeddings.float]

    def construct_prompt(self, prompt: str, role: str):
        return {"role": role, "text": prompt}
