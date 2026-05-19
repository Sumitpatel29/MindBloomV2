from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User
from app import bcrypt
import re

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    display_name = data.get('display_name', '').strip()

    # Validation
    errors = []
    if not username or len(username) < 3:
        errors.append('Username must be at least 3 characters.')
    if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        errors.append('Please enter a valid email address.')
    if not password or len(password) < 6:
        errors.append('Password must be at least 6 characters.')
    if User.query.filter_by(username=username).first():
        errors.append('Username already taken.')
    if User.query.filter_by(email=email).first():
        errors.append('Email already registered.')

    if errors:
        return jsonify({'errors': errors}), 400

    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(
        username=username,
        email=email,
        password_hash=pw_hash,
        display_name=display_name or username,
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({
        'message': 'Registration successful!',
        'token': token,
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'errors': ['Email and password are required.']}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'errors': ['No account found with this email. Please register first.'], 'error_type': 'not_registered'}), 401
    if not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({'errors': ['Incorrect password. Please try again.']}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({
        'message': 'Login successful!',
        'token': token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'errors': ['User not found.']}), 404
    return jsonify({'user': user.to_dict()}), 200
