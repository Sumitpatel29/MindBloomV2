import os
import json
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, JournalEntry, JournalPrompt

journal_bp = Blueprint('journal', __name__)

FEELING_OPTIONS = [
    'Happy', 'Sad', 'Anxious', 'Calm', 'Excited', 'Tired',
    'Grateful', 'Frustrated', 'Hopeful', 'Lonely', 'Confident',
    'Overwhelmed', 'Peaceful', 'Angry', 'Motivated', 'Bored',
    'Loved', 'Scared', 'Proud', 'Confused'
]

ACTIVITY_OPTIONS = [
    'Exercise', 'Reading', 'Meditation', 'Cooking', 'Walking',
    'Music', 'Art', 'Socializing', 'Work', 'Gaming',
    'Shopping', 'Cleaning', 'Studying', 'Watching TV', 'Journaling',
    'Yoga', 'Dancing', 'Photography', 'Gardening', 'Travel'
]


@journal_bp.route('/options', methods=['GET'])
@jwt_required()
def get_options():
    return jsonify({
        'feelings': FEELING_OPTIONS,
        'activities': ACTIVITY_OPTIONS,
    }), 200


@journal_bp.route('/prompts/<journal_type>', methods=['GET'])
@jwt_required()
def get_prompts(journal_type):
    valid_types = ['release_worry', 'calm_anxiety', 'feeling_angry', 'feeling_happy']
    if journal_type not in valid_types:
        return jsonify({'errors': [f'Invalid journal type. Must be one of: {valid_types}']}), 400
    prompts = JournalPrompt.query.filter_by(journal_type=journal_type).order_by(JournalPrompt.order_num).all()
    return jsonify({'prompts': [p.to_dict() for p in prompts]}), 200


@journal_bp.route('/entries', methods=['GET'])
@jwt_required()
def get_entries():
    user_id = int(get_jwt_identity())
    entries = JournalEntry.query.filter_by(user_id=user_id).order_by(JournalEntry.created_at.desc()).all()
    return jsonify({'entries': [e.to_dict() for e in entries]}), 200


@journal_bp.route('/entries', methods=['POST'])
@jwt_required()
def create_entry():
    user_id = int(get_jwt_identity())

    # Handle multipart form data (for photo upload)
    if request.content_type and 'multipart' in request.content_type:
        journal_type = request.form.get('journal_type', '')
        note = request.form.get('note', '')
        mood = int(request.form.get('mood', 3))
        feelings = json.loads(request.form.get('feelings', '[]'))
        activities = json.loads(request.form.get('activities', '[]'))
        answers = json.loads(request.form.get('answers', '{}'))
        photo_url = ''

        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename:
                ext = photo.filename.rsplit('.', 1)[-1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                photo_url = f"/uploads/{filename}"
    else:
        data = request.get_json()
        journal_type = data.get('journal_type', '')
        note = data.get('note', '')
        mood = data.get('mood', 3)
        feelings = data.get('feelings', [])
        activities = data.get('activities', [])
        answers = data.get('answers', {})
        photo_url = data.get('photo_url', '')

    valid_types = ['release_worry', 'calm_anxiety', 'feeling_angry', 'feeling_happy']
    if journal_type not in valid_types:
        return jsonify({'errors': ['Invalid journal type.']}), 400

    entry = JournalEntry(
        user_id=user_id,
        journal_type=journal_type,
        note=note,
        mood=mood,
        feelings=json.dumps(feelings),
        activities=json.dumps(activities),
        photo_url=photo_url,
        answers=json.dumps(answers),
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'entry': entry.to_dict()}), 201
