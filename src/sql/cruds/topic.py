from datetime import datetime, timedelta, UTC

from sqlalchemy import or_
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
