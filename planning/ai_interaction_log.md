# AstraNotes — AI Interaction Log

This log records every significant AI interaction during the AstraNotes project (Week 1–10).
For each interaction it shows: the **prompt** used, the **AI output**, the **decision** (Accepted / Refined / Rejected), and the **human verification** step taken before acceptance.

Full detail for each entry is in the week sections below the summary table.

---

## Summary Table

| # | Week | Prompt Summary | AI Output | Decision | Human Verification |
|---|------|---------------|-----------|----------|--------------------|
| 1 | W1 | "Design a simple storage system for AstraNotes so users can save notes in Python." | Single-class `AstraNotesStorage` backed by JSON file, no abstraction or privacy layer | **Rejected** | Read output — no module boundaries, no `AbstractNoteRepository`, no `PrivacyPolicy`; does not meet project requirements |
| 2 | W1 | "Act as a senior software architect… Define the note model, storage interface, error handling, privacy boundaries, testability…" | 6-layer modular architecture: `NoteModel`, `AbstractNotesRepo`, named errors, `NotePrivacyPolicy`, DI | **Refined** | Verified against FR-01 (body optional) — AI made body required; corrected before adopting |
| 3 | W1 | "Refine the design so that AstraNotes supports text notes first, but can later support voice or image notes without rewriting the storage layer." | `NoteBase` hierarchy, `NoteFactory`, version history in abstract repo, three-layer validation | **Accepted** | Confirmed architecture matches FR-01–FR-09; adopted as canonical design; documented in `architecture_decision_log.md` |
| 4 | W2 | "Generate a product backlog and Sprint Zero plan for AstraNotes with the following epics…" | 20-item backlog with epics: Auth, CRUD, Privacy, Tags, History, UI | **Refined** | Removed 4 over-scoped items (real-time sync, plugin marketplace, voice note upload, ML tagging); kept 16 |
| 5 | W3 | "Review the AstraNotes requirements for ambiguity and inconsistency. Flag any requirement that could be interpreted two ways." | 7 ambiguity findings across FR-01–FR-09 | **Accepted** | Cross-checked each finding against `requirements.md` baseline; all 7 were valid — applied refinements |
| 6 | W3 | "Generate the `AbstractNoteRepository` interface for AstraNotes based on these domain requirements." | Clean abstract interface with `save`, `get`, `list`, `update`, `delete`, `list_versions`, `get_version` | **Accepted** | Read output — matched DI principle exactly; no unnecessary methods; adopted without change |
| 7 | W4 | "Generate a threat scope statement for AstraNotes covering confidentiality, integrity, and availability." | Threat scope with 6 governance items (G-01 to G-06), SZ-06 open decision on note encryption | **Refined** | Resolved SZ-06 (2026-05-05): chose access-control-only (no encryption at rest); documented rationale in ADL |
| 8 | W4 | "Generate UML class, sequence, activity, component, and use-case diagrams for AstraNotes." | 5 draw.io diagrams covering all major flows | **Accepted** | Verified each diagram against `planning/DESIGN.md`; minor label corrections applied to class diagram |
| 9 | W5 | "Create a traceability matrix mapping FR-01–FR-09 to UML diagrams and test IDs." | `TRACEABILITY.md` with FR → UML → test ID linkages | **Refined** | Added missing FR-07 (emergency unlock) and FR-08 (auto-save) rows that AI omitted |
| 10 | W6 | "Scaffold a FastAPI application with JWT auth, `/auth/register`, `/auth/login`, and `/notes/` CRUD endpoints." | Full FastAPI app structure with Pydantic schemas, router modules, dependency injection | **Accepted** | Ran `pytest` (58 tests passing); reviewed router separation manually |
| 11 | W6 | "Should we use SQLite or PostgreSQL? Compare both options for this project's constraints." | Two-option analysis: SQLite (simpler, free-tier compatible) vs PostgreSQL (more scalable) | **Accepted** | Chose SQLite per ADR-WEB-01; reasoning: demo scope, no online deployment required |
| 12 | W7 | "Implement `SqliteNoteRepository` using SQLAlchemy ORM for AstraNotes." | ORM-based repository using `Session`, `DeclarativeBase`, relationship objects | **Rejected** | Read output — ORM adds unnecessary complexity (session lifecycle, lazy loading) at this scale; switched to SQLAlchemy Core per ADR-WEB-02 |
| 13 | W7 | "Implement `SqliteNoteRepository` using SQLAlchemy Core (text queries, parameterized)." | Core-based repository with `text()` queries, `CursorResult`, parameterized inserts | **Refined** | Discovered test isolation issue: `sqlite:///:memory:` creates new DB per connection; changed engine to use `StaticPool` for consistent in-memory DB |
| 14 | W7 | "Generate the module-level SQLAlchemy engine in `auth.py`." | `engine = create_engine(DATABASE_URL)` at module level | **Rejected** | Running tests showed engine creation at import time pollutes all test sessions; replaced with lazy initialization via `get_engine()` factory |
| 15 | W8 | "Draft a pull request description for `feature/search-filter` covering Change, Why, Risks, and Evidence." | PR description with all four sections; mentioned AND tag semantics | **Accepted** (with minor edits) | Read PR description before posting; added one sentence on case-sensitivity; used as final PR body |
| 16 | W8 | "Generate four code review questions for `feature/search-filter` (architecture, edge cases, backward compat, test coverage)." | 4 review questions; Q4 identified missing tag AND-logic test | **Accepted** | 3 of 4 questions surfaced real issues; Q4 added to review comment; drove TNA-09 in Week 9 |
| 17 | W8 | "Check `Note.__post_init__` and `NoteCreate` schema for validation inconsistencies." | Identified whitespace-title gap: domain accepted `"   "` but schema rejected it | **Accepted** | Reproduced bug: `Note("   ")` passed `__post_init__`; confirmed with Python REPL |
| 18 | W8 | "Assess whether `feature/search-filter` PR is ready to merge." | Not ready — missing AND-semantics docstring in `GET /notes/` endpoint | **Accepted** | Merge held; added one-line docstring; PR then approved |
| 19 | W8 | "Explain why `HTTPBearer()` returns 403 instead of 401 when the Authorization header is missing." | FastAPI version difference: `auto_error=True` intercepts missing header and raises 403; fix is `auto_error=False` | **Accepted** | Applied fix to `app/auth/dependencies.py`; CI passed on both Python 3.11 and 3.12 |
| 20 | W8 | "Should tag filtering be case-insensitive? AI recommendation." | Yes — apply `.lower()` at query time | **Rejected** | Tag canonicalization belongs at creation time, not query time; domain stores tags as-is; changing query behavior would create inconsistency with stored data |
| 21 | W9 | "Critique the existing test suite for quality issues (Prompt 1 of 7-prompt bank)." | TVH-02 uses positional index `versions[1]` — brittle if history order changes | **Accepted** | Read `app/routers/history.py` — ordering is by implementation detail, not contract; changed to version-keyed assertion |
| 22 | W9 | "Identify test coverage gaps in the AstraNotes test suite (Prompt 2 of 7)." | 3 gaps: tags AND semantics untested, note password branches untested, PATCH/DELETE non-owner 403 untested | **Accepted** | Verified each: read `notes.py:59` (AND logic), `notes.py:16–27` (3 password branches), `PrivacyPolicy.can_update()` (raises `AccessDeniedError`) |
| 23 | W9 | "Identify Unicode whitespace validation edge cases (Prompt 6 of 7)." | `" "` (non-breaking space U+00A0) passes `.strip()` — bug in title validator | **Accepted** | Confirmed with Python REPL: `" ".strip()` returns `" "` (non-empty); `re.search(r'\S', " ")` returns `None`; applied fix |
| 24 | W9 | "Add a test for `emergency-unlock` endpoint (AI suggestion)." | Test scaffold for `POST /notes/{id}/emergency-unlock` | **Rejected** | Out of scope for Week 9 test quality lab; endpoint is real but coverage deferred to Week 10 security review |
| 25 | W9 | "Add a PATCH-specific note-password test (AI suggestion)." | PATCH note with `X-Note-Password` header test | **Rejected** | PATCH calls `_require_note_password()` via `service.get_note()` — same code path as TNA-10/11/12 already covers; adding PATCH-specific test adds complexity without covering new behavior |
| 26 | W10 | "Generate a SAST security checklist for AstraNotes covering OWASP-aligned checks." | 7 security checks: SQL injection, hardcoded secrets, password in response, eval/exec, path traversal, bcrypt factor, HTTPS | **Accepted** | Verified each check by reading actual source: `sqlite_repository.py` (parameterized queries), `config.py` (env var), `notes.py` (hash never in `NoteResponse`) |
| 27 | W10 | "Generate a DAST test scenario list for AstraNotes covering auth bypass and cross-user access." | 8 test scenarios covering token bypass, cross-user GET/PATCH/DELETE, note password bypass, SQL injection | **Accepted** | Executed each scenario against running application; verified HTTP responses match expected status codes |
| 28 | W10 | "Generate a CI/CD pipeline configuration for AstraNotes (GitHub Actions)." | `ci.yml` with Python 3.11 + 3.12 matrix, `pytest -q`, artifact upload | **Accepted** | Reviewed trigger conditions (push to `main` + PR); verified both Python versions in matrix; CI caught real HTTPBearer bug in Week 8 |

---

## Week 1 — Architecture Design (Three-Round Prompt Iteration)

### Interaction 1 — Weak Prompt → Rejected

**Prompt:**
> "Design a simple storage system for AstraNotes so users can save notes in Python."

**AI Output:** Single class `AstraNotesStorage` backed by a JSON file with CRUD methods. No module separation, no error handling, no privacy layer, no abstraction interface.

**Decision: Rejected**

**Reason:** Output does not meet project requirements: no `AbstractNoteRepository` interface (cannot swap storage backends or test in isolation), no `PrivacyPolicy` (FR-04 violation), no named error types (FR error handling requirement), everything in one class (unmaintainable for a multi-month project).

**Human Verification:** Read the full AI output. Checked each missing requirement against the preliminary FR list. Confirmed that the output cannot be extended to support privacy, versioning, or testability without a complete rewrite.

---

### Interaction 2 — Strong Prompt → Refined

**Prompt:**
> "Act as a senior software architect. AstraNotes is a local note-taking system for individual users that must protect private notes and remain maintainable over a multi-month project. Design a modular storage architecture in Python. Think step by step. Define: the note model, the storage interface, file persistence behavior, error handling, privacy boundaries, and how this design remains testable and extensible over time."

**AI Output:** 6-layer modular architecture with `NoteModel` (dataclass), `AbstractNotesRepo` interface, `JsonFileNotesRepo` + `InMemoryNotesRepo` adapters, 5 named domain errors, `NotePrivacyPolicy` class, and DI setup. AI made `body` a required field in `NoteModel`.

**Decision: Refined** — Architecture accepted; `body` field corrected to optional.

**Human Verification:** Checked `body` against FR-01: "A note must have a title; body is optional." AI output made body required (non-None). Changed `body: Optional[str] = None` before adopting.

---

### Interaction 3 — Refined Prompt → Accepted

**Prompt:**
> "Refine the design so that AstraNotes supports text notes first, but can later support voice or image notes without rewriting the storage layer. Show the major components, their responsibilities, and where validation, privacy, and version history should live."

**AI Output:** `NoteBase` abstract hierarchy with `TextNote` / `VoiceNote` / `ImageNote` subclasses, `NoteFactory.from_dict()`, `AbstractNoteRepository` extended with `history(note_id)`, three-layer validation (domain / service / storage), `PrivacyPolicy` enforced at service entry, `NoteVersion` snapshot model.

**Decision: Accepted**

**Human Verification:** Mapped each component to FR-01–FR-09. All requirements covered. Module map matches the `AstraNotes_v1/` directory structure implemented in Sprint 1–5. Documented as the canonical architecture in `architecture_decision_log.md`.

---

## Week 2 — Planning Artifacts

### Interaction 4 — Backlog + Sprint Zero Plan → Refined

**Prompt:**
> "Generate a product backlog and Sprint Zero plan for AstraNotes with epics covering: authentication, note CRUD, privacy (public/private), tag management, version history, and a basic web UI."

**AI Output:** 20-item backlog with 6 epics, Sprint Zero plan covering environment setup, architecture baseline, and initial domain layer scaffolding.

**Decision: Refined** — 16 of 20 items kept; 4 removed.

**Items removed by human:**
- Real-time multi-user sync (out of scope: single-developer, single-user app)
- Plugin marketplace (premature architecture for a 10-week project)
- Voice note upload pipeline (no audio infrastructure)
- ML-based auto-tagging (no ML stack in scope)

**Human Verification:** Compared each item against the project scope defined in the initial requirements and course constraints (Python, local storage, 10-week timeline). Kept only items traceable to explicit FRs.

---

## Week 3 — Requirements Engineering

### Interaction 5 — Ambiguity Review → Accepted

**Prompt:**
> "Review the AstraNotes requirements for ambiguity and inconsistency. Flag any requirement that could be interpreted two different ways."

**AI Output:** 7 ambiguity findings: (1) "private note" definition unclear — access-control-only vs encrypted-at-rest, (2) tag matching semantics unspecified (AND vs OR), (3) version history retention policy unspecified, (4) "update" vs "overwrite" for notes unclear, (5) "author" field scope (single-user vs multi-user), (6) `body` optional but search behavior on empty body unspecified, (7) visibility default value not stated.

**Decision: Accepted**

**Human Verification:** Cross-checked all 7 findings against `requirements.md` v1 (Week 1.2 baseline). Confirmed each was a genuine ambiguity. Applied 7 corresponding refinements in `requirements.md` v2 (Week 3.1 baseline), including: SZ-06 open decision (private = access-control-only), tag AND semantics, version history unlimited.

### Interaction 6 — AbstractNoteRepository Interface → Accepted

**Prompt:**
> "Generate the `AbstractNoteRepository` interface for AstraNotes domain layer in Python."

**AI Output:** Abstract base class with `save`, `get`, `list`, `update`, `delete`, `list_versions`, `get_version` methods, each raising `NotImplementedError`.

**Decision: Accepted**

**Human Verification:** Verified that every method maps to an explicit functional requirement (FR-01–FR-06, FR-09). No extraneous methods. Adopted unchanged; now lives at `AstraNotes_v1/repositories/abstract_note_repository.py`.

---

## Week 4 — Governance and UML

### Interaction 7 — Threat Scope Statement → Refined

**Prompt:**
> "Generate a threat scope statement for AstraNotes covering confidentiality, integrity, and availability risks."

**AI Output:** Threat scope with 6 governance gaps (G-01–G-06), including SZ-06 (private note encryption mechanism unresolved).

**Decision: Refined** — SZ-06 resolved by human.

**Human Verification (SZ-06 resolution on 2026-05-05):** Evaluated two options: (A) access-control-only, no encryption at rest; (B) field-level encryption with bcrypt/Fernet. Chose Option A — encryption at rest adds significant implementation complexity and is not required by any FR. Decision recorded in `architecture_decision_log.md` with explicit rationale.

### Interaction 8 — UML Diagrams → Accepted

**Prompt:**
> "Generate class, sequence, activity, component, and use-case UML diagrams for AstraNotes."

**AI Output:** 5 draw.io diagrams covering system structure, authentication flow, note CRUD sequence, privacy enforcement activity, and user stories.

**Decision: Accepted**

**Human Verification:** Verified each diagram against `planning/DESIGN.md`. Applied minor label corrections to the class diagram (`NoteService` → `NoteService.create_note()` method names). All diagrams stored in `UML/`.

---

## Week 5 — Traceability

### Interaction 9 — Traceability Matrix → Refined

**Prompt:**
> "Create a requirements traceability matrix for AstraNotes mapping FR-01 through FR-09 to UML diagram references and test IDs."

**AI Output:** Matrix with 7 rows (FR-01–FR-07), UML references, and test ID stubs.

**Decision: Refined** — Added 2 missing rows.

**Human Verification:** Compared AI output against full FR list in `requirements.md`. Found FR-07 (emergency unlock) and FR-08 (auto-save debounce) missing. Added both rows with correct UML and test ID references. Final `TRACEABILITY.md` has 9 FR rows.

---

## Week 6 — Web Pivot (ADR-WEB-01)

### Interaction 10 — FastAPI Scaffold → Accepted

**Prompt:**
> "Scaffold a FastAPI application with JWT authentication, `/auth/register`, `/auth/login`, and `/notes/` CRUD endpoints. Use Pydantic for request/response schemas and dependency injection for the current user."

**AI Output:** Full FastAPI app: `app/main.py`, `app/routers/auth.py`, `app/routers/notes.py`, `app/schemas/`, `app/auth/jwt.py`, `app/auth/dependencies.py`.

**Decision: Accepted**

**Human Verification:** Ran full `pytest` suite — 58 tests passing. Manually reviewed router separation (auth vs notes). Confirmed `get_current_user` dependency wires correctly.

### Interaction 11 — SQLite vs PostgreSQL → Accepted

**Prompt:**
> "Compare SQLite vs PostgreSQL for AstraNotes given: free-tier deployment, single developer, demo scope, no need for concurrent writes."

**AI Output:** SQLite recommended for demo/prototype scale; PostgreSQL for production multi-user systems.

**Decision: Accepted** — SQLite chosen per ADR-WEB-01.

**Human Verification:** Verified against project constraints: no online deployment required (professor confirmed); SQLite sufficient for demo; no managed PostgreSQL available on free tier without paid plan. Documented in `architecture_decision_log.md` (ADR-WEB-01, 2026-05-06).

---

## Week 7 — SQLite Implementation (ADR-WEB-02)

### Interaction 12 — SQLAlchemy ORM → Rejected

**Prompt:**
> "Implement `SqliteNoteRepository` for AstraNotes using SQLAlchemy ORM."

**AI Output:** ORM repository with `DeclarativeBase`, `Session`, mapped `Note` model class, relationship objects.

**Decision: Rejected**

**Reason:** ORM introduces session lifecycle complexity (commit/rollback, session scope), lazy loading pitfalls, and a heavyweight mapping layer for a simple CRUD app. At this scale, direct SQL is clearer and easier to reason about.

**Human Verification:** Read the generated code. Counted 3 unnecessary abstraction layers (DeclarativeBase → mapped class → session) for operations that are 3–4 lines of `text()` query. Switched to SQLAlchemy Core per ADR-WEB-02 (2026-05-12).

### Interaction 13 — SQLAlchemy Core Repository → Refined

**Prompt:**
> "Implement `SqliteNoteRepository` using SQLAlchemy Core with `text()` queries and parameterized inputs."

**AI Output:** Core-based repository using `text()` queries, `CursorResult`, parameterized dict bindings. Engine created with `create_engine("sqlite:///:memory:")` for tests.

**Decision: Refined** — Core approach accepted; test engine configuration corrected.

**Human Verification:** Ran integration tests — found intermittent failures where the in-memory DB was empty between calls. Diagnosed: `sqlite:///:memory:` creates a new DB per connection. Fixed by passing `connect_args={"check_same_thread": False}` and `poolclass=StaticPool` — all tests use same in-memory connection. Verified: 58 tests passing consistently.

### Interaction 14 — Module-Level Engine Singleton → Rejected

**Prompt:**
> AI generated `engine = create_engine(DATABASE_URL)` at module level in `auth.py`.

**AI Output:** Module-level engine that executes `create_engine()` on import.

**Decision: Rejected**

**Reason:** Module-level engine creation during import pollutes all test sessions with a shared engine state. Tests that need different DB configurations cannot override it.

**Human Verification:** Observed test failures when multiple test modules imported `auth.py`. Replaced with a `get_engine()` factory using lazy initialization — engine is created on first call and cached. Verified isolation: each test module can now inject its own in-memory engine.

---

## Week 8 — PR Review and Branching

### Interaction 15 — PR Description Draft → Accepted

**Prompt:**
> "Draft a pull request description for `feature/search-filter` with four sections: Change, Why, Risks, and Evidence."

**AI Output:** PR description with all four sections; mentioned tag AND semantics and case-sensitivity behavior.

**Decision: Accepted** (with minor edits)

**Human Verification:** Read description before posting to GitHub. Added one clarifying sentence on case-sensitivity ("tags are matched case-sensitively; `Python` ≠ `python`"). Used as the final PR body.

### Interaction 16 — PR Review Questions → Accepted

**Prompt:**
> "Generate four code review questions for `feature/search-filter` covering: architecture, edge cases, backward compatibility, and test coverage."

**AI Output:** Q1 (filtering in router vs service), Q2 (empty tag list behavior), Q3 (backward compat with existing tag-less notes), Q4 (AND semantics test coverage gap).

**Decision: Accepted**

**Human Verification:** Verified each question against the codebase. Q4 was the most valuable — confirmed `set.issubset()` in `notes.py:59` implements AND logic with no test covering the multi-tag case. Added Q4 to the PR review comment; became TNA-09 in Week 9.

### Interaction 17 — Whitespace Title Bug Detection → Accepted

**Prompt:**
> "Check for validation inconsistencies between `Note.__post_init__` and `NoteCreate` schema for title validation."

**AI Output:** `Note.__post_init__` uses `if not self.title` (falsy check) — accepts `"   "` (whitespace-only). `NoteCreate` uses `.strip()` — rejects `"   "`. Domain and API layer behave differently.

**Decision: Accepted**

**Human Verification:** Reproduced the bug: `Note("   ")` constructed successfully without error. Confirmed API rejects it. Fixed `__post_init__` to use `if not self.title.strip()`. Created `test/title-validation` branch; added 3 domain tests. 61 tests passing.

### Interaction 18 — Merge Readiness Assessment → Accepted

**Prompt:**
> "Assess whether `feature/search-filter` PR is ready to merge."

**AI Output:** Not ready — `GET /notes/` endpoint docstring does not document AND tag semantics or case-sensitivity. A future developer reading the endpoint would not know the matching behavior.

**Decision: Accepted**

**Human Verification:** Agreed — the behavior is non-obvious and not documented. Added one-line docstring. Issued `Request changes` review decision. PR approved after docstring update.

### Interaction 19 — CI 403/401 Bug Diagnosis → Accepted

**Prompt:**
> "Explain why `test_notes_without_token_returns_401` fails on CI (Python 3.11) but passes locally (Python 3.12). The test asserts 401 but gets 403."

**AI Output:** `HTTPBearer(auto_error=True)` (default) intercepts missing `Authorization` header before the route handler and raises HTTP 403. FastAPI 0.115 (CI) vs 0.136 (local) handle this differently. Fix: use `HTTPBearer(auto_error=False)` and raise 401 explicitly in the handler.

**Decision: Accepted**

**Human Verification:** Applied fix to `app/auth/dependencies.py`. CI passed on both Python 3.11 and 3.12 after the change. Semantically correct: 401 = unauthenticated, 403 = authenticated but unauthorized.

### Interaction 20 — Case-Insensitive Tag Filter → Rejected

**Prompt:**
> "Should tag filtering be case-insensitive? Recommendation?"

**AI Output:** Yes — apply `.lower()` at query time so `python` matches `Python`.

**Decision: Rejected**

**Reason:** Tag canonicalization belongs at creation time, not query time. The domain stores tags as entered. Making query behavior case-insensitive while storage is case-sensitive creates an inconsistency: a user who creates tag `"Python"` and then filters by `"python"` sees a match, but the stored tag is still `"Python"`. If canonicalization is desired, it should be applied in `NoteCreate` at save time — a separate decision.

**Human Verification:** Reviewed FR-03 (tag requirements): no case normalization specified. Kept case-sensitive behavior with a note in the `GET /notes/` docstring.

---

## Week 9 — Test Quality Improvement (7-Prompt Bank)

### Interaction 21 — Test Quality Critique (Prompt 1) → Accepted

**Prompt:**
> "Critique the existing AstraNotes test suite for quality issues — focus on brittle assertions, unclear intent, and reliability risks."

**AI Output:** TVH-02 uses `versions[1]` (positional index) to access version history — brittle if the history ordering changes.

**Decision: Accepted**

**Human Verification:** Read `app/routers/history.py` — history is returned sorted oldest-first by implementation detail, not by contract. A future ordering change would silently break this test. Changed assertion to version-number keyed lookup: `by_version = {v["version"]: v for v in versions}; assert by_version[1]["body"] == ...`.

### Interaction 22 — Coverage Gap Analysis (Prompt 2) → Accepted

**Prompt:**
> "Identify test coverage gaps in the AstraNotes test suite — focus on untested branches and missing behavioral coverage."

**AI Output:** 3 gaps: (1) `?tags=a&tags=b` AND semantics never tested, (2) `_require_note_password()` has 3 branches (missing / wrong / correct password) all untested, (3) PATCH and DELETE by non-owner 403 path untested.

**Decision: Accepted**

**Human Verification:**
- Gap 1: Read `notes.py:59` — `tag_set.issubset(note_tag_set)` is AND logic. Confirmed changing to `any()` would pass all existing tests undetected.
- Gap 2: Read `notes.py:16–27` — three distinct `if` branches, none reached by existing tests.
- Gap 3: Read `PrivacyPolicy.can_update()` and `can_delete()` — both raise `AccessDeniedError` → mapped to 403 in router; no test registered a second user.

Added TNA-09, TNA-10, TNA-11, TNA-12, TNA-13, TNA-14. All pass.

### Interaction 23 — Unicode Whitespace Validation (Prompt 6) → Accepted

**Prompt:**
> "Identify Unicode whitespace edge cases that could bypass the title `.strip()` validator."

**AI Output:** U+00A0 (non-breaking space) is not stripped by Python's `.strip()` — a title containing only `" "` passes the validator silently.

**Decision: Accepted**

**Human Verification:** Confirmed with Python REPL:
```python
>>> " ".strip()   # U+00A0 non-breaking space
' '              # non-empty — bug confirmed
>>> import re; re.search(r'\S', " ")
# returns None — correct: no non-whitespace characters
```
Fixed both `app/schemas/note.py` and `AstraNotes_v1/note.py` to use `re.search(r'\S', v)`. Added TNA-15.

### Interaction 24 — Emergency Unlock Test Scaffold → Rejected

**Prompt:**
> "Generate a test for the `POST /notes/{id}/emergency-unlock` endpoint."

**AI Output:** Test scaffold covering success and failure cases for the emergency unlock flow.

**Decision: Rejected**

**Reason:** Out of scope for the Week 9 test quality lab, which focused on existing test coverage gaps. The `emergency-unlock` endpoint is implemented but its test coverage was explicitly deferred to the Week 10 security review.

**Human Verification:** Checked the Week 9 lab scope statement — coverage of new endpoints was not part of the lab deliverable. Recorded the gap in the coverage improvement table for Week 10 tracking.

### Interaction 25 — PATCH Note Password Test → Rejected

**Prompt:**
> "Add a PATCH-specific note password test (analogous to TNA-10)."

**AI Output:** Test that sends PATCH with correct/incorrect `X-Note-Password` header.

**Decision: Rejected**

**Reason:** PATCH calls `_require_note_password()` through `service.get_note()` — the same code path already exercised by TNA-10, TNA-11, TNA-12. A PATCH-specific test would not cover any new branch.

**Human Verification:** Traced the PATCH handler in `app/routers/notes.py` — it calls `service.get_note(note_id, requesting_user)`, which internally calls `_require_note_password()`. The three password-check branches are already covered. Adding a PATCH variant adds test complexity without behavioral coverage.

---

## Week 10 — Security and Release

### Interaction 26 — SAST Security Checklist → Accepted

**Prompt:**
> "Generate a SAST security checklist for AstraNotes covering SQL injection, hardcoded secrets, password exposure, dangerous functions, and path security."

**AI Output:** 7-item checklist: raw SQL interpolation, hardcoded secrets, password in API response, `eval()`/`exec()`, SQLite file path, bcrypt work factor, HTTPS enforcement.

**Decision: Accepted**

**Human Verification:** Verified each item by reading source code:
- SQL injection: Read `sqlite_repository.py` — all queries use `text()` with `:param` bindings. ✅
- Hardcoded secrets: Read `config.py` — `JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret")`. ✅
- Password in response: Read `NoteResponse` schema — `note_password_hash` excluded. ✅
- `eval()`/`exec()`: `grep -r "eval\|exec" app/` — none found. ✅
- SQLite path: Read `config.py` — `DATABASE_URL` from environment. ✅

### Interaction 27 — DAST Scenario List → Accepted

**Prompt:**
> "Generate a DAST test scenario list for AstraNotes covering authentication bypass, cross-user access, and injection."

**AI Output:** 8 test scenarios targeting: no-token access, invalid token, cross-user private note GET, cross-user PATCH/DELETE, note password bypass (missing/wrong/correct), SQL injection via title.

**Decision: Accepted**

**Human Verification:** Executed all 8 scenarios against the running application (`uvicorn app.main:app --port 8001`). Verified HTTP response codes match expected (401/403/201 as appropriate). SQL injection scenario stored the injection string as a literal — confirmed by reading the inserted row directly via SQLite CLI.

### Interaction 28 — GitHub Actions CI Configuration → Accepted

**Prompt:**
> "Generate a GitHub Actions workflow for AstraNotes that runs pytest on Python 3.11 and 3.12 on every push to `main` and every PR."

**AI Output:** `ci.yml` with `strategy.matrix.python-version: ["3.11", "3.12"]`, `pytest -q --tb=short`, artifact upload (test results, 7-day retention).

**Decision: Accepted**

**Human Verification:** Reviewed trigger conditions (`on: push: branches: [main]`, `pull_request: branches: [main]`). Verified Python matrix covers both versions. CI was activated — it caught the real HTTPBearer 403/401 bug in Week 8 before it was merged to `main`, demonstrating the value of the CI gate.

---

*Source documents: `planning/architecture_decision_log.md`, `planning/collaboration_log.md`, `planning/ai_code_validation_checklist.md`, `planning/requirements.md`, `planning/TRACEABILITY.md`*
