import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from utils.logger import logger
from src.services.base import BaseService

class YouTubeService(BaseService):
    def __init__(self):
        super().__init__()
        scopes_raw = os.getenv("YOUTUBE_SCOPES", "https://www.googleapis.com/auth/youtube.upload")
        if scopes_raw:
            self.scopes = [ s.strip() for s in scopes_raw.split(",") if s.strip()]
        else:
            self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        
        self.google_secret_file = os.getenv("GOOGLE_CLIENT_SECRET")
        self.google_token_file = os.getenv("GOOGLE_TOKEN_PICKLE")
        self.youtube_client = self.__authenticate_and_login()

    def __authenticate_and_login(self):
        credentials = None
        
        if os.path.exists(self.google_token_file):
            with open(self.google_token_file, "rb") as token:
                credentials = pickle.load(token)
                
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                logger.info("YouTube Access token expired. Refreshing background session...")
                credentials.refresh(Request())
            else:
                logger.info("No valid token session found. Launching local interactive auth browser...")
                if not os.path.exists(self.google_secret_file):
                    logger.critical(f"Missing critical OAuth secret configuration file at: {self.google_secret_file}")
                    raise FileNotFoundError(f"Please place client_secret.json at: {self.google_secret_file}")
                
                flow = InstalledAppFlow.from_client_secrets_file(self.google_secret_file, self.scopes)
                credentials = flow.run_local_server(port=0)
            
            with open(self.google_token_file, "wb") as token:
                pickle.dump(credentials, token)

        return build("youtube", "v3", credentials=credentials)

    def upload_shorts_video(self, video_file_path: str, title: str, description: str, tags_list: list) -> str:
        if not os.path.exists(video_file_path):
            logger.error(f"Upload aborted. Video target missing from storage: {video_file_path}")
            raise FileNotFoundError(f"Missing video binary at: {video_file_path}")

        final_title = title if "#shorts" in title.lower() else f"{title} #Shorts"
        
        logger.info(f"Streaming binary chunks into YouTube Ingestion Pipeline: '{final_title}'")
        logger.info(f"Tags: {tags_list}")
        
        body = {
            "snippet": {
                "title": final_title,
                "description": description,
                "tags": tags_list,
                "categoryId": "22"  # Category 22 is for People & Blogs / Entertainment
            },
            "status": {
                "privacyStatus": "public",  # Direct live publish. Use 'private' or 'unlisted' for testing.
                "selfDeclaredMadeForKids": False
            }
        }

        try:
            media = MediaFileUpload(video_file_path, chunksize=1024*1024, resumable=True, mimetype="video/mp4")
            
            request = self.youtube_client.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Uploading Data Stream Completion Metrics: {int(status.progress() * 100)}%")
            
            video_id = response.get("id")
            logger.info(f"SUCCESS! Video is now available on YouTube. Video ID Asset Link: https://youtu.be/{video_id}")
            return video_id

        except Exception as api_fault:
            logger.error(f"YouTube API dropped active broadcasting connection stream: {str(api_fault)}")
            raise RuntimeError("Broadcast platform lifecycle failure") from api_fault