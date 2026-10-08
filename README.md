# FocusFlow

AI-assisted learning sessions: watch YouTube content while a browser-side focus model scores attention and stores results in PostgreSQL.

## Stack

- **Backend:** FastAPI, SQLAlchemy 2, Alembic, JWT + bcrypt
- **Frontend:** React + Vite + TypeScript, onnxruntime-web
- **Database:** PostgreSQL 16 (Docker)

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Local development

### Database

```bash
docker compose up db -d
```

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
set DATABASE_URL=postgresql+psycopg2://myuser:123@localhost:5432/postgres
uvicorn app.main:app --reload --port 8000
```

Optional migrations:

```bash
cd backend
alembic upgrade head
```

### Frontend

```bash
cd frontend
npm install
set VITE_API_URL=http://localhost:8000/api
npm run dev
```

## Learning architecture

Request flow:

`Router` → `dependencies` (JWT / DB) → `services` → SQLAlchemy models → PostgreSQL

## Main API

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check |
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Current user |
| GET/POST | `/api/content/videos` | List / add videos |
| POST | `/api/sessions/start` | Start watch session |
| POST | `/api/sessions/{id}/focus` | Save focus sample |
| POST | `/api/sessions/{id}/end` | End session |
| GET | `/api/sessions/history` | Own history |

## Notes

- Passwords are hashed with bcrypt; JWTs are signed with `JWT_SECRET`.
- Camera frames stay in the browser; only numeric focus scores are sent to the server.
- Place ONNX weights under `frontend/public/models/` (default: `v4_2.onnx`).
