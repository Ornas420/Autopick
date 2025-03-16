import pytest
import sys
import os

# Add backend directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, db, User, bcrypt  # Now it should work
from flask import json
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    """Creates a test client for Flask and sets up a test database."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Use in-memory database
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def token(client):
    """Creates a test user and returns a valid JWT token."""
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')
        user = User(username='testuser', password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return create_access_token(identity='testuser')

def test_update_user_success(client, token):
    """Test successful user update."""
    response = client.put(
        "/update_user",
        headers={'Authorization': f'Bearer {token}'},
        data=json.dumps({"username": "newusername", "password": "newpassword"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json["message"] == "User information updated successfully"

    # Verify user information is updated in the database
    with app.app_context():
        user = User.query.filter_by(username="newusername").first()
        assert user is not None
        assert bcrypt.check_password_hash(user.password, "newpassword")

def test_update_user_username_exists(client, token):
    """Test update failure when the new username already exists."""
    with app.app_context():
        # Create another user with the new username
        hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')
        another_user = User(username='newusername', password=hashed_password)
        db.session.add(another_user)
        db.session.commit()

    response = client.put(
        "/update_user",
        headers={'Authorization': f'Bearer {token}'},
        data=json.dumps({"username": "newusername", "password": "newpassword"}),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert "error" in response.json
    assert response.json["error"] == "Username already exists"

def test_update_user_not_found(client):
    """Test update failure when the user is not found."""
    with app.app_context():
        # Generate a token for a non-existent user
        non_existent_token = create_access_token(identity='nonexistentuser')

    response = client.put(
        "/update_user",
        headers={'Authorization': f'Bearer {non_existent_token}'},
        data=json.dumps({"username": "newusername", "password": "newpassword"}),
        content_type="application/json",
    )
    assert response.status_code == 404
    assert "error" in response.json
    assert response.json["error"] == "User not found"