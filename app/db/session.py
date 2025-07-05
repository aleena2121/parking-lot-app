from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.load_config import DBSettings

engine = create_engine(str(DBSettings.SQLALCHEMY_DATABASE_URI))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
