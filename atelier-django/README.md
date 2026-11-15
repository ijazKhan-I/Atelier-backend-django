# Atelier Django REST API

Django REST Framework backend for the Atelier storefront. Deployed on Vercel with Neon PostgreSQL.

## Local development

```bash
cd atelier-django
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then set DATABASE_URL (or leave unset for SQLite)
python manage.py migrate
python manage.py seed_atelier
python manage.py runserver 8000
```

- API: http://localhost:8000  
- Admin: http://localhost:8000/admin/ — `admin` / `admin123`  
- Demo user: `demo` / `demo1234`

## Production URLs

- Backend: https://atelier-backend-django.vercel.app  
- Frontend: https://atelier-frontend.vercel.app  

## Vercel env vars (backend project)

Set these in **Vercel → Atelier-backend-django → Settings → Environment Variables**:

| Name | Example value |
|------|----------------|
| `DATABASE_URL` | Neon pooled URL (`sslmode=require`) |
| `DJANGO_SECRET_KEY` | long random secret |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `.vercel.app,atelier-backend-django.vercel.app` |
| `PUBLIC_BASE_URL` | `https://atelier-backend-django.vercel.app` |
| `FRONTEND_URL` | `https://atelier-frontend.vercel.app` |
| `CORS_ALLOWED_ORIGINS` | `https://atelier-frontend.vercel.app,http://localhost:3000` |
| `CSRF_TRUSTED_ORIGINS` | `https://atelier-frontend.vercel.app,https://atelier-backend-django.vercel.app` |

Optional: `ADMIN_NOTIFICATION_EMAIL`, `SMTP_*`.

After setting env vars, redeploy the backend. Run migrations once (local against Neon, or Vercel build/SSH):

```bash
python manage.py migrate
python manage.py seed_atelier   # optional sample data
```

## Frontend Vercel env

In the **frontend** Vercel project:

| Name | Value |
|------|--------|
| `NEXT_PUBLIC_API_URL` | `https://atelier-backend-django.vercel.app` |
