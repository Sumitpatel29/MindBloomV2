import hashlib
import json
import os
import random
import threading
import uuid
from datetime import date, datetime, timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .auth import admin_required, create_access_token, jwt_required
from .models import (
    AssessmentQuestion,
    AssessmentResult,
    Alert,
    AlertAudit,
    DailyTask,
    JournalEntry,
    JournalPrompt,
    TestDefinition,
    TestResult,
    User,
)
from .ml_models import job_tracker


FEELING_OPTIONS = ['Happy', 'Sad', 'Anxious', 'Calm', 'Excited', 'Tired', 'Grateful', 'Frustrated', 'Hopeful', 'Lonely', 'Confident', 'Overwhelmed', 'Peaceful', 'Angry', 'Motivated', 'Bored', 'Loved', 'Scared', 'Proud', 'Confused']
ACTIVITY_OPTIONS = ['Exercise', 'Reading', 'Meditation', 'Cooking', 'Walking', 'Music', 'Art', 'Socializing', 'Work', 'Gaming', 'Shopping', 'Cleaning', 'Studying', 'Watching TV', 'Journaling', 'Yoga', 'Dancing', 'Photography', 'Gardening', 'Travel']

MUSIC_BY_MOOD = {
    1: [
        {'title': 'Weightless', 'artist': 'Marconi Union', 'genre': 'Ambient', 'emoji': '🎵', 'reason': 'Scientifically shown to reduce anxiety'},
        {'title': 'Clair de Lune', 'artist': 'Debussy', 'genre': 'Classical', 'emoji': '🌙', 'reason': 'Gentle melodies to soothe your mind'},
        {'title': 'Skinny Love', 'artist': 'Bon Iver', 'genre': 'Indie Folk', 'emoji': '🍂', 'reason': 'Sometimes sad music helps you process emotions'},
        {'title': 'River Flows in You', 'artist': 'Yiruma', 'genre': 'Piano', 'emoji': '🎹', 'reason': 'Calming piano to ease your thoughts'},
    ],
    2: [
        {'title': 'Better Days', 'artist': 'OneRepublic', 'genre': 'Pop', 'emoji': '🌤️', 'reason': 'A hopeful reminder that things get better'},
        {'title': 'Fix You', 'artist': 'Coldplay', 'genre': 'Alternative', 'emoji': '💫', 'reason': 'A comforting melody for tough times'},
        {'title': 'Breathe Me', 'artist': 'Sia', 'genre': 'Indie', 'emoji': '🫧', 'reason': 'Let it out - it is okay to feel'},
        {'title': 'Holocene', 'artist': 'Bon Iver', 'genre': 'Indie Folk', 'emoji': '🏔️', 'reason': 'Find peace in the bigger picture'},
    ],
    3: [
        {'title': 'Lo-fi Study Beats', 'artist': 'Chillhop', 'genre': 'Lo-fi', 'emoji': '☕', 'reason': 'Perfect background for a calm day'},
        {'title': 'Electric Feel', 'artist': 'MGMT', 'genre': 'Indie Pop', 'emoji': '⚡', 'reason': 'A subtle energy boost for your day'},
        {'title': 'Here Comes the Sun', 'artist': 'The Beatles', 'genre': 'Classic Rock', 'emoji': '☀️', 'reason': 'A timeless mood brightener'},
        {'title': 'Sunflower', 'artist': 'Post Malone', 'genre': 'Pop', 'emoji': '🌻', 'reason': 'Light and easy vibes'},
    ],
    4: [
        {'title': 'Happy', 'artist': 'Pharrell Williams', 'genre': 'Pop', 'emoji': '😊', 'reason': 'Match your great mood!'},
        {'title': 'Walking on Sunshine', 'artist': 'Katrina & The Waves', 'genre': 'Pop Rock', 'emoji': '🌈', 'reason': 'Keep the good energy flowing'},
        {'title': 'Uptown Funk', 'artist': 'Bruno Mars', 'genre': 'Funk Pop', 'emoji': '🕺', 'reason': 'Dance it out!'},
        {'title': "Don't Stop Me Now", 'artist': 'Queen', 'genre': 'Rock', 'emoji': '🚀', 'reason': 'You are unstoppable today'},
    ],
    5: [
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
    2: {'message': 'Tough days make you stronger. Take it one step at a time.', 'emoji': '🌱', 'color': '#66BB6A'},
    3: {'message': 'A balanced day is a good day. Small joys make a big difference.', 'emoji': '☀️', 'color': '#FFB74D'},
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

DEFAULT_NOTEBOOK_TASKS = [
    'Wake up at 6:30 AM',
    'Morning study session',
    'Cold shower',
    '5 hours of focused study',
    'Workout 15 min',
    'Meditation 5 min',
    'Read 5 pages',
    'Eat 80% clean and no junk',
    'Drink 2L of water',
    'Clean my environment',
    'Skin and hair care',
    'Plan next day',
    'Journaling',
    'Dinner between 7-9 PM',
    'Brush at night',
    'Sleep between 10-11 PM',
]

QUOTE_INTROS = {
    'high': [
        'You showed real consistency today.',
        'Your effort today was disciplined and focused.',
        'This was the kind of day that builds confidence.',
    ],
    'mid': [
        'You made meaningful progress today.',
        'You kept moving even when everything was not perfect.',
        'There is clear momentum in your day.',
    ],
    'low': [
        'Even on a hard day, you still showed up.',
        'Today may have felt uneven, but your effort still counts.',
        'Small wins today can become bigger wins tomorrow.',
    ],
}

QUOTE_CLOSERS = [
    'Keep one small promise to yourself next, and the rest will follow.',
    'One more deliberate step tonight can make tomorrow lighter.',
    'Protect this momentum with a calm evening routine.',
    'Progress stacks when you stay honest and steady like this.',
]


def parse_json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


def json_error(errors, status=400):
    return JsonResponse({'errors': errors}, status=status)


def parse_iso_date(date_text):
    if not date_text:
        return date.today()
    try:
        return datetime.strptime(date_text, '%Y-%m-%d').date()
    except ValueError:
        return None


def ensure_default_tasks(user, task_date):
    existing = list(DailyTask.objects.filter(user=user, task_date=task_date).order_by('id'))
    if existing:
        return existing

    for title in DEFAULT_NOTEBOOK_TASKS:
        DailyTask.objects.create(
            user=user,
            title=title,
            task_type='custom',
            status=DailyTask.STATUS_PENDING,
            completed=False,
            note='',
            task_date=task_date,
        )
    return list(DailyTask.objects.filter(user=user, task_date=task_date).order_by('id'))


def build_task_summary(task_items):
    total = len(task_items)
    done = sum(1 for task in task_items if task.status == DailyTask.STATUS_DONE)
    missed = sum(1 for task in task_items if task.status == DailyTask.STATUS_MISSED)
    pending = total - done - missed
    percentage = round((done / total) * 100) if total else 0
    return {
        'total': total,
        'done': done,
        'missed': missed,
        'pending': pending,
        'percentage': percentage,
    }


def save_uploaded_file(uploaded_file, prefix):
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    filename = f'{prefix}_{uuid.uuid4().hex}{ext}'
    storage = FileSystemStorage(location=settings.MEDIA_ROOT)
    saved_name = storage.save(filename, uploaded_file)
    return f'/uploads/{saved_name}'


def get_result_text(test_title, score, total):
    pct = (score / total * 100) if total > 0 else 0
    if pct >= 80:
        return f'Excellent! You scored very high on {test_title}. You demonstrate strong traits in this area. Keep nurturing these qualities!'
    if pct >= 60:
        return f"Great job! You show solid traits in {test_title}. There's room for growth, but you're on the right track."
    if pct >= 40:
        return f'You have a balanced perspective on {test_title}. Consider exploring areas where you can grow further.'
    return f"This is an area for growth in {test_title}. Don't worry - self-awareness is the first step to improvement!"


def get_assessment_summary(score, total):
    pct = (score / total * 100) if total > 0 else 0
    if pct >= 80:
        return {'category': 'Thriving', 'summary': 'You are doing exceptionally well in your personal growth journey! You demonstrate strong self-awareness, healthy habits, and meaningful connections. Keep up the great work!', 'tips': ['Continue mentoring others on their growth journey', 'Set more ambitious long-term goals', 'Share your strategies with your community']}
    if pct >= 60:
        return {'category': 'Growing', 'summary': 'You are making good progress in your personal development. There are some areas where you can improve, but overall you are on a positive path.', 'tips': ['Focus on consistency in your daily habits', 'Try journaling to deepen self-reflection', 'Seek feedback from trusted friends or mentors']}
    if pct >= 40:
        return {'category': 'Developing', 'summary': 'You are in a transitional phase of growth. There is significant potential for improvement, and small changes can make a big difference.', 'tips': ['Start with one small positive habit each week', 'Practice mindfulness for 5 minutes daily', 'Connect with a supportive community or group']}
    return {'category': 'Beginning', 'summary': 'Your growth journey is just starting. This is a great first step! Self-awareness is the foundation of all personal development.', 'tips': ['Be gentle with yourself as you start this journey', 'Set one small, achievable goal this week', 'Consider speaking with a counselor or coach']}


@csrf_exempt
def register(request):
    if request.method != 'POST':
        return json_error(['Method not allowed.'], status=405)

    data = parse_json_body(request)
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    display_name = data.get('display_name', '').strip()

    errors = []
    if not username or len(username) < 3:
        errors.append('Username must be at least 3 characters.')
    if not email or '@' not in email or '.' not in email:
        errors.append('Please enter a valid email address.')
    if not password or len(password) < 6:
        errors.append('Password must be at least 6 characters.')
    if User.objects.filter(username=username).exists():
        errors.append('Username already taken.')
    if User.objects.filter(email=email).exists():
        errors.append('Email already registered.')

    if errors:
        return json_error(errors)

    user = User.objects.create(
        username=username,
        email=email,
        password_hash=make_password(password),
        display_name=display_name or username,
        is_email_verified=False,
    )

    otp = random.randint(100000, 999999)
    otp_str = str(otp)
    otp_hash = hashlib.sha256(otp_str.encode('utf-8')).hexdigest()

    from django.utils import timezone as dj_timezone

    now = dj_timezone.now()
    otp_valid_minutes = int(os.environ.get('OTP_VALID_MINUTES', '10'))

    user.otp_code_hash = otp_hash
    user.otp_expires_at = now + timedelta(minutes=otp_valid_minutes)
    user.otp_attempts = 0
    user.otp_last_sent_at = now
    user.save(update_fields=['otp_code_hash', 'otp_expires_at', 'otp_attempts', 'otp_last_sent_at', 'is_email_verified'])

    # Console-based OTP delivery (Railway-friendly)
    print(f"[MindBloom][OTP] email={email} otp={otp_str} expires_at={user.otp_expires_at.isoformat()}")

    return JsonResponse({
        'message': 'Registration successful. OTP sent. Please verify to continue.',
        'otp_required': True,
        'email': user.email,
    }, status=201)


@csrf_exempt
def verify_otp(request):
    if request.method != 'POST':
        return json_error(['Method not allowed.'], status=405)

    data = parse_json_body(request)
    email = data.get('email', '').strip().lower()
    otp = str(data.get('otp', '')).strip()

    if not email or not otp:
        return json_error(['Email and OTP are required.'])

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return json_error(['User not found.'], status=404)

    from django.utils import timezone as dj_timezone

    max_attempts = int(os.environ.get('OTP_MAX_ATTEMPTS', '5'))

    if user.is_email_verified:
        token = create_access_token(user.id, remember_me=bool(data.get('remember_me', False)))
        return JsonResponse({'message': 'Already verified.', 'token': token, 'user': user.to_dict()})

    if user.otp_attempts >= max_attempts:
        return json_error(['OTP attempts exceeded. Please register again.'], status=403)

    if not user.otp_expires_at or dj_timezone.now() > user.otp_expires_at:
        return json_error(['OTP expired. Please register again.'], status=403)

    otp_hash = hashlib.sha256(otp.encode('utf-8')).hexdigest()

    if otp_hash != (user.otp_code_hash or ''):
        user.otp_attempts = (user.otp_attempts or 0) + 1
        user.save(update_fields=['otp_attempts'])
        return json_error(['Invalid OTP.'], status=400)

    user.is_email_verified = True
    user.otp_code_hash = ''
    user.otp_expires_at = None
    user.otp_attempts = 0
    user.save(update_fields=['is_email_verified', 'otp_code_hash', 'otp_expires_at', 'otp_attempts'])

    remember_me = bool(data.get('remember_me', False))
    token = create_access_token(user.id, remember_me=remember_me)
    return JsonResponse({'message': 'OTP verified. Login successful.', 'token': token, 'user': user.to_dict()}, status=200)


@csrf_exempt
def login(request):
    if request.method != 'POST':
        return json_error(['Method not allowed.'], status=405)

    data = parse_json_body(request)
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return json_error(['Email and password are required.'])

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({'errors': ['No account found with this email. Please register first.'], 'error_type': 'not_registered'}, status=401)

    if not check_password(password, user.password_hash):
        return json_error(['Incorrect password. Please try again.'], status=401)

    if not getattr(user, 'is_email_verified', False):
        return JsonResponse({'errors': ['Email not verified. Please verify OTP first.'], 'error_type': 'email_not_verified', 'email': user.email}, status=403)

    remember_me = bool(data.get('remember_me', False))
    token = create_access_token(user.id, remember_me=remember_me)

    try:
        from django.utils import timezone as dj_timezone
        user.last_login_at = dj_timezone.now()
        user.save(update_fields=['last_login_at'])
    except Exception:
        pass

    return JsonResponse({'message': 'Login successful!', 'token': token, 'user': user.to_dict()})


@jwt_required
def me(request):
    # best-effort activity tracking
    try:
        from django.utils import timezone as dj_timezone
        request._current_user.last_activity_at = dj_timezone.now()
        request._current_user.save(update_fields=['last_activity_at'])
    except Exception:
        pass

    return JsonResponse({'user': request._current_user.to_dict()})


@jwt_required
def tasks(request):
    user = request._current_user
    requested_date = parse_iso_date(request.GET.get('day'))
    if requested_date is None:
        return json_error(['Invalid day. Use YYYY-MM-DD.'])

    if request.method == 'GET':
        user_tasks = ensure_default_tasks(user, requested_date)
        summary = build_task_summary(user_tasks)
        return JsonResponse({'tasks': [task.to_dict() for task in user_tasks], 'day': requested_date.isoformat(), **summary})

    if request.method == 'POST':
        data = parse_json_body(request)
        title = data.get('title', '').strip()
        task_type = data.get('task_type', 'custom')
        note = data.get('note', '').strip()
        if not title:
            return json_error(['Task title is required.'])
        task = DailyTask.objects.create(
            user=user,
            title=title,
            task_type=task_type,
            status=DailyTask.STATUS_PENDING,
            completed=False,
            note=note,
            task_date=requested_date,
        )
        return JsonResponse({'task': task.to_dict()}, status=201)

    return json_error(['Method not allowed.'], status=405)


@csrf_exempt
@jwt_required
def toggle_task(request, task_id):
    if request.method != 'PUT':
        return json_error(['Method not allowed.'], status=405)

    try:
        task = DailyTask.objects.get(id=task_id, user=request._current_user)
    except DailyTask.DoesNotExist:
        return json_error(['Task not found.'], status=404)

    data = parse_json_body(request)
    next_status = data.get('status')
    note = data.get('note')

    note_only_update = next_status is None and isinstance(note, str)

    if next_status:
        if next_status not in [DailyTask.STATUS_PENDING, DailyTask.STATUS_DONE, DailyTask.STATUS_MISSED]:
            return json_error(['Invalid status.'])
        task.status = next_status
        task.completed = next_status == DailyTask.STATUS_DONE
    elif not note_only_update:
        cycle = {
            DailyTask.STATUS_PENDING: DailyTask.STATUS_DONE,
            DailyTask.STATUS_DONE: DailyTask.STATUS_MISSED,
            DailyTask.STATUS_MISSED: DailyTask.STATUS_PENDING,
        }
        task.status = cycle.get(task.status, DailyTask.STATUS_PENDING)
        task.completed = task.status == DailyTask.STATUS_DONE

    if isinstance(note, str):
        task.note = note.strip()

    task.save(update_fields=['status', 'completed', 'note'])
    return JsonResponse({'task': task.to_dict()})


@csrf_exempt
@jwt_required
def analyze_day(request):
    if request.method != 'POST':
        return json_error(['Method not allowed.'], status=405)

    user = request._current_user
    data = parse_json_body(request)
    requested_date = parse_iso_date(data.get('day'))
    if requested_date is None:
        return json_error(['Invalid day. Use YYYY-MM-DD.'])

    reflection = data.get('reflection', '').strip()
    task_items = ensure_default_tasks(user, requested_date)
    summary = build_task_summary(task_items)

    done_titles = [task.title for task in task_items if task.status == DailyTask.STATUS_DONE]
    missed_titles = [task.title for task in task_items if task.status == DailyTask.STATUS_MISSED]
    noted_items = [f"{task.title}: {task.note.strip()}" for task in task_items if task.note.strip()]

    if summary['percentage'] >= 80:
        intro = random.choice(QUOTE_INTROS['high'])
    elif summary['percentage'] >= 45:
        intro = random.choice(QUOTE_INTROS['mid'])
    else:
        intro = random.choice(QUOTE_INTROS['low'])

    done_hint = f"You completed {summary['done']} tasks, including {', '.join(done_titles[:2])}." if done_titles else 'You can still secure a small win by completing one key task now.'
    missed_hint = f"The main misses were {', '.join(missed_titles[:2])}, so anchor tomorrow around those first." if missed_titles else 'You avoided major misses today, which shows steady intent.'
    note_hint = f"Your notes show self-awareness: {random.choice(noted_items)}." if noted_items else 'Add quick notes to tasks tomorrow to make patterns easier to improve.'
    reflection_hint = f"Your reflection says: \"{reflection[:120]}\"." if reflection else ''
    closer = random.choice(QUOTE_CLOSERS)

    quote = f"{intro} {done_hint} {missed_hint} {note_hint} {reflection_hint} You are at {summary['percentage']}% completion today. {closer}".strip()

    return JsonResponse({
        'day': requested_date.isoformat(),
        'result': {
            **summary,
            'label': 'Excellent work!' if summary['percentage'] >= 80 else 'Good progress!' if summary['percentage'] >= 60 else 'Keep going!' if summary['percentage'] >= 35 else 'You can restart now.',
            'caption': 'Consistency beats perfection. Keep stacking small wins.' if summary['percentage'] >= 60 else 'A stronger evening routine can quickly lift tomorrow.',
        },
        'quote': quote,
        'quote_source': 'MindBloom daily analysis',
        'signals': {
            'completed_examples': done_titles[:3],
            'missed_examples': missed_titles[:3],
            'has_reflection': bool(reflection),
            'notes_count': len(noted_items),
        },
    })


@jwt_required
def quest(request):
    user = request._current_user
    tests_completed = TestResult.objects.filter(user=user).count()
    return JsonResponse({'tests_completed': min(tests_completed, 3), 'total_required': 3, 'unlocked': tests_completed >= 3})


@jwt_required
def suggestions(request):
    user = request._current_user
    latest = JournalEntry.objects.filter(user=user).order_by('-created_at').first()
    mood = latest.mood if latest else 3
    music = MUSIC_BY_MOOD.get(mood, MUSIC_BY_MOOD[3])
    activities = ACTIVITIES_BY_MOOD.get(mood, ACTIVITIES_BY_MOOD[3])
    insight = MOOD_INSIGHTS.get(mood, MOOD_INSIGHTS[3])
    recommended_tests = MOOD_TEST_RECOMMENDATIONS.get(mood, MOOD_TEST_RECOMMENDATIONS[3])
    selected_music = random.sample(music, min(2, len(music)))
    selected_activities = random.sample(activities, min(3, len(activities)))

    hour = datetime.now().hour
    if hour < 6:
        time_context = "It's late - consider winding down soon."
    elif hour < 12:
        time_context = 'Morning is a great time to set intentions.'
    elif hour < 17:
        time_context = 'Afternoon energy - stay focused and hydrated.'
    elif hour < 21:
        time_context = 'Evening - time to reflect on your day.'
    else:
        time_context = 'Night time - relax and prepare for rest.'

    entries_this_week = JournalEntry.objects.filter(
        user=user,
        created_at__gte=datetime.combine(date.today() - timedelta(days=7), datetime.min.time()),
    ).count()
    tests_taken = TestResult.objects.filter(user=user).count()

    return JsonResponse({
        'mood': mood,
        'mood_label': ['', 'Very Sad', 'Sad', 'Normal', 'Happy', 'Very Happy'][mood],
        'insight': insight,
        'music': selected_music,
        'activities': selected_activities,
        'recommended_tests': recommended_tests,
        'time_context': time_context,
        'stats': {'journal_entries_this_week': entries_this_week, 'total_tests_taken': tests_taken},
    })


@jwt_required
def journal_options(request):
    return JsonResponse({'feelings': FEELING_OPTIONS, 'activities': ACTIVITY_OPTIONS})


@jwt_required
def journal_prompts(request, journal_type):
    valid_types = ['release_worry', 'calm_anxiety', 'feeling_angry', 'feeling_happy']
    if journal_type not in valid_types:
        return json_error([f'Invalid journal type. Must be one of: {valid_types}'])
    prompts = JournalPrompt.objects.filter(journal_type=journal_type).order_by('order_num')
    return JsonResponse({'prompts': [prompt.to_dict() for prompt in prompts]})


@jwt_required
def journal_entries(request):
    user = request._current_user

    if request.method == 'GET':
        entries = JournalEntry.objects.filter(user=user).order_by('-created_at')
        return JsonResponse({'entries': [entry.to_dict() for entry in entries]})

    if request.method != 'POST':
        return json_error(['Method not allowed.'], status=405)

    if request.content_type and 'multipart' in request.content_type:
        payload = request.POST
        journal_type = payload.get('journal_type', '')
        note = payload.get('note', '')
        mood = int(payload.get('mood', 3))
        feelings = json.loads(payload.get('feelings', '[]'))
        activities = json.loads(payload.get('activities', '[]'))
        answers = json.loads(payload.get('answers', '{}'))
        photo_url = ''
        if request.FILES.get('photo'):
            photo_url = save_uploaded_file(request.FILES['photo'], 'journal')
    else:
        payload = parse_json_body(request)
        journal_type = payload.get('journal_type', '')
        note = payload.get('note', '')
        mood = payload.get('mood', 3)
        feelings = payload.get('feelings', [])
        activities = payload.get('activities', [])
        answers = payload.get('answers', {})
        photo_url = payload.get('photo_url', '')

    if journal_type not in ['release_worry', 'calm_anxiety', 'feeling_angry', 'feeling_happy']:
        return json_error(['Invalid journal type.'])

    entry = JournalEntry.objects.create(
        user=user,
        journal_type=journal_type,
        note=note,
        mood=mood,
        feelings=json.dumps(feelings),
        activities=json.dumps(activities),
        photo_url=photo_url,
        answers=json.dumps(answers),
    )
    return JsonResponse({'entry': entry.to_dict()}, status=201)


@jwt_required
def tests_list(request):
    user = request._current_user
    search = request.GET.get('search', '').strip()
    query = TestDefinition.objects.all()
    if search:
        query = query.filter(title__icontains=search)

    tests = list(query)
    taken_ids = set(TestResult.objects.filter(user=user).values_list('test_id', flat=True))

    def enrich(test):
        data = test.to_dict()
        data['taken'] = test.id in taken_ids
        data['times_taken'] = TestResult.objects.filter(user=user, test=test).count()
        return data

    return JsonResponse({'featured': [enrich(t) for t in tests if t.is_featured], 'tests': [enrich(t) for t in tests]})


@jwt_required
def test_detail(request, test_id):
    user = request._current_user
    try:
        test = TestDefinition.objects.get(id=test_id)
    except TestDefinition.DoesNotExist:
        return json_error(['Test not found.'], status=404)

    times_taken = TestResult.objects.filter(user=user, test=test).count()
    data = test.to_dict(include_questions=True)

    if times_taken > 0:
        random.seed(user.id + times_taken)
        random.shuffle(data['questions'])

    data['taken'] = times_taken > 0
    data['times_taken'] = times_taken
    return JsonResponse({'test': data})


@csrf_exempt
@jwt_required
def submit_test(request, test_id):
    if request.method != 'POST':
        return json_error(['Method not allowed.'], status=405)

    user = request._current_user
    try:
        test = TestDefinition.objects.get(id=test_id)
    except TestDefinition.DoesNotExist:
        return json_error(['Test not found.'], status=404)

    payload = parse_json_body(request)
    answers = payload.get('answers', {})

    score = sum(1 for v in answers.values() if v is True)
    total = test.questions.count()

    result = TestResult.objects.create(
        user=user,
        test=test,
        answers_json=json.dumps(answers),
        score=score,
        result_text=get_result_text(test.title, score, total),
    )

    return JsonResponse({
        'result': result.to_dict(),
        'score': score,
        'total': total,
        'percentage': round(score / total * 100) if total > 0 else 0,
    }, status=201)


@jwt_required
def test_results(request):
    user = request._current_user
    results = TestResult.objects.filter(user=user).order_by('-created_at')
    return JsonResponse({'results': [r.to_dict() for r in results]})


@jwt_required
def assessment(request):
    user = request._current_user

    if request.method == 'GET':
        questions = AssessmentQuestion.objects.order_by('order_num')
        times_taken = AssessmentResult.objects.filter(user=user).count()
        question_list = [q.to_dict() for q in questions]
        if times_taken > 0:
            random.seed(user.id + times_taken)
            random.shuffle(question_list)
        return JsonResponse({'questions': question_list, 'has_taken': times_taken > 0, 'times_taken': times_taken})

    if request.method != 'POST':
        return json_error(['Method not allowed.'], status=405)

    payload = parse_json_body(request)
    answers = payload.get('answers', {})
    score = sum(1 for v in answers.values() if v is True)
    total = len(answers)

    summary = get_assessment_summary(score, total)
    result = AssessmentResult.objects.create(
        user=user,
        answers_json=json.dumps(answers),
        score=score,
        result_summary=json.dumps(summary),
        category=summary['category'],
    )

    return JsonResponse({
        'result': result.to_dict(),
        'score': score,
        'total': total,
        'percentage': round(score / total * 100) if total > 0 else 0,
        'summary': summary,
    }, status=201)


@jwt_required
def assessment_results(request):
    user = request._current_user
    results = AssessmentResult.objects.filter(user=user).order_by('-created_at')

    parsed = []
    for result in results:
        data = result.to_dict()
        try:
            data['parsed_summary'] = json.loads(result.result_summary)
        except (json.JSONDecodeError, TypeError):
            data['parsed_summary'] = None
        parsed.append(data)

    return JsonResponse({'results': parsed})


@admin_required
def admin_alerts(request):
    if request.method != 'GET':
        return json_error(['Method not allowed.'], status=405)

    status_filter = request.GET.get('status', '').strip()
    severity = request.GET.get('severity', '').strip()

    alerts = Alert.objects.select_related('user', 'reviewed_by').order_by('-created_at')
    if status_filter:
        alerts = alerts.filter(status=status_filter)
    if severity.isdigit():
        alerts = alerts.filter(severity=int(severity))

    payload = []
    for alert in alerts:
        data = alert.to_dict()
        data['user'] = alert.user.to_dict()
        payload.append(data)

    return JsonResponse({'alerts': payload})


@admin_required
def admin_alert_detail(request, alert_id):
    if request.method != 'GET':
        return json_error(['Method not allowed.'], status=405)

    try:
        alert = Alert.objects.select_related('user', 'reviewed_by').get(id=alert_id)
    except Alert.DoesNotExist:
        return json_error(['Alert not found.'], status=404)

    audits = AlertAudit.objects.filter(alert=alert).order_by('created_at')
    return JsonResponse({'alert': alert.to_dict(), 'user': alert.user.to_dict(), 'audits': [a.to_dict() for a in audits]})


@csrf_exempt
@admin_required
def admin_alert_acknowledge(request, alert_id):
    if request.method != 'POST':
        return json_error(['Method not allowed.'], status=405)

    try:
        alert = Alert.objects.get(id=alert_id)
    except Alert.DoesNotExist:
        return json_error(['Alert not found.'], status=404)

    from .ml_models.alert_service import acknowledge_alert

    payload = parse_json_body(request)
    note = payload.get('note', '')
    updated = acknowledge_alert(alert, request._current_user, note=note)
    return JsonResponse({'alert': updated.to_dict()})


@csrf_exempt
@admin_required
def admin_alert_resolve(request, alert_id):
    if request.method != 'POST':
        return json_error(['Method not allowed.'], status=405)

    try:
        alert = Alert.objects.get(id=alert_id)
    except Alert.DoesNotExist:
        return json_error(['Alert not found.'], status=404)

    from .ml_models.alert_service import resolve_alert

    payload = parse_json_body(request)
    note = payload.get('note', '')
    status = payload.get('status', Alert.STATUS_RESOLVED)
    if status not in {Alert.STATUS_RESOLVED, Alert.STATUS_FALSE}:
        status = Alert.STATUS_RESOLVED

    updated = resolve_alert(alert, request._current_user, note=note, status=status)
    return JsonResponse({'alert': updated.to_dict()})


@admin_required
def admin_alert_stats(request):
    if request.method != 'GET':
        return json_error(['Method not allowed.'], status=405)

    alerts = Alert.objects.all()
    totals = {
        'total_alerts': alerts.count(),
        'new_alerts': alerts.filter(status=Alert.STATUS_NEW).count(),
        'acknowledged_alerts': alerts.filter(status=Alert.STATUS_ACK).count(),
        'in_review_alerts': alerts.filter(status=Alert.STATUS_IN_REVIEW).count(),
        'resolved_alerts': alerts.filter(status=Alert.STATUS_RESOLVED).count(),
        'false_positive_alerts': alerts.filter(status=Alert.STATUS_FALSE).count(),
        'high_severity_alerts': alerts.filter(severity__gte=4).count(),
    }
    return JsonResponse({'stats': totals})


@csrf_exempt
@admin_required
def admin_alert_score(request):
    if request.method != 'POST':
        return json_error(['Method not allowed.'], status=405)

    data = parse_json_body(request)
    model_dir = data.get('model_dir', 'backend/ml_models')
    feature_path = data.get('feature_path', 'backend/ml_data/features.parquet')
    threshold = float(data.get('threshold', 0.8))

    if not os.path.exists(feature_path):
        return json_error(['Feature file not found. Run feature extraction first.'], status=400)

    if not os.path.exists(os.path.join(model_dir, 'meta.joblib')):
        return json_error(['Model artifacts not found. Train the anomaly model first.'], status=400)

    import pandas as pd
    from .ml_models.anomaly_ensemble import load_artifacts, score_features
    from .ml_models.alert_service import create_alerts_from_scores

    df = pd.read_parquet(feature_path)
    artifacts = load_artifacts(model_dir)
    scored = score_features(artifacts, df)
    created = create_alerts_from_scores(df, scored, threshold=threshold)

    return JsonResponse({'scored_rows': len(scored), 'alerts_created': len(created), 'threshold': threshold})


@csrf_exempt
@admin_required
def admin_model_retrain(request):
    if request.method != 'POST':
        return json_error(['Method not allowed.'], status=405)

    payload = parse_json_body(request)
    model_dir = payload.get('model_dir', 'backend/ml_models')
    feature_path = payload.get('feature_path', 'backend/ml_data/features.parquet')
    epochs = int(payload.get('epochs', 40))
    batch_size = int(payload.get('batch_size', 32))
    contamination = float(payload.get('contamination', 0.1))

    if not os.path.exists(feature_path):
        return json_error(['Feature file not found. Run feature extraction first.'], status=400)

    job_meta = {'epochs': epochs, 'batch_size': batch_size, 'contamination': contamination}
    os.makedirs(model_dir, exist_ok=True)
    job_id = job_tracker.start_job(model_dir, meta=job_meta)

    def _train_worker(job_id_inner):
        import sys
        import subprocess

        try:
            job_tracker.update_job(model_dir, job_id_inner, status='running', note='Training started')
            cmd = [
                sys.executable,
                '-m',
                'api.ml_training.train_anomaly',
                '--features',
                feature_path,
                '--model-dir',
                model_dir,
                '--contamination',
                str(contamination),
                '--epochs',
                str(epochs),
                '--batch-size',
                str(batch_size),
                '--verbose',
                '1',
            ]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                job_tracker.update_job(model_dir, job_id_inner, note=line.strip())
            ret = proc.wait()
            if ret == 0:
                job_tracker.update_job(model_dir, job_id_inner, status='completed', note='Training completed')
            else:
                job_tracker.update_job(model_dir, job_id_inner, status='failed', note=f'Training process exited with code {ret}')
        except Exception as exc:
            try:
                job_tracker.update_job(model_dir, job_id_inner, status='failed', note=f'Error: {exc}')
            except Exception:
                pass

    try:
        from .tasks import retrain_model_task
        retrain_model_task.apply_async(args=(job_id, model_dir, feature_path, contamination, epochs, batch_size))
    except Exception:
        thread = threading.Thread(target=_train_worker, args=(job_id,), daemon=True)
        thread.start()

    return JsonResponse({'message': 'Retrain job queued', 'job_id': job_id, 'model_dir': model_dir})


@admin_required
def admin_model_job_status(request, job_id):
    if request.method != 'GET':
        return json_error(['Method not allowed.'], status=405)

    model_dir = request.GET.get('model_dir', 'backend/ml_models')
    job = job_tracker.get_job(model_dir, job_id)
    if not job:
        return json_error(['Job not found.'], status=404)
    return JsonResponse({'job': job})


@admin_required
def admin_model_jobs_list(request):
    if request.method != 'GET':
        return json_error(['Method not allowed.'], status=405)

    model_dir = request.GET.get('model_dir', 'backend/ml_models')
    jobs = job_tracker.list_jobs(model_dir)
    return JsonResponse({'jobs': jobs})


@csrf_exempt
@jwt_required
def profile(request):
    user = request._current_user
    if request.method == 'GET':
        return JsonResponse({'user': user.to_dict()})
    if request.method != 'PUT':
        return json_error(['Method not allowed.'], status=405)

    if request.content_type and 'multipart' in request.content_type:
        display_name = request.POST.get('display_name', user.display_name)
        avatar = request.FILES.get('avatar')
        if avatar and avatar.name:
            user.avatar_url = save_uploaded_file(avatar, 'avatar')
        user.display_name = display_name
    else:
        payload = parse_json_body(request)
        if 'display_name' in payload:
            user.display_name = payload['display_name']
        if 'avatar_url' in payload:
            user.avatar_url = payload['avatar_url']

    user.save(update_fields=['display_name', 'avatar_url'])
    return JsonResponse({'user': user.to_dict()})


@csrf_exempt
@jwt_required
def change_password(request):
    if request.method != 'POST':
        return json_error(['Method not allowed.'], status=405)

    user = request._current_user
    payload = parse_json_body(request)

    current_pw = payload.get('current_password', '')
    new_pw = payload.get('new_password', '')

    if not check_password(current_pw, user.password_hash):
        return json_error(['Current password is incorrect.'])

    if len(new_pw) < 6:
        return json_error(['New password must be at least 6 characters.'])

    user.password_hash = make_password(new_pw)
    user.save(update_fields=['password_hash'])
    return JsonResponse({'message': 'Password changed successfully.'})

