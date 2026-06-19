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
        self.model_name = os.getenv("AI_MODEL_NAME")
        self.provider = os.getenv("AI_PROVIDER_NAME")
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
            You are an elite YouTube Shorts writer.

            Topic: {topic}

            Goal:
            Maximize retention and rewatch rate.

            Rules:
            - 55-75 words
            - First line must create shock, surprise, or curiosity
            - Never reveal the answer immediately
            - Every sentence should create a new question
            - Build suspense continuously
            - Use simple Hindi
            - Keep sentences short
            - Final line must deliver the payoff
            - End with a thought-provoking statement

            Formula:
            Hook
            +
            Mystery
            +
            Escalation
            +
            Reveal

            Return ONLY narration text.
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

            Content:
            {content}

            Requirements:

            TITLE:
            - Maximum 55 characters
            - Curiosity-driven
            - High click-through rate
            - No clickbait
            - No emojis
            - Must create urgency or intrigue

            DESCRIPTION:
            - 1-2 short sentences
            - Summarize the video
            - Encourage engagement naturally

            HASHTAGS:
            - Generate 5 relevant hashtags
            - No # symbol
            - Include niche hashtags
            - Include one broad viral hashtag

            Return ONLY JSON.
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
            You are a viral YouTube Shorts strategist.

            Generate ONE highly viral Shorts topic.

            Requirements:
            - Must trigger curiosity
            - Must sound surprising
            - Must be fact-based
            - Suitable for a 30-60 second video
            - Must have potential for high retention
            - Must make viewers think "Wait, really?"
            - Avoid generic motivation topics
            - Avoid celebrity gossip
            - Prefer:
            - AI
            - Technology
            - Science
            - Space
            - Psychology
            - History
            - Mystery facts
            - Business secrets

            Return ONLY the topic text.

            Categories:
            {category_text}
        """
        return self._generate(prompt)
