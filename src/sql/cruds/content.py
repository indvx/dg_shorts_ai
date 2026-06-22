from src.sql.models.content import Content
from sqlalchemy.orm import Session
from src.enums.content import ContentStatus
from datetime import datetime, timedelta, UTC
from sqlalchemy import asc, desc, or_


def create_content(db: Session, content_data: dict) -> Content:
    content = Content()
    content.title = content_data.get("title")
    content.content = content_data.get("content")
    content.status = content_data.get("status")
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


def get_days_old_contents(db: Session, days: int = 7) -> list[Content]:
    query = db.query(Content)
    if days is not None and days != 0:
        filter_date = datetime.now(UTC) - timedelta(days=days)
        query = query.filter(Content.created_at <= filter_date)
    return query.all()


def get_content(db: Session, content_id: int) -> Content:
    return db.query(Content).filter(Content.id == content_id).first()


def update_content(db: Session, content: Content, content_data: dict) -> Content:
    if "title" in content_data:
        content.title = content_data["title"]
    if "content" in content_data:
        content.content = content_data["content"]
    if "status" in content_data:
        content.status = content_data["status"]
    if "audio_path" in content_data:
        content.audio_path = content_data["audio_path"]
    db.commit()
    db.refresh(content)
    return content


def delete_content(db: Session, content: Content) -> bool:
    db.delete(content)
    db.commit()
    return True


def get_contents_by_status(db: Session, status: str):
    return db.query(Content).filter(Content.status == status).all()


def get_ready_to_process_content(
    db: Session,
    target_status: list[str] = [],
    excluded: bool = False,
):
    if excluded:
        return (
            db.query(Content)
            .filter(
                Content.status.notin_(target_status),
                Content.status != ContentStatus.VIDEO_PUBLISHED,
            )
            .first()
        )
    else:
        return (
            db.query(Content)
            .filter(
                Content.status.in_(target_status),
                Content.status != ContentStatus.VIDEO_PUBLISHED,
            )
            .first()
        )


def get_all_contents(
    db: Session,
    filter: str = None,
    id: int = None,
    ids: list[int] = None,
    status: str = None,
    limit: int = 10,
    page: int = 1,
    sort_by: str = "id",
    order_by: str = "desc",
    start_date: str = None,
    end_date: str = None,
):
    query = db.query(Content)
    if filter and filter != "":
        filter_string = "%" + filter.strip() + "%"
        query = query.filter(
            or_(
                Content.title.like(filter_string),
                Content.content.like(filter_string),
                Content.voice_id.like(filter_string),
                Content.audio_path.like(filter_string),
            )
        )
    if id and id != 0:
        query = query.filter(Content.id == id)

    if ids and len(ids) > 0:
        query = query.filter(Content.id.in_(ids))

    if status and status != "":
        query = query.filter(Content.status == status)

    if sort_by and sort_by != "":
        order_direction = desc if order_by == "desc" else asc
        query = query.order_by(order_direction(getattr(Content, sort_by)))

    if start_date is not None:
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            end_date = end_date + timedelta(days=1) - timedelta(seconds=1)

        query = query.filter(Content.created_at >= start_date).filter(
            Content.created_at <= end_date
        )

    total_count = query.count()
    if page and page > 0:
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

    items = query.all()
    return {
        "contents": items,
        "total": total_count,
        "page": page,
        "limit": limit,
    }
