import json
from typing import List
from pydantic import BaseModel
from google import genai
from google.genai import types
from src.services.base import BaseService
from utils.logger import app_logger as logger
from src.sql.cruds import content as content_crud
from src.enums.content import ContentStatus


class VideoMetadata(BaseModel):
    title: str
    description: str
    hashtags: List[str]


class LLMService(BaseService):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        super().__init__(provider_name="LLM", env_key_name="GEMINI_API_KEY")
        self.model_name = model_name
        self.client = genai.Client(api_key=self._get_secure_key())
        logger.info(f"LLM client initialized. Target model: {self.model_name}")

    def generate_script(self, topic: str) -> str:
        content = {"title": topic}
        prompt = (
            f"Write a short 50-word YouTube short script about '{topic}' in plain simple Hindi language. "
            f"Do not include brackets, structural cues, scene instructions, emojis or punctuation labels. "
            f"Output must strictly be raw verbal spoken paragraphs text narration only."
        )
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Failed to generate script: {str(e)}")
            raise Exception("Failed to generate script")

    def generate_metadata(self, content: str) -> dict:
        prompt = (
            f"Generate title, description and hashtags for the following content: '{content}' in plain simple and English or Hindi language. "
            f"Do not include brackets, structural cues, scene instructions, emojis or punctuation labels. "
            f"Output must strictly be raw verbal spoken paragraphs text narration only."
        )
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=VideoMetadata,
                ),
            )
            clean_data = response.text.strip()
            logger.info(f"Metadata processed: {clean_data}")
            return json.loads(clean_data)
        except Exception as e:
            logger.error(f"Failed to generate title: {str(e)}")
            raise Exception("Failed to generate metadata")
