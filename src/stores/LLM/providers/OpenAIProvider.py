from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums
from openai import OpenAI
import logging
from typing import List, Union


class OpenAIProvider(LLMInterface):

    def __init__(
        self,
        api_key: str,
        api_url: str = None,
        default_input_max_characters: int = 1000,
        default_output_max_tokens: int = 1000,
        default_temperature: float = 0.1,
    ):
        self.api_key = api_key
        self.api_url = api_url
        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_tokens = default_output_max_tokens
        self.default_temperature = default_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(api_key=self.api_key, base_url=self.api_url)
        self.logger = logging.getLogger(__name__)

        self.enums = OpenAIEnums

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def generate_text(
        self,
        prompt: str,
        chat_history: list = [],
        max_output_token: int = None,
        temperature: float = None,
    ):
        if not self.client:
            self.logger.error("OpenAI client is not initialized properly.")
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

        chat_history.append(self.construct_prompt(prompt, self.enums.USER.value))

        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_token,
            temperature=temperature,
        )

        if (
            not response
            or not response.choices
            or len(response.choices) == 0
            or not response.choices[0].message
        ):
            self.logger.error("Failed to get response from OpenAI.")
            return None

        return response.choices[0].message.content

    def embed_text(self, text: Union[List[str], str], document_type: str = None):
        if not self.client:
            self.logger.error("OpenAI client is not initialized properly.")
            return None

        if not self.embedding_model_id or not self.embedding_size:
            self.logger.error("Embedding model ID or size is not set.")
            return None

        if isinstance(text, str):
            text = [text]

        response = self.client.embeddings.create(
            input=text, model=self.embedding_model_id
        )

        if (
            not response
            or not response.data
            or len(response.data) == 0
            or not response.data[0].embedding
        ):
            self.logger.error("Failed to get embedding from OpenAI.")
            return None

        return [f.embedding for f in response.data]

    def construct_prompt(self, prompt: str, role: str):
        return {"role": role, "content": prompt}

    def process_text(self, text: str):
        text = text.strip()
        if len(text) > self.default_input_max_characters:
            text = text[: self.default_input_max_characters]
        return text
