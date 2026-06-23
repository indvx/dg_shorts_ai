from src.services.base import BaseService
from src.integrations.llm import LLMService
from src.integrations.elevenlabs import ElevenLabsService
from src.sql.cruds import content as content_crud, topic as topic_crud
from src.sql.models.content import Content
from src.enums.content import ContentStatus
from utils.logger import logger
from fastapi import HTTPException

class ContentService(BaseService):
    def __init__(self):
        super().__init__()
        self.llm_service = LLMService()
        self.elevenlab_service = ElevenLabsService()

    def create_content(self, topic_id: int):
        try:
            topic = topic_crud.get_unused_topic(self.db, id=topic_id)
            if not topic:
                raise HTTPException(status_code=404, detail="Topic not found, may be all topics are used.")

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

    def generate_audio_from_content(self, content_id: int):
        content = self.get_content(content_id)
        if content.status != ContentStatus.DRAFT:
            raise HTTPException(status_code=400, detail="Content is already processed to generate audio.")

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
        return content

    def get_content(self, content_id: int):
        try:
            content = content_crud.get_content(self.db, content_id)
            if not content:
                raise HTTPException(status_code=404, detail="Content not found")
            return content
        except Exception as e:
            logger.error(f"Internal Server Error: {str(e)}")
            raise Exception(str(e))

    def delete_content(self, content_id: int):
        try:
            content = self.get_content(content_id)
            content_crud.delete_content(self.db, content)
            return {"message": "Content deleted successfully"}
        except Exception as e:
            logger.error(f"Internal Server Error: {str(e)}")
            raise Exception(str(e))

    def get_ready_to_process_content(
        self,
        target_status: list[str] = [],
        excluded: bool = False,
    ):
        try:
            content = content_crud.get_ready_to_process_content(
                self.db, target_status=target_status, excluded=excluded
            )
            return content
        except Exception as e:
            logger.error(f"Internal Server Error: {str(e)}")
            raise Exception(str(e))

    def update_content(self, content_id: int, content_data: dict):
        try:
            content = self.get_content(content_id)
            content_crud.update_content(self.db, content, content_data)
            return content
        except Exception as e:
            logger.error(f"Internal Server Error: {str(e)}")
            raise Exception(str(e))

    def get_days_old_contents(self, days: int = 7):
        try:
            content = content_crud.get_days_old_contents(self.db, days)
            return content
        except Exception as e:
            logger.error(f"Internal Server Error: {str(e)}")
            raise Exception(str(e))

    def get_all_contents(
        self,
        filter: str = None,
        id: int = None,
        ids: list[int] = None,
        status: str = None,
        limit: int = 10,
        page: int = 1,
        sort_by: str = "id",
        order_by: str = "desc",
        start_date: str = None,
        end_date: str = None,
    ):
        try:
            if start_date:
                start_date = datetime.fromisoformat(start_date, "%Y-%m-%d")
            if end_date:
                end_date = datetime.fromisoformat(end_date, "%Y-%m-%d")

            content = content_crud.get_all_contents(
                self.db,
                filter=filter,
                id=id,
                ids=ids,
                status=status,
                limit=limit,
                page=page,
                sort_by=sort_by,
                order_by=order_by,
                start_date=start_date,
                end_date=end_date,
            )
            return content
        except Exception as e:
            logger.error(f"Internal Server Error: {str(e)}")
            raise Exception(str(e))
