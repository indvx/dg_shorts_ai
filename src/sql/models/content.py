from src.db.base import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.enums.content import ContentStatus


class Content(Base):
    __tablename__ = "contents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    voice_id = Column(String(255), nullable=True, default="JBFqnCBsd6RMkjVDRZzb")
    status = Column(Enum(ContentStatus), nullable=True, default=ContentStatus.DRAFT)
    audio_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    short_video = relationship(
        "ShortVideo", back_populates="content", cascade="all, delete-orphan"
    )
