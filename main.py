from fastapi import FastAPI
from uvicorn import run
from apscheduler.schedulers.background import BackgroundScheduler

from src.api.logs import router as log_router
from src.api.routes import router as api_router
from src.services.utility import UtilityService
from utils.logger import app_logger as logger

app = FastAPI(title="GoudShorts AI Backend")

app.include_router(log_router)
app.include_router(api_router)

utility_service = UtilityService()
scheduler = BackgroundScheduler()


@app.on_event("startup")
def startup_event():
    logger.info("Application started")
    scheduler.add_job(utility_service.clean_uploaded_video, "interval", seconds=10)
    scheduler.add_job(utility_service.upload_video_on_youtube, "interval", minutes=3)
    scheduler.start()


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
    logger.info("Application shutdown")
