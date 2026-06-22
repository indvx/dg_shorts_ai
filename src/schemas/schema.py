from pydantic import BaseModel
import typing as t


class TopicCreateSchema(BaseModel):
    name: str


class TopicSchema(BaseModel):
    id: int
    name: str
    slug: str
    used_count: int
    last_used_at: t.Any
    created_at: t.Any
    updated_at: t.Any

class JobResponseSchema(BaseModel):
    id: str
    next_run_time: t.Any
    trigger: t.Optional[str]
