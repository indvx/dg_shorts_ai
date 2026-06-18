from src.services.base import BaseService
from utils.logger import logger
from src.sql.cruds import content as content_crud, short_video as short_video_crud
from src.enums import short_video as short_video_status, content as content_status
from src.services.script import ScriptService
from src.services.video_merge import VideoMergeService
from src.services.integrations.video_generator import VideoGeneratorService
from fastapi import HTTPException
import os
from datetime import datetime, UTC, timedelta


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
            logger.error(f"Error 1: Internal server error: {str(e)}")
            return

    def clean_last_7_days_log_file(self):
        logger.info("Starting log cleanup")
        log_dir = "logs"
        try:
            cutoff = datetime.now(UTC).date() - timedelta(days=7)
            for log_file in os.listdir(log_dir):
                if not log_file.endswith(".log"):
                    continue
                try:
                    file_date = datetime.strptime(log_file[:-4], "%Y-%m-%d").date()
                    if file_date < cutoff:
                        full_path = os.path.join(log_dir, log_file)
                        logger.info(f"Deleting {full_path}")
                        os.remove(full_path)
                        logger.info(f"Deleted {full_path}")
                except ValueError:
                    logger.warning(f"Invalid log filename: {log_file}")
        except Exception as e:
            logger.error(f"Error 2: Internal server error: {str(e)}")
            return

    def upload_video_on_youtube(self):
        logger.info(f"Starting to upload video to youtube")
        logger.info(f"Step 1/2: Getting video content")
        short_video = short_video_crud.get_ready_to_upload_short_video(self.db)
        logger.info(f"Step 2/2: Got video content")

        try:
            if not short_video:
                logger.info(f"No short video found to process")
                return
            logger.info(f"Step 3/4: Uploading video to youtube")
            self.script_service.upload_video_to_youtube(short_video.id)
            logger.info(f"Step 4/4: Uploaded video to youtube")
        except Exception as e:
            logger.error(f"Error 3: Internal server error: {str(e)}")
            return

    def create_content(self):
        logger.info(f"Starting to create content")
        logger.info(f"Step 1/3: Generating topic")
        topic = self.script_service.generate_topic()
        logger.info(f"Step 2/3: Generated topic: '{topic}'")

        try:
            logger.info(f"Step 3/3: Creating content with topic")
            content = self.script_service.generate_script(topic)
            logger.info(f"Step 4/4: Created content with topic: '{topic}'")
        except Exception as e:
            logger.error(f"Error 4: Internal server error: {str(e)}")
            return

    def create_audio(self):
        logger.info(f"Starting to create audio")
        logger.info(f"Step 1/4: Getting content")
        excluded_statuses = [
            content_status.ContentStatus.AUDIO_GENERATED,
            content_status.ContentStatus.VIDEO_GENERATED,
            content_status.ContentStatus.MERGED,
            content_status.ContentStatus.ERROR,
        ]
        content = content_crud.get_ready_to_process_content(
            self.db, excluded_statuses, excluded=True
        )

        try:
            if not content:
                logger.info(f"No content found to process")
                return
            logger.info(f"Step 2/4: Got content")
            logger.info(f"Step 3/4: Generating audio for content")
            self.script_service.generate_audio_from_content(content_id=content.id)
            logger.info(f"Step 4/4: Generated audio for content")
        except Exception as e:
            logger.error(f"Error 5: Internal server error: {str(e)}")
            return

    def fetch_and_generate_video(self):
        logger.info(f"Starting to fetch and generate video")
        target_statuses = [content_status.ContentStatus.AUDIO_GENERATED]
        logger.info(f"Step 1/2: Getting content")
        content = content_crud.get_ready_to_process_content(
            self.db, target_statuses, excluded=False
        )

        try:
            if not content:
                logger.error(f"No content found to process")
                return
            logger.info(f"Step 2/4: Got content")
            logger.info(f"Step 3/4: Fetching and generating video for content")
            self.video_generator_service.fetch_and_download_background(
                content_id=content.id
            )
            logger.info(f"Step 4/4: Fetched and generated video for content")
        except Exception as e:
            logger.error(f"Error 6: Internal server error: {str(e)}")
            return

    def merge_video_and_audio(self):
        logger.info(f"Starting to merge video and audio")
        logger.info(f"Step 1/4: Getting content")
        target_statuses = [
            content_status.ContentStatus.VIDEO_GENERATED,
        ]
        content = content_crud.get_ready_to_process_content(
            self.db, target_statuses, excluded=False
        )

        try:
            if not content:
                logger.error(f"No content found to process")
                return
            logger.info(f"Step 2/4: Got content")
            logger.info(f"Step 3/4: Merging video and audio for content")
            self.video_merge_service.merge_and_mute_video(content_id=content.id)
            logger.info(f"Step 4/4: Merged video and audio for content")
        except Exception as e:
            logger.error(f"Error 12: Internal server error: {str(e)}")
            return

    def update_video_metadata(self):
        logger.info(f"Starting to update video metadata")
        logger.info(f"Step 1/4: Getting content")
        short_video = short_video_crud.get_ready_to_metadata_short_video(self.db)

        try:
            if not short_video:
                logger.info(f"No short video found to process")
                return
            logger.info(f"Step 2/4: Got content")
            logger.info(f"Step 3/4: Updating video metadata for content")
            self.script_service.update_video_content_metadata(short_video.id)
            logger.info(f"Step 4/4: Updated video metadata for content")
        except Exception as e:
            logger.error(f"Error 7: Internal server error: {str(e)}")
            return

    def clean_last_7_days_contents(self):
        logger.info(f"Step 1/4: Getting contents")
        contents = content_crud.get_all_contents(self.db, days=7)
        logger.info(f"Step 2/4: Got contents {len(contents)}")

        try:
            if len(contents) == 0:
                logger.error(f"No contents found to process")
                return

            logger.info(f"Step 3/4: Cleaning last 7 days contents")
            for content in contents:
                logger.info(f"Checking content {content.id}")
                if len(content.short_video) == 0 or content.status == content_status.ContentStatus.ERROR:
                    logger.info(f"Cleaning content {content.id}")
                    if content.audio_path is not None:
                        os.remove(content.audio_path)
                        logger.info(f"Cleaned content {content.id} audio path")
                    if content.video_path is not None:
                        os.remove(content.video_path)
                        logger.info(f"Cleaned content {content.id} video path")
                    content_crud.delete_content(self.db, content)
                    logger.info(f"Cleaned content {content.id}")
            logger.info(f"Step 4/4: Cleaned last 7 days contents")
        except Exception as e:
            logger.error(f"Error 8: Internal server error: {str(e)}")
            return
