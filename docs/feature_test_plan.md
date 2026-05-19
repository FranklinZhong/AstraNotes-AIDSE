# AstraNotes — Feature / Functional Test Plan

**Version:** 2.0 (Week 6.2 — updated for Web Multi-User API)
**Aligned to:** User Stories US-01–US-06 + Auth flows
**Test tool:** pytest + FastAPI TestClient (httpx)
**Auth prerequisite:** All /notes/ tests require a valid JWT (from register/login)

---

## FT-AUTH — Authentication Flows

**Requirement:** Foundation for multi-user access (GOV-01)

### Main Success Scenarios
```
POST /auth/register  {"username": "alice", "password": "pw"}  → 201 + JWT
POST /auth/login     {"username": "alice", "password": "pw"}  → 200 + JWT
```

### Failure / Edge Cases
| Scenario | Expected |
|----------|----------|
| Register duplicate username | 400 Bad Request |
| Login wrong password | 401 Unauthorized |
| Login unknown username | 401 Unauthorized |
| Access /notes/ without token | 401 Unauthorized |
| Access /notes/ with tampered token | 401 Unauthorized |
| Access /notes/ with expired token | 401 Unauthorized |

### What to Validate
- JWT contains correct `sub` (username)
- Token is accepted on all /notes/ endpoints
- Two different users get different tokens and see different notes

---

## FT-01 — Create Note (US-01, FR-01)

**User story:** As a registered user, I want to create a note with a title and optional body.

### Main Success Scenario
```
POST /notes/
Headers: Authorization: Bearer <token>
Body:    {"title": "Meeting Notes", "body": "Discuss Q3 roadmap"}

→ 201 Created
{
  "id":         "<uuid>",
  "title":      "Meeting Notes",
  "body":       "Discuss Q3 roadmap",
  "visibility": "private",
  "author_id":  "alice",
  "version":    1,
  "created_at": "...",
  "updated_at": "..."
}
```

### Failure / Edge Cases
| Input | Expected |
|-------|----------|
| Empty title `""` | 422 Unprocessable Entity |
| Whitespace-only title `"   "` | 422 |
| Missing title field | 422 |
| Empty body (omitted) | 201, body defaults to `""` |
| visibility = "public" | 201, note is publicly visible |
| No auth token | 401 |

### What to Validate
- UUID generated and unique per note
- `created_at == updated_at` on creation
- `version == 1` on creation
- `author_id` matches authenticated user's username

---

## FT-02 — Edit Note (US-02, FR-02) — Sprint 7

**User story:** As a registered user, I want to edit a note and save my changes.

### Main Success Scenario
```
PATCH /notes/{id}
Body: {"title": "Final Version", "body": "Revised"}

→ 200 OK
{ "title": "Final Version", "version": 2, "updated_at": "<new timestamp>" }
```

### Failure / Edge Cases
| Scenario | Expected |
|----------|----------|
| PATCH to clear title `""` | 422 |
| PATCH non-existent note ID | 404 Not Found |
| PATCH another user's private note | 403 Forbidden |
| PATCH with no fields (empty body `{}`) | 200, note unchanged |
| `updated_at` after PATCH | Must be later than `created_at` |
| `created_at` after PATCH | Must be unchanged |

### What to Validate
- `version` increments by 1 each PATCH
- `updated_at` refreshes; `created_at` stays the same
- Partial PATCH: only provided fields change

---

## FT-03 — Delete Note (US-03, FR-03) — Sprint 7

**User story:** As a registered user, I want to delete a note.

### Main Success Scenario
```
DELETE /notes/{id}   → 204 No Content

GET /notes/          → note absent from list
```

### Failure / Edge Cases
| Scenario | Expected |
|----------|----------|
| DELETE non-existent ID | 404 Not Found |
| DELETE another user's private note | 403 Forbidden |
| GET deleted note by ID | 404 Not Found |

### What to Validate
- Note absent from list after deletion
- Note absent from GET by ID after deletion
- Deletion is persisted (survives server restart)

---

## FT-04 — Private Notes (US-04, FR-04, GOV-01) — Sprint 8

**User story:** As a registered user, I want to mark a note as private so others can't read it.

### Main Success Scenario
```
# Alice creates private note
POST /notes/  {"title": "Secret", "visibility": "private"}  (as alice)  → 201

# Alice can read it
GET /notes/{id}  (as alice)  → 200

# Bob cannot read it
GET /notes/{id}  (as bob)    → 403 Forbidden

# Alice's list shows it; Bob's list does not
GET /notes/  (as alice)  → [includes "Secret"]
GET /notes/  (as bob)    → [does not include "Secret"]
```

### Failure / Edge Cases
| Scenario | Expected |
|----------|----------|
| Bob tries to PATCH alice's private note | 403 |
| Bob tries to DELETE alice's private note | 403 |
| Alice changes visibility to public | Bob can now read it |

### What to Validate
- `author_id` matches JWT `sub` claim
- PrivacyPolicy enforced at service layer, not just router
- visibility persisted in SQLite and restored correctly

---

## FT-05 — Note Persistence (US-05, FR-05) — Sprint 7/8

**User story:** As a user, I want my notes saved so I don't lose work after restart.

### Main Success Scenario
```
# Create notes, then simulate server restart (reload DB)
POST /notes/ × 3  → 201 each
# Restart server (or reinitialize repository)
GET /notes/       → all 3 notes present
```

### Failure / Edge Cases
| Scenario | Expected |
|----------|----------|
| notes.db file missing on startup | Empty collection (no crash) |
| notes.db corrupted on startup | 500 with logged error (not silent crash) |
| Write fails mid-operation | StorageIOError raised, 500 returned |

### What to Validate
- Notes survive server restart (SQLite file persists)
- note count and field values match after reload
- New notes after restart get UUIDs not conflicting with old ones

---

## FT-06 — Timestamps (US-06, FR-07) — Sprint 7

**User story:** As a user, I want to see the created and modified dates on each note.

### Main Success Scenario
```
POST /notes/  → created_at = updated_at = <now>
PATCH /notes/{id}  → updated_at advances; created_at unchanged
GET /notes/{id}    → both timestamps present and correct
```

### What to Validate
- `created_at` format: ISO 8601 with Z suffix (`2026-05-06T18:00:00Z`)
- `created_at` never changes after creation
- `updated_at` changes on every successful PATCH
- Timestamps preserved in SQLite and returned accurately

---

## End-to-End Regression Checklist (run after each Sprint)

```
[ ] FT-AUTH: register + login + access /notes/ with token
[ ] FT-01:   create note with empty title → 422
[ ] FT-01:   create note with valid title → 201, correct fields
[ ] FT-04:   private note not visible to other user (403 / absent from list)
[ ] FT-05:   notes survive server restart
[ ] All 37 unit/integration tests pass:
    python -m pytest app/tests/ AstraNotes_v1/tests/ -q
```
