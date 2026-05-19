# AstraNotes — Unit Test Documentation

**Version:** 2.0 (Week 6.2 — updated for Web Multi-User)
**Framework:** pytest 7+ / FastAPI TestClient (httpx)
**Current total:** 37 passed, 4 skipped

---

## Test Architecture

```
AstraNotes/
├── AstraNotes_v1/tests/     ← Layer 1: Domain unit tests (29 tests)
│   ├── test_note_model.py
│   ├── test_repository.py
│   ├── test_service.py
│   ├── test_privacy_policy.py
│   └── test_version_history.py
└── app/tests/               ← Layer 2: API integration tests (8 tests + 4 skipped)
    ├── conftest.py           ← Shared fixtures
    ├── test_health.py
    ├── test_auth.py
    └── test_notes_api.py
```

**Run all tests:**
```bash
python -m pytest app/tests/ AstraNotes_v1/tests/ -v
```

---

## Layer 1 — Domain Unit Tests (`AstraNotes_v1/tests/`)

These tests are isolated from HTTP and storage. They validate the core domain logic and will never need to change when the transport layer changes.

### `test_note_model.py` — Note dataclass

| Test | Validates | Requirement |
|------|-----------|-------------|
| valid note creation | UUID generated, timestamps set, version=1 | FR-01 |
| empty title → ValidationError | title="" rejected | FR-01 |
| whitespace title → ValidationError | title="   " rejected | FR-01 |
| empty body accepted | body="" is valid (FR-01 fix) | FR-01 |
| invalid visibility → ValidationError | "secret" rejected | FR-04 |
| patch() updates title, increments version | title changes, version = old+1 | FR-02 |
| patch() empty title → ValidationError | cannot clear title via patch | FR-02 |
| to_dict / from_dict round-trip | serialization preserves all fields | FR-05 |

### `test_repository.py` — JsonFileNoteRepository

| Test | Validates | Requirement |
|------|-----------|-------------|
| create + get | note stored and retrieved | FR-05 |
| create + list | note appears in list | FR-05 |
| update | fields overwritten | FR-02 |
| delete | note removed, returns True | FR-03 |
| delete non-existent → False | no exception | FR-03 |
| missing file → empty collection | no crash on first run | FR-05 |
| corrupted JSON → StorageCorruptionError | graceful error | NFR-03 |
| atomic write | no temp file left behind | NFR-02 |

### `test_service.py` — NoteService

| Test | Validates | Requirement |
|------|-----------|-------------|
| create_note success | correct author_id, fields set | FR-01 |
| create_note empty title → ValidationError | propagates from Note | FR-01 |
| get_note success | correct note returned | FR-05 |
| get_note not found → NoteNotFoundError | missing ID handled | FR-05 |
| list_notes filters private notes | non-owner excluded | GOV-01 |
| update_note patches fields | version incremented | FR-02 |
| delete_note → True | note removed | FR-03 |

### `test_privacy_policy.py` — PrivacyPolicy

| Test | Validates | Requirement |
|------|-----------|-------------|
| owner reads own private note | allowed | FR-04, GOV-01 |
| non-owner reads private note → AccessDeniedError | blocked | GOV-01 |
| anyone reads public note | allowed | FR-04 |
| non-owner updates private note → AccessDeniedError | blocked | GOV-01 |
| non-owner deletes private note → AccessDeniedError | blocked | GOV-01 |

### `test_version_history.py` — VersionHistory

| Test | Validates | Requirement |
|------|-----------|-------------|
| add_entry create | entry recorded with op="create" | FR-06 |
| add_entry update | incremented version recorded | FR-06 |
| revert to earlier version | fields restored | FR-06 |
| revert to non-existent → NoteNotFoundError | missing version handled | FR-06 |

---

## Layer 2 — API Integration Tests (`app/tests/`)

These tests validate the HTTP layer using FastAPI's `TestClient`. They test auth flows and endpoint contracts, not domain logic.

### `conftest.py` — Shared Fixtures

| Fixture | Returns | Used by |
|---------|---------|---------|
| `client` | FastAPI TestClient | all API tests |
| `auth_token` | JWT string for "testuser" | auth_headers |
| `auth_headers` | `{"Authorization": "Bearer ..."}` | all /notes/ tests |
| `clear_users` (autouse) | resets in-memory store | all tests auto |

### `test_health.py` — Smoke Tests

| Test | Validates |
|------|-----------|
| health check returns 200 | server is running |
| response includes service name | correct app identity |

### `test_auth.py` — Auth Endpoints

| Test | Validates |
|------|-----------|
| register new user → 201 + JWT | happy path |
| register duplicate username → 400 | constraint enforced |
| login valid credentials → 200 + JWT | happy path |
| login wrong password → 401 | auth rejection |
| GET /notes/ without token → 401 | auth required |

### `test_notes_api.py` — Notes Endpoints (US-aligned)

| Test | User Story | Status |
|------|-----------|--------|
| create note valid title → 201 | US-01 | ⏳ `@skip` Sprint 7 |
| create note empty title → 422 | US-01 | ✅ Active (Pydantic rejects now) |
| list notes empty initially → 200 | US-05 | ⏳ `@skip` Sprint 7 |
| update note increments version | US-02 | ⏳ `@skip` Sprint 7 |
| delete note → 204 | US-03 | ⏳ `@skip` Sprint 7 |

**Activating skipped tests:** remove `@pytest.mark.skip` as each Sprint 7 endpoint is wired to NoteService.

---

## Sprint 7 Test Additions (Planned)

| Test | What it validates |
|------|------------------|
| create → list flow | note persists in SQLite, appears in list |
| private note filtered from other user's list | PrivacyPolicy enforced via API |
| invalid JWT → 401 | token tampering rejected |
| expired JWT → 401 | token expiry enforced |
| 500-note list performance | NFR-01: list completes < 1s |
