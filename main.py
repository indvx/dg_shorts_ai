from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from apscheduler.schedulers.background import BackgroundScheduler

from src.api.v1 import logs, content, video
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

scheduler = BackgroundScheduler(jobstores=jobstores)
scheduler.start()


@app.on_event("startup")
def startup_event():
    logger.info("Application started")

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

    # Generate topic at 15 minutes past every hour from 6 AM to 8 PM
    scheduler.add_job(
        automation_jobs.generate_topic_job,
        "cron",
        id="generate_topic",
        hour="6,9,12,13,14,15,17,18,19,20",
        minute=15,
        max_instances=1,
        replace_existing=True,
    )

    # Create content at 10:30 AM, 3:30 PM, 6:30 PM, 8:30 PM
    scheduler.add_job(
        automation_jobs.create_content_job,
        "cron",
        id="create_content",
        hour="10,15,18,20",
        minute=30,
        max_instances=1,
        replace_existing=True,
    )

    # Create audio at 10:31 AM, 3:31 PM, 6:31 PM, 8:31 PM
    scheduler.add_job(
        automation_jobs.create_audio_job,
        "cron",
        id="create_audio",
        hour="10,15,18,20",
        minute=31,
        max_instances=1,
        replace_existing=True,
    )

    # Fetch and generate video at 10:32 AM, 3:32 PM, 6:32 PM, 8:32 PM
    scheduler.add_job(
        automation_jobs.fetch_and_generate_video_job,
        "cron",
        id="fetch_and_generate_video",
        hour="10,15,18,20",
        minute=32,
        max_instances=1,
        replace_existing=True,
    )

    # Merge video and audio at 10:33 AM, 3:33 PM, 6:33 PM, 8:33 PM
    scheduler.add_job(
        automation_jobs.merge_video_and_audio_job,
        "cron",
        id="merge_video_and_audio",
        hour="10,15,18,20",
        minute=33,
        max_instances=1,
        replace_existing=True,
    )

    # Update video metadata at 10:34 AM, 3:34 PM, 6:34 PM, 8:34 PM
    scheduler.add_job(
        automation_jobs.update_video_metadata_job,
        "cron",
        id="update_video_metadata",
        hour="10,15,18,20",
        minute=34,
        max_instances=1,
        replace_existing=True,
    )

    # Upload video on youtube at 10:35 AM, 3:35 PM, 6:35 PM, 8:35 PM
    scheduler.add_job(
        automation_jobs.upload_video_on_youtube_job,
        "cron",
        id="upload_video_on_youtube",
        hour="10,15,18,20",
        minute=35,
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


