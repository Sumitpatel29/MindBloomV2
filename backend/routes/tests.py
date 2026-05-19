import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, TestDefinition, TestResult

tests_bp = Blueprint('tests', __name__)


def get_result_text(test_title, score, total):
    pct = (score / total * 100) if total > 0 else 0
    if pct >= 80:
        return f"Excellent! You scored very high on {test_title}. You demonstrate strong traits in this area. Keep nurturing these qualities!"
    elif pct >= 60:
        return f"Great job! You show solid traits in {test_title}. There's room for growth, but you're on the right track."
    elif pct >= 40:
        return f"You have a balanced perspective on {test_title}. Consider exploring areas where you can grow further."
    else:
        return f"This is an area for growth in {test_title}. Don't worry - self-awareness is the first step to improvement!"


@tests_bp.route('', methods=['GET'])
@jwt_required()
def list_tests():
    user_id = int(get_jwt_identity())
    search = request.args.get('search', '').strip()
    query = TestDefinition.query
    if search:
        query = query.filter(TestDefinition.title.ilike(f'%{search}%'))
    tests = query.all()

    # Check which tests this user has taken
    taken_test_ids = set(
        r.test_id for r in TestResult.query.filter_by(user_id=user_id).all()
    )

    def enrich(t):
        d = t.to_dict()
        d['taken'] = t.id in taken_test_ids
        d['times_taken'] = TestResult.query.filter_by(user_id=user_id, test_id=t.id).count()
        return d

    featured = [enrich(t) for t in tests if t.is_featured]
    popular = [enrich(t) for t in tests]
    return jsonify({'featured': featured, 'tests': popular}), 200


@tests_bp.route('/<int:test_id>', methods=['GET'])
@jwt_required()
def get_test(test_id):
    user_id = int(get_jwt_identity())
    test = TestDefinition.query.get(test_id)
    if not test:
        return jsonify({'errors': ['Test not found.']}), 404

    times_taken = TestResult.query.filter_by(user_id=user_id, test_id=test_id).count()
    d = test.to_dict(include_questions=True)

    # On retake, shuffle questions so it feels fresh
    if times_taken > 0:
        import random
        random.seed(user_id + times_taken)  # Deterministic per attempt
        random.shuffle(d['questions'])

    d['taken'] = times_taken > 0
    d['times_taken'] = times_taken
    return jsonify({'test': d}), 200


@tests_bp.route('/<int:test_id>/submit', methods=['POST'])
@jwt_required()
def submit_test(test_id):
    user_id = int(get_jwt_identity())
    test = TestDefinition.query.get(test_id)
    if not test:
        return jsonify({'errors': ['Test not found.']}), 404

    data = request.get_json()
    answers = data.get('answers', {})  # {question_id: true/false}

    # Calculate score (true = 1 point)
    score = sum(1 for v in answers.values() if v is True)
    total = len(test.questions)
    result_text = get_result_text(test.title, score, total)

    result = TestResult(
        user_id=user_id,
        test_id=test_id,
        answers_json=json.dumps(answers),
        score=score,
        result_text=result_text,
    )
    db.session.add(result)
    db.session.commit()

    return jsonify({
        'result': result.to_dict(),
        'score': score,
        'total': total,
        'percentage': round(score / total * 100) if total > 0 else 0,
    }), 201


@tests_bp.route('/results', methods=['GET'])
@jwt_required()
def get_results():
    user_id = int(get_jwt_identity())
    results = TestResult.query.filter_by(user_id=user_id).order_by(TestResult.created_at.desc()).all()
    return jsonify({'results': [r.to_dict() for r in results]}), 200
