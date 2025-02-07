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


@pytest.fixture
def create_asset(login_user):
    asset_data = {
        "name": "Test Asset",
        "serial_number": "123456",
        "type": "Test Type",
        "owner_email": "testuser@example.com",
    }
    client.post("/assets/add", data=asset_data, cookies=login_user)
    return asset_data


def test_add_asset(login_user):
    asset_data = {
        "name": "New Asset",
        "serial_number": "654321",
        "type": "New Type",
        "owner_email": "testuser@example.com",
    }
    response = client.post(
        "/assets/add", data=asset_data, cookies=login_user, allow_redirects=False
    )
    assert response.status_code == 302

    redirect_response = client.get("/dashboard", cookies=login_user)
    assert "Asset added successfully" in redirect_response.text


def test_add_asset_with_nonexistent_owner(login_user):
    asset_data = {
        "name": "Nonexistent Asset",
        "serial_number": "111222",
        "type": "Nonexistent Type",
        "owner_email": "nonexistent@example.com",
    }
    response = client.post(
        "/assets/add", data=asset_data, cookies=login_user, allow_redirects=False
    )
    assert response.status_code == 302

    redirect_response = client.get("/dashboard", cookies=login_user)
    assert "User not found" in redirect_response.text


def test_get_asset_by_id(create_asset):
    response = client.get("/assets/getById?asset_id=1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Asset"


def test_update_asset(login_user, create_asset):
    updated_asset_data = {
        "name": "Updated Asset",
        "serial_number": "654321",
        "type": "Updated Type",
        "status": "active",
        "owner_email": "testuser@example.com",
    }
    response = client.post(
        "/assets/update/1",
        data=updated_asset_data,
        cookies=login_user,
        allow_redirects=False,
    )
    assert response.status_code == 302

    redirect_response = client.get("/dashboard", cookies=login_user)
    assert "Asset successfully updated" in redirect_response.text


def test_update_asset_with_nonexistent_owner(login_user, create_asset):
    updated_asset_data = {
        "name": "Updated Asset",
        "serial_number": "654321",
        "type": "Updated Type",
        "status": "active",
        "owner_email": "nonexistent@example.com",
    }
    response = client.post(
        "/assets/update/1",
        data=updated_asset_data,
        cookies=login_user,
        allow_redirects=False,
    )
    assert response.status_code == 302

    redirect_response = client.get("/dashboard", cookies=login_user)
    assert "User not found" in redirect_response.text


def test_delete_asset(login_user, create_asset):
    response = client.post(
        "/assets/delete/1", cookies=login_user, allow_redirects=False
    )
    assert response.status_code == 302

    redirect_response = client.get("/dashboard", cookies=login_user)
    assert "Asset successfully deleted" in redirect_response.text


def test_delete_nonexistent_asset(login_user):
    response = client.post(
        "/assets/delete/999", cookies=login_user, allow_redirects=False
    )
    assert response.status_code == 302

    redirect_response = client.get("/dashboard", cookies=login_user)
    assert "Failed to delete asset" in redirect_response.text
