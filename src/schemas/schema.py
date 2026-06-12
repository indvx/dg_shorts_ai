from pydantic import BaseModel


class GenerateScriptSchema(BaseModel):
    topic: str
