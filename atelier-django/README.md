# Atelier Django REST API

Django REST Framework backend that replaces Strapi for the Atelier storefront. API paths and response shapes stay compatible with `atelier-frontend` (`{ data, meta }`, `documentId`, JWT auth).

## Quick start

```bash
cd atelier-django
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_atelier
python manage.py runserver 8000
```

- API base: `http://localhost:8000`
- Admin: `http://localhost:8000/admin` — `admin` / `admin123`
- Demo customer: `demo` / `demo1234`

Point the frontend at this server:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
# legacy alias also supported:
# NEXT_PUBLIC_STRAPI_URL=http://localhost:8000
```

## Main endpoints

| Method | Path | Auth |
|--------|------|------|
| POST | `/api/auth/local` | public |
| POST | `/api/auth/local/register` | public |
| GET | `/api/home-page` | public |
| GET | `/api/shop-page` | public |
| GET | `/api/about` | public |
| GET | `/api/contact-page` | public |
| GET | `/api/products` | public |
| GET | `/api/products/<documentId>` | public |
| GET | `/api/categories` | public |
| POST | `/api/orders` | JWT |
| GET | `/api/orders/my-orders` | JWT |
| GET | `/api/orders/track/<orderNumber>` | JWT or `?email=` |
| GET | `/api/orders/delivery-session?token=` | public |
| POST | `/api/orders/share-driver-location` | public |
| POST | `/api/drivers/register` | JWT |
| GET | `/api/drivers/me` | JWT |
| GET | `/api/drivers/my-orders` | JWT |
| POST | `/api/drivers/share-location` | JWT |
| POST | `/api/newsletter-subscribers/subscribe` | public |
| POST | `/api/contact-inquiries/submit` | public |

Media files are served under `/uploads/` in development.
