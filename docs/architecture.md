# Architecture

## Overview

Doonjuma is a monorepo containing a cross-platform mobile/web app and a FastAPI backend.

## Components

### Frontend (`frontend/`)

- **Expo SDK 54** React Native app
- Supports **iOS**, **Android**, and **Web** (PWA)
- Uses **Expo Router** for file-based routing
- **Offline-first**: service worker + CacheStorage on web, AsyncStorage on native
- PWA manifest and service worker in `frontend/public/`

### Backend (`backend/`)

- **FastAPI** Python backend
- CORS-enabled for local Expo web dev servers
- Health check endpoint at `/health`
- Interactive API docs at `/docs` (Swagger UI)

### Docs (`docs/`)

- Project documentation and references

## Directory Layout

```
doonjuma/
├── frontend/           # Expo React Native app
│   ├── app/            # Expo Router screens
│   ├── assets/         # Images, icons, fonts
│   ├── components/     # Reusable UI components
│   ├── constants/      # Theme and app constants
│   ├── hooks/          # Custom React hooks
│   ├── public/         # PWA manifest, service worker, offline page
│   ├── scripts/        # Utility scripts
│   ├── app.json        # Expo configuration
│   ├── package.json    # Frontend dependencies
│   └── tsconfig.json   # TypeScript config with @/* path alias
│
├── backend/            # FastAPI backend
│   ├── app/
│   │   ├── main.py     # FastAPI app entry point
│   │   ├── config.py   # Settings (pydantic-settings)
│   │   └── routers/    # API routers (future)
│   ├── requirements.txt
│   └── .env.example    # Environment variable template
│
└── docs/               # Documentation
```

## Data Flow

```
[React Native App]  <--HTTP/JSON-->  [FastAPI Backend]
       |                                     |
       |-- Offline cache (AsyncStorage)      |-- CORS middleware
       |-- Service worker (web)              |-- /health endpoint
```

## Development

- **Frontend**: `cd frontend && npm install && npx expo start`
- **Backend**: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`