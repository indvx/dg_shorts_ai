import os, uuid
import requests
from utils.logger import app_logger as logger
from src.services.base import BaseService
from src.sql.cruds import content as content_crud
from src.enums.content import ContentStatus


class VideoGeneratorService(BaseService):
    def __init__(self):
        super().__init__(
            provider_name="Pexels Video Generator", env_key_name="PEXELS_API_KEY"
        )
        self.api_url = "https://api.pexels.com/videos/search"

    def fetch_and_download_background(self, content_id: int) -> str:
        content = content_crud.get_content(self.db, content_id)
        if not content:
            raise ValueError("Content not found")
        if not content.status == ContentStatus.AUDIO_GENERATED:
            raise ValueError("Content audio not generated.")

        search_query = content.title
        headers = {"Authorization": self._get_secure_key()}
        params = {"query": search_query, "per_page": 5, "orientation": "portrait"}

        try:
            logger.info(f"Searching Pexels for vertical stock videos: '{search_query}'")
            response = requests.get(
                self.api_url, headers=headers, params=params, timeout=10
            )
            if response.status_code != 200:
                raise RuntimeError(f"Pexels API error: {response.text}")

            data = response.json()
            download_url = self.parse_and_extract_hd_link(data)
            logger.info(f"Downloading binary stream from Pexels CDN...")
            video_data = requests.get(download_url, stream=True, timeout=30)

            filename = f"{content.audio_path.split("/")[-1].replace(".mp3", ".mp4")}"
            os.makedirs("data/video", exist_ok=True)
            download_path = f"data/video/{filename}"
            with open(download_path, "wb") as f:
                for chunk in video_data.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Background video asset saved at: {download_path}")

            content_crud.update_content(
                self.db,
                content,
                {
                    "video_path": download_path,
                    "status": ContentStatus.VIDEO_GENERATED,
                },
            )

            return download_path

        except Exception as e:
            logger.error(f"Failed to fetch video from Pexels API: {str(e)}")
            raise e

    def parse_and_extract_hd_link(self, pexels_response_json: dict) -> str:
        videos = pexels_response_json.get("videos", [])
        if not videos:
            logger.warning(
                "Empty video array block processed from stock metadata provider."
            )
            raise ValueError(
                "Empty video array block processed from stock metadata provider."
            )

        target_video = videos[0]
        video_files = target_video.get("video_files", [])

        selected_link = None

        for file_node in video_files:
            width = file_node.get("width")
            height = file_node.get("height")

            if width == 1080 and height == 1920:
                selected_link = file_node.get("link")
                logger.info(
                    f"Perfect 1080x1920 Portrait stream verified: {selected_link}"
                )
                break

        if not selected_link and video_files:
            selected_link = video_files[0].get("link")
            logger.warning(
                f"Exact HD 1080x1920 matching node missing. Falling back to alternative size track."
            )

        return selected_link
