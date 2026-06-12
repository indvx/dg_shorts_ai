from src.db.base import Base
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.enums.short_video import ShortVideoStatus


class ShortVideo(Base):
    __tablename__ = "short_videos"
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=False)
    title = Column(String)
    output_path = Column(String)
    status = Column(Enum(ShortVideoStatus), nullable=True, default=ShortVideoStatus.NOT_STARTED)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    content = relationship("Content", back_populates="short_video")