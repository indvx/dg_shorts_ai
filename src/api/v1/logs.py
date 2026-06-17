import os
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import PlainTextResponse
from utils.logger import logger

router = APIRouter(
    prefix="/v1/logs",
    tags=["Logs"],
    responses={404: {"description": "Log not found"}},
)

LOG_DIR = "logs"


@router.get("/current", response_class=PlainTextResponse)
def get_current_logs():
    logger.info("Admin API Request: Fetching current live logs.")
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_log_file = os.path.join(LOG_DIR, f"{current_date}.log")

    if not os.path.exists(current_log_file):
        logger.warning(f"Current log file not found on disk: {current_log_file}")
        return "No logs recorded for today yet. App is running clean!"

    try:
        with open(current_log_file, "r", encoding="utf-8") as file:
            lines = file.readlines()
            return "".join(lines[-500:])
    except Exception as e:
        logger.error(f"Failed to read current log file: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error reading logs."
        )


@router.get("/filter", response_class=PlainTextResponse)
def get_filtered_logs(
    date: str = Query(
        ..., description="Target date format in YYYY-MM-DD (e.g., 2026-06-12)"
    )
):
    logger.info(f"Admin API Request: Filtering archival logs for date: {date}")

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        logger.warning(
            f"Refused log request. Invalid date format parameter parsed: {date}"
        )
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD format."
        )

    target_log_file = os.path.join(LOG_DIR, f"{date}.log")

    if not os.path.exists(target_log_file):
        logger.warning(
            f"Archive lookup failed. No log file records exist for date: {date}"
        )
        raise HTTPException(
            status_code=404, detail=f"No archival log data verified for date: {date}"
        )

    try:
        with open(target_log_file, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error indexing log profile repository: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching archival records.")
