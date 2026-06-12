import os
import requests
from sqlalchemy.orm import Session
from src.services.base import BaseService
from utils.logger import app_logger as logger
from src.sql.cruds import content as content_crud
from elevenlabs.client import ElevenLabs
from src.enums.content import ContentStatus
import uuid
from io import BytesIO


class AudioService(BaseService):
    def __init__(self):
        super().__init__(
            provider_name="ElevenLabs Voice Engine", env_key_name="ELEVENLABS_API_KEY"
        )
        self._elevenlabs = ElevenLabs(api_key=self._get_secure_key())

    def generate_speech_file(self, content_id: int) -> str:
        logger.info(
            "Initializing Text-to-Speech synthesis pipeline sequence via ElevenLabs..."
        )

        content = content_crud.get_content(self.db, content_id)
        if not content:
            raise ValueError("Content not found")

        if content.status in [
            ContentStatus.AUDIO_GENERATED,
            ContentStatus.VIDEO_GENERATED,
            ContentStatus.MERGED,
            ContentStatus.VIDEO_PUBLISHED,
        ]:
            raise ValueError("Content already processed.")

        output_destination = f"data/audio/{content.id}#{uuid.uuid4()}.mp3"
        try:
            response = self._elevenlabs.text_to_speech.convert(
                text=content.content,
                voice_id="JBFqnCBsd6RMkjVDRZzb",
                model_id="eleven_v3",
                output_format="mp3_44100_128",
            )

            logger.info(f"ElevenLabs response: {response}")
            audio_stream = BytesIO()
            for chunk in response:
                if chunk:
                    audio_stream.write(chunk)
            audio_stream.seek(0)
            with open(output_destination, "wb") as audio_file:
                audio_file.write(audio_stream.read())

            logger.info(
                f"Audio binary output completely stream-flushed onto local disk path: {output_destination}"
            )

            content_crud.update_content(
                self.db,
                content,
                {
                    "status": ContentStatus.AUDIO_GENERATED,
                    "audio_path": output_destination,
                },
            )
            return {
                "audio_path": output_destination,
                "content_id": content.content,
                "message": "Audio generated successfully",
            }

        except Exception as audio_fault:
            logger.error(
                f"Failed synthesizing voice sequence array: {str(audio_fault)}"
            )
            raise RuntimeError(
                "Audio pipeline orchestration breakdown"
            ) from audio_fault
