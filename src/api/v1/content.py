from fastapi import APIRouter, HTTPException
from src.schemas.content import GenerateScriptSchema, ContentUpdateSchema
from src.services.content import ContentService
from utils.logger import logger
import typing as t

router = APIRouter(
    prefix="/v1/content",
    tags=["Content"],
    responses={
        400: {"description": "Bad request"},
        500: {"description": "Internal Server Error"},
    },
)


@router.post("/generate")
def generate_content(data: GenerateScriptSchema):
    try:
        logger.info("Generating content")
        topic = data.topic_id
        if not topic:
            raise HTTPException(status_code=400, detail="Topic is required")

        content = ContentService().create_content(topic)
        logger.info(f"Generated content for topic: '{content.title}'")
        return content
    except Exception as e:
        logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id:int}")
def get_content(id: int):
    try:
        logger.info("Getting content")
        content = ContentService().get_content(id)
        return content
    except Exception as e:
        logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{id:int}/generate-audio")
def generate_text_to_audio(id: int):
    try:
        logger.info("Generating audio")
        if not id:
            raise HTTPException(status_code=400, detail="Content ID is required")
        audio = ContentService().generate_audio_from_content(id)
        logger.info(f"Generated audio for content_id: '{id}'")
        return {"message": audio}
    except Exception as e:
        logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
def get_next_ready_to_process_content():
    try:
        logger.info("Getting next ready to process content")
        content = ContentService().get_ready_to_process_content()
        if not content:
            raise HTTPException(status_code=404, detail="No content data available to process.")
        return content
    except Exception as e:
        logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{id:int}")
def update_content(id: int, content: ContentUpdateSchema):
    try:
        logger.info("Updating content")
        content = ContentService().update_content(id, content)
        logger.info(f"Updated content for content_id: '{id}'")
        return {"message": content}
    except Exception as e:
        logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{days:int}/old")
def get_old_content(days: int):
    try:
        logger.info("Getting old content")
        content = ContentService().get_days_old_contents(days)
        return content
    except Exception as e:
        logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list")
def get_all_contents(
    filter: t.Optional[str] = None,
    id: t.Optional[int] = None,
    ids: t.Optional[str] = None,
    status: t.Optional[str] = None,
    page: t.Optional[int] = 1,
    limit: t.Optional[int] = 10,
    sort_by: t.Optional[str] = "created_at",
    sort_order: t.Literal["asc", "desc"] = "desc",
    start_date: t.Optional[str] = None,
    end_date: t.Optional[str] = None,
):
    try:
        logger.info("Getting all contents")
        ids = [int(i) for i in ids.split(",")] if ids else None
        content = ContentService().get_all_contents(
            filter=filter,
            id=id,
            ids=ids,
            status=status,
            page=page,
            limit=limit,
            sort_by=sort_by,
            order_by=sort_order,
            start_date=start_date,
            end_date=end_date,
        )
        return content
    except Exception as e:
        logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))
