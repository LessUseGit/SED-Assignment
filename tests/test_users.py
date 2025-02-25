import pytest
from fastapi.testclient import TestClient
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


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def create_user():
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "is_admin": False,
    }
    client.post("/register", data=user_data)
    return user_data


@pytest.fixture
def login_user(create_user):
    response = client.post(
        "/login",
        data={"username": create_user["username"], "password": create_user["password"]},
    )
    return response.cookies


def test_add_user(login_user):
    user_data = {
        "username": "new_user",
        "email": "new_user@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "is_admin": False,
        "is_active": True,
    }
    response = client.post(
        "/users/add", data=user_data, cookies=login_user, follow_redirects=False
    )
    assert response.status_code == 302

    redirect_response = client.get("/users/management", cookies=login_user)
    assert redirect_response.status_code == 200
    assert "User added successfully" in redirect_response.text


def test_add_user_with_existing_email(login_user):
    user_duplicate_email_1 = {
        "username": "duplicate_email_user",
        "email": "duplicate@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "is_admin": False,
        "is_active": True,
    }

    user_duplicate_email_2 = {
        "username": "another_user",
        "email": "duplicate@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "is_admin": False,
        "is_active": True,
    }
    client.post(
        "/users/add",
        data=user_duplicate_email_1,
    )

    response = client.post(
        "/users/add",
        data=user_duplicate_email_2,
        cookies=login_user,
        follow_redirects=False,
    )
    assert response.status_code == 302

    redirect_response = client.get("/users/management", cookies=login_user)
    assert redirect_response.status_code == 200
    assert "User with this email already exists" in redirect_response.text


def test_update_user(login_user):
    user_data = {
        "username": "user",
        "email": "user@example.com",
        "password": "newpassword123",
        "is_admin": True,
        "is_active": True,
    }

    updated_user_data = {
        "username": "updated_user",
        "email": "updated_user@example.com",
        "password": "newpassword123",
        "is_admin": False,
        "is_active": False,
    }
    # Assume the user created in create_user has user_id=1
    client.post(
        "/users/add",
        data=user_data,
        cookies=login_user,
    )

    response = client.post(
        "/users/update/2",
        data=updated_user_data,
        cookies=login_user,
        follow_redirects=False,
    )
    assert response.status_code == 302

    redirect_response = client.get("/users/management", cookies=login_user)
    assert redirect_response.status_code == 200
    # assert "User successfully updated" in redirect_response.text


def test_update_user_with_existing_email(login_user):
    existing_user_email_1 = {
        "username": "existing_email_user",
        "email": "existing_email@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "is_admin": False,
        "is_active": True,
    }

    existing_user_email_2 = {
        "username": "updated_user",
        "email": "existing_email@example.com",
        "password": "newpassword123",
        "is_admin": True,
        "is_active": True,
    }

    client.post(
        "/users/add",
        data=existing_user_email_1,
    )
    response = client.post(
        "/users/update/2", data=existing_user_email_2, follow_redirects=False
    )
    assert response.status_code == 302

    redirect_response = client.get("/users/management", cookies=login_user)
    assert redirect_response.status_code == 200
    # assert "User with this email already exists" in redirect_response.text


# def test_update_user_with_nonexistent_id():
#     user_data = {
#         "username": "nonexistent_user",
#         "email": "nonexistent@example.com",
#         "password": "newpassword123",
#         "is_admin": True,
#         "is_active": True,
#     }

#     response = client.post("/users/update/999", data=user_data)
#     assert response.status_code == 401
#     assert "Failed to update user" in response.text


# def test_delete_user(create_user, login_user):
#     response = client.post("/users/delete/1", cookies=login_user)
#     assert response.status_code == 401
#     assert "User deleted successfully" in response.text


# def test_delete_nonexistent_user():
#     response = client.post("/users/delete/999")
#     assert response.status_code == 401
#     assert "Failed to delete user" in response.text
