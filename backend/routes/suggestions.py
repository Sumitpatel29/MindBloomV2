import random
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, JournalEntry, TestResult

suggestions_bp = Blueprint('suggestions', __name__)

MUSIC_BY_MOOD = {
    1: [  # Very Sad
        {'title': 'Weightless', 'artist': 'Marconi Union', 'genre': 'Ambient', 'emoji': '🎵', 'reason': 'Scientifically shown to reduce anxiety'},
        {'title': 'Clair de Lune', 'artist': 'Debussy', 'genre': 'Classical', 'emoji': '🌙', 'reason': 'Gentle melodies to soothe your mind'},
        {'title': 'Skinny Love', 'artist': 'Bon Iver', 'genre': 'Indie Folk', 'emoji': '🍂', 'reason': 'Sometimes sad music helps you process emotions'},
        {'title': 'River Flows in You', 'artist': 'Yiruma', 'genre': 'Piano', 'emoji': '🎹', 'reason': 'Calming piano to ease your thoughts'},
    ],
    2: [  # Sad
        {'title': 'Better Days', 'artist': 'OneRepublic', 'genre': 'Pop', 'emoji': '🌤️', 'reason': 'A hopeful reminder that things get better'},
        {'title': 'Fix You', 'artist': 'Coldplay', 'genre': 'Alternative', 'emoji': '💫', 'reason': 'A comforting melody for tough times'},
        {'title': 'Breathe Me', 'artist': 'Sia', 'genre': 'Indie', 'emoji': '🫧', 'reason': 'Let it out — it is okay to feel'},
        {'title': 'Holocene', 'artist': 'Bon Iver', 'genre': 'Indie Folk', 'emoji': '🏔️', 'reason': 'Find peace in the bigger picture'},
    ],
    3: [  # Normal
        {'title': 'Lo-fi Study Beats', 'artist': 'Chillhop', 'genre': 'Lo-fi', 'emoji': '☕', 'reason': 'Perfect background for a calm day'},
        {'title': 'Electric Feel', 'artist': 'MGMT', 'genre': 'Indie Pop', 'emoji': '⚡', 'reason': 'A subtle energy boost for your day'},
        {'title': 'Here Comes the Sun', 'artist': 'The Beatles', 'genre': 'Classic Rock', 'emoji': '☀️', 'reason': 'A timeless mood brightener'},
        {'title': 'Sunflower', 'artist': 'Post Malone', 'genre': 'Pop', 'emoji': '🌻', 'reason': 'Light and easy vibes'},
    ],
    4: [  # Happy
        {'title': 'Happy', 'artist': 'Pharrell Williams', 'genre': 'Pop', 'emoji': '😊', 'reason': 'Match your great mood!'},
        {'title': 'Walking on Sunshine', 'artist': 'Katrina & The Waves', 'genre': 'Pop Rock', 'emoji': '🌈', 'reason': 'Keep the good energy flowing'},
        {'title': 'Uptown Funk', 'artist': 'Bruno Mars', 'genre': 'Funk Pop', 'emoji': '🕺', 'reason': 'Dance it out!'},
        {'title': "Don't Stop Me Now", 'artist': 'Queen', 'genre': 'Rock', 'emoji': '🚀', 'reason': 'You are unstoppable today'},
    ],
    5: [  # Very Happy
        {'title': 'Levitating', 'artist': 'Dua Lipa', 'genre': 'Dance Pop', 'emoji': '✨', 'reason': 'You are on top of the world!'},
        {'title': 'Blinding Lights', 'artist': 'The Weeknd', 'genre': 'Synth Pop', 'emoji': '💃', 'reason': 'Celebrate this amazing feeling'},
        {'title': 'On Top of the World', 'artist': 'Imagine Dragons', 'genre': 'Pop Rock', 'emoji': '🏆', 'reason': 'A soundtrack for your best day'},
        {'title': 'Good as Hell', 'artist': 'Lizzo', 'genre': 'Pop', 'emoji': '💪', 'reason': 'Confidence anthem for a great day'},
    ],
}

ACTIVITIES_BY_MOOD = {
    1: [
        {'title': 'Take a warm bath or shower', 'emoji': '🛁', 'duration': '20 min', 'benefit': 'Relaxes tension in your body'},
        {'title': 'Write 3 things you are grateful for', 'emoji': '📝', 'duration': '5 min', 'benefit': 'Shifts focus to positive things'},
        {'title': 'Call or text someone you trust', 'emoji': '📱', 'duration': '10 min', 'benefit': 'Connection heals sadness'},
        {'title': 'Watch a comforting movie', 'emoji': '🎬', 'duration': '90 min', 'benefit': 'Distraction and emotional release'},
        {'title': 'Gentle stretching or yoga', 'emoji': '🧘', 'duration': '15 min', 'benefit': 'Release physical tension from emotions'},
    ],
    2: [
        {'title': 'Go for a slow walk outside', 'emoji': '🚶', 'duration': '20 min', 'benefit': 'Nature and movement lift mood'},
        {'title': 'Try a guided meditation', 'emoji': '🧘', 'duration': '10 min', 'benefit': 'Calm your racing thoughts'},
        {'title': 'Cook your favorite comfort food', 'emoji': '🍲', 'duration': '30 min', 'benefit': 'Nourish your body and soul'},
        {'title': 'Read a few pages of a book', 'emoji': '📖', 'duration': '15 min', 'benefit': 'Escape into another world'},
        {'title': 'Organize one small space', 'emoji': '🧹', 'duration': '15 min', 'benefit': 'Small wins build momentum'},
    ],
    3: [
        {'title': 'Try a new hobby or skill', 'emoji': '🎨', 'duration': '30 min', 'benefit': 'Curiosity sparks creativity'},
        {'title': 'Plan something fun for the weekend', 'emoji': '📅', 'duration': '10 min', 'benefit': 'Anticipation boosts happiness'},
        {'title': 'Listen to a podcast', 'emoji': '🎧', 'duration': '20 min', 'benefit': 'Learn something new'},
        {'title': 'Do a 15-minute workout', 'emoji': '💪', 'duration': '15 min', 'benefit': 'Endorphins elevate your day'},
        {'title': 'Practice deep breathing', 'emoji': '🌬️', 'duration': '5 min', 'benefit': 'Reset and recharge'},
    ],
    4: [
        {'title': 'Share your happiness with a friend', 'emoji': '💬', 'duration': '10 min', 'benefit': 'Shared joy is doubled joy'},
        {'title': 'Start a creative project', 'emoji': '🎭', 'duration': '30 min', 'benefit': 'Channel your positive energy'},
        {'title': 'Dance to your favorite songs', 'emoji': '💃', 'duration': '15 min', 'benefit': 'Express joy through movement'},
        {'title': 'Write a thank-you note to someone', 'emoji': '💌', 'duration': '10 min', 'benefit': 'Spread your positive energy'},
        {'title': 'Try a challenging puzzle or game', 'emoji': '🧩', 'duration': '20 min', 'benefit': 'Ride the wave of mental clarity'},
    ],
    5: [
        {'title': 'Set an ambitious goal today', 'emoji': '🎯', 'duration': '10 min', 'benefit': 'Use this energy to dream big'},
        {'title': 'Help someone in need', 'emoji': '🤝', 'duration': '20 min', 'benefit': 'Share your overflow of positivity'},
        {'title': 'Try something you have been afraid of', 'emoji': '🦸', 'duration': '30 min', 'benefit': 'Courage peaks with great mood'},
        {'title': 'Document this amazing day', 'emoji': '📸', 'duration': '10 min', 'benefit': 'Create memories to revisit later'},
        {'title': 'Plan a surprise for someone you love', 'emoji': '🎁', 'duration': '15 min', 'benefit': 'Multiply the joy'},
    ],
}

MOOD_INSIGHTS = {
    1: {'message': "It's okay to not be okay. Be gentle with yourself today.", 'emoji': '💙', 'color': '#42A5F5'},
    2: {'message': "Tough days make you stronger. Take it one step at a time.", 'emoji': '🌱', 'color': '#66BB6A'},
    3: {'message': "A balanced day is a good day. Small joys make a big difference.", 'emoji': '☀️', 'color': '#FFB74D'},
    4: {'message': "You're radiating positive energy! Share it with the world.", 'emoji': '✨', 'color': '#FF6B9D'},
    5: {'message': "What an incredible day! You're absolutely glowing.", 'emoji': '🌟', 'color': '#6C63FF'},
}

MOOD_TEST_RECOMMENDATIONS = {
    1: ['Emotional Intelligence', 'Stress Resilience', 'Mindfulness Awareness'],
    2: ['Stress Resilience', 'Self-Confidence', 'Mindfulness Awareness'],
    3: ['Personality Type', 'Communication Style', 'Emotional Intelligence'],
    4: ['Communication Style', 'Personality Type', 'Self-Confidence'],
    5: ['Self-Confidence', 'Communication Style', 'Personality Type'],
}


def get_user_mood(user_id):
    """Get user's latest mood from journal entries, default to 3 (Normal)."""
    latest = JournalEntry.query.filter_by(user_id=user_id).order_by(
        JournalEntry.created_at.desc()
    ).first()
    return latest.mood if latest else 3


@suggestions_bp.route('/suggestions', methods=['GET'])
@jwt_required()
def get_suggestions():
    user_id = int(get_jwt_identity())
    mood = get_user_mood(user_id)

    # Get mood-based suggestions
    music = MUSIC_BY_MOOD.get(mood, MUSIC_BY_MOOD[3])
    activities = ACTIVITIES_BY_MOOD.get(mood, ACTIVITIES_BY_MOOD[3])
    insight = MOOD_INSIGHTS.get(mood, MOOD_INSIGHTS[3])
    recommended_tests = MOOD_TEST_RECOMMENDATIONS.get(mood, MOOD_TEST_RECOMMENDATIONS[3])

    # Pick 2 random music and 3 random activities
    selected_music = random.sample(music, min(2, len(music)))
    selected_activities = random.sample(activities, min(3, len(activities)))

    # Check time of day for contextual greeting
    from datetime import datetime
    hour = datetime.now().hour
    if hour < 6:
        time_context = "It's late — consider winding down soon."
    elif hour < 12:
        time_context = "Morning is a great time to set intentions."
    elif hour < 17:
        time_context = "Afternoon energy — stay focused and hydrated."
    elif hour < 21:
        time_context = "Evening — time to reflect on your day."
    else:
        time_context = "Night time — relax and prepare for rest."

    # Journal streak info
    from datetime import date, timedelta
    entries_this_week = JournalEntry.query.filter(
        JournalEntry.user_id == user_id,
        JournalEntry.created_at >= datetime.combine(date.today() - timedelta(days=7), datetime.min.time())
    ).count()

    tests_taken = TestResult.query.filter_by(user_id=user_id).count()

    return jsonify({
        'mood': mood,
        'mood_label': ['', 'Very Sad', 'Sad', 'Normal', 'Happy', 'Very Happy'][mood],
        'insight': insight,
        'music': selected_music,
        'activities': selected_activities,
        'recommended_tests': recommended_tests,
        'time_context': time_context,
        'stats': {
            'journal_entries_this_week': entries_this_week,
            'total_tests_taken': tests_taken,
        }
    }), 200
