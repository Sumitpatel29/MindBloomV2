from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from django.conf import settings
from django.http import JsonResponse

from .models import User


def create_access_token(user_id, remember_me: bool = False):
    now = datetime.now(timezone.utc)
    exp_days = settings.JWT_ACCESS_TOKEN_EXPIRES_DAYS
    if remember_me:
        exp_days = int(getattr(settings, 'JWT_REMEMBER_TOKEN_EXPIRES_DAYS', 30))

    payload = {
        'sub': str(user_id),
        'iat': now,
        'exp': now + timedelta(days=exp_days),
        'rm': bool(remember_me),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')


def get_token_from_request(request):
    header = request.META.get('HTTP_AUTHORIZATION', '')
    if header.startswith('Bearer '):
        return header.split(' ', 1)[1].strip()
    return None


def decode_access_token(token):
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])


def get_current_user(request):
    if hasattr(request, '_current_user'):
        return request._current_user

    token = get_token_from_request(request)
    if not token:
        return None

    try:
        payload = decode_access_token(token)
        user_id = int(payload.get('sub'))
    except Exception:
        return None

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

    request._current_user = user
    return user


def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = get_current_user(request)
        if not user:
            return JsonResponse({'errors': ['Authentication required.']}, status=401)
        request._current_user = user
        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = get_current_user(request)
        if not user:
            return JsonResponse({'errors': ['Authentication required.']}, status=401)
        if not getattr(user, 'is_admin', False):
            return JsonResponse({'errors': ['Admin access required.']}, status=403)
        request._current_user = user
        return view_func(request, *args, **kwargs)

    return wrapper

