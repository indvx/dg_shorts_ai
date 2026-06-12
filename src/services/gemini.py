from google import genai
from openai import OpenAI
from src.services.base import BaseService
from utils.logger import app_logger as logger


class ScriptService(BaseService):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        # BaseService sets self.provider = provider_name
        super().__init__(provider_name="gemini", env_key_name="GEMINI_API_KEY")
        self.model_name = model_name

        # Instantiate the new Google GenAI Client
        self.client = genai.Client(api_key=self._get_secure_key())
        logger.info(f"Gemini client initialized. Target model: {self.model_name}")

    def openai_client(self, prompt: str) -> str:
        # Standard OpenAI client initialization and chat completions API
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {
                    "role": "system",
                    "content": "You are a script writer for YouTube shorts. Write a short 50-word YouTube short script in plain simple Hindi language. Do not include brackets, structural cues, scene instructions, emojis or punctuation labels. Output must strictly be raw verbal spoken paragraphs text narration only.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content

    def generate_short_script(self, topic: str) -> str:
        content = {"title": topic}
        prompt = (
            f"Write a short 50-word YouTube short script about '{topic}' in plain simple Hindi language. "
            f"Do not include brackets, structural cues, scene instructions, emojis or punctuation labels. "
            f"Output must strictly be raw verbal spoken paragraphs text narration only."
        )

        try:
            # Check self.provider instead of self.provider_name
            if self.provider == "openai":
                clean_script = self.openai_client(prompt).strip()
            else:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
                clean_script = response.text.strip()

            logger.info(f"Script processed: {len(clean_script.split())} words.")
            content["content"] = clean_script
            content["status"] = ContentStatus.DRAFT
            content_crud.create_content(self.db, content)
            return clean_script
        except Exception as e:
            logger.error(f"Failed to generate script: {str(e)}")
            raise Exception("Failed to generate script")
