from fastapi import FastAPI
from uvicorn import run
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
    # scheduler.add_job(automation_service.clean_uploaded_video, "interval", seconds=10)
    # scheduler.add_job(automation_service.upload_video_on_youtube, "interval", minutes=30)
    # scheduler.add_job(automation_service.upload_tagged_video, "interval", minutes=1)
    # scheduler.add_job(automation_service.create_content, "interval", minutes=1)
    scheduler.start()


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
    logger.info("Application shutdown")
