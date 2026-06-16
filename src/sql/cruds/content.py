from src.sql.models.content import Content
from sqlalchemy.orm import Session
from src.enums.content import ContentStatus


def create_content(db: Session, content_data: dict):
    content = Content()
    content.title = content_data.get("title")
    content.content = content_data.get("content")
    content.status = content_data.get("status")
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


def get_all_contents(db: Session):
    return db.query(Content).all()


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
    if "video_path" in content_data:
        content.video_path = content_data["video_path"]
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
