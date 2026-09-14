import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
load_dotenv()
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine
)

Base = declarative_base()

with engine.connect() as connection:
    print("数据库连接成功")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
