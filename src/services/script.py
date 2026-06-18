from src.services.base import BaseService
from utils.logger import logger
from src.sql.cruds import (
    content as content_crud,
    short_video as short_video_crud,
    topic as topic_crud,
)
from src.enums.content import ContentStatus
from src.enums.short_video import ShortVideoStatus
from src.services.integrations.llm import LLMService
from src.services.integrations.elevenlabs import ElevenLabsService
from src.services.integrations.youtube import YouTubeService
from datetime import datetime, UTC


class ScriptService(BaseService):
    def __init__(self):
        super().__init__()
        logger.info(f"Script Service initialized.")
        self.llm_service = LLMService()
        self.elevenlab_service = ElevenLabsService()

    def generate_topic(self, topic: str | None = None) -> str:
        try:
            new_topic = self.llm_service.generate_topic(topic)
        except Exception as e:
            logger.error(f"Failed to generate topic: {str(e)}")
            raise Exception(f"Failed to generate topic: {str(e)}")
        
        topic_slug = self.get_topic_slug(new_topic)
        existing = topic_crud.get_topic_by_slug(self.db, topic_slug)
        if existing:
            return existing.name
        new_topic = topic_crud.add_topic(self.db, new_topic, topic_slug)
        return new_topic.name

    def generate_script(self, topic_id: int):
        try:
            topic = topic_crud.get_unused_topic(self.db, id=topic_id)
            if not topic:
                raise ValueError("Topic not found, may be all topics are used.")

            content = {"title": topic.name}
            script = self.llm_service.generate_script(topic.name)
            logger.info(f"Script processed: {len(script.split())} words.")
            content["content"] = script
            content["status"] = ContentStatus.DRAFT
            new_content = content_crud.create_content(self.db, content)
            topic_crud.update_topic(self.db, topic)
            return new_content
        except Exception as e:
            logger.error(f"Failed to generate script: {str(e)}")
            raise Exception(f"Failed to generate content: {str(e)}")

    def generate_audio_from_content(self, content_id: int) -> dict:
        content = content_crud.get_content(self.db, content_id)
        if not content:
            raise ValueError("Content not found")

        if content.status in [
            ContentStatus.AUDIO_GENERATED,
            ContentStatus.VIDEO_GENERATED,
            ContentStatus.MERGED,
            ContentStatus.ERROR,
        ]:
            raise ValueError("Content already processed.")

        try:
            response = self.elevenlab_service.generate_speech_file(content)
        except Exception as e:
            logger.error(f"Failed to generate audio: {str(e)}")
            raise Exception(f"Failed to generate audio: {str(e)}")

        content_crud.update_content(
            self.db,
            content,
            {
                "status": ContentStatus.AUDIO_GENERATED,
                "audio_path": response,
            },
        )
        return {
            "content_id": content.id,
            "audio_path": response,
            "status": ContentStatus.AUDIO_GENERATED,
        }

    def update_video_content_metadata(self, video_id: int):
        logger.info(f"Updating video path in database for content: {video_id}")
        short_video = short_video_crud.get_short_video(self.db, video_id)
        if not short_video:
            raise ValueError("Short video not found for provided content id")

        if short_video.status != ShortVideoStatus.NOT_STARTED:
            raise ValueError("Short video already processed or failed!")

        content_text = short_video.content.content

        # generate metadata
        try:
            metadata = self.llm_service.generate_metadata(content_text)
            metadata_dict = (
                metadata.model_dump()
                if hasattr(metadata, "model_dump")
                else metadata.dict()
            )
        except Exception as e:
            logger.error(f"Failed to generate metadata: {str(e)}")
            raise Exception(f"Failed to generate metadata: {str(e)}")

        updated_short_video = short_video_crud.update_short_video(
            self.db, short_video, metadata_dict
        )
        return {
            "content_id": short_video.content.id,
            "video_id": updated_short_video.id,
            "title": updated_short_video.title,
            "video_path": updated_short_video.output_path,
            "description": updated_short_video.description,
            "tags": updated_short_video.tags,
            "status": updated_short_video.status,
        }

    def upload_video_to_youtube(self, video_id: int):
        short_video = short_video_crud.get_short_video(self.db, video_id)
        if not short_video:
            raise ValueError("Short video not found for provided content id")

        if short_video.status in [
            ShortVideoStatus.COMPLETED,
            ShortVideoStatus.PUBLISHED,
        ]:
            raise ValueError("Short video already published.")

        video_path = short_video.output_path
        title = short_video.title
        description = short_video.description
        tags_list = [t.strip() for t in short_video.tags.split(",") if t.strip()]

        try:
            response = YouTubeService().upload_shorts_video(
                video_path, title, description, tags_list
            )
            # Update database status on successful upload
            short_video_crud.update_short_video(
                self.db,
                short_video,
                {
                    "youtube_video_path": f"https://youtu.be/{response}",
                    "status": ShortVideoStatus.PUBLISHED,
                    "published_at": datetime.now(UTC),
                },
            )
            content_crud.update_content(
                self.db,
                short_video.content,
                {
                    "status": ContentStatus.VIDEO_PUBLISHED,
                },
            )
            return response
        except Exception as e:
            logger.error(f"Failed to upload video: {str(e)}")
            raise Exception(f"Failed to upload video: {str(e)}")
