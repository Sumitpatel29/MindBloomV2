import os

# Celery is optional for local test runs. Import lazily to avoid hard dependency.
try:
    from celery import Celery
except Exception:
    Celery = None

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindbloom.settings')

if Celery is not None:
    app = Celery('mindbloom')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks()
else:
    # Provide a lightweight placeholder so Django can import this module during tests.
    class _DummyCeleryApp:
        def __getattr__(self, name):
            def _noop(*args, **kwargs):
                return None
            return _noop

    app = _DummyCeleryApp()
