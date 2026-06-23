from src.services.base import BaseService
from src.sql.cruds import short_video as short_video_crud, content as content_crud
from src.enums.content import ContentStatus
from src.enums.short_video import ShortVideoStatus
from src.services.integrations.video_generator import VideoGeneratorService
from src.services.integrations.video_merge import VideoMergeService
from src.services.integrations.llm import LLMService
from src.services.integrations.youtube import YouTubeService
from fastapi import HTTPException
from utils.logger import logger
from datetime import datetime, UTC


class ShortVideoService(BaseService):
    def __init__(self):
        super().__init__()
        self.video_generator_service = VideoGeneratorService()
        self.video_merge_service = VideoMergeService()
        self.llm_service = LLMService()
        self.youtube_service = YouTubeService()

    def generate_and_download_background_video(self, content_id: int):
        try:
            content = content_crud.get_content(self.db, content_id)
            if not content:
                raise HTTPException(status_code=404, detail="Content not found")

            if content.status != ContentStatus.AUDIO_GENERATED:
                raise HTTPException(
                    status_code=400, detail="Content not audio generated."
                )

            background_video_url = (
                self.video_generator_service.fetch_and_download_background(content)
            )
            short_video = short_video_crud.create_short_video(
                self.db,
                {
                    "content_id": content.id,
                    "background_video_url": background_video_url,
                    "status": ShortVideoStatus.NOT_STARTED,
                },
            )
            content_crud.update_content(
                self.db,
                content,
                {
                    "status": ContentStatus.VIDEO_GENERATED,
                },
            )
            return short_video
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail))
        except Exception as e:
            logger.error(f"Failed to generate and download background video: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def construct_original_video(self, short_video_id: int):
        try:
            video = self.get_short_video(short_video_id)
            if not video:
                raise HTTPException(status_code=404, detail="Short video not found")
            if video.status == ShortVideoStatus.NOT_STARTED:
                pass
            else:
                raise HTTPException(status_code=400, detail="Short video not started.")
            video_url = self.video_merge_service.merge_and_mute_video(video)
            short_video = short_video_crud.update_short_video(
                self.db,
                video,
                {
                    "output_path": video_url,
                    "status": ShortVideoStatus.PROCESSING,
                },
            )
            content_crud.update_content(
                self.db,
                video.content,
                {
                    "status": ContentStatus.MERGED,
                },
            )
            return short_video
        except HTTPException as e:
            logger.error(f"Failed to construct original video: {str(e)}")
            raise HTTPException(status_code=e.status_code, detail=str(e.detail))
        except Exception as e:
            logger.error(f"Failed to construct original video: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def update_video_metadata(self, short_video_id: int):
        try:
            short_video = self.get_short_video(short_video_id)
            if not short_video:
                raise HTTPException(status_code=404, detail="Short video not found")

            if short_video.status != ShortVideoStatus.PROCESSING:
                raise HTTPException(
                    status_code=400,
                    detail="Short video is not proper constructed or  already generated with metadata!",
                )

            metadata = self.llm_service.generate_metadata(short_video.content.title)
            metadata_dict = (
                metadata.model_dump()
                if hasattr(metadata, "model_dump")
                else metadata.dict()
            )
            metadata_dict["status"] = ShortVideoStatus.METADATA_GENERATED
            updated_short_video = short_video_crud.update_short_video(
                self.db, short_video, metadata_dict
            )
            return updated_short_video
        except HTTPException as e:
            logger.error(f"Failed to update video metadata: {str(e)}")
            raise HTTPException(status_code=e.status_code, detail=str(e.detail))
        except Exception as e:
            logger.error(f"Failed to update video metadata: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def upload_video_on_youtube(self, short_video_id: int):
        short_video = self.get_short_video(short_video_id)
        if short_video.status != ShortVideoStatus.METADATA_GENERATED:
            raise HTTPException(
                status_code=404, detail="Short video is not ready for upload."
            )

        video_path = short_video.output_path
        title = short_video.title
        description = short_video.description
        tags_list = [t.strip() for t in short_video.tags.split(",") if t.strip()]

        try:
            response = self.youtube_service.upload_shorts_video(
                video_path, title, description, tags_list
            )
            short_video_crud.update_short_video(
                self.db,
                short_video,
                {
                    "youtube_video_url": f"https://youtu.be/{response}",
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

    def get_short_video(self, short_video_id: int):
        try:
            video = short_video_crud.get_short_video(self.db, short_video_id)
            if not video:
                raise HTTPException(status_code=404, detail="Short video not found")
            return video
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail))
        except Exception as e:
            logger.error(f"Failed to get short video: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def delete_short_video(self, short_video_id: int):
        try:
            video = self.get_short_video(short_video_id)
            short_video_crud.delete_short_video(self.db, video)
            return {"message": "Short video deleted successfully"}
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=str(e.detail))
        except Exception as e:
            logger.error(f"Failed to delete short video: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def get_short_video_by_status(self, status: ShortVideoStatus):
        try:
            video = short_video_crud.get_short_video_by_status(self.db, status)
            return video
        except Exception as e:
            logger.error(f"Failed to get short videos by status: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def list_short_videos(
        self,
        filter: str = None,
        id: int = None,
        ids: list[int] = None,
        status: str = None,
        limit: int = 10,
        page: int = 1,
        sort_by: str = "id",
        sort_order: str = "desc",
        start_date: str = None,
        end_date: str = None,
        content_id: int = None,
        youtube_url: str = None,
    ):
        try:
            if start_date:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")

            videos = short_video_crud.get_short_videos(
                self.db,
                filter=filter,
                id=id,
                ids=ids,
                content_id=content_id,
                youtube_url=youtube_url,
                status=status,
                page=page,
                limit=limit,
                sort_by=sort_by,
                sort_order=sort_order,
                start_date=start_date,
                end_date=end_date,
            )
            return videos
        except Exception as e:
            logger.error(f"Failed to list short videos: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
