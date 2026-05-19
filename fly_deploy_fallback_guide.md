# Fly.io deployment guide (free) — MindBloom

## Prereqs
- Fly CLI installed (`flyctl`)
- A reachable **MySQL** database (external or self-hosted)
- Decide backend + frontend as **two Fly apps** (recommended)

This guide assumes:
- backend Fly app uses `backend/Dockerfile`
- frontend Fly app uses `frontend/Dockerfile`

## 1) Backend Fly app
### 1.1 Launch (generates fly.toml)
From repo root:
```bash
fly launch --no-deploy --name <YOUR_BACKEND_APP> --dockerfile backend/Dockerfile
```

### 1.2 Set required env vars
In Fly console / CLI:
```bash
fly secrets set \
  DJANGO_DEBUG=False \
  DJANGO_ALLOWED_HOSTS=<YOUR_BACKEND_APP>.fly.dev \
  DATABASE_URL='mysql+pymysql://USER:PASSWORD@HOST:3306/mindbloom?charset=utf8mb4' \
  JWT_SECRET_KEY='<LONG_RANDOM_SECRET>' \
  CORS_ALLOWED_ORIGINS='https://<YOUR_FRONTEND_APP>.fly.dev' \
  CSRF_TRUSTED_ORIGINS='https://<YOUR_FRONTEND_APP>.fly.dev'
```

### 1.3 Deploy backend
```bash
fly deploy
```

### 1.4 Bootstrap DB (seed)
SSH into the machine (or run as one-off task):
```bash
fly ssh console -C "python manage.py bootstrap_db"
```

## 2) Frontend Fly app
### 2.1 Launch frontend
```bash
fly launch --no-deploy --name <YOUR_FRONTEND_APP> --dockerfile frontend/Dockerfile
```

### 2.2 Set frontend env var
Your frontend uses `VITE_API_BASE_URL` at build time, so set it **before deploy**:
```bash
fly secrets set VITE_API_BASE_URL='https://<YOUR_BACKEND_APP>.fly.dev'
```

If your frontend Dockerfile does not run the Vite build with env injection, you must rebuild with build args.
If that’s the case, update `frontend/Dockerfile` to use `ARG VITE_API_BASE_URL` and export it during `npm run build`.

### 2.3 Deploy frontend
```bash
fly deploy
```

## 3) Verify
- Open: `https://<YOUR_FRONTEND_APP>.fly.dev`
- Create account, login
- Post a journal entry with photo
- Confirm photo loads (uploads)

## Notes about uploads
Django stores uploads under `MEDIA_ROOT` (repo uses `backend/uploads`).
On Fly, you need a writable volume and must map it to that path.
If uploads fail:
- add a Fly volume + mount it to `/app/uploads` inside the backend container.

