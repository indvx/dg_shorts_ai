from datetime import date as dt_date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.sql.models.short_video import ShortVideo
from src.sql.models.content import Content
from src.enums.short_video import ShortVideoStatus


def create_short_video(db: Session, short_video_data: dict):
    short_video = ShortVideo()
    short_video.content_id = short_video_data.get("content_id")
    short_video.title = short_video_data.get("title")
    short_video.background_video_url = short_video_data.get("background_video_url")
    short_video.status = short_video_data.get("status")
    db.add(short_video)
    db.commit()
    db.refresh(short_video)
    return short_video


def get_short_video(db: Session, short_video_id: int) -> ShortVideo:
    return db.query(ShortVideo).filter(ShortVideo.id == short_video_id).first()


def get_short_video_by_content_id(db: Session, content_id: int) -> ShortVideo:
    return db.query(ShortVideo).filter(ShortVideo.content_id == content_id).first()


def get_ready_to_upload_short_video(db: Session) -> ShortVideo:
    return (
        db.query(ShortVideo)
        .filter(
            ShortVideo.status == ShortVideoStatus.METADATA_GENERATED,
            ShortVideo.published_at == None,
            ShortVideo.tags != None,
            ShortVideo.description != None,
        )
        .first()
    )


def get_ready_to_metadata_short_video(db: Session) -> ShortVideo:
    return (
        db.query(ShortVideo)
        .filter(
            ShortVideo.status == ShortVideoStatus.PROCESSING,
            ShortVideo.tags == None,
            ShortVideo.youtube_video_url == None,
        )
        .first()
    )


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
        hashtags = short_video_data["hashtags"]
        if isinstance(hashtags, list):
            short_video.tags = ",".join(hashtags)
        else:
            short_video.tags = hashtags
    if "youtube_video_url" in short_video_data:
        short_video.youtube_video_url = short_video_data["youtube_video_url"]
    db.commit()
    db.refresh(short_video)
    return short_video


def delete_short_video(db: Session, short_video: ShortVideo) -> bool:
    db.delete(short_video)
    db.commit()
    return True


def get_all_short_videos(db: Session):
    return db.query(ShortVideo).all()


def get_short_videos_by_status(db: Session, statuses: str, date: dt_date = None):

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


def get_short_video_by_status(db: Session, status: str):
    return db.query(ShortVideo).filter(ShortVideo.status == status).first()


def get_ready_to_process_content(
    db: Session,
    status: str,
    excluded: bool = True,
):
    query = db.query(Content)
    if excluded:
        query = query.filter(Content.status != status)
    else:
        query = query.filter(Content.status == status)
    return query.order_by(Content.id.asc()).first()


def get_short_videos(
    db: Session,
    filter: str = None,
    content_id: int = None,
    ids: list[int] = None,
    id: int = None,
    youtube_url: str = None,
    status: str = None,
    page: int = 1,
    limit: int = 10,
    sort_by: str = "id",
    sort_order: str = "desc",
    start_date: str = None,
    end_date: str = None,
):
    query = db.query(ShortVideo).join(Content, ShortVideo.content_id == Content.id)
    if filter and filter != "":
        search_query = "%" + filter.strip() + "%"
        query = query.filter(
            or_(
                ShortVideo.title.like(search_query),
                ShortVideo.description.like(search_query),
                ShortVideo.tags.like(search_query),
                Content.content.like(search_query),
                ShortVideo.status.like(search_query),
                ShortVideo.output_path.like(search_query),
                ShortVideo.youtube_video_url.like(search_query),
            )
        )
    if content_id and content_id != "":
        query = query.filter(ShortVideo.content_id == content_id)
    if ids and ids != "":
        query = query.filter(ShortVideo.id.in_(ids))
    if id and id != "":
        query = query.filter(ShortVideo.id == id)
    if youtube_url and youtube_url != "":
        query = query.filter(ShortVideo.youtube_video_url == youtube_url)
    if status and status != "":
        query = query.filter(ShortVideo.status == status)
    if sort_by and sort_by != "":
        order_direction = desc if sort_order == "desc" else asc
        query = query.order_by(order_direction(getattr(ShortVideo, sort_by)))
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    if start_date is not None:
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            end_date = end_date + timedelta(days=1) - timedelta(seconds=1)
        query = query.filter(ShortVideo.created_at >= start_date).filter(
            ShortVideo.created_at <= end_date
        )
    total = query.count()
    if page:
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

    return {
        "videos": query.all(),
        "total": total,
        "page": page,
        "limit": limit,
    }
