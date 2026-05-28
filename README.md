# AstraNotes

A secure, multi-user note-taking web application built with Python, FastAPI, and SQLite.


## Features

- **Multi-user**: Each user's notes are owner-only; access control enforced at the service layer via `PrivacyPolicy`
- **JWT Authentication**: Secure register/login with bcrypt password hashing
- **Full Note CRUD**: Create, read, update, delete notes via REST API
- **Visibility & Note Passwords**: Private notes can be password-protected (`X-Note-Password` header); emergency unlock via account password clears the note hash
- **Auto-Save**: Web UI auto-saves 2 seconds after typing stops; status indicator (Unsaved / Saving… / Saved)
- **Web UI**: Single-page application served alongside the API
- **Tags & Filtering**: Tag notes and filter by tags (AND semantics — all specified tags must be present)
- **Version History**: Every note tracks create/update/revert snapshots; restore any past version via API
- **Tested**: 81 tests across unit, integration, and API layers (75 passing; 6 pre-existing visibility-drift failures tracked)

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Setup

```bash
git clone <repo-url>
cd AstraNotes

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional)
cp .env.example .env
# Edit .env to set JWT_SECRET for production
```

### Run locally

```bash
uvicorn app.main:app --reload
```

Open http://localhost:8000 for the web UI, or http://localhost:8000/docs for the interactive API docs.

## Architecture

```
AstraNotes/
├── app/                          # FastAPI web layer
│   ├── main.py                   # App entry point, routes, static file serving
│   ├── config.py                 # Settings (JWT secret, DB URL)
│   ├── auth/                     # JWT token creation & verification
│   ├── routers/
│   │   ├── auth.py               # POST /auth/register, /auth/login
│   │   ├── notes.py              # CRUD /notes/ + note password enforcement
│   │   └── history.py            # GET /notes/{id}/versions, POST /notes/{id}/revert/{v}
│   ├── schemas/                  # Pydantic request/response models
│   ├── db/
│   │   └── sqlite_repository.py  # SQLite adapter (SQLAlchemy Core)
│   ├── service_deps.py           # FastAPI dependency injection
│   └── static/
│       └── index.html            # Single-page web UI
│
└── AstraNotes_v1/                # Domain layer (framework-agnostic)
    ├── note.py                   # Note entity (dataclass)
    ├── exceptions.py             # Custom exception hierarchy
    ├── repositories/
    │   └── abstract_note_repository.py  # Repository interface
    ├── services/
    │   └── note_service.py       # Business logic orchestration
    ├── policies/
    │   └── privacy_policy.py     # Access control (can_read/update/delete)
    └── history/
        └── version_history.py    # Version audit trail
```

### Design Decisions (Architecture Decision Log)

- **Repository pattern**: `AbstractNoteRepository` interface decouples business logic from storage
- **Privacy via PrivacyPolicy**: Access control is enforced at the service layer, not the HTTP layer
- **SQLAlchemy Core (not ORM)**: Chosen for simplicity and direct SQL control at Sprint 7 scale
- **JWT authentication**: Stateless, scalable; `user_id` derived from token (no session storage)

## API Reference

All note endpoints require `Authorization: Bearer <token>`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Create account, receive JWT |
| POST | /auth/login | Authenticate, receive JWT |
| GET | /health | Health check |
| POST | /notes/ | Create note |
| GET | /notes/ | List owner's notes (optional `?tags=a&tags=b` filter — AND logic) |
| GET | /notes/{id} | Get single note (private+password → requires `X-Note-Password` header) |
| PATCH | /notes/{id} | Update note fields |
| DELETE | /notes/{id} | Delete note |
| GET | /notes/{id}/versions | List all version snapshots for a note |
| POST | /notes/{id}/revert/{version} | Revert note to a previous version snapshot |
| POST | /notes/{id}/emergency-unlock | Clear note password hash using account password |

Interactive API docs: http://localhost:8000/docs

## Testing

```bash
# Run all tests
python -m pytest -q

# With verbose output
python -m pytest -v
```

**Test results:** 75 passed, 6 pre-existing failures tracked, 0 new failures

> The 6 tracked failures are pre-existing design-drift tests written when default visibility was `"private"` and public notes were cross-user visible. Current implementation enforces owner-only access for all notes via `PrivacyPolicy`. These tests are kept as a record of the design shift.

| Test File | Count | Level | Coverage |
|-----------|-------|-------|---------|
| `AstraNotes_v1/tests/` | 32 | Unit | Domain model, service, policy, repository, version history |
| `app/tests/test_sqlite_repository.py` | 17 | Unit | SQLite adapter CRUD + version history (TSQ-01~17) |
| `app/tests/test_notes_api.py` | 20 | Integration | HTTP endpoints, tag filter (TNA-01~15), note passwords, access control |
| `app/tests/test_version_history_api.py` | 5 | Integration | Version history endpoints (TVH-01~05) |
| `app/tests/test_auth.py` | 5 | Integration | Auth register/login |
| `app/tests/test_health.py` | 2 | Integration | Health endpoint |

## Deployment (Render)

1. Create a new **Web Service** on [render.com](https://render.com)
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `JWT_SECRET=<your-secret-key>`

## Project Artifacts

| Artifact | Location | Status |
|----------|----------|--------|
| Requirements | `planning/requirements.md` | ✅ Complete (updated for web multi-user) |
| User Stories | `planning/user-stories.md` | ✅ Complete (US-01~06) |
| Architecture Decision Log | `planning/architecture_decision_log.md` | ✅ Complete (incl. ADR-WEB-01/02) |
| UML Diagrams | `UML/` | ✅ Complete (Week 4 design) |
| Traceability Matrix | `planning/TRACEABILITY.md` | ✅ Complete (updated post-Sprint 7) |
| Test Plans | `docs/unit_test_plan.md`, `docs/feature_test_plan.md` | ✅ Complete |
| Sprint Backlogs | `planning/sprint-backlog.md`, `planning/sprint7-backlog.md` | ✅ Complete |
| Working Agreement | `planning/working_agreement.md` | ✅ Complete |
| CI/CD Pipeline | `.github/workflows/ci.yml` | ✅ Configured |
| Collaboration Log | `planning/collaboration_log.md` | 🔄 Week 8-9 complete; Week 10 pending |
| Deployment Plan | `planning/deployment_plan.md` | 🔄 Draft (Render URL pending Week 10) |
| Maintenance Plan | `planning/maintenance_plan.md` | 🔄 Draft (security audit pending Week 10) |

## AI Development Process

This project was built using an AI-native development workflow (Claude Code):
- AI generated architecture proposals, test scaffolding, and implementation drafts
- Human review accepted, refined, or rejected each AI output
- All commits represent human-approved, verified code

Key decisions made by human judgment:
- Selected access-control-only privacy (rejected encryption for Sprint 1-7 scope)
- Chose SQLAlchemy Core over ORM (simpler for current scale)
- Deferred bcrypt auth to match test safety constraints
- Rejected AI-generated tests that had no requirement linkage

---

AstraNotes ·  · Spring 2026
