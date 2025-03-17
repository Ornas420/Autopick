import pytest
from backend.app import app, db, User
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    """Set up a test client with a separate test database."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # In-memory test database
    app.config["JWT_SECRET_KEY"] = "test_secret"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create test tables
        yield client
        with app.app_context():
            db.drop_all()  # Clean up after tests

@pytest.fixture
def test_user(client):
    """Create a test user and return their token."""
    client.post("/register", json={"username": "testuser", "password": "testpassword"})  # Register user
    login_response = client.post("/login", json={"username": "testuser", "password": "testpassword"})  # Log in
    return login_response.json["token"]  # Return the authentication token

def test_delete_account(client, test_user):
    """Test deleting an account"""
    headers = {"Authorization": f"Bearer {test_user}"}
    
    # Send DELETE request
    delete_response = client.delete("/delete_account", headers=headers)

    # Validate response
    assert delete_response.status_code == 200
    assert delete_response.json["message"] == "Account deleted successfully"

    # Ensure the user no longer exists in the database
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        assert user is None  # User should be deleted
