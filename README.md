# AstraNotes

A secure, multi-user note-taking web application built with Python, FastAPI, and SQLite. Built across Spring 2026 as the capstone project for CSEN 296B-2 (AI-Driven Software Development) at Santa Clara University.

## Features

- **JWT Authentication**: Secure register/login with bcrypt password hashing; token stored in `localStorage`, sent as Bearer on every request
- **Multi-user Access Control**: Each user's notes are owner-only; `NotePrivacyPolicy` enforces access at the service layer, not just the HTTP layer
- **Full Note CRUD**: Create, read, update, delete notes via REST API
- **Visibility & Note Passwords**: Private notes can be password-protected (`X-Note-Password` header); emergency unlock via account password
- **Tags & Filtering**: Tag notes and filter by tag (AND semantics — all specified tags must be present via `?tags=a&tags=b`)
- **Version History**: Every save creates a snapshot; restore any past version via API or Web UI history panel
- **Auto-Save**: Web UI auto-saves 2 seconds after typing stops; Unsaved → Saving… → Saved status indicator
- **Sidebar Search & Tag Filter**: Search notes by title; expandable tag panel lets you click any tag to filter the note list; both filters combine with AND logic
- **Single-Page Web UI**: Dark-themed UI served alongside the API at `http://localhost:8000`
- **CI/CD**: GitHub Actions runs full test suite on Python 3.11 and 3.12 on every push

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Setup

```bash
git clone https://github.com/FranklinZhong/AstraNotes-AIDSE
cd AstraNotes

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional)
cp .env.example .env
# Edit .env to set JWT_SECRET for production use
```

### Run locally

```bash
uvicorn app.main:app --reload
```

Open **http://localhost:8000** for the web UI, or **http://localhost:8000/docs** for the interactive API docs.

## Architecture

Three-layer clean architecture — each layer depends only on the one below it:

```
AstraNotes/
├── app/                              # Layer 1: FastAPI Web API
│   ├── main.py                       # Entry point, CORS, static serving
│   ├── config.py                     # Settings (JWT secret, DB URL via env)
│   ├── auth/                         # JWT creation & verification
│   │   ├── jwt.py
│   │   └── dependencies.py           # FastAPI dependency: get_current_user
│   ├── routers/
│   │   ├── auth.py                   # POST /auth/register, /auth/login
│   │   ├── notes.py                  # CRUD /notes/ + note password enforcement
│   │   └── history.py                # GET /notes/{id}/versions, POST /notes/{id}/revert/{v}
│   ├── schemas/                      # Pydantic request/response models
│   ├── db/
│   │   └── sqlite_repository.py      # SQLite adapter (SQLAlchemy Core)
│   ├── service_deps.py               # Dependency injection wiring
│   ├── static/
│   │   └── index.html                # Single-page web UI (CSS + HTML + JS)
│   └── tests/                        # API-layer integration tests
│
├── AstraNotes_v1/                    # Layer 2: Domain Logic (pure Python, no framework)
│   ├── note.py                       # Note entity (dataclass)
│   ├── exceptions.py                 # Custom exception hierarchy
│   ├── repositories/
│   │   └── abstract_note_repository.py   # Repository interface (DI contract)
│   ├── services/
│   │   └── note_service.py           # Business rule orchestration
│   ├── policies/
│   │   └── privacy_policy.py         # Access control (can_read / update / delete)
│   ├── history/
│   │   └── version_history.py        # Version snapshot model
│   └── tests/                        # Domain-layer unit tests
│
├── planning/                         # All SDLC planning documents (31 files)
├── UML/                              # 5 draw.io UML diagrams
├── .github/workflows/ci.yml          # GitHub Actions CI (Python 3.11 + 3.12)
├── requirements.txt
├── requirements-dev.txt
└── pytest.ini
```

### Key Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Storage abstraction | `AbstractNoteRepository` interface | Decouples domain logic from storage; swapping SQLite → PostgreSQL requires changing only `sqlite_repository.py` |
| Access control location | Service layer (`NotePrivacyPolicy`) | Cannot be bypassed by calling the API directly; enforced before any DB read |
| ORM vs Core | SQLAlchemy Core (not ORM) | Simpler, no session complexity, direct SQL control at this scale |
| Authentication | PyJWT + bcrypt | Stateless; `user_id` embedded in token, no server-side session storage |

Full decision history: [`planning/architecture_decision_log.md`](planning/architecture_decision_log.md)

## API Reference

All note endpoints require `Authorization: Bearer <token>`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create account, receive JWT |
| POST | `/auth/login` | Authenticate, receive JWT |
| GET | `/health` | Health check |
| POST | `/notes/` | Create note |
| GET | `/notes/` | List owner's notes (`?tags=a&tags=b` — AND filter) |
| GET | `/notes/{id}` | Get note (private+password → `X-Note-Password` header required) |
| PATCH | `/notes/{id}` | Update note fields |
| DELETE | `/notes/{id}` | Delete note |
| GET | `/notes/{id}/versions` | List all version snapshots |
| POST | `/notes/{id}/revert/{version}` | Revert to a previous snapshot |
| POST | `/notes/{id}/emergency-unlock` | Clear note password using account password |

Interactive docs: **http://localhost:8000/docs**

## Testing

```bash
# Run all tests
python -m pytest -q

# Verbose output
python -m pytest -v

# Run only domain-layer unit tests
python -m pytest AstraNotes_v1/tests/ -v

# Run only API integration tests
python -m pytest app/tests/ -v
```

**Test results: 84 passed, 0 failed** (Python 3.11 + 3.12, CI green)

| Test File | Tests | Level | What it covers |
|-----------|-------|-------|----------------|
| `AstraNotes_v1/tests/test_note_model.py` | 11 | Unit | Note entity validation, Unicode title |
| `AstraNotes_v1/tests/test_service.py` | 5 | Unit | NoteService CRUD + error paths |
| `AstraNotes_v1/tests/test_privacy_policy.py` | 6 | Unit | Access control rules |
| `AstraNotes_v1/tests/test_repository.py` | 7 | Unit | JsonFile repository adapter |
| `AstraNotes_v1/tests/test_version_history.py` | 3 | Unit | Version snapshot model |
| `app/tests/test_sqlite_repository.py` | 17 | Integration | SQLite adapter CRUD + version history (TSQ-01~17) |
| `app/tests/test_notes_api.py` | 23 | Integration | HTTP endpoints, tag filter, note passwords, access control, emergency unlock (TNA-01~18) |
| `app/tests/test_version_history_api.py` | 5 | Integration | Version history endpoints (TVH-01~05) |
| `app/tests/test_auth.py` | 5 | Integration | Register / login flows |
| `app/tests/test_health.py` | 2 | Integration | Health endpoint |

Extended live-server scenario tests (150 scenarios, requires running server):

```bash
# Start server first: uvicorn app.main:app --port 8001
python app/tests/scenario_tests.py           # Scenarios 1–50
python app/tests/scenario_tests_extended.py  # Scenarios 51–150
```

## Project Artifacts

All SDLC artifacts developed across the 10-week course are in `planning/`:

| Artifact | File | Week |
|----------|------|------|
| Initial Requirements | `planning/initial_requirements.md` | W1-2 |
| Architecture Decision Log | `planning/architecture_decision_log.md` | W1-10 (complete) |
| Working Agreement | `planning/working_agreement.md` | W2-1 |
| Definition of Done | `planning/definition_of_done.md` | W2-1 |
| Product Backlog | `planning/backlog.md` | W2-2 |
| Sprint Zero Plan | `planning/sprint-zero-plan.md` | W2-2 |
| Refined Requirements Baseline | `planning/requirements.md` | W3-1 |
| Threat Scope Statement (Governance) | `planning/threat_scope_statement.md` | W3-2 |
| Design Package | `planning/DESIGN.md` | W4 |
| UML Diagrams (5 diagrams) | `UML/` | W4 |
| Traceability Matrix | `planning/TRACEABILITY.md` | W5-1 |
| Sprint Log (all sprints) | `planning/sprint_log.md` | W6 → W10 |
| Testing Strategy | `planning/week7-testing-strategy.md` | W7-2 |
| Collaboration & AI Log | `planning/collaboration_log.md` | W8 → W10 |
| AI Interaction Log | `planning/ai_interaction_log.md` | W1 → W10 |
| AI Code Validation Checklist | `planning/ai_code_validation_checklist.md` | W8 |
| CI/CD Workflow Plan | `planning/cicd_workflow_plan.md` | W10 |
| Deployment Plan | `planning/deployment_plan.md` | W10 |
| Maintenance Plan | `planning/maintenance_plan.md` | W10 |
| Functional Spec | `planning/functional_spec.md` | W6 |
| Unit Test Plan | `planning/unit_test_plan.md` | W7 |
| Feature Test Plan | `planning/feature_test_plan.md` | W7 |

## AI-Native Development Process

This project was built using an AI-native workflow — Claude assisted at every SDLC stage while the human acted as reviewer, validator, and decision-maker.

**Three categories of AI output:**

| Outcome | Example |
|---------|---------|
| **Accepted** | `AbstractNoteRepository` interface — clean, matched dependency-inversion principle exactly |
| **Refined** | Note `body` field changed from required to optional after checking FR-01 (AI missed the spec) |
| **Rejected** | SQLAlchemy ORM → switched to Core; ORM added unnecessary complexity at this scale |

All decisions are recorded in [`planning/architecture_decision_log.md`](planning/architecture_decision_log.md) and [`planning/collaboration_log.md`](planning/collaboration_log.md).

---

*AstraNotes · CSEN 296B-2 · Santa Clara University · Spring 2026*
