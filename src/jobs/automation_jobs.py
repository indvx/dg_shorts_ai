from src.services.script import ScriptService


# Clean log files
def clean_last_7_days_log_file_job():
    ScriptService().clean_last_7_days_log_file()


# Clean contents
def clean_last_7_days_contents_job():
    ScriptService().clean_last_7_days_contents()


# Clean uploaded videos
# def clean_uploaded_video_job():
#     ScriptService().clean_uploaded_video()


# Generate topic
def generate_topic_job():
    ScriptService().generate_topic()


# Create content
def create_content_job():
    ScriptService().create_content()


# Create audio
def create_audio_job():
    ScriptService().create_audio()


# Fetch and generate video
def fetch_and_generate_video_job():
    ScriptService().generate_bg_video()


# Merge video and audio
def merge_video_and_audio_job():
    ScriptService().merge_video_and_audio()


# Update video metadata
def update_video_metadata_job():
    ScriptService().update_video_metadata()


# Upload video on youtube
def upload_video_on_youtube_job():
    ScriptService().upload_video_on_youtube()
