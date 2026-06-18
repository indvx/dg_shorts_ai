from dotenv import load_dotenv
from sqlalchemy.orm import Session
from src.db.dependencies import get_db
import hashlib
import re

load_dotenv()


class BaseService:
    def __init__(self):
        self.db: Session = next(get_db())

    def _db_close(self):
        self.db.close()

    def normalize_topic(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^a-z0-9\s]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text

    def get_topic_slug(self, text: str) -> str:
        normalized = self.normalize_topic(text)
        return hashlib.sha256(normalized.encode()).hexdigest()
