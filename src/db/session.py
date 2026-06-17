from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_DATABASE_URL = "{}://{}:{}@{}:{}/{}".format(
    os.getenv("DB_CONNECTION", default="mysql+pymysql"),
    os.getenv("DB_USER", default="root"),
    os.getenv("DB_PASSWORD", default="root"),
    os.getenv("DB_HOST", default="localhost"),
    os.getenv("DB_PORT", default="3306"),
    os.getenv("DB_NAME", default="python"),
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
