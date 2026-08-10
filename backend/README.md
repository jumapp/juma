# Doonjuma Backend

FastAPI backend for the Doonjuma app.

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

## Run

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Endpoints

| Method | Path       | Description                    |
|--------|------------|--------------------------------|
| GET    | `/`        | Root endpoint with app info    |
| GET    | `/health`  | Health check                   |
| GET    | `/docs`    | Interactive API docs (Swagger) |
| GET    | `/redoc`   | ReDoc API docs                 |

## CORS

CORS is configured via the `CORS_ORIGINS` environment variable (comma-separated list). Defaults allow local Expo web dev servers.