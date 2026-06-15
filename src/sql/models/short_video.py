from src.db.base import Base
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.enums.short_video import ShortVideoStatus


class ShortVideo(Base):
    __tablename__ = "short_videos"
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=False)
    title = Column(String)
    description = Column(Text, nullable=True)
    tags = Column(String, nullable=True)
    output_path = Column(String)
    youtube_video_path = Column(String, nullable=True)
    status = Column(Enum(ShortVideoStatus), nullable=True, default=ShortVideoStatus.NOT_STARTED)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    content = relationship("Content", back_populates="short_video")