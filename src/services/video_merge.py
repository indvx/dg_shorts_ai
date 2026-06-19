from src.services.base import BaseService
from utils.logger import logger

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeAudioClip,
)
from moviepy.audio.fx import AudioLoop, MultiplyVolume, AudioFadeIn, AudioFadeOut
from src.sql.cruds import content as content_crud
from src.sql.cruds import short_video as short_video_crud
from src.enums.content import ContentStatus
from src.enums.short_video import ShortVideoStatus
import math
import os, random


class VideoMergeService(BaseService):
    def __init__(self):
        super().__init__()
        self.output_directory = os.getenv("VIDEO_OUTPUT_DIRECTORY")
        self.music_directory = os.getenv("MUSIC_DIRECTORY")

    def merge_and_mute_video(self, content_id: int):
        logger.info(f"Audio-Video Stitching Module started... {content_id}")

        content = content_crud.get_content(self.db, content_id)
        if not content:
            logger.error(f"Content with id {content_id} not found.")
            raise ValueError(f"Content with id {content_id} not found.")

        if content.status != ContentStatus.VIDEO_GENERATED:
            logger.error(
                f"Content with id {content_id} is not in video generated state: {content.status}"
            )
            raise ValueError(
                f"Content with id {content_id} is not in video generated state."
            )
        os.makedirs(self.output_directory, exist_ok=True)
        os.makedirs(self.music_directory, exist_ok=True)
        output_path = content.video_path.replace("video", "output")
        video_clip = None
        audio_clip = None
        final_clip = None
        music_clip = None
        final_audio = None
        base_video = None

        try:
            audio_clip = AudioFileClip(content.audio_path)
            audio_duration = audio_clip.duration

            music_name = random.choice(os.listdir(self.music_directory))
            music_clip = AudioFileClip(os.path.join(self.music_directory, music_name))
            music_clip = music_clip.with_effects(
                [
                    AudioLoop(duration=audio_duration),
                    MultiplyVolume(0.12),
                    AudioFadeIn(1),
                    AudioFadeOut(2),
                ]
            )

            final_audio = CompositeAudioClip([audio_clip, music_clip])

            logger.info(f"Target Audio Duration: {final_audio.duration:.2f} seconds.")

            base_video = VideoFileClip(content.video_path).without_audio()
            video_duration = base_video.duration
            logger.info(f"Raw Background Video Duration: {video_duration:.2f} seconds.")

            if video_duration < final_audio.duration:
                loop_factor = math.ceil(final_audio.duration / video_duration)
                logger.warning(
                    f"Duration Warning! Audio ({final_audio.duration:.2f}s) is longer than Video ({video_duration:.2f}s). "
                    f"Chaining video sequentially [{loop_factor} times] to extend timeline..."
                )

                video_clip = concatenate_videoclips([base_video] * loop_factor)
            else:
                logger.info("Video length is sufficient for the audio track.")
                video_clip = base_video

            trimmed_video = video_clip.subclipped(0, final_audio.duration)

            final_clip = trimmed_video.with_audio(final_audio)

            logger.info(
                f"Rendering loop-stabilized isolated video container: {output_path}"
            )
            final_clip.write_videofile(
                output_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                logger=None,
                threads=4,
            )
            logger.info("Video compiled flawlessly without pipeline execution gaps!")

            content_crud.update_content(
                self.db, content, {"status": ContentStatus.MERGED}
            )
            short_video_crud.create_short_video(
                self.db,
                {
                    "content_id": content.id,
                    "output_path": output_path,
                    "status": ShortVideoStatus.NOT_STARTED,
                },
            )

            return output_path

        except Exception as e:
            logger.error(f"Failed media rendering sequence framework loops: {str(e)}")
            raise RuntimeError("Video orchestration system failure") from e

        finally:
            logger.info("Flushing temporary multi-media streams from RAM buffers...")
            if final_clip:
                final_clip.close()
            if video_clip and video_clip != base_video:
                video_clip.close()
            if base_video:
                base_video.close()
            if audio_clip:
                audio_clip.close()
