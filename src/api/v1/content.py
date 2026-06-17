from fastapi import APIRouter, HTTPException
from src.schemas.schema import GenerateScriptSchema
from src.services.script import ScriptService
from src.services.integrations.video_generator import VideoGeneratorService
from src.services.video_merge import VideoMergeService
from utils.logger import logger

router = APIRouter(
    prefix="/v1/content",
    tags=["Content"],
    responses={
        400: {"description": "Bad request"},
        500: {"description": "Internal Server Error"},
    },
)


@router.post("/generate-script")
def generate_short_script(data: GenerateScriptSchema):
    try:
        logger.info("API Request: Generating script")
        topic = data.topic
        if not topic:
            raise HTTPException(status_code=400, detail="Topic is required")

        script = ScriptService().generate_script(topic)
        logger.info(f"Generated script for topic: '{topic}'")
        return {"message": script}
    except HTTPException as e:
        logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid request body parsed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/text/{content_id:int}/generate-audio")
def generate_text_to_audio(content_id: int):
    try:
        logger.info("API Request: Generating audio")
        if not content_id:
            raise HTTPException(status_code=400, detail="Content ID is required")
        audio = ScriptService().generate_audio_from_content(content_id)
        logger.info(f"Generated audio for content_id: '{content_id}'")
        return {"message": audio}
    except HTTPException as e:
        logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid request body parsed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
