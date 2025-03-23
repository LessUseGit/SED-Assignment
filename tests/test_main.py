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


def test_dashboard(login_user):
    response = client.get("/dashboard", cookies=login_user)

    assert response.status_code == 200
    assert "Asset Management Dashboard" in response.text


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"msg": "hello world :)"}


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "IT Asset Management Application" in response.text
