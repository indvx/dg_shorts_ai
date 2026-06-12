from enum import Enum


class ContentStatus(str, Enum):
    DRAFT = "draft"
    AUDIO_GENERATED = "audio_generated"
    VIDEO_GENERATED = "video_generated"
    MERGED = "merged"