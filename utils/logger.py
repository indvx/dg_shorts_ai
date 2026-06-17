import logging
import os
import sys
from datetime import datetime


class DGShortsLogger:
    def __init__(self, log_directory: str = "logs", log_level: int = logging.INFO):
        self.log_dir = log_directory
        self.log_level = log_level
        os.makedirs(self.log_dir, exist_ok=True)

        self.logger = logging.getLogger("DGShortsAI")
        self.logger.setLevel(self.log_level)

        self.__configure_handlers()

        self.logger.info("Logger initialized successfully.")

    def __configure_handlers(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        log_file_path = os.path.join(self.log_dir, f"{current_date}.log")

        log_format = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] ➔ %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setFormatter(log_format)
        file_handler.setLevel(self.log_level)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_format)
        console_handler.setLevel(self.log_level)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self) -> logging.Logger:
        return self.logger


logger = DGShortsLogger().get_logger()
