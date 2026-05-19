from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, DailyTask, TestResult

home_bp = Blueprint('home', __name__)


@home_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = int(get_jwt_identity())
    today = date.today()
    tasks = DailyTask.query.filter_by(user_id=user_id, task_date=today).all()

    # Auto-create default tasks if none exist for today
    if not tasks:
        defaults = [
            ('Daily Good Deed: Compliment someone today', 'good_deed'),
            ('Relaxing Activity: Take a 5-minute breathing break', 'relaxing_game'),
            ('Self-Care: Drink 8 glasses of water', 'custom'),
        ]
        for title, ttype in defaults:
            task = DailyTask(user_id=user_id, title=title, task_type=ttype, task_date=today)
            db.session.add(task)
        db.session.commit()
        tasks = DailyTask.query.filter_by(user_id=user_id, task_date=today).all()

    return jsonify({
        'tasks': [t.to_dict() for t in tasks],
        'total': len(tasks),
        'completed': sum(1 for t in tasks if t.completed),
    }), 200


@home_bp.route('/tasks', methods=['POST'])
@jwt_required()
def add_task():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    title = data.get('title', '').strip()
    task_type = data.get('task_type', 'custom')

    if not title:
        return jsonify({'errors': ['Task title is required.']}), 400

    task = DailyTask(user_id=user_id, title=title, task_type=task_type, task_date=date.today())
    db.session.add(task)
    db.session.commit()
    return jsonify({'task': task.to_dict()}), 201


@home_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def toggle_task(task_id):
    user_id = int(get_jwt_identity())
    task = DailyTask.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({'errors': ['Task not found.']}), 404
    task.completed = not task.completed
    db.session.commit()
    return jsonify({'task': task.to_dict()}), 200


@home_bp.route('/quest', methods=['GET'])
@jwt_required()
def get_quest():
    user_id = int(get_jwt_identity())
    tests_completed = TestResult.query.filter_by(user_id=user_id).count()
    return jsonify({
        'tests_completed': min(tests_completed, 3),
        'total_required': 3,
        'unlocked': tests_completed >= 3,
    }), 200
