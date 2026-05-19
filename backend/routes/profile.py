import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User
from app import bcrypt

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'errors': ['User not found.']}), 404
    return jsonify({'user': user.to_dict()}), 200


@profile_bp.route('', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'errors': ['User not found.']}), 404

    if request.content_type and 'multipart' in request.content_type:
        display_name = request.form.get('display_name', user.display_name)
        if 'avatar' in request.files:
            avatar = request.files['avatar']
            if avatar.filename:
                ext = avatar.filename.rsplit('.', 1)[-1].lower()
                filename = f"avatar_{uuid.uuid4().hex}.{ext}"
                avatar.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                user.avatar_url = f"/uploads/{filename}"
        user.display_name = display_name
    else:
        data = request.get_json()
        if 'display_name' in data:
            user.display_name = data['display_name']
        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url']

    db.session.commit()
    return jsonify({'user': user.to_dict()}), 200


@profile_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    data = request.get_json()

    current_pw = data.get('current_password', '')
    new_pw = data.get('new_password', '')

    if not bcrypt.check_password_hash(user.password_hash, current_pw):
        return jsonify({'errors': ['Current password is incorrect.']}), 400
    if len(new_pw) < 6:
        return jsonify({'errors': ['New password must be at least 6 characters.']}), 400

    user.password_hash = bcrypt.generate_password_hash(new_pw).decode('utf-8')
    db.session.commit()
    return jsonify({'message': 'Password changed successfully.'}), 200
