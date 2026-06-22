from enum import Enum


class ShortVideoStatus(str, Enum):
    NOT_STARTED = "not_started"
    PROCESSING = "processing"
    METADATA_GENERATED = "metadata_generated"
    PUBLISHED = "published"
    FAILED = "failed"
