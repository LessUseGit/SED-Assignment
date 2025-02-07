import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_successful_registration():
    test_user = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "is_admin": False,
    }
    response = client.post(
        "/register",
        data=test_user,
    )
    assert response.status_code == 200
    assert "Successfully registered" in response.text


def test_registration_with_existing_email():
    test_user_2 = {
        "username": "testuser2",
        "email": "existing_email@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "is_admin": False,
    }

    new_user = {
        "username": "newuser",
        "email": "existing_email@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "is_admin": False,
    }

    client.post(
        "/register",
        data=test_user_2,
    )

    response = client.post(
        "/register",
        data=new_user,
    )
    assert response.status_code == 200
    assert "User with that email already exists" in response.text


def test_registration_with_existing_username():
    test_user_3 = {
        "username": "testuser3",
        "email": "testuser3@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "is_admin": False,
    }

    test_user_3_diff_details = {
        "username": "testuser3",
        "email": "new_email@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "is_admin": False,
    }

    client.post(
        "/register",
        data=test_user_3,
    )

    response = client.post(
        "/register",
        data=test_user_3_diff_details,
    )
    assert response.status_code == 200
    assert "User with that username already exists" in response.text


def test_registration_with_password_mismatch():
    test_user_4 = {
        "username": "testuser4",
        "email": "testuser4@example.com",
        "password": "password123",
        "confirm_password": "mismatch123",
        "is_admin": False,
    }
    response = client.post(
        "/register",
        data=test_user_4,
    )
    assert response.status_code == 200
    assert "Passwords do not match" in response.text


def test_successful_login():
    user_data = {
        "username": "testuser5",
        "email": "testuser5@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "is_admin": False,
    }
    client.post("/register", data=user_data)

    response = client.post(
        "/login",
        data={
            "username": "testuser5",
            "password": "password123",
        },
        allow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/dashboard"
    assert "access_token" in response.cookies


def test_failed_login():
    response = client.post(
        "/login",
        data={
            "username": "non_existent_user",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.text


def test_access_protected_route_with_valid_token():
    user_data = {
        "username": "testuser6",
        "email": "testuser6@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "is_admin": False,
    }
    client.post("/register", data=user_data)

    login_response = client.post(
        "/login",
        data={
            "username": "testuser6",
            "password": "password123",
        },
        allow_redirects=False,
    )

    token = login_response.cookies["access_token"]

    response = client.get("/dashboard", cookies={"access_token": token})

    assert response.status_code == 200


def test_access_protected_route_with_invalid_token():
    payload = {"sub": "user@example.com"}
    secret = "wrong_secret"
    invalid_token = jwt.encode(payload, secret, algorithm="HS256")
    response = client.get("/dashboard", cookies={"access_token": invalid_token})
    assert response.status_code == 401


def test_successful_logout():
    # Register new user
    user_data = {
        "username": "testuser6",
        "email": "testuser6@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "is_admin": False,
    }
    client.post("/register", data=user_data)

    # Login with user
    login_response = client.post(
        "/login",
        data={"username": "testuser6", "password": "password123"},
        allow_redirects=False,
    )
    assert login_response.status_code == 302

    # Ensure access token has been issued
    access_token = login_response.cookies.get("access_token")
    assert access_token is not None

    # Test logging user out
    logout_response = client.get(
        "/logout", cookies={"access_token": access_token}, allow_redirects=False
    )
    assert logout_response.status_code == 302

    # Follow redirect after logout
    logout_redirect = client.get("/login")
    assert "Logout successful" in logout_redirect.text
    assert logout_redirect.status_code == 200
    assert logout_redirect.cookies.get("access_token") is None
