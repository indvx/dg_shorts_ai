from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from apscheduler.schedulers.background import BackgroundScheduler

from src.api.v1 import logs, content, video, topic
from src.jobs import automation_jobs
from src.db.session import jobstores
from utils.logger import logger
from src.schemas.schema import JobResponseSchema

app = FastAPI(
    title="DGShorts AI Backend",
    description="API for DGShorts AI",
    version="1.0.0",
)

app.include_router(logs.router, prefix="/api")
app.include_router(content.router, prefix="/api")
app.include_router(video.router, prefix="/api")
app.include_router(topic.router, prefix="/api")


scheduler = BackgroundScheduler(jobstores=jobstores)


@app.on_event("startup")
def startup_event():
    logger.info("Application started")
    scheduler.start()


    # Clean last 7 days log file every day at 12 AM
    scheduler.add_job(
        automation_jobs.clean_last_7_days_log_file_job,
        "cron",
        id="clean_last_7_days_log_file",
        hour=0,
        max_instances=1,
        replace_existing=True,
    )

    # Clean last 7 days contents every day at 12:10 AM
    scheduler.add_job(
        automation_jobs.clean_last_7_days_contents_job,
        "cron",
        id="clean_last_7_days_contents",
        hour=0,
        minute=10,
        max_instances=1,
        replace_existing=True,
    )

    # Clean uploaded videos every day at 12:30 AM
    scheduler.add_job(
        automation_jobs.clean_uploaded_video_job,
        "cron",
        id="clean_uploaded_video",
        hour=0,
        minute=30,
        max_instances=1,
        replace_existing=True,
    )

    # Generate topic at 7:53 AM, 12:53 PM, 5:53 PM, 7:53 PM
    scheduler.add_job(
        automation_jobs.generate_topic_job,
        "cron",
        id="generate_topic",
        hour="7,12,17,19,14",
        minute=3,
        max_instances=1,
        replace_existing=True,
    )

    # Create content at 7:54 AM, 12:54 PM, 5:54 PM, 7:54 PM
    scheduler.add_job(
        automation_jobs.create_content_job,
        "cron",
        id="create_content",
        hour="7,12,17,19,14",
        minute=4,
        max_instances=1,
        replace_existing=True,
    )

    # Create audio at 7:55 AM, 12:55 PM, 5:55 PM, 7:55 PM
    scheduler.add_job(
        automation_jobs.create_audio_job,
        "cron",
        id="create_audio",
        hour="7,12,17,19,14",
        minute=5,
        max_instances=1,
        replace_existing=True,
    )

    # Fetch and generate video at 7:56 AM, 12:56 PM, 5:56 PM, 7:56 PM
    scheduler.add_job(
        automation_jobs.fetch_and_generate_video_job,
        "cron",
        id="fetch_and_generate_video",
        hour="7,12,17,19,14",
        minute=6,
        max_instances=1,
        replace_existing=True,
    )

    # Merge video and audio at 7:58 AM, 12:58 PM, 5:58 PM, 7:58 PM
    scheduler.add_job(
        automation_jobs.merge_video_and_audio_job,
        "cron",
        id="merge_video_and_audio",
        hour="7,12,17,19,14",
        minute=8,
        max_instances=1,
        replace_existing=True,
    )

    # Update video metadata at 7:59 AM, 12:59 PM, 5:59 PM, 7:59 PM
    scheduler.add_job(
        automation_jobs.update_video_metadata_job,
        "cron",
        id="update_video_metadata",
        hour="7,12,17,19,14",
        minute=9,
        max_instances=1,
        replace_existing=True,
    )

    # Upload video on youtube at 8:00 AM, 1:00 PM, 6:00 PM, 8:00 PM
    scheduler.add_job(
        automation_jobs.upload_video_on_youtube_job,
        "cron",
        id="upload_video_on_youtube",
        hour="8,13,18,20,14",
        minute=10,
        max_instances=1,
        replace_existing=True,
    )


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
    logger.info("Application shutdown")


@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/v1/jobs", response_model=list[JobResponseSchema], tags=["Jobs"])
def get_jobs():
    try:
        jobs = scheduler.get_jobs()
        return [
            JobResponseSchema(
                id=job.id,
                next_run_time=(job.next_run_time),
                trigger=str(job.trigger),
            )
            for job in jobs
        ]
    except Exception as e:
        logger.error(f"Error getting jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"{str(e)}")
