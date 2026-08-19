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

## Documentation

See the [docs](docs/) directory for architecture overview and API reference.

## Tech Stack

| Layer    | Technology                       |
|----------|----------------------------------|
| Mobile   | React Native (Expo SDK 54)       |
| Web      | React Native Web / PWA           |
| Backend  | FastAPI (Python)                 |
| Routing  | Expo Router (file-based)         |
| Database | TBD                              |