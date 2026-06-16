from dotenv import load_dotenv
from sqlalchemy.orm import Session
from src.db.dependencies import get_db

load_dotenv()


class BaseService:
    def __init__(self):
        self.db: Session = next(get_db())

    def _db_close(self):
        self.db.close()
