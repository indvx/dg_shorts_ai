import os
from utils.logger import app_logger as logger
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from src.db.dependencies import get_db

load_dotenv()


class BaseService:
    def __init__(self, provider_name: str, env_key_name: str, check_env_key=True):
        self.provider = provider_name
        self.__api_key = os.getenv(env_key_name)
        self.db: Session = next(get_db())

        if check_env_key and not self.__api_key:
            logger.critical(
                f"Initialization Failed: Key '{env_key_name}' missing in environment."
            )
            raise EnvironmentError(f"Missing configuration token for {self.provider}")

        logger.info(f"{self.provider} service subclass initialized successfully.")

    def _get_secure_key(self) -> str:
        return self.__api_key
