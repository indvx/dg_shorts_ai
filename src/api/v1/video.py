from fastapi import APIRouter, HTTPException
from src.schemas.schema import GenerateScriptSchema
from src.services.script import ScriptService
from src.services.integrations.video_generator import VideoGeneratorService
from src.services.video_merge import VideoMergeService
from utils.logger import logger

router = APIRouter(
    prefix="/v1/video",
    tags=["Video"],
    responses={
        400: {"description": "Bad request"},
        500: {"description": "Internal Server Error"},
    },
)


@router.post("/content/{content_id:int}/generate-video")
def generate_get_video(content_id: int):
    try:
        logger.info("API Request: Generating video")
        if not content_id:
            raise HTTPException(status_code=400, detail="Content ID is required")
        video = VideoGeneratorService().fetch_and_download_background(content_id)
        logger.info(f"Generated video for content_id: '{content_id}'")
        return video
    except HTTPException as e:
        logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid request body parsed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/content/{content_id:int}/merge-video")
def merge_text_video(content_id: int):
    try:
        logger.info("API Request: Merging video")
        if not content_id:
            raise HTTPException(status_code=400, detail="Content ID is required")
        video = VideoMergeService().merge_and_mute_video(content_id)
        logger.info(f"Generated video for content_id: '{content_id}'")
        return video
    except HTTPException as e:
        logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid request body parsed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/video/{video_id:int}/metadata")
def create_metadata(video_id: int):
    try:
        logger.info("API Request: Updating metadata")
        if not video_id:
            raise HTTPException(status_code=400, detail="Video ID is required")
        metadata = ScriptService().update_video_content_metadata(video_id)
        logger.info(f"Updated metadata for video_id: '{video_id}'")
        return metadata
    except HTTPException as e:
        logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid request body parsed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/video/{video_id:int}/publish")
def publish_video(video_id: int):
    try:
        logger.info("API Request: Publishing video")
        if not video_id:
            raise HTTPException(status_code=400, detail="Video ID is required")
        video = ScriptService().upload_video_to_youtube(video_id)
        logger.info(f"Published video for video_id: '{video_id}'")
        return {"message": video}
    except HTTPException as e:
        logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid request body parsed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
