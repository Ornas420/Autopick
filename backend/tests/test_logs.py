# audit_logs.py
import pytest
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)

# Setup Flask app (not importing your app.py)
db = SQLAlchemy()
jwt = JWTManager()


# Define test models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(255), nullable=False)
    action = db.Column(db.String(255), nullable=False)


# Define test-only audit logs route
def create_test_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "test_secret"

    db.init_app(app)
    jwt.init_app(app)

    @app.route("/api/logs", methods=["GET"])
    @jwt_required()
    def get_logs():
        logs = AuditLog.query.order_by(AuditLog.id.desc()).all()
        return jsonify([
            {
                "id": log.id,
                "user": log.user,
                "action": log.action
            } for log in logs
        ])

    return app


@pytest.fixture
def client():
    app = create_test_app()
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            db.session.add(User(username="admin", password="hashed"))
            db.session.add(AuditLog(user="admin", action="Logged In"))
            db.session.commit()
        yield client


def get_auth_headers(app):
    with app.app_context():  # 🧠 THIS is the fix
        token = create_access_token(identity="admin")
        return {"Authorization": f"Bearer {token}"}



def test_get_logs(client):
    from test_logs import create_test_app  # or however you defined your app
    app = create_test_app()
    headers = get_auth_headers(app)
    response = client.get("/api/logs", headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(log["action"] == "Logged In" for log in data)
