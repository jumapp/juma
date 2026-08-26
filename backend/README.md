# Jumapp Backend

FastAPI backend for the Jumapp app.

## Setup

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and adjust values as needed:

```bash
cp .env.example .env
```

## Database

### PostGIS Installation

The app requires the PostGIS extension. `init_db.py` runs `CREATE EXTENSION IF NOT EXISTS postgis`, but the extension must first be **installed on the PostgreSQL server itself** — `CREATE EXTENSION` only activates an extension that already exists on the server's filesystem.

#### Windows (local PostgreSQL)

PostGIS is **not** bundled with the base PostgreSQL installer. Install it via **Stack Builder**:

1. Open **Stack Builder** (installed alongside PostgreSQL, in the Start Menu under "PostgreSQL 16").
2. Select your local PostgreSQL server and click **Next**.
3. Expand **Spatial Extensions** → check **PostGIS 3.x for PostgreSQL 16** → **Next**.
4. Follow the wizard. When prompted for a database, you can leave it blank (the extension is enabled by `init_db.py`) or select your target database.

Alternatively, download the standalone installer matching your PostgreSQL version from <https://download.osgeo.org/postgis/windows/> (e.g., `postgis-bundle-pg16x64-setup-3.4.x.exe`) and run it, pointing it at your existing PostgreSQL installation.

#### macOS (Homebrew)

```bash
brew install postgis
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt install postgis postgresql-16-postgis-3
```

#### Docker

Use the official `postgis/postgis` image instead of plain `postgres`:

```bash
docker run -d --name jumapp-db \
  -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=jumapp \
  -p 5432:5432 \
  postgis/postgis:16-3.4
```

This image has PostGIS pre-installed, so `CREATE EXTENSION postgis` will work.

#### Managed Cloud

- **Neon / Supabase**: PostGIS is available — run `CREATE EXTENSION postgis;` in the SQL editor.
- **Google Cloud SQL / AWS RDS**: Enable the PostGIS extension via the console/CLI before `CREATE EXTENSION` will succeed.

#### Verify

After installing, verify PostGIS is available:

```sql
SELECT PostGIS_Version();
```

If it returns a version string, PostGIS is ready and you can run the initialization script below.

### Initialize Database

Run the database initialization script to create tables and seed data:

```bash
python app/init_db.py
```

### Database Health Check

Check the database health:

```bash
python -c "from app.health_check import run_health_check; import asyncio; asyncio.run(run_health_check())"
```

## Run

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Versioning

All API endpoints use versioned routes (`/api/v1`).

## Endpoints

### General

| Method | Path       | Description                    |
|--------|------------|--------------------------------|
| GET    | `/`        | Root endpoint with app info    |
| GET    | `/health`  | Health check                   |
| GET    | `/health/full` | Full health check with database |
| GET    | `/docs`    | Interactive API docs (Swagger) |
| GET    | `/redoc`   | ReDoc API docs                 |

### Masjids

| Method | Path                 | Description                                      |
|--------|----------------------|--------------------------------------------------|
| GET    | `/api/v1/masjids`    | List masjids                                     |
| GET    | `/api/v1/masjids/{id}` | Get masjid by ID                               |
| POST   | `/api/v1/masjids`    | Create masjid                                    |
| PATCH  | `/api/v1/masjids/{id}` | Update masjid                                  |
| DELETE | `/api/v1/masjids/{id}` | Delete masjid                                  |

### Salat Schedules

| Method | Path                         | Description                              |
|--------|------------------------------|------------------------------------------|
| GET    | `/api/v1/schedules`          | List schedules                          |
| GET    | `/api/v1/schedules/{id}`     | Get schedule by ID                      |
| POST   | `/api/v1/schedules`          | Create schedule                         |
| PATCH  | `/api/v1/schedules/{id}`     | Update schedule                         |
| DELETE | `/api/v1/schedules/{id}`     | Delete schedule                         |

### Programs

| Method | Path                     | Description                        |
|--------|--------------------------|------------------------------------|
| GET    | `/api/v1/programs`       | List programs                      |
| GET    | `/api/v1/programs/{id}`  | Get program by ID                  |
| POST   | `/api/v1/programs`       | Create program                     |
| PATCH  | `/api/v1/programs/{id}`  | Update program                     |
| DELETE | `/api/v1/programs/{id}`  | Delete program                     |

### People (Committee Members)

| Method | Path                     | Description                        |
|--------|--------------------------|------------------------------------|
| GET    | `/api/v1/people`         | List people                        |
| GET    | `/api/v1/people/{id}`    | Get person by ID                   |
| POST   | `/api/v1/people`         | Create person                      |
| PATCH  | `/api/v1/people/{id}`    | Update person                      |
| DELETE | `/api/v1/people/{id}`    | Delete person                      |

### Photos

| Method | Path                             | Description                        |
|--------|----------------------------------|------------------------------------|
| POST   | `/api/v1/masjids/{id}/photos`    | Upload photo to masjid            |
| DELETE | `/api/v1/masjids/{id}/photos/{photoId}` | Delete masjid photo              |

### Sync (Offline Support)

| Method | Path                     | Description                        |
|--------|--------------------------|------------------------------------|
| GET    | `/api/v1/sync`           | Get sync snapshot/delta            |
| POST   | `/api/v1/sync/mutations`| Sync mutations                    |

### Admin

| Method | Path                         | Description                        |
|--------|------------------------------|------------------------------------|
| GET    | `/api/v1/admin/role-requests` | List role requests                |
| PATCH  | `/api/v1/admin/role-requests/{id}` | Update role request status      |
| GET    | `/api/v1/admin/audit-events` | List audit events                 |

## CORS

CORS is configured via the `CORS_ORIGINS` environment variable (comma-separated list). Defaults allow local Expo web dev servers.

## Frontend API URL Configuration

The frontend (Expo) uses platform-aware API URL resolution via `lib/config.ts`:
- **Web**: `EXPO_PUBLIC_API_URL` → `http://localhost:8000`
- **Mobile**: `EXPO_PUBLIC_API_URL_MOBILE` → ngrok tunnel URL (set by `scripts/start-proxy.js`)

This allows both web and mobile clients to connect to the backend simultaneously without manual `.env` changes.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | postgresql+asyncpg://postgres:postgres@localhost:5432/jumapp |
| `DB_ECHO` | Log SQL queries | false |
| `DB_AUTO_CREATE` | Auto-create database and tables | true |
| `CORS_ORIGINS` | Allowed CORS origins | http://localhost:8081,http://localhost:19006,http://localhost:3000 |
| `AUTH_MODE` | Authentication mode | dev |
| `SUPER_ADMIN_TOKEN` | Super admin token for dev mode | dev-super-admin-token |
| `UPLOAD_DIR` | Local upload directory | uploads |
| `UPLOAD_URL_PREFIX` | URL prefix for uploads | /uploads |
| `MAX_UPLOAD_SIZE_BYTES` | Maximum upload size | 5242880 |
| `MAX_PHOTOS_PER_MASJID` | Maximum photos per masjid | 5 |
| `GCS_BUCKET` | GCS bucket name | (empty) |
| `GCS_PROJECT_ID` | GCS project ID | (empty) |

## Technical Notes

### Database Setup

This implementation uses direct SQLAlchemy table creation instead of Alembic migrations for better control and simpler deployment. The database is created automatically on startup if `DB_AUTO_CREATE` is true.

### Authentication

Authentication is currently implemented in dev mode using header-based authentication. In production, this would be replaced with a proper identity provider integration.

### Photo Storage

Photos are stored locally by default. Google Cloud Storage integration is configured but requires credentials to be provided via environment variables.

### Offline Support

The backend provides sync endpoints to support offline-first operations, allowing the client to queue mutations and synchronize when online.

### Error Handling

All API endpoints use standard FastAPI error handling with Pydantic validation for request bodies and query parameters.

## Development

### Running Tests

```bash
pytest
```

### Running Backend

```bash
uvicorn app.main:app --reload
```

### API Documentation

Visit `http://localhost:8000/docs` for Swagger documentation or `http://localhost:8000/redoc` for ReDoc.