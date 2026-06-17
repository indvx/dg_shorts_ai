import os
from src.services.base import BaseService
from utils.logger import app_logger as logger
from elevenlabs.client import ElevenLabs
import uuid
from io import BytesIO


class ElevenLabsService(BaseService):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self._elevenlabs = ElevenLabs(api_key=self.api_key)
        self.audio_directory = os.getenv("AUDIO_DIRECTORY", "data/audio")

    def generate_speech_file(self, content) -> str:
        logger.info(
            "Initializing Text-to-Speech synthesis pipeline sequence via ElevenLabs..."
        )
        os.makedirs(self.audio_directory, exist_ok=True)
        output_destination = os.path.join(self.audio_directory, f"{content.id}#{uuid.uuid4()}.mp3")
        try:
            response = self._elevenlabs.text_to_speech.convert(
                text=content.content,
                voice_id=content.voice_id or "JBFqnCBsd6RMkjVDRZzb",
                model_id="eleven_v3",
                output_format="mp3_44100_128",
            )
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
            return output_destination

        except Exception as audio_fault:
            logger.error(f"Failed synthesizing voice sequence array: {str(audio_fault)}")
            raise RuntimeError("Audio pipeline orchestration breakdown") from audio_fault