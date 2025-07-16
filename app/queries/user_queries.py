from sqlalchemy.orm import Session

from app.models.attendant_model import Attendant
from app.models.user_model import User


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, id: str):
    return db.query(User).filter(User.user_id == id).first()


def get_all_users(db: Session):
    return db.query(User).all()


def get_attendant(db: Session, user_id: str):
    return db.query(Attendant).filter(Attendant.user_id == user_id).first()
