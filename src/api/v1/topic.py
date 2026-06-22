from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from src.schemas.schema import TopicCreateSchema, TopicSchema
from src.services.main.topic import TopicService
from utils.logger import logger

router = APIRouter(
    prefix="/v1/topic",
    tags=["Topic"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=TopicSchema)
def generate_topic(topic: TopicCreateSchema):
    try:
        topic = TopicService().create_topic(topic.name)
        return topic
    except Exception as e:
        logger.error(f"Failed to generate topic: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, detail=f"Failed to generate topic: {str(e)}"
        )


@router.get("/{id:int}", response_model=TopicSchema)
def get_topic_by_id(id: int):
    try:
        topic = TopicService().get_topic(id)
        return topic
    except Exception as e:
        logger.error(f"Failed to get topic: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to get topic: {str(e)}")


@router.get("/random", response_model=TopicSchema)
def get_random_unused_topic():
    try:
        topic = TopicService().get_random_unused_topic()
        if not topic:
            raise HTTPException(status_code=404, detail="No unused topic found")
        return topic
    except Exception as e:
        logger.error(f"Failed to get random unused topic: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, detail=f"Failed to get random unused topic: {str(e)}"
        )


@router.delete("/{id:int}")
def delete_topic(id: int):
    try:
        topic = TopicService().delete_topic(id)
        return topic
    except HTTPException as e:
        logger.error(f"Failed to delete topic: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Failed to delete topic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{id:int}/usage")
def update_topic_usage(id: int):
    try:
        topic = TopicService().update_topic_usage(id)
        return topic
    except HTTPException as e:
        logger.error(f"Failed to update topic usage: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Failed to update topic usage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
def get_all_topics(
    page: int = 1,
    limit: int = 10,
    used_count: int = None,
    last_used_at: str = None,
    filter: str = None,
    id: int = None,
    ids: str = None,
    sort_by: str = "id",
    sort_order: str = "asc",
    start_date: str = None,
    end_date: str = None,
):
    try:
        ids = [int(i) for i in ids.split(",")] if ids else None
        topics = TopicService().get_all_topics(
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
        logger.error(f"Failed to get all topics: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
