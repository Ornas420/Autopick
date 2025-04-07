import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_register(client):
    response = client.post("/register", json={
        "username": "testuser1",
        "password": "testpass"
    })
    assert response.status_code == 200 or response.status_code == 400  # handle already exists case

def test_login(client):
    response = client.post("/login", json={
        "username": "testuser1",
        "password": "testpass"
    })
    assert response.status_code == 200

def test_logout_flow(client):
    test_user = {
        "username": "testuser2",
        "password": "testpass"
    }

    # Register the user
    response = client.post("/register", json=test_user)
    assert response.status_code == 200 or response.status_code == 400

    # Log the user in
    response = client.post("/login", json=test_user)
    assert response.status_code == 200

    # Log the user out
    response = client.post("/logout")
    assert response.status_code == 200
