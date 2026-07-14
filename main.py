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


    # Clean last 7 days log file every day at 12 AM and 12 PM
    scheduler.add_job(
        automation_jobs.clean_last_7_days_log_file_job,
        "cron",
        id="clean_last_7_days_log_file",
        hour="0,12",
        max_instances=1,
        replace_existing=True,
    )

    # Clean last 7 days contents every day at 12:10 AM and 12:10 PM
    scheduler.add_job(
        automation_jobs.clean_last_7_days_contents_job,
        "cron",
        id="clean_last_7_days_contents",
        hour="0,12",
        minute=10,
        max_instances=1,
        replace_existing=True,
    )

    # Clean uploaded videos every day at 12:30 AM and 12:30 PM
    # scheduler.add_job(
    #     automation_jobs.clean_uploaded_video_job,
    #     "cron",
    #     id="clean_uploaded_video",
    #     hour="0,12",
    #     minute=30,
    #     max_instances=1,
    #     replace_existing=True,
    # )

    # Generate topic at 10:00 AM, 1:00 PM, 6:00 PM, 
    scheduler.add_job(
        automation_jobs.generate_topic_job,
        "cron",
        id="generate_topic",
        hour="10,13,18",
        # minute=50,
        max_instances=1,
        replace_existing=True,
    )

    # Create content at 10:01 AM, 1:01 PM, 6:01 PM,
    scheduler.add_job(
        automation_jobs.create_content_job,
        "cron",
        id="create_content",
        hour="10,13,18",
        minute=1,
        max_instances=1,
        replace_existing=True,
    )

    # Create audio at 10:02 AM, 1:02 PM, 6:02 PM,
    scheduler.add_job(
        automation_jobs.create_audio_job,
        "cron",
        id="create_audio",
        hour="10,13,18",
        minute=2,
        max_instances=1,
        replace_existing=True,
    )

    # Fetch and generate video at 10:04 AM, 1:04 PM, 6:04 PM,
    scheduler.add_job(
        automation_jobs.fetch_and_generate_video_job,
        "cron",
        id="fetch_and_generate_video",
        hour="10,13,18",
        minute=4,
        max_instances=1,
        replace_existing=True,
    )

    # Merge video and audio at 10:06 AM, 1:06 PM, 6:06 PM,
    scheduler.add_job(
        automation_jobs.merge_video_and_audio_job,
        "cron",
        id="merge_video_and_audio",
        hour="10,13,18",
        minute=6,
        # second=30,
        max_instances=1,
        replace_existing=True,
    )

    # Update video metadata at 10:09 AM, 1:09 PM, 6:09 PM,
    scheduler.add_job(
        automation_jobs.update_video_metadata_job,
        "cron",
        id="update_video_metadata",
        hour="10,13,18",
        minute=9,
        max_instances=1,
        replace_existing=True,
    )

    # Upload video on youtube at 10:11 AM, 1:11 PM, 6:11 PM, 
    scheduler.add_job(
        automation_jobs.upload_video_on_youtube_job,
        "cron",
        id="upload_video_on_youtube",
        hour="10,13,18",
        minute=11,
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
