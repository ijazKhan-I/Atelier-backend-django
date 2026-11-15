# Atelier

E-commerce storefront + API.

| Folder | Role |
|--------|------|
| `atelier-frontend` | Next.js UI (Vercel) |
| `atelier-django` | Django REST Framework API (Vercel + Neon) |

## Run locally

```bash
# Terminal 1 — API
cd atelier-django
source .venv/bin/activate
python manage.py runserver 8000

# Terminal 2 — Frontend
cd atelier-frontend
npm run dev
```

- Store: http://localhost:3000  
- API / admin: http://localhost:8000/admin/ (`admin` / `admin123`)  
- Demo login: `demo` / `demo1234`

## Production

- Frontend: https://atelier-frontend.vercel.app  
- Backend: https://atelier-backend-django.vercel.app  

See `atelier-django/README.md` for Vercel environment variables.
