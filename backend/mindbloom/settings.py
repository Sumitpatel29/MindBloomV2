from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'mindbloom-django-secret-key-change-in-production')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = [host.strip() for host in os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',') if host.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mindbloom.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mindbloom.wsgi.application'

# --- Database ---
# Railway typically provides either a full DATABASE_URL (common) OR individual
# MYSQL_HOST/MYSQL_USER/MYSQL_PASSWORD/MYSQL_DATABASE variables.

database_url = (
    os.environ.get('DATABASE_URL', '')
    or os.environ.get('MYSQL_URL', '')
    or os.environ.get('CLEARDB_DATABASE_URL', '')
    or os.environ.get('JAWSDB_URL', '')
)

mysql_host = (os.environ.get('MYSQL_HOST', '') or os.environ.get('MYSQLHOST', '')).strip()
mysql_user = (os.environ.get('MYSQL_USER', '') or os.environ.get('MYSQLUSER', '')).strip()
mysql_password = os.environ.get('MYSQL_PASSWORD', '') or os.environ.get('MYSQLPASSWORD', '')
mysql_name = (os.environ.get('MYSQL_DATABASE', '') or os.environ.get('MYSQLDATABASE', '')).strip()
mysql_port = (os.environ.get('MYSQL_PORT', '') or os.environ.get('MYSQLPORT', '3306')).strip()

if database_url and database_url.startswith('mysql'):
    from urllib.parse import urlparse, unquote

    parsed = urlparse(database_url)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': unquote(parsed.path.lstrip('/')),
            'USER': unquote(parsed.username or ''),
            'PASSWORD': unquote(parsed.password or ''),
            'HOST': parsed.hostname or 'localhost',
            'PORT': parsed.port or 3306,
            'OPTIONS': {'charset': 'utf8mb4'},
        }
    }
elif mysql_host and mysql_name:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': mysql_name or 'mindbloom',
            'USER': mysql_user or 'root',
            'PASSWORD': mysql_password,
            'HOST': mysql_host,
            'PORT': mysql_port or '3306',
            'OPTIONS': {'charset': 'utf8mb4'},
        }
    }
else:
    # If no DB env vars are present, fall back to sqlite3.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Auth
AUTH_PASSWORD_VALIDATORS = []

# --- Internationalization ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- Static/Media ---
STATIC_URL = '/static/'
MEDIA_URL = '/uploads/'
MEDIA_ROOT = BASE_DIR / 'uploads'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# --- CORS ---
CORS_ALLOW_ALL_ORIGINS = True

cors_origins = [origin.strip() for origin in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if origin.strip()]
if cors_origins:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = cors_origins

csrf_trusted_origins = [origin.strip() for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()]
if csrf_trusted_origins:
    CSRF_TRUSTED_ORIGINS = csrf_trusted_origins

# --- Security ---
if not DEBUG:
    SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SECURE_SSL_REDIRECT', 'False').lower() == 'true'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_SECURE_HSTS_SECONDS', '0'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', 'False').lower() == 'true'
    SECURE_HSTS_PRELOAD = os.environ.get('DJANGO_SECURE_HSTS_PRELOAD', 'False').lower() == 'true'

# --- JWT ---
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
JWT_ACCESS_TOKEN_EXPIRES_DAYS = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_DAYS', '7'))
JWT_REMEMBER_TOKEN_EXPIRES_DAYS = int(os.environ.get('JWT_REMEMBER_TOKEN_EXPIRES_DAYS', '30'))

# --- Celery ---

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', CELERY_BROKER_URL)
CELERY_TASK_ALWAYS_EAGER = os.environ.get('CELERY_TASK_ALWAYS_EAGER', 'False').lower() == 'true'
CELERY_TASK_EAGER_PROPAGATES = os.environ.get('CELERY_TASK_EAGER_PROPAGATES', 'True').lower() == 'true'

