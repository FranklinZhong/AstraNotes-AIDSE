# AstraNotes Functional Specification

**Version:** 2.0 (Week 6.2 — updated for Web Multi-User)
**Scope:** Web REST API, multi-user, SQLite storage
**Stack:** FastAPI + SQLite + PyJWT + Render

---

## 1. Application Overview

AstraNotes is a REST API for multi-user note-taking. Users register, authenticate via JWT, then create, read, update, and delete their own notes. Private notes are only accessible to their author. The API is documented automatically via FastAPI's built-in Swagger UI at `/docs`.

---

## 2. Scope Track

**Chosen track:** Web Multi-User (REST API)
**Default baseline:** Matches professor's stated direction (Week 6.2)
**Phase 1 storage:** SQLite (`notes.db`) via `SqliteNoteRepository`
**Auth:** JWT Bearer token (PyJWT)
**Frontend:** None — Swagger UI at `/docs` serves as interactive demo

---

## 3. Authentication Behavior

### POST /auth/register
- **Input:** `{ "username": str, "password": str }`
- **Success:** 201 + `{ "access_token": str, "token_type": "bearer" }`
- **Failure:** 400 if username already taken

### POST /auth/login
- **Input:** `{ "username": str, "password": str }`
- **Success:** 200 + `{ "access_token": str, "token_type": "bearer" }`
- **Failure:** 401 if credentials invalid

### Protected endpoints
All `/notes/*` endpoints require `Authorization: Bearer <token>` header.
Missing or invalid token → 401 Unauthorized.

---

## 4. Notes API — Endpoint Behavior

### POST /notes/ — Create Note (FR-01, US-01)
| Case | Behavior |
|------|----------|
| Valid title, optional body | 201 + NoteResponse (UUID, timestamps, version=1) |
| Empty title `""` | 422 Unprocessable Entity (Pydantic validation) |
| Whitespace-only title | 422 (field_validator strips and rejects) |
| No auth token | 401 |

### GET /notes/ — List Notes (FR-05, US-05)
| Case | Behavior |
|------|----------|
| User has notes | 200 + `{ "notes": [...], "total": N }` |
| User has no notes | 200 + `{ "notes": [], "total": 0 }` |
| Private note from another user | Excluded from results (PrivacyPolicy) |
| No auth token | 401 |

### GET /notes/{id} — Get Note (FR-01, US-01)
| Case | Behavior |
|------|----------|
| Own note (public or private) | 200 + NoteResponse |
| Another user's public note | 200 + NoteResponse |
| Another user's private note | 403 Forbidden (PrivacyPolicy → AccessDeniedError) |
| Non-existent ID | 404 Not Found |
| No auth token | 401 |

### PATCH /notes/{id} — Update Note (FR-02, US-02)
| Case | Behavior |
|------|----------|
| Valid partial update | 200 + NoteResponse (version incremented, updated_at refreshed) |
| Empty title in patch | 422 |
| Another user's private note | 403 |
| Non-existent ID | 404 |

### DELETE /notes/{id} — Delete Note (FR-03, US-03)
| Case | Behavior |
|------|----------|
| Own note | 204 No Content |
| Another user's private note | 403 |
| Non-existent ID | 404 |

---

## 5. Privacy Rules (GOV-01, FR-04)

- `author_id` is set from the JWT `sub` claim (username) at note creation
- `visibility` defaults to `"private"`
- **Private note:** only readable/editable/deletable by its `author_id`
- **Public note:** readable by any authenticated user; editable/deletable only by `author_id`
- Enforcement: `PrivacyPolicy` (existing domain layer, unchanged)

---

## 6. Request / Response Format

```
Content-Type:  application/json
Authorization: Bearer <jwt_token>     (all /notes/* endpoints)
```

**NoteResponse schema:**
```json
{
  "id":         "uuid-string",
  "title":      "My Note",
  "body":       "Note content",
  "visibility": "private",
  "author_id":  "alice",
  "created_at": "2026-05-06T18:00:00Z",
  "updated_at": "2026-05-06T18:00:00Z",
  "version":    1
}
```

---

## 7. Implemented vs Planned

| Feature | Requirement | Status | Sprint |
|---------|-------------|--------|--------|
| Register / Login | — | ✅ Done | 5 |
| JWT auth on all /notes/ | GOV-01 | ✅ Done | 5 |
| Create Note endpoint | FR-01, US-01 | ⏳ Stub | 7 |
| List Notes endpoint | FR-05, US-05 | ⏳ Stub | 7 |
| Get Note endpoint | FR-01 | ⏳ Stub | 7 |
| Update Note endpoint | FR-02, US-02 | ⏳ Stub | 7 |
| Delete Note endpoint | FR-03, US-03 | ⏳ Stub | 7 |
| Privacy enforcement | FR-04, GOV-01 | ⏳ Stub | 8 |
| Version history | FR-06, US-05 | ⏳ Stub | 8 |
| Render deployment | — | ⏳ Planned | 8 |

---

## 8. Assumptions

- One SQLite file per deployment (`notes.db` in project root)
- Passwords stored in plaintext in Phase 1 (passlib/bcrypt added Sprint 7)
- No rate limiting or pagination in Phase 1
- No email verification or password reset
- Python 3.12+ required

---

## Sprint 9 Additions (2026-05-26)

### New Endpoint: Emergency Unlock

**POST `/notes/{id}/emergency-unlock`**

Clears the note-level password hash by verifying the user's account password. Used when the user has forgotten the note password and cannot access content via `X-Note-Password`.

| Field | Value |
|-------|-------|
| Auth | `Authorization: Bearer <token>` (owner only) |
| Request body | `{"account_password": "<plaintext account password>"}` |
| Success response | `200 OK` — `NoteResponse` with `is_protected: false` and `note_password_hash` cleared |
| Error: wrong account password | `403 Forbidden` — `{"detail": "Incorrect account password"}` |
| Error: note not found | `404 Not Found` |
| Error: not owner | `403 Forbidden` (AccessDeniedError from PrivacyPolicy) |

Implementation: `app/routers/notes.py::emergency_unlock()`. Delegates password verification to `verify_user_password()` in `app/routers/auth.py`.

### Note Password Fields (NoteCreate / NoteUpdate)

Both `NoteCreate` (POST /notes/) and `NoteUpdate` (PATCH /notes/{id}) accept an optional `note_password` field:

```json
{
  "title": "Sensitive Note",
  "visibility": "private",
  "note_password": "my-note-password"
}
```

- The password is hashed with bcrypt before storage; never returned in any response
- When `visibility` switches to `"public"`, the note password hash is automatically cleared
- `NoteResponse` includes `is_protected: true/false` to indicate whether a note password is active

### Auto-Save Behavior (Client-Side)

Auto-save is a client-side behavior only; no new server endpoints are required.

- 2 seconds after the last keystroke in title, body, or tags, the UI sends `PATCH /notes/{id}` with current content
- Status indicator transitions: `● Unsaved` (amber) → `⟳ Saving…` (muted) → `✓ Saved` (green)
- Visibility toggle and password changes trigger immediate save (no debounce) to prevent state inconsistency
- `_isSaving` flag prevents concurrent requests; pending timers are cancelled on note switch or logout

### Unicode Title Validation Fix

Both the Pydantic `NoteCreate` validator and the domain `Note.__post_init__` / `Note.patch()` now use `re.search(r'\S', value)` instead of `value.strip()` to detect whitespace-only titles. This correctly rejects titles consisting only of non-breaking spaces (` `), which Python's `str.strip()` does not remove. Verified by TNA-15.
