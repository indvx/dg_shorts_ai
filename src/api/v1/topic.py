from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from src.schemas.schema import TopicCreateSchema, TopicSchema
from src.services.script import ScriptService
from utils.logger import logger

router = APIRouter(
    prefix="/v1/topic",
    tags=["Topic"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=TopicSchema)
def generate_topic(topic: TopicCreateSchema):
    try:
        topic = ScriptService().generate_topic(topic.name)
        return topic
    except Exception as e:
        logger.error(f"Failed to generate topic: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate topic: {str(e)}"
        )
