import json
import time
from typing import List, Optional
from pydantic import BaseModel, ValidationError

from google import genai
from openai import OpenAI

from src.services.base import BaseService
from utils.logger import logger
import os


class VideoMetadata(BaseModel):
    title: str
    description: str
    hashtags: List[str]


class LLMService(BaseService):
    def __init__(self):
        super().__init__()

        self.gemini_client = None
        self.openai_client = None
        self.model_name = os.getenv("AI_MODEL_NAME", "gemini-2.5-flash")
        self.provider = os.getenv("AI_PROVIDER_NAME", "gemini")
        self.api_key = os.getenv("AI_API_KEY")

        logger.info(f"AI Provider: {self.provider}")
        logger.info(f"AI Model: {self.model_name}")

        if self.provider == "gemini":
            self.gemini_client = genai.Client(api_key=self.api_key)
        else:
            self.openai_client = OpenAI(api_key=self.api_key)

        logger.info(f"LLM initialized using provider: {self.provider}")

    def _generate(self, prompt: str) -> str:
        max_retries = 3
        delay = 2

        for attempt in range(max_retries):
            try:
                if self.provider == "gemini":
                    response = self.gemini_client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                    )
                    return response.text.strip()

                else:
                    response = self.openai_client.chat.completions.create(
                        model=self.model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                    )
                    return response.choices[0].message.content.strip()

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")

                if attempt == max_retries - 1:
                    logger.error("LLM generation failed permanently")
                    raise RuntimeError("LLM generation failed") from e

                time.sleep(delay)
                delay *= 2

        raise RuntimeError("Unreachable code reached in _generate")

    def generate_script(self, topic: str) -> str:
        prompt = f"""
            Write a 50-word YouTube Shorts script in simple Hindi.
            Topic: {topic}
            Rules:
                - Only narration text
                - No emojis
                - No scene instructions
                - No labels
                - Natural spoken style
            """
        return self._generate(prompt)

    def generate_metadata(self, content: str) -> VideoMetadata:
        prompt = f"""
            Return ONLY valid JSON.
            Schema:
            {{
                "title": "string",
                "description": "string",
                "hashtags": ["tag1", "tag2", "tag3"]
            }}
            Rules:
                - Generate a catchy, click-worthy title for the YouTube Short based on the content.
                - Generate an engaging description summarizing the content.
                - Generate 3 to 5 relevant hashtags (without the '#' symbol) based on the content and place them in the 'hashtags' list.
                - Return ONLY the JSON object. No extra text, no markdown block, no explanation.
            Content: {content}
        """

        raw = self._generate(prompt)
        try:
            data = json.loads(raw)
            logger.info(f"Metadata generated: {data}")
            return VideoMetadata(**data)

        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Metadata parsing failed: {str(e)}")
            raise RuntimeError("Invalid metadata format") from e

    def generate_topic(self, categories: Optional[str] = None) -> str:
        category_text = (
            f"Choose from: {categories}"
            if categories
            else "Choose any interesting topic"
        )

        prompt = f"""
            Generate ONE viral YouTube Shorts topic.
            Requirements:
                - Curiosity driven
                - 30–60 second video
                - Catchy and short
                - Return ONLY topic text
            {category_text}
        """
        return self._generate(prompt)
