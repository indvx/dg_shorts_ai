from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

from src.api.v1 import logs, content, video
from src.services.automation import AutomationService
from utils.logger import logger

app = FastAPI(
    title="DGShorts AI Backend",
    description="API for DGShorts AI",
    version="1.0.0",
)

app.include_router(logs.router, prefix="/api")
app.include_router(content.router, prefix="/api")
app.include_router(video.router, prefix="/api")

automation_service = AutomationService()
scheduler = BackgroundScheduler()


@app.on_event("startup")
def startup_event():
    logger.info("Application started")

    # Clean last 7 days log file every day at 12 AM
    scheduler.add_job(
        automation_service.clean_last_7_days_log_file,
        "cron",
        hour=0,
        max_instances=1,
    )

    # Clean last 7 days contents every day at 12:10 AM
    scheduler.add_job(
        automation_service.clean_last_7_days_contents,
        "cron",
        hour=0,
        minute=10,
        max_instances=1,
    )

    # Clean uploaded videos every day at 12:30 AM
    scheduler.add_job(
        automation_service.clean_uploaded_video,
        "cron",
        hour=0,
        minute=30,
        max_instances=1,
    )

    # Create content at 10:30 AM, 3:30 PM, 6:30 PM, 8:30 PM
    scheduler.add_job(
        automation_service.create_content,
        "cron",
        hour="10,15,18,20",
        minute=30,
        max_instances=1,
    )

    # Create audio at 10:31 AM, 3:31 PM, 6:31 PM, 8:31 PM
    scheduler.add_job(
        automation_service.create_audio,
        "cron",
        hour="10,15,18,20",
        minute=31,
        max_instances=1,
    )

    # Fetch and generate video at 10:32 AM, 3:32 PM, 6:32 PM, 8:32 PM
    scheduler.add_job(
        automation_service.fetch_and_generate_video,
        "cron",
        hour="10,15,18,20",
        minute=32,
        max_instances=1,
    )

    # Merge video and audio at 10:33 AM, 3:33 PM, 6:33 PM, 8:33 PM
    scheduler.add_job(
        automation_service.merge_video_and_audio,
        "cron",
        hour="10,15,18,20",
        minute=33,
        max_instances=1,
    )

    # Update video metadata at 10:34 AM, 3:34 PM, 6:34 PM, 8:34 PM
    scheduler.add_job(
        automation_service.update_video_metadata,
        "cron",
        hour="10,15,18,20",
        minute=34,
        max_instances=1,
    )

    # Upload video on youtube at 10:35 AM, 3:35 PM, 6:35 PM, 8:35 PM
    scheduler.add_job(
        automation_service.upload_video_on_youtube,
        "cron",
        hour="10,15,18,20",
        minute=35,
        max_instances=1,
    )

    scheduler.start()


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
    logger.info("Application shutdown")
