import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, AssessmentQuestion, AssessmentResult

growth_bp = Blueprint('growth', __name__)


def get_assessment_summary(score, total):
    pct = (score / total * 100) if total > 0 else 0
    if pct >= 80:
        return {
            'category': 'Thriving',
            'summary': 'You are doing exceptionally well in your personal growth journey! You demonstrate strong self-awareness, healthy habits, and meaningful connections. Keep up the great work!',
            'tips': [
                'Continue mentoring others on their growth journey',
                'Set more ambitious long-term goals',
                'Share your strategies with your community',
            ]
        }
    elif pct >= 60:
        return {
            'category': 'Growing',
            'summary': 'You are making good progress in your personal development. There are some areas where you can improve, but overall you are on a positive path.',
            'tips': [
                'Focus on consistency in your daily habits',
                'Try journaling to deepen self-reflection',
                'Seek feedback from trusted friends or mentors',
            ]
        }
    elif pct >= 40:
        return {
            'category': 'Developing',
            'summary': 'You are in a transitional phase of growth. There is significant potential for improvement, and small changes can make a big difference.',
            'tips': [
                'Start with one small positive habit each week',
                'Practice mindfulness for 5 minutes daily',
                'Connect with a supportive community or group',
            ]
        }
    else:
        return {
            'category': 'Beginning',
            'summary': 'Your growth journey is just starting. This is a great first step! Self-awareness is the foundation of all personal development.',
            'tips': [
                'Be gentle with yourself as you start this journey',
                'Set one small, achievable goal this week',
                'Consider speaking with a counselor or coach',
            ]
        }


@growth_bp.route('/assessment', methods=['GET'])
@jwt_required()
def get_assessment():
    user_id = int(get_jwt_identity())
    questions = AssessmentQuestion.query.order_by(AssessmentQuestion.order_num).all()
    times_taken = AssessmentResult.query.filter_by(user_id=user_id).count()

    q_list = [q.to_dict() for q in questions]
    # Shuffle on retake so it feels different
    if times_taken > 0:
        import random
        random.seed(user_id + times_taken)
        random.shuffle(q_list)

    return jsonify({
        'questions': q_list,
        'has_taken': times_taken > 0,
        'times_taken': times_taken,
    }), 200


@growth_bp.route('/assessment', methods=['POST'])
@jwt_required()
def submit_assessment():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    answers = data.get('answers', {})  # {question_id: true/false}

    score = sum(1 for v in answers.values() if v is True)
    total = len(answers)
    summary_data = get_assessment_summary(score, total)

    result = AssessmentResult(
        user_id=user_id,
        answers_json=json.dumps(answers),
        score=score,
        result_summary=json.dumps(summary_data),
        category=summary_data['category'],
    )
    db.session.add(result)
    db.session.commit()

    return jsonify({
        'result': result.to_dict(),
        'score': score,
        'total': total,
        'percentage': round(score / total * 100) if total > 0 else 0,
        'summary': summary_data,
    }), 201


@growth_bp.route('/results', methods=['GET'])
@jwt_required()
def get_results():
    user_id = int(get_jwt_identity())
    results = AssessmentResult.query.filter_by(user_id=user_id).order_by(AssessmentResult.created_at.desc()).all()
    parsed = []
    for r in results:
        d = r.to_dict()
        try:
            d['parsed_summary'] = json.loads(r.result_summary)
        except (json.JSONDecodeError, TypeError):
            d['parsed_summary'] = None
        parsed.append(d)
    return jsonify({'results': parsed}), 200
