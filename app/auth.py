from datetime import timedelta, datetime
from fastapi import Cookie, Depends, HTTPException
from jose import jwt
from sqlalchemy.orm import Session

from app.crud.user_crud import get_user_by_email, get_user_by_username
from app.database.database import get_db
from app.security import verify_password

# Constants for token generation
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    """
    Create a JWT access token.

    :param data: Data to encode into the token (e.g., user's email).
    :param expires_delta: Time until the token expires.
    :return: Encoded JWT token as a string.
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    """
    Authenticates the user by email and password.

    :param username: The username of the user trying to log in.
    :param password: The plain text password provided by the user.
    :param db: The SQLAlchemy database session.
    :return: The User object if authentication is successful, False otherwise.
    """
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_current_user(
    db: Session = Depends(get_db), cookie: str = Cookie(None, alias="access_token")
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not cookie:
        raise HTTPException(
            status_code=401,
            detail="No access token/cookie provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        token = cookie.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
    except:
        raise credentials_exception

    if email is None:
        raise credentials_exception

    user = get_user_by_email(db, email)

    if user is None:
        raise credentials_exception

    return user
