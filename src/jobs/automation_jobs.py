from src.services.automation import AutomationService


# Clean log files
def clean_last_7_days_log_file_job():
    AutomationService().clean_last_7_days_log_file()


# Clean contents
def clean_last_7_days_contents_job():
    AutomationService().clean_last_7_days_contents()


# Clean uploaded videos
def clean_uploaded_video_job():
    AutomationService().clean_uploaded_video()


# Generate topic
def generate_topic_job():
    AutomationService().generate_topic()


# Create content
def create_content_job():
    AutomationService().create_content()


# Create audio
def create_audio_job():
    AutomationService().create_audio()


# Fetch and generate video
def fetch_and_generate_video_job():
    AutomationService().fetch_and_generate_video()


# Merge video and audio
def merge_video_and_audio_job():
    AutomationService().merge_video_and_audio()


# Update video metadata
def update_video_metadata_job():
    AutomationService().update_video_metadata()


# Upload video on youtube
def upload_video_on_youtube_job():
    AutomationService().upload_video_on_youtube()
