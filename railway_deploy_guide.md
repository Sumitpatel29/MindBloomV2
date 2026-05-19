# Railway Deployment Guide - MindBloom

This repo is now set up so Railway can run it without needing a local MySQL server.

## Services
- Backend service: `backend/Dockerfile`
- Frontend service: `frontend/Dockerfile`

## Backend setup

1. Create a Railway service from the repo and point it at `backend/Dockerfile`.
2. Add environment variables.

Recommended MySQL-backed setup:
```bash
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<YOUR_BACKEND_SERVICE>.up.railway.app
DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:3306/mindbloom?charset=utf8mb4
JWT_SECRET_KEY=<LONG_RANDOM_SECRET>
CORS_ALLOWED_ORIGINS=https://<YOUR_FRONTEND_SERVICE>.up.railway.app
CSRF_TRUSTED_ORIGINS=https://<YOUR_FRONTEND_SERVICE>.up.railway.app
```

Railway MySQL plugins often expose variables like `MYSQL_URL`, `MYSQLHOST`, `MYSQLDATABASE`, `MYSQLUSER`, `MYSQLPASSWORD`, and `MYSQLPORT`. The backend now understands those too.

If you do not attach MySQL, the backend will fall back to SQLite inside the container and still boot, but data will not be durable across redeploys.

3. Deploy the backend.
4. Run the bootstrap command once if you are using a fresh database:
```bash
python manage.py bootstrap_db
```

## Frontend setup

1. Create a second Railway service and point it at `frontend/Dockerfile`.
2. Set the frontend build variable before deploy:
```bash
VITE_API_BASE_URL=https://<YOUR_BACKEND_SERVICE>.up.railway.app
```
3. Deploy the frontend.

## Verify
- Open the frontend Railway URL.
- Register and log in.
- Check that API requests go to your backend Railway URL.

## Notes
- The backend now binds to `0.0.0.0` in container environments.
- The frontend Dockerfile accepts `VITE_API_BASE_URL` as a build argument.
- If you use SQLite fallback on Railway, expect data to reset when the container is replaced.
