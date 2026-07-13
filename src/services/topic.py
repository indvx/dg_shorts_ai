from src.services.base import BaseService
from src.sql.cruds import topic as topic_crud
from src.integrations.llm import LLMService
from utils.logger import logger
from datetime import datetime
from fastapi import HTTPException


class TopicService(BaseService):
    def __init__(self):
        super().__init__()
        self.llm_service = LLMService()

    def create_topic(self, topic_name: str = None):
        try:
            topics = topic_crud.get_topics(self.db)
            existing_topics = [topic.name for topic in topics]
            new_topic = self.llm_service.generate_topic(topic_name, existing_topics)
        except Exception as e:
            logger.error(f"Failed to generate topic: {str(e)}")
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=500, detail=f"Failed to generate topic: {str(e)}"
            )

        topic_slug = self.get_topic_slug(new_topic)
        existing = topic_crud.get_topic_by_slug(self.db, topic_slug)
        if existing:
            return existing
        new_topic = topic_crud.add_topic(self.db, new_topic, topic_slug)
        return new_topic

    def get_random_unused_topic(self):
        try:
            topic = topic_crud.get_unused_topic(self.db)
            return topic
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            logger.error(f"Internal Server Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_topic(self, id: int):
        try:
            topic = topic_crud.get_topic(self.db, id)
            if not topic:
                raise HTTPException(status_code=404, detail=f"Topic not found: {id}")
            return topic
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            logger.error(f"Internal Server Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def delete_topic(self, id: int):
        try:
            topic = self.get_topic(id)
            topic_crud.delete_topic(self.db, topic)
            return {"message": "Topic deleted successfully"}
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            logger.error(f"Internal Server Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def update_topic_usage(self, id: int):
        try:
            topic = self.get_topic(id)
            topic_crud.update_topic(self.db, topic)
            return topic
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            logger.error(f"Internal Server Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_all_topics(
        self,
        page: int = 1,
        limit: int = 10,
        used_count: int = None,
        last_used_at: str = None,
        filter: str = None,
        id: int = None,
        ids: list[int] = None,
        sort_by: str = "id",
        sort_order: str = "asc",
        start_date: str = None,
        end_date: str = None,
    ):
        try:
            if start_date:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            if last_used_at:
                last_used_at = datetime.strptime(last_used_at, "%Y-%m-%d")

            topics = topic_crud.get_all_topics(
                self.db,
                page=page,
                limit=limit,
                used_count=used_count,
                last_used_at=last_used_at,
                filter=filter,
                id=id,
                ids=ids,
                sort_by=sort_by,
                sort_order=sort_order,
                start_date=start_date,
                end_date=end_date,
            )
            return topics
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            logger.error(f"Internal Server Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
