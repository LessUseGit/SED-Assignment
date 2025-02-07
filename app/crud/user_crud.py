from sqlalchemy.orm import Session
from app.security import get_password_hash
from app.database.models import User
from app.schemas.user_schemas import UserCreate, UserUpdate


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.user_id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_email_from_user_id(db: Session, user_id: int):
    return db.query(User).filter(User.user_id == user_id).with_entities(User.email).first()[0]


def get_users(db: Session):
    return db.query(User).all()


def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_admin=user.is_admin,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = get_user_by_id(db, user_id)
    # If the password is updated, hash before changing db entry
    if user_update.password:
        user_update.password = get_password_hash(user_update.password)
    if db_user:
        for key, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    # Check if the user exists in the database
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user
