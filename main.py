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
    
    # Clean last 7 days log file every 10 minutes
    scheduler.add_job(automation_service.clean_last_7_days_log_file, "interval", minutes=1, max_instances=1)
    # Clean uploaded videos at 00:30
    scheduler.add_job(automation_service.clean_uploaded_video, "cron", hour=0, minute=30, max_instances=1)
    
    # Generate content every 20 minutes
    scheduler.add_job(
        automation_service.create_content, "interval", minutes=20, max_instances=1
    )
    # Generate audio every 25 minutes
    scheduler.add_job(
        automation_service.create_audio, "interval", minutes=25, max_instances=1
    )
    # Generate video every 30 minutes
    scheduler.add_job(
        automation_service.fetch_and_generate_video, "interval", minutes=30, max_instances=1,
    )
    # Merge video and audio every 35 minutes
    scheduler.add_job(
        automation_service.merge_video_and_audio, "interval", minutes=35, max_instances=1,
    )
    
    # Update video metadata every 40 minutes
    scheduler.add_job(
        automation_service.update_video_metadata, "interval", minutes=40, max_instances=1,
    )

    # Upload video on youtube every 5 hours
    scheduler.add_job(
        automation_service.upload_video_on_youtube, "cron", hour="0,5,10,15,20", max_instances=1
    )
    # Clean uploaded videos at 01:30 and 6:30 and 11:30 and 16:30 and 21:30
    scheduler.add_job(
        automation_service.clean_uploaded_video, "cron", hour="1,6,11,16,21", minute=30, max_instances=1
    )

    scheduler.start()


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
    logger.info("Application shutdown")
