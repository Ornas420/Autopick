from flask import Flask, jsonify, request, Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity, get_jwt
)
from openai import OpenAI
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@127.0.0.1/autopick_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

jwt = JWTManager(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)

blacklisted_tokens = set()

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(255), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class QuestionnaireResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    must_haves = db.Column(db.Text)
    use_cases = db.Column(db.Text)
    seats = db.Column(db.String(20))
    vehicle_type = db.Column(db.String(50))
    snow_driving = db.Column(db.String(10))
    fuel_type = db.Column(db.String(50))
    fuel_efficiency_importance = db.Column(db.String(50))
    interior_space = db.Column(db.String(10))
    main_needs = db.Column(db.Text)
    recommendation = db.Column(db.Text)

    user = db.relationship('User', backref=db.backref('responses', lazy=True))

with app.app_context():
    db.create_all()

# Logging
def log_action(user, action):
    db.session.add(AuditLog(user=user, action=action))
    db.session.commit()

# Auth and main routes
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    log_action(username, "Registered")

    return jsonify({'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=username)
    log_action(username, "Logged In")
    return jsonify({'token': access_token, 'message': 'Login successful'})

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    current_user = get_jwt_identity()
    log_action(current_user, "Logged Out")
    jti = get_jwt()["jti"]
    blacklisted_tokens.add(jti)
    return jsonify({'message': 'Logout successful. Token invalidated.'})

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_data):
    return jwt_data["jti"] in blacklisted_tokens

@app.route('/home', methods=['GET'])
@jwt_required()
def protected_home():
    current_user = get_jwt_identity()
    return jsonify({'message': f'Welcome {current_user}, you are logged in!'})

@app.route('/delete_account', methods=['DELETE'])
@jwt_required()
def delete_account():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    log_action(current_user, "Deleted Account")
    return jsonify({"message": "Account deleted successfully"}), 200

@app.route('/update_user', methods=['PUT'])
@jwt_required()
def update_user():
    data = request.get_json()
    new_username = data.get('username')
    new_password = data.get('password')

    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if new_username and new_username != current_user:
        if User.query.filter_by(username=new_username).first():
            return jsonify({'error': 'Username already exists'}), 400
        user.username = new_username

    if new_password:
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')

    db.session.commit()
    log_action(current_user, "Updated Account")
    return jsonify({'message': 'User information updated successfully'})

@app.route('/submit_questionnaire', methods=['POST'])
@jwt_required()
def submit_questionnaire():
    data = request.get_json()
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    prompt = (
        f"Please recommend exactly 5 specific car models based on the following user preferences:\n"
        f"- Must-Haves: {', '.join(data.get('mustHaves', []))}\n"
        f"- Use Cases: {', '.join(data.get('useCases', []))}\n"
        f"- Seating Needs: {data.get('seats')}\n"
        f"- Vehicle Type: {data.get('vehicleType')}\n"
        f"- Fuel Type: {data.get('fuelType')}\n"
        f"- Cargo Space: {'Required' if 'Interior cargo space' in data.get('mustHaves', []) or data.get('interiorSpace') == 'yes' else 'Not important'}\n"
        f"- Drives in Snow: {'Yes' if data.get('snowDriving') == 'yes' else 'No'}\n"
        f"- Fuel Efficiency: {data.get('fuelEfficiencyImportance')}\n"
        f"- Main Usage Needs: {', '.join(data.get('mainNeeds', []))}\n\n"
        "Return ONLY:\n"
        "1. A numbered list of 5 car models that best match the criteria (no explanations).\n"
        "2. Below that, include a one-sentence summary in a smaller font style (like a tip or note).\n"
        "3. If no cars match, just say: 'No suitable cars found for the selected preferences.'"
    )

    gpt_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful car expert."},
            {"role": "user", "content": prompt}
        ]
    )

    recommendation = gpt_response.choices[0].message.content.strip()

    response = QuestionnaireResponse(
        user_id=user.id,
        must_haves=",".join(data.get("mustHaves", [])),
        use_cases=",".join(data.get("useCases", [])),
        seats=data.get("seats"),
        vehicle_type=data.get("vehicleType"),
        snow_driving=data.get("snowDriving"),
        fuel_type=data.get("fuelType"),
        fuel_efficiency_importance=data.get("fuelEfficiencyImportance"),
        interior_space=data.get("interiorSpace"),
        main_needs=",".join(data.get("mainNeeds", [])),
        recommendation=recommendation
    )
    db.session.add(response)
    db.session.commit()

    return jsonify({"recommendation": recommendation})

@app.route('/routes', methods=['GET'])
def list_routes():
    return jsonify({rule.rule: rule.endpoint for rule in app.url_map.iter_rules()})

# 🔁 Blueprint for /api/logs/<id> (filtered by user)
logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/api/logs/<id>', methods=['GET'])
@jwt_required()
def get_logs(id):
    current_user = get_jwt_identity()
    logs = AuditLog.query.filter_by(user=current_user).order_by(AuditLog.timestamp.desc()).all()
    return jsonify([
        {
            'id': log.id,
            'user': log.user,
            'action': log.action,
            'timestamp': (log.timestamp + timedelta(hours=9)).isoformat()
        } for log in logs
    ])

app.register_blueprint(logs_bp)

if __name__ == '__main__':
    app.run(debug=True)
