# Render.com deployment guide (two services)

This repo is configured as two Render web services:
- **mindbloom-backend**: Django + gunicorn
- **mindbloom-frontend**: Vite React build served as static files

## 1) Create the services in Render
Deploy using the included `render.yaml`.

If Render does not automatically pick up `render.yaml`, create two **Web Service** entries manually.

## 2) Backend (mindbloom-backend)
### Required env vars
Set these in Render for the backend service:
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS` = your backend host/domain (or `*` during testing)
- `DATABASE_URL` = `mysql+pymysql://USER:PASSWORD@HOST:3306/mindbloom?charset=utf8mb4`
- `JWT_SECRET_KEY` = any long random string
- `CORS_ALLOWED_ORIGINS` = `https://<frontend-render-domain>` (comma-separated if multiple)
- `CSRF_TRUSTED_ORIGINS` = `https://<frontend-render-domain>`

Optional:
- `CELERY_BROKER_URL` (only if you actually use Celery workers)

### Migrations / bootstrapping
This codebase expects initial schema/seed.
Options:
1) Run `python manage.py migrate` in a one-off job (recommended), then run `python manage.py bootstrap_db` if needed.
2) If you rely on runtime bootstrapping, add it to the Render start command.

## 3) Frontend (mindbloom-frontend)
### Build command
- `npm ci`
- `npm run build`

### Env vars
- `VITE_API_BASE_URL` = `https://<backend-render-domain>`

## 4) Static uploads
Backend stores uploads in `backend/uploads/` (configured as `MEDIA_ROOT = BASE_DIR / 'uploads'`).
On Render you must use a writable storage:
- attach Render Disk/File Storage and mount it at the Django `MEDIA_ROOT` path, or
- override `MEDIA_ROOT` via env + code change.

## 5) Verify
After deploy:
- Visit frontend URL and create/login.
- Check API calls succeed (no CORS errors in browser console).
- Confirm uploads show after posting journal photos.

