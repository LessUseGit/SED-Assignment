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
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict):
    """
    Generates a JWT access token with an expiration time (60 mins).

    Args:
        data (dict): Data to encode into the token (e.g., user's email).

    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    """
    Authenticates a user by verifying their username and password.

    Args:
        username (str): The username of the user attempting to log in.
        password (str): The plain text password provided by the user.
        db (Session): The SQLAlchemy database session.

    Returns:
        User: The authenticated User object if successful.
        bool: False if authentication fails.
    """
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


def get_current_user(
    db: Session = Depends(get_db), cookie: str = Cookie(None, alias="access_token")
):
    """
    Retrieves the currently authenticated user based on the provided access token.

    Args:
        db (Session): Database session dependency for querying the user.
        cookie (str): Access token stored in a cookie, used for authentication.

    Returns:
        User: The authenticated user object if the token is valid.

    Raises:
        HTTPException: 
            - 401 Unauthorized if no access token is provided.
            - 401 Unauthorized if the token is invalid or expired.
            - 401 Unauthorized if the user does not exist in the database.
    """
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
