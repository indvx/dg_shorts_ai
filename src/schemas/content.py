from pydantic import BaseModel
import typing as t
from src.enums.content import ContentStatus


class GenerateScriptSchema(BaseModel):
    topic_id: int


class ContentUpdateSchema(BaseModel):
    title: t.Optional[str]
    content: t.Optional[str]
    voice_id: t.Optional[str]
    status: t.Optional[ContentStatus]
    audio_path: t.Optional[str]
