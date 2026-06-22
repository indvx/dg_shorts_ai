from pydantic import BaseModel
from src.enums.short_video import ShortVideoStatus
from src.schemas.content import ContentUpdateSchema
import typing as t


class ShortVideoSchema(BaseModel):
    id: t.Optional[int]
    content_id: t.Optional[int]
    title: t.Optional[str]
    description: t.Optional[str]
    tags: t.Optional[str]
    background_video_url: t.Optional[str]
    output_path: t.Optional[str]
    youtube_video_url: t.Optional[str]
    status: t.Optional[ShortVideoStatus]
    created_at: t.Optional[t.Any]
    updated_at: t.Optional[t.Any]
    published_at: t.Optional[t.Any]
    content: t.Optional[ContentUpdateSchema]
