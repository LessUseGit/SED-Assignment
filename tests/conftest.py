import pytest
from slowapi import Limiter
from starlette.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Creates a test client with access to the FastAPI app."""
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_rate_limiter(client):
    """Resets the rate limiter cache so each test starts fresh."""
    if hasattr(client.app.state, "limiter") and isinstance(client.app.state.limiter, Limiter):
        client.app.state.limiter.reset()