# Jumapp

A cross-platform mobile/web app built with **Expo SDK 54** (React Native) and a **FastAPI** backend.

## Project Structure

```
jumapp/
├── frontend/     # Expo React Native app (iOS / Android / Web / PWA)
├── backend/      # FastAPI Python backend
└── docs/         # Project documentation
```

## Quick Start

### Frontend

```bash
cd frontend
npm install
npx expo start
```

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
uvicorn app.main:app --reload
```

### From Root

```bash
npm run frontend        # Start Expo dev server
npm run backend         # Start FastAPI dev server
```

## Implementation Status

### ✅ Phase 1: Database Setup (Completed)
- PostgreSQL with PostGIS extension for spatial queries
- SQLAlchemy 2.0 models with all relationships
- Composite indexes and constraints on all filterable fields
- DDL triggers for automatic `updated_at` timestamps
- Seed data for testing

### ✅ Phase 2: Backend APIs (Mostly Completed)
- FastAPI CRUD endpoints for all entities
- Role-based authorization middleware
- Photo upload service (local/GCS)
- Sync endpoints for offline support
- Admin endpoints for role requests and audit logs
- Comprehensive validation and error handling

### ⬜ Phase 3-7: Frontend & Production (Not Started)
- Frontend core infrastructure
- Multi-step masjid form
- Display components
- Integration testing
- Production deployment

## Backend API Reference

Base URL: `http://localhost:8000/api/v1`

### Masjids
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/masjids` | List masjids with filters |
| GET | `/masjids/{id}` | Get masjid by ID |
| POST | `/masjids` | Create masjid |
| PATCH | `/masjids/{id}` | Update masjid |
| DELETE | `/masjids/{id}` | Delete masjid |

### Salat Schedules
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/schedules` | List schedules |
| GET | `/schedules/{id}` | Get schedule by ID |
| POST | `/schedules` | Create schedule |
| PATCH | `/schedules/{id}` | Update schedule |
| DELETE | `/schedules/{id}` | Delete schedule |

### Programs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/programs` | List programs |
| GET | `/programs/{id}` | Get program by ID |
| POST | `/programs` | Create program |
| PATCH | `/programs/{id}` | Update program |
| DELETE | `/programs/{id}` | Delete program |

### People (Committee Members)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/people` | List people |
| GET | `/people/{id}` | Get person by ID |
| POST | `/people` | Create person |
| PATCH | `/people/{id}` | Update person |
| DELETE | `/people/{id}` | Delete person |

### Photos
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/photos/masjids/{masjid_id}/photos` | Upload photo |
| DELETE | `/photos/masjids/{masjid_id}/photos/{photo_id}` | Delete photo |

### Sync (Offline Support)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sync` | Get sync snapshot |
| POST | `/sync/mutations` | Process mutations |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/role-requests` | List role requests |
| PATCH | `/admin/role-requests/{id}` | Update role request |
| GET | `/admin/audit-events` | List audit events |

## Backend Setup

### Prerequisites
- Python 3.12+
- PostgreSQL 16+ with PostGIS extension
- (Optional) GCS bucket for photo storage

### Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

```bash
cd backend
cp .env.example .env
# Edit .env with your values
```

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `AUTH_MODE` - Set to `dev` (only supported mode currently)
- `SUPER_ADMIN_TOKEN` - Token for super admin access
- `GCS_BUCKET` - Google Cloud Storage bucket (optional)
- `DB_AUTO_CREATE` - Set to `true` to auto-create tables on startup

### Database Setup

The database is initialized automatically when `DB_AUTO_CREATE=true` on application startup via `init_db.py`. This replaces Alembic migrations for better control.

> **PostGIS required:** The app uses the PostGIS extension for spatial queries. It must be installed on the PostgreSQL server itself before `init_db.py` runs `CREATE EXTENSION postgis`. See [PostGIS Installation](backend/README.md#postgis-installation) for platform-specific setup (Windows, macOS, Linux, Docker, managed cloud).

### Running the Backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Health Checks

- Basic: `GET /health`
- Full (with DB): `GET /health/full`

## Authentication

Currently uses a dev-mode token system:

1. **Super Admin**: Use header `X-Super-Admin-Token: dev-super-admin-token`
2. **Masjid Editor**: Use header `X-Masjid-Editor-Token: <masjid_id>`
3. **Viewer**: No token required (read-only)

Production will integrate with a proper identity provider.

## Documentation

- [Implementation Plan](docs/plans/masjid-save-and-display-frontend-backend-implementation.md)
- [OpenAPI Spec](docs/api/openapi.json) - *Coming soon*
- Architecture docs: `docs/`

## Tech Stack

| Layer | Technology |
|-------|------------|
| Mobile | React Native (Expo SDK 54) |
| Web | React Native Web / PWA |
| Backend | FastAPI (Python) |
| Routing | Expo Router (file-based) |
| Database | PostgreSQL 16+ with PostGIS |
| ORM | SQLAlchemy 2.0 (async) |
| Auth | Token-based (dev), OIDC (prod planned) |
| Storage | Local filesystem / GCS |

## License

MIT