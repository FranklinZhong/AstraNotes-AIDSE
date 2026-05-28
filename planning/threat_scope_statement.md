# AstraNotes — Threat Scope Statement (v2.0 Web)

> **Governance item:** GOV-B-04 (from Week 3.2 governance review, G-05)
> **Related:** ADL SZ-06, ADR-WEB-01, `planning/DESIGN.md`, `requirements.md` FR-04/GOV-01
> **Updated:** Week 10 (2026-06-01) — supersedes v1.0 local-app scope; reflects ADR-WEB-01 pivot to FastAPI+JWT+SQLite multi-user web application.

This document defines the threat surface for AstraNotes v2.0. It is not a full threat model — it is a scope statement that clarifies what the system is and is not designed to protect against.

---

## What AstraNotes Is (v2.0)

AstraNotes is a **multi-user web application** built with FastAPI (REST API), SQLite (persistent storage via SQLAlchemy Core), and JWT authentication (PyJWT + bcrypt via passlib). Users register and log in with account credentials; each user's notes are isolated at the application layer by `PrivacyPolicy`. Private notes can be additionally protected with a note-level bcrypt password. The application is deployed on Render's free-tier web service.

**Architecture change from v1.0:** The original scope (Week 3.2) described a local single-user application with no network stack, no authentication, and JSON file storage. ADR-WEB-01 (2026-05-06) pivoted to a multi-user web application. This document supersedes the original scope for all Sprint 6+ work.

---

## In-Scope Threats

These are the threats the current design is intended to address:

| Threat | Mechanism | How AstraNotes Mitigates It |
|--------|-----------|----------------------------|
| **Unauthorized access to another user's notes** | Authenticated user calls GET/PATCH/DELETE on a note they do not own | `PrivacyPolicy.can_read/update/delete()` checks `author_id == user_id` at the service layer before every operation; raises `AccessDeniedError` → HTTP 403. Verified by TNA-13 (PATCH) and TNA-14 (DELETE). |
| **Unauthenticated access to any note** | API call without a valid `Authorization: Bearer <token>` header | `get_current_user()` dependency raises HTTP 401 for missing or invalid tokens. `HTTPBearer(auto_error=False)` passes `None` credentials; handler explicitly raises 401. Verified by `test_notes_without_token_returns_401`. |
| **Note password bypass** | GET /notes/{id} called without `X-Note-Password` header on a password-protected private note | `_require_note_password()` enforces 401 (header missing) / 403 (wrong password) before any content is returned. Verified by TNA-10 (401) and TNA-11 (403). |
| **Brute-force login** | Repeated POST /auth/login attempts to guess a password | bcrypt verification is computationally expensive by design (passlib default cost factor); each attempt takes ~100ms+. Future hardening: rate limiting. |
| **JWT token theft / replay** | Stolen bearer token used to impersonate a user | Tokens carry only `user_id` and `exp`; no session state server-side. HTTPS in production prevents interception. Short-lived tokens (configurable TTL, default 24h) limit replay window. |
| **SQL injection** | Malicious input in note title, body, or tags | SQLAlchemy Core uses parameterized queries throughout `sqlite_repository.py`; no raw string interpolation in any DB operation. |
| **Weak password storage** | Plaintext account or note passwords readable from SQLite | All account passwords hashed with bcrypt before storage; never returned in API responses. Note passwords also bcrypt-hashed (`note_password_hash` field); emergency unlock clears hash without revealing original password. |
| **Data corruption from concurrent writes** | Multiple PATCH requests to the same note simultaneously | SQLAlchemy transactions provide atomicity; `version` field increments on every update, enabling optimistic conflict detection. |

---

## Out-of-Scope Threats

| Threat | Reason Out of Scope |
|--------|-------------------|
| **DDoS / volumetric attacks** | Render free tier has no rate limiting; out of scope for student demo scale |
| **Encrypted storage at rest** | SQLite database file is unencrypted on disk; acceptable for course demo (SZ-06 decision: access-control-only, no encryption) |
| **Session fixation / CSRF** | JWT bearer tokens are stateless; no server-side session; CSRF does not apply to `Authorization` header auth |
| **Multi-tenant DB-level isolation** | Single SQLite file shared across all users; isolation enforced at application layer (PrivacyPolicy), not DB-level row security |
| **Third-party data exposure** | No third-party integrations, no telemetry, no external API calls in AstraNotes v1.0 |
| **Supply chain attacks on dependencies** | Dependencies are pinned in `requirements.txt`; no automated supply chain scanning configured (future: Dependabot) |
| **Infrastructure attacks on Render hosting** | Out of scope; delegated to Render's platform security |

---

## Security Assessment Summary (Week 10 SAST Review)

Manual code review performed against key security concerns:

| Check | Result |
|-------|--------|
| Raw SQL string interpolation | ✅ None found — SQLAlchemy parameterized queries throughout |
| JWT_SECRET hardcoded | ✅ Read from environment variable (`config.py`); never committed |
| Passwords in API responses | ✅ `note_password_hash` never included in `NoteResponse`; account password never returned |
| `eval()` / `exec()` usage | ✅ None found |
| bcrypt work factor | ⚠️ passlib default (~12 rounds); adequate for demo; not configurable via env var |
| HTTPS enforcement | ⚠️ Render provides HTTPS; not enforced at application level (acceptable for demo) |

---

## User Disclosure (v2.0)

- **Account passwords:** stored as bcrypt hash in SQLite; never retrievable in plaintext; not included in any API response
- **Note passwords:** stored as bcrypt hash (`note_password_hash`); emergency unlock clears hash but does not recover the original password
- **Note content:** stored unencrypted in SQLite; protected by JWT authentication + PrivacyPolicy access control
- **JWT tokens:** stored in browser `sessionStorage`; cleared on logout; expire after configurable TTL (default 24h)
- **No third-party data sharing:** AstraNotes makes no external API calls and collects no telemetry
