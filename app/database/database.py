import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL","sqlite:///./database.sqlite")

if "pytest" in os.environ.get("_", ""):
    DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
