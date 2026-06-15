from src.services.integrations.youtube import YouTubeService
from utils.logger import app_logger as logger


class OrchestrationEngine:
    def __init__(self, db_session):
        self.db = db_session
        self.uploader_engine = YouTubeService()

    def execute_pipeline(self, topic: str):
        try:
            video_output_path = "data/output/final_short.mp4"
            video_title = f"Mind Blowing Facts About {topic}"
            video_desc = f"Learn something new today! \n\n#facts #technology #shorts \nAutomated via GoudShorts AI System."

            logger.info("Initializing automatic YouTube distribution sequence...")
            self.uploader_engine.upload_shorts_video(
                video_file_path=video_output_path,
                title=video_title,
                description=video_desc,
            )
            return True
        except Exception as e:
            logger.critical(f"Critical crash on Orchestration loop pipeline: {str(e)}")
            return False
