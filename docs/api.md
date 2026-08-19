# API Reference

## Base URL

Production: `https://api.jumapp.com`

Local development: `http://localhost:8000`

## Endpoints

### `GET /`

Root endpoint. Returns basic API information.

**Response**

```json
{
  "name": "Jumapp API",
  "version": "0.1.0",
  "docs": "/docs",
  "health": "/health"
}
```

### `GET /health`

Health check endpoint. Returns API status and version.

**Response**

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

## Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## CORS

The API allows cross-origin requests from configured origins. Defaults:

- `http://localhost:8081`
- `http://localhost:19006`
- `http://localhost:3000`

Configure via the `CORS_ORIGINS` environment variable (comma-separated) in the backend `.env` file.