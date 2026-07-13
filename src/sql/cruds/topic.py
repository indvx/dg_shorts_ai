from datetime import datetime, timedelta, UTC

from sqlalchemy import or_, asc, desc
from sqlalchemy.orm import Session

from src.sql.models.topic import Topic


def get_topic(db: Session, topic_id: int) -> Topic:
    return db.query(Topic).filter(Topic.id == topic_id).first()


def get_topic_by_slug(db: Session, topic_slug: str) -> Topic:
    return db.query(Topic).filter(Topic.slug == topic_slug).first()


def get_unused_topic(db: Session, days: int = 10, id: int | None = None) -> Topic:
    query = db.query(Topic).filter(
        or_(
            Topic.last_used_at < datetime.now(UTC) - timedelta(days=days),
            Topic.used_count < 3,
        )
    )

    if id is not None and id != 0:
        query = query.filter(Topic.id == id)

    result = query.order_by(Topic.used_count.asc()).first()
    return result


def update_topic(db: Session, topic: Topic) -> Topic:
    topic.used_count += 1
    topic.last_used_at = datetime.now(UTC)
    db.commit()
    db.refresh(topic)
    return topic


def add_topic(db: Session, topic_name, topic_slug):
    topic = Topic(name=topic_name, slug=topic_slug, used_count=0)
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


def get_all_topics(
    db: Session,
    page: int = 1,
    limit: int = 10,
    used_count: int = None,
    last_used_at: datetime = None,
    filter: str = None,
    id: int = None,
    ids: list[int] = None,
    sort_by: str = "id",
    sort_order: str = "asc",
    start_date: datetime = None,
    end_date: datetime = None,
):
    query = db.query(Topic)
    if used_count is not None:
        query = query.filter(Topic.used_count == used_count)

    if filter is not None and filter != "":
        search_term = f"%{filter.strip()}%"
        query = query.filter(
            or_(Topic.name.like(search_term), Topic.slug.like(search_term))
        )
    if sort_by and sort_by != "":
        direction = asc if sort_order == "asc" else desc
        query = query.order_by(direction(getattr(Topic, sort_by)))

    if id is not None and id != 0:
        query = query.filter(Topic.id == id)

    if ids is not None and len(ids) > 0:
        query = query.filter(Topic.id.in_(ids))

    if start_date is not None:
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            end_date = end_date + timedelta(days=1) - timedelta(seconds=1)

        query = query.filter(Topic.created_at >= start_date).filter(
            Topic.created_at <= end_date
        )

    if last_used_at is not None:
        query = query.filter(Topic.last_used_at <= last_used_at)

    total_count = query.count()
    if page and page > 0:
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

    items = query.all()
    return {
        "topics": items,
        "total": total_count,
        "page": page,
        "limit": limit,
    }


def delete_topic(db: Session, topic: Topic) -> bool:
    db.delete(topic)
    db.commit()
    return True


def get_topics(db: Session):
    query = db.query(Topic)
    items = query.all()
    return items
