from enum import Enum


class ShortVideoStatus(str, Enum):
    NOT_STARTED = "not_started"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PUBLISHED = "published"
    FAILED = "failed"
