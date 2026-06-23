from src.services.base import BaseService
from utils.logger import logger
from src.sql.cruds import (
    content as content_crud,
    short_video as short_video_crud,
    topic as topic_crud,
)
from src.enums import short_video as short_video_status, content as content_status
from src.services.main.topic import TopicService
from src.services.main.content import ContentService
from src.services.main.short_video import ShortVideoService
from fastapi import HTTPException
import os
from datetime import datetime, UTC, timedelta


class ScriptService(BaseService):
    def __init__(self):
        super().__init__()
        self.topic_service = TopicService()
        self.content_service = ContentService()
        self.short_video_service = ShortVideoService()

    def clean_uploaded_video(self):
        logger.info(f"Starting to clean uploaded videos")
        try:
            videos = self.short_video_service.get_short_videos_by_status(
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
            if isinstance(e, HTTPException):
                logger.error(f"Error 1: {e.status_code} - {e.detail}")
            else:
                logger.error(f"Error 1: {str(e)}")
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
            if isinstance(e, HTTPException):
                logger.error(f"Error 2: {e.status_code} - {e.detail}")
            else:
                logger.error(f"Error 2: {str(e)}")
            return

    def generate_topic(self):
        try:
            logger.info(f"Starting to generate topic")
            logger.info(f"Step 1/2: Generating topic")
            topic = self.topic_service.create_topic(topic_name=None)
            logger.info(f"Step 2/2: Generated topic: '{topic.name}'")
        except Exception as e:
            if isinstance(e, HTTPException):
                logger.error(f"Error 3: {e.status_code} - {e.detail}")
            else:
                logger.error(f"Error 3: {str(e)}")
            return

    def create_content(self):
        logger.info(f"Starting to create content")
        logger.info(f"Step 1/3: Getting topic")
        topic = self.topic_service.get_random_unused_topic()
        logger.info(f"Step 2/3: Got topic: {topic}")

        try:
            if not topic:
                logger.info(f"No topic found to process")
                return
            logger.info(f"Step 3/3: Creating content with topic")
            self.content_service.create_content(topic.id)
            logger.info(f"Step 3/3: Created content with topic: {topic.id}")
        except Exception as e:
            if isinstance(e, HTTPException):
                logger.error(f"Error 4: {e.status_code} - {e.detail}")
            else:
                logger.error(f"Error 4: {str(e)}")
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
        content = self.content_service.get_ready_to_process_content(
            excluded_statuses, excluded=True
        )

        try:
            if not content:
                logger.info(f"No content found to process")
                return
            logger.info(f"Step 2/4: Got content: {content}")
            logger.info(f"Step 3/4: Generating audio for content")
            self.content_service.generate_audio_from_content(content.id)
            logger.info(f"Step 4/4: Generated audio for content")
        except Exception as e:
            if isinstance(e, HTTPException):
                logger.error(f"Error 5: {e.status_code} - {e.detail}")
            else:
                logger.error(f"Error 5: {str(e)}")
            return

    def generate_bg_video(self):
        logger.info(f"Starting to fetch and generate video")
        target_statuses = [content_status.ContentStatus.AUDIO_GENERATED]
        logger.info(f"Step 1/2: Getting content")
        content = self.content_service.get_ready_to_process_content(
            target_statuses, excluded=False
        )

        try:
            if not content:
                logger.error(f"No content found to process")
                return
            logger.info(f"Step 2/4: Got content: {content}")
            logger.info(f"Step 3/4: Generating and downloading video for content")
            self.short_video_service.generate_and_download_background_video(
                content_id=content.id
            )
            logger.info(f"Step 4/4: Generated and downloaded video for content")
        except Exception as e:
            if isinstance(e, HTTPException):
                logger.error(f"Error 6: {e.status_code} - {e.detail}")
            else:
                logger.error(f"Error 6: {str(e)}")
            return

    def merge_video_and_audio(self):
        logger.info(f"Starting to merge video and audio")
        video = self.short_video_service.get_short_video_by_status(
            short_video_status.ShortVideoStatus.NOT_STARTED,
        )
        try:
            if not video:
                logger.error(f"No video found to process")
                return
            logger.info(f"Step 2/4: Got video: {video}")
            logger.info(f"Step 3/4: Merging video and audio for video")
            self.short_video_service.construct_original_video(video.id)
            logger.info(f"Step 4/4: Merged video and audio for video")
        except Exception as e:
            if isinstance(e, HTTPException):
                logger.error(f"Error 7: {e.status_code} - {e.detail}")
            else:
                logger.error(f"Error 7: {str(e)}")
            return

    def update_video_metadata(self):
        logger.info(f"Starting to update video metadata")
        short_video = self.short_video_service.get_short_video_by_status(
            short_video_status.ShortVideoStatus.PROCESSING,
        )
        try:
            if not short_video:
                logger.error(f"No short video found to process")
                return
            logger.info(f"Step 2/2: Updating video metadata for content")
            self.short_video_service.update_video_metadata(short_video.id)
            logger.info(f"Step 4/4: Updated video metadata for content")
        except Exception as e:
            if isinstance(e, HTTPException):
                logger.error(f"Error 7: {e.status_code} - {e.detail}")
            else:
                logger.error(f"Error 7: {str(e)}")
            return

    def upload_video_on_youtube(self):
        logger.info(f"Starting to upload video to youtube")
        short_video = self.short_video_service.get_short_video_by_status(
            short_video_status.ShortVideoStatus.METADATA_GENERATED,
        )
        try:
            if not short_video:
                logger.info(f"No short video found to process")
                return
            self.short_video_service.upload_video_on_youtube(short_video.id)
        except Exception as e:
            if isinstance(e, HTTPException):
                logger.error(f"Error 7: {e.status_code} - {e.detail}")
            else:
                logger.error(f"Error 7: {str(e)}")
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
                if (
                    len(content.short_video) == 0
                    or content.status == content_status.ContentStatus.ERROR
                ):
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
            if isinstance(e, HTTPException):
                logger.error(f"Error 8: {e.status_code} - {e.detail}")
            else:
                logger.error(f"Error 8: {str(e)}")
            return
