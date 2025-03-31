from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from datetime import timedelta

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to a secure key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # Tokens expire in 1 hour
jwt = JWTManager(app)

CORS(app)

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1/autopick_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Token Blacklist (Temporary storage, use Redis or DB in production)
blacklisted_tokens = set()

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

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

# Create Tables
with app.app_context():
    db.create_all()

# Account Deletion Route
@app.route('/delete_account', methods=['DELETE'])
@jwt_required()  # Ensure only authenticated users can delete accounts
def delete_account():
    try:
        # Get the user identity from the JWT token (which should store 'username' instead of 'email')
        current_username = get_jwt_identity()

        # Query user from the database using 'username' instead of 'email'
        user = User.query.filter_by(username=current_username).first()

        if not user:
            return jsonify({"message": "User not found"}), 404

        # Delete user from database
        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "Account deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
# Registration Route
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

    return jsonify({'message': 'User registered successfully'})
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

    db.session.commit()  # Commit the changes to the database

    return jsonify({'message': 'User information updated successfully'})
# Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=username)
    return jsonify({'token': access_token, 'message': 'Login successful'})

# **Protected Home Route (Requires Token)**
@app.route('/home', methods=['GET'])
@jwt_required()
def protected_home():
    current_user = get_jwt_identity()
    return jsonify({'message': f'Welcome {current_user}, you are logged in!'})

# **Logout Route (Blacklist Token)**
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # Get token's unique ID
    blacklisted_tokens.add(jti)  # Add to blacklist
    return jsonify({'message': 'Logout successful. Token invalidated.'})

# **Check if Token is Blacklisted**
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_data):
    return jwt_data["jti"] in blacklisted_tokens  # Reject if blacklisted

# **List API Routes (Debugging)**
@app.route('/routes', methods=['GET'])
def list_routes():
    return jsonify({rule.rule: rule.endpoint for rule in app.url_map.iter_rules()})

@app.route('/submit_questionnaire', methods=['POST'])
@jwt_required()
def submit_questionnaire():
    data = request.get_json()
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    # 🔷 Construct prompt with all preferences
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

    # 🔷 Call OpenAI and get recommendation
    gpt_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful car expert."},
            {"role": "user", "content": prompt}
        ]
    )

    recommendation = gpt_response.choices[0].message.content.strip()

    # 🔷 Save everything to DB (including GPT result)
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


if __name__ == '__main__':
    app.run(debug=True)
