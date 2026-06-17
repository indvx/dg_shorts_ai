from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

from src.api.logs import router as log_router
from src.api.routes import router as api_router
from src.services.automation import AutomationService
from utils.logger import app_logger as logger

app = FastAPI(title="GoudShorts AI Backend")

app.include_router(log_router)
app.include_router(api_router)

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

    # Clean uploaded videos every day at 12:30 AM
    scheduler.add_job(
        automation_service.clean_uploaded_video,
        "cron",
        hour=0,
        minute=30,
        max_instances=1,
    )

    # Create content at 10:29 AM, 1:29 PM, 4:29 PM, 7:29 PM, 8:29 PM
    scheduler.add_job(
        automation_service.create_content,
        "cron",
        hour="10,15,18,20",
        minute=29,
        max_instances=1,
    )

    # Create audio at 10:31 AM, 1:31 PM, 4:31 PM, 7:31 PM, 8:31 PM
    scheduler.add_job(
        automation_service.create_audio,
        "cron",
        hour="10,15,18,20",
        minute=31,
        max_instances=1,
    )

    # Fetch and generate video at 10:32 AM, 1:32 PM, 4:32 PM, 7:32 PM, 8:32 PM
    scheduler.add_job(
        automation_service.fetch_and_generate_video,
        "cron",
        hour="10,15,18,20",
        minute=32,
        max_instances=1,
    )

    # Merge video and audio at 10:33 AM, 1:33 PM, 4:33 PM, 7:33 PM, 8:33 PM
    scheduler.add_job(
        automation_service.merge_video_and_audio,
        "cron",
        hour="10,15,18,20",
        minute=33,
        max_instances=1,
    )

    # Update video metadata at 10:34 AM, 1:34 PM, 4:34 PM, 7:34 PM, 8:34 PM
    scheduler.add_job(
        automation_service.update_video_metadata,
        "cron",
        hour="10,15,18,20",
        minute=34,
        max_instances=1,
    )

    # Upload video on youtube at 10:35 AM, 3:35 PM, 8:35 PM
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
