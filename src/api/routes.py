from fastapi import APIRouter, HTTPException
from src.schemas.schema import GenerateScriptSchema
from src.services.sript import ScriptService
from src.services.integrations.video_generator import VideoGeneratorService
from src.services.video_merge import VideoMergeService
from src.services.integrations.youtube import YouTubeService
from utils.logger import app_logger

router = APIRouter(prefix="/api/v1")


@router.post("/generate-script")
def generate_short_script(data: GenerateScriptSchema):
    try:
        app_logger.info("Admin API Request: Generating script")
        topic = data.topic
        if not topic:
            raise HTTPException(status_code=400, detail="Topic is required")

        script = ScriptService().generate_script(topic)
        app_logger.info(f"Generated script for topic: '{topic}'")
        return {"message": script}
    except HTTPException as e:
        app_logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid request body parsed: {str(e)}"
        )
    except Exception as e:
        app_logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/text/{content_id:int}/generate-audio")
def generate_text_to_audio(content_id: int):
    try:
        app_logger.info("Admin API Request: Generating audio")
        if not content_id:
            raise HTTPException(status_code=400, detail="Content ID is required")
        audio = ScriptService().create_script_from_content(content_id)
        app_logger.info(f"Generated audio for content_id: '{content_id}'")
        return {"message": audio}
    except HTTPException as e:
        app_logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid request body parsed: {str(e)}"
        )
    except Exception as e:
        app_logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/text/{content_id:int}/get-video")
def generate_get_video(content_id: int):
    try:
        app_logger.info("Admin API Request: Generating video")
        if not content_id:
            raise HTTPException(status_code=400, detail="Content ID is required")
        video = VideoGeneratorService().fetch_and_download_background(content_id)
        app_logger.info(f"Generated video for content_id: '{content_id}'")
        return {"message": video}
    except HTTPException as e:
        app_logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid request body parsed: {str(e)}"
        )
    except Exception as e:
        app_logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/content/{content_id:int}/merge-video")
def merge_text_video(content_id: int):
    try:
        app_logger.info("Admin API Request: Merging video")
        if not content_id:
            raise HTTPException(status_code=400, detail="Content ID is required")
        video = VideoMergeService().merge_and_mute_video(content_id)
        app_logger.info(f"Generated video for content_id: '{content_id}'")
        return {"message": video}
    except HTTPException as e:
        app_logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid request body parsed: {str(e)}"
        )
    except Exception as e:
        app_logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/video/{content_id:int}/metadata")
def create_metadata(content_id: int):
    try:
        app_logger.info("Admin API Request: Updating metadata")
        if not content_id:
            raise HTTPException(status_code=400, detail="Content ID is required")
        metadata = ScriptService().update_video_content_metadata(content_id)
        app_logger.info(f"Generated metadata for content_id: '{content_id}'")
        return metadata
    except HTTPException as e:
        app_logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid request body parsed: {str(e)}"
        )
    except Exception as e:
        app_logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/video/{video_id:int}/publish")
def publish_video(video_id: int):
    try:
        app_logger.info("Admin API Request: Publishing video")
        if not video_id:
            raise HTTPException(status_code=400, detail="Video ID is required")
        video = ScriptService().upload_video_to_youtube(video_id)
        app_logger.info(f"Published video for video_id: '{video_id}'")
        return {"message": video}
    except HTTPException as e:
        app_logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid request body parsed: {str(e)}"
        )
    except Exception as e:
        app_logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
