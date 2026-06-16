from src.services.base import BaseService
from utils.logger import app_logger as logger
from src.sql.cruds import content as content_crud, short_video as short_video_crud
from src.enums import short_video as short_video_status, content as content_status
from src.services.script import ScriptService
from src.services.video_merge import VideoMergeService
from src.services.integrations.video_generator import VideoGeneratorService
from fastapi import HTTPException
import os
from datetime import datetime, UTC


class AutomationService(BaseService):
    def __init__(self):
        super().__init__()
        self.script_service = ScriptService()
        self.video_merge_service = VideoMergeService()
        self.video_generator_service = VideoGeneratorService()

    def clean_uploaded_video(self):
        logger.info(f"Starting to clean uploaded videos")
        try:
            videos = short_video_crud.get_short_videos_by_status(
                self.db, short_video_status.ShortVideoStatus.PUBLISHED
            )
            for video in videos:
                if os.path.exists(video.output_path):
                    os.remove(video.output_path)
                if os.path.exists(video.content.audio_path):
                    os.remove(video.content.audio_path)
                if os.path.exists(video.content.video_path):
                    os.remove(video.content.video_path)
                content_crud.delete_content(self.db, video.content)
                short_video_crud.delete_short_video(self.db, video)
        except Exception as e:
            logger.error(f"Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )
    
    def clean_last_7_days_log_file(self):
        logger.info(f"Starting to clean last 7 days log file")
        try:
            logger.info(f"Step 1/2: Getting log files")
            log_file_path = "logs/"
            log_files = os.listdir(log_file_path)
            logger.info(f"Step 2/2: Got log files: {log_files}")
        except Exception as e:
            logger.error(f"Error 1/2: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

        try:
            logger.info(f"Step 3/4: Cleaning log files")
            for log_file in log_files:
                if log_file.endswith(".log"):
                    logger.info(f"Step 3/4: Processing log file: {log_file}")
                    full_log_file_path = os.path.join(log_file_path, log_file)
                    file_creation_date = datetime.fromtimestamp(os.path.getctime(full_log_file_path), UTC)
                    if (datetime.now(UTC) - file_creation_date).days > 7:
                        os.remove(full_log_file_path)
                        logger.info(f"Cleaned log file: {full_log_file_path}")
            logger.info(f"Step 4/4: Cleaned last 7 days log file")
        except Exception as e:
            logger.error(f"Error 2/2: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error 2/2: Internal server error: {str(e)}"
            )

    def upload_video_on_youtube(self):
        logger.info(f"Starting to upload video to youtube")
        try:
            logger.info(f"Step 1/2: Getting video content")
            short_video = short_video_crud.get_ready_to_upload_short_video(self.db)
            logger.info(f"Step 2/2: Got video content")
        except Exception as e:
            logger.error(f"Error 1/2: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

        try:
            if not short_video:
                logger.info(f"No short video found to process")
                return
            logger.info(f"Step 3/4: Uploading video to youtube")
            self.script_service.upload_video_to_youtube(short_video.id)
            logger.info(f"Step 4/4: Uploaded video to youtube")
        except Exception as e:
            logger.error(f"Error 2/2: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error 2/2: Internal server error: {str(e)}"
            )

    def create_content(self):
        logger.info(f"Starting to create content")
        try:
            logger.info(f"Step 1/3: Generating topic")
            topic = self.script_service.generate_topic()
            logger.info(f"Step 2/3: Generated topic: '{topic}'")
        except Exception as e:
            logger.error(f"Error 1/2: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

        try:
            logger.info(f"Step 3/3: Creating content with topic")
            content = self.script_service.generate_script(topic)
            logger.info(f"Step 4/4: Created content with topic: '{topic}'")
        except Exception as e:
            logger.error(f"Error 2/2: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    def create_audio(self):
        logger.info(f"Starting to create audio")
        try:
            logger.info(f"Step 1/2: Getting content")
            excluded_statuses = [
                content_status.ContentStatus.AUDIO_GENERATED,
                content_status.ContentStatus.VIDEO_GENERATED,
                content_status.ContentStatus.MERGED,
                content_status.ContentStatus.ERROR,
            ]
            content = content_crud.get_ready_to_process_content(
                self.db, excluded_statuses, excluded=True
            )
            logger.info(f"Step 2/2: Got content")
        except Exception as e:
            logger.error(f"Error 1/2: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

        try:
            if not content:
                logger.info(f"No content found to process")
                return
            logger.info(f"Step 3/4: Generating audio for content")
            self.script_service.generate_audio_from_content(content_id=content.id)
            logger.info(f"Step 4/4: Generated audio for content")
        except Exception as e:
            logger.error(f"Error 2/2: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error 2/2: Internal server error: {str(e)}"
            )

    def fetch_and_generate_video(self):
        logger.info(f"Starting to fetch and generate video")
        try:
            target_statuses = [content_status.ContentStatus.AUDIO_GENERATED]
            logger.info(f"Step 1/2: Getting content")
            content = content_crud.get_ready_to_process_content(
                self.db, target_statuses, excluded=False
            )
            logger.info(f"Step 2/2: Got content")
        except Exception as e:
            logger.error(f"Error 1/2: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

        try:
            if not content:
                logger.info(f"No content found to process")
                return
            logger.info(f"Step 3/4: Fetching and generating video for content")
            self.video_generator_service.fetch_and_download_background(
                content_id=content.id
            )
            logger.info(f"Step 4/4: Fetched and generated video for content")
        except Exception as e:
            logger.error(f"Error 2/2: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error 2/2: Internal server error: {str(e)}"
            )

    def merge_video_and_audio(self):
        logger.info(f"Starting to merge video and audio")
        try:
            logger.info(f"Step 1/2: Getting content")
            target_statuses = [
                content_status.ContentStatus.VIDEO_GENERATED,
            ]
            content = content_crud.get_ready_to_process_content(
                self.db, target_statuses, excluded=False
            )
            logger.info(f"Step 2/2: Got content")
        except Exception as e:
            logger.error(f"Error 1/2: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

        try:
            if not content:
                logger.info(f"No content found to process")
                return
            logger.info(f"Step 3/4: Merging video and audio for content")
            self.video_merge_service.merge_and_mute_video(content_id=content.id)
            logger.info(f"Step 4/4: Merged video and audio for content")
        except Exception as e:
            logger.error(f"Error 2/2: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error 2/2: Internal server error: {str(e)}"
            )

    def update_video_metadata(self):
        logger.info(f"Starting to update video metadata")
        try:
            logger.info(f"Step 1/2: Getting content")
            short_video = short_video_crud.get_ready_to_metadata_short_video(self.db)
            logger.info(f"Step 2/2: Got content")
        except Exception as e:
            logger.error(f"Error 1/2: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

        try:
            if not short_video:
                logger.info(f"No short video found to process")
                return
            logger.info(f"Step 3/4: Updating video metadata for content")
            self.script_service.update_video_content_metadata(short_video.content_id)
            logger.info(f"Step 4/4: Updated video metadata for content")
        except Exception as e:
            logger.error(f"Error 2/2: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error 2/2: Internal server error: {str(e)}"
            )
