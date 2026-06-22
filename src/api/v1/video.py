from fastapi import APIRouter, HTTPException
from src.services.main.short_video import ShortVideoService
from src.schemas.short_video import ShortVideoSchema
import typing as t
from src.enums.short_video import ShortVideoStatus
from utils.logger import logger

router = APIRouter(
    prefix="/v1/video",
    tags=["Video"],
    responses={
        400: {"description": "Bad request"},
        500: {"description": "Internal Server Error"},
    },
)


@router.post("/content/{content_id:int}/background", response_model=ShortVideoSchema)
def generate_background_video(content_id: int):
    try:
        logger.info(f"Generating video for content_id: '{content_id}'")
        video = ShortVideoService().generate_and_download_background_video(content_id)
        logger.info(f"Generated video for content_id: '{content_id}'")
        return video
    except Exception as e:
        logger.error(f"Refused API Request: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id:int}", response_model=ShortVideoSchema)
def get_video(id: int):
    try:
        logger.info(f"Getting video for video_id: '{id}'")
        video = ShortVideoService().get_short_video(id)
        logger.info(f"Got video for video_id: '{id}'")
        return video
    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video/{video_id:int}/merge", response_model=ShortVideoSchema)
def make_original_video(video_id: int):
    try:
        logger.info(f"Making original video for video_id: '{video_id}'")
        video = ShortVideoService().construct_original_video(video_id)
        logger.info(f"Generated video for video_id: '{video_id}'")
        return video
    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video/{video_id:int}/metadata", response_model=ShortVideoSchema)
def create_metadata(video_id: int):
    try:
        logger.info(f"Updating metadata for video_id: '{video_id}'")
        video = ShortVideoService().update_video_metadata(video_id)
        logger.info(f"Updated metadata for video_id: '{video_id}'")
        return video
    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video/{video_id:int}/publish", response_model=ShortVideoSchema)
def publish_video(video_id: int):
    try:
        logger.info(f"Publishing video for video_id: '{video_id}'")
        video = ShortVideoService().upload_video_on_youtube(video_id)
        logger.info(f"Published video for video_id: '{video_id}'")
        return video
    except HTTPException as e:
        logger.error(f"Refused API Request: Invalid request body parsed: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Invalid request body parsed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{id:int}")
def delete_video(id: int):
    try:
        logger.info(f"Deleting video for video_id: '{id}'")
        video = ShortVideoService().delete_short_video(id)
        logger.info(f"Deleted video for video_id: '{id}'")
        return {"message": video}
    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{status:str}")
def get_short_videos_by_status(
    status: t.Literal[
        ShortVideoStatus.FAILED,
        ShortVideoStatus.NOT_STARTED,
        ShortVideoStatus.PROCESSING,
        ShortVideoStatus.PUBLISHED,
    ],
):
    try:
        logger.info(f"Getting videos for status: '{status}'")
        videos = ShortVideoService().get_short_videos_by_status(status)
        logger.info(f"Got videos for status: '{status}'")
        return videos
    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=t.List[ShortVideoSchema])
def get_short_videos(
    filter: t.Optional[str] = None,
    id: t.Optional[int] = None,
    ids: t.Optional[str] = None,
    status: t.Optional[str] = None,
    limit: t.Optional[int] = 10,
    page: t.Optional[int] = 1,
    sort_by: t.Optional[str] = "id",
    order_by: t.Optional[str] = "desc",
    start_date: t.Optional[str] = None,
    end_date: t.Optional[str] = None,
):
    try:
        logger.info("Getting videos")
        ids = [int(i) for i in ids.split(",")] if ids else None
        videos = ShortVideoService().list_short_videos(
            filter=filter,
            content_id=content_id,
            ids=ids,
            id=id,
            youtube_url=youtube_url,
            status=status,
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            start_date=start_date,
            end_date=end_date,
        )
        logger.info("Got videos")
        return videos
    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
