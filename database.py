from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# .env を読み込む
load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# SSL接続を有効化
ssl_args = {
    "ssl": {
        "ca": os.getenv("SSL_CA_PATH"),
        "ssl_mode": os.getenv("DATABASE_SSL_MODE", "require")
    }
}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=ssl_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
