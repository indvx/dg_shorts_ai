from pydantic import BaseModel
import typing as t

class GenerateScriptSchema(BaseModel):
    topic_id: int

    
class JobResponseSchema(BaseModel):
    id: str
    next_run_time: t.Any
    trigger: t.Optional[str]
