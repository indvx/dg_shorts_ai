from datetime import date as dt_date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.sql.models.short_video import ShortVideo


def create_short_video(db: Session, short_video_data: dict):
    short_video = ShortVideo()
    short_video.content_id = short_video_data.get("content_id")
    short_video.title = short_video_data.get("title")
    short_video.output_path = short_video_data.get("output_path")
    short_video.status = short_video_data.get("status")
    db.add(short_video)
    db.commit()
    db.refresh(short_video)
    return short_video


def get_short_video(db: Session, short_video_id: int) -> ShortVideo:
    return db.query(ShortVideo).filter(ShortVideo.id == short_video_id).first()


def get_short_video_by_content_id(db: Session, content_id: int) -> ShortVideo:
    return db.query(ShortVideo).filter(ShortVideo.content_id == content_id).first()


def update_short_video(
    db: Session, short_video: ShortVideo, short_video_data: dict
) -> ShortVideo:
    if "content_id" in short_video_data:
        short_video.content_id = short_video_data["content_id"]
    if "title" in short_video_data:
        short_video.title = short_video_data["title"]
    if "output_path" in short_video_data:
        short_video.output_path = short_video_data["output_path"]
    if "status" in short_video_data:
        short_video.status = short_video_data["status"]
    if "published_at" in short_video_data:
        short_video.published_at = short_video_data["published_at"]
    if "description" in short_video_data:
        short_video.description = short_video_data["description"]
    if "hashtags" in short_video_data:
        short_video.tags = short_video_data["hashtags"]
    if "youtube_video_path" in short_video_data:
        short_video.youtube_video_path = short_video_data["youtube_video_path"]
    db.commit()
    db.refresh(short_video)
    return short_video


def delete_short_video(db: Session, short_video: ShortVideo) -> bool:
    db.delete(short_video)
    db.commit()
    return True


def get_all_short_videos(db: Session):
    return db.query(ShortVideo).all()


def get_short_videos_by_status(db: Session, status: str, date: dt_date = None):

    if date:
        return (
            db.query(ShortVideo)
            .filter(
                ShortVideo.status == status,
                func.date(ShortVideo.published_at) == date,
            )
            .all()
        )
    else:
        last_7_days = dt_date.today() - timedelta(days=7)
        return (
            db.query(ShortVideo)
            .filter(
                ShortVideo.status == status,
                ShortVideo.published_at >= last_7_days,
            )
            .all()
        )
    
