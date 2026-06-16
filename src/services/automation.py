from src.services.base import BaseService
from utils.logger import app_logger as logger
from src.sql.cruds import content as content_crud, short_video as short_video_crud
from src.enums import short_video as short_video_status
from src.services.script import ScriptService
from src.services.video_merge import VideoMergeService
from src.services.integrations.video_generator import VideoGeneratorService
from fastapi import HTTPException
import os


class AutomationService(BaseService):
    def __init__(self):
        super().__init__()
        self.script_service = ScriptService()
        self.video_merge_service = VideoMergeService()
        self.video_generator_service = VideoGeneratorService()

    def clean_uploaded_video(self):
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

    def upload_video_on_youtube(self):
        logger.info(f"Step 1/13: Started uploading video on youtube")
        try:
            logger.info(f"Step 1/14: Generating topic")
            topic = self.script_service.generate_topic()
            logger.info(f"Step 2/14: Generated topic: '{topic}'")
        except Exception as e:
            logger.error(f"Error 1/7: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

        try:
            logger.info(f"Step 3/14: Generating script: '{topic}'")
            content = self.script_service.generate_script(topic)
            logger.info(f"Step 4/14: Generated script: '{topic}'")
        except Exception as e:
            logger.error(f"Error 2/7: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

        try:
            logger.info(f"Step 5/14: Generating audio for script: '{topic}'")
            self.script_service.generate_audio_from_content(content_id=content.id)
            logger.info(f"Step 6/14: Generated audio for script: '{topic}'")
        except Exception as e:
            logger.error(f"Error 3/7: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

        try:
            logger.info(f"Step 7/14: Generating video for script: '{topic}'")
            self.video_generator_service.fetch_and_download_background(
                content_id=content.id
            )
            logger.info(f"Step 8/14: Generated video for script: '{topic}'")
        except Exception as e:
            logger.error(f"Error 4/7: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

        try:
            logger.info(f"Step 9/14: Merging video and audio for script: '{topic}'")
            self.video_merge_service.merge_and_mute_video(content_id=content.id)
            logger.info(f"Step 10/14: Merged video for script: '{topic}'")
        except Exception as e:
            logger.error(f"Error 5/7: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

        try:
            logger.info(f"Step 11/14: Updating video meta data")
            short_video = self.script_service.update_video_content_metadata(
                content_id=content.id
            )
            logger.info(f"Step 12/14: Updated video meta data")
        except Exception as e:
            logger.error(f"Error 6/7: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

        try:
            logger.info(f"Step 13/14: Uploading video to youtube")
            self.script_service.upload_video_to_youtube(
                video_id=short_video["video_id"]
            )
            logger.info(f"Step 14/14: Uploaded video to youtube")
        except Exception as e:
            logger.error(f"Error 7/7: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

    def upload_tagged_video(self):
        try:
            logger.info(f"Step 1/4: Getting video to upload")
            short_video = short_video_crud.get_ready_to_upload_short_video(self.db)
            logger.info(f"Step 2/4: Got video to upload")
        except Exception as e:
            logger.error(f"Error 1/2: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )

        try:
            if not short_video:
                raise HTTPException(status_code=404, detail=f"No video found to upload")
            logger.info(f"Step 3/4: Uploading video to youtube")
            self.script_service.upload_video_to_youtube(video_id=short_video.id)
            logger.info(f"Step 4/4: Uploaded video to youtube")
        except Exception as e:
            logger.error(f"Error 2/2: Internal server error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error 2/2: Internal server error: {str(e)}"
            )

    def create_content(self):
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
