# AstraNotes — Architecture Decision Log


---

## Round 1 — Weak Prompt

### Prompt Used
```
Design a simple storage system for AstraNotes so users can save notes in Python.
```

### AI Response Summary
Copilot generated a single-class solution (`AstraNotesStorage`) backed by a JSON file with the following capabilities:
- `create_note(title, body, metadata)` — saves a note with UUID and timestamps
- `get_note(note_id)` — retrieves by ID
- `list_notes()` — returns all notes
- `update_note(note_id, ...)` — partial update with timestamp refresh
- `delete_note(note_id)` — removes by ID
- `search_notes(query)` — case-insensitive title/body search

### Key Excerpt from AI Response
> *"Simple and portable (single JSON file). No external DB dependency. Easy to enhance (SQLite integration, atomic writes, concurrency, encryption). Good fit for user 'save notes in Python' requirement without over-engineering."*

### What the Weak Prompt Did Well
- Recognized the need for a note data model (id, title, body, timestamps)
- Produced working CRUD operations
- Avoided external dependencies

### What the Weak Prompt Did Poorly
- **No module boundaries**: everything is in one class — storage logic, data model, and operations are all mixed together
- **No error handling**: no try/except around file I/O; a corrupted JSON file would crash the app
- **No privacy layer**: no concept of private notes or any access control
- **No validation**: no checks before saving (e.g. empty title, invalid note_id)
- **No testability design**: no interface or abstraction — impossible to swap out the storage backend for tests
- **No extensibility plan**: tightly coupled to JSON; adding SQLite or encryption would require rewriting the class

---

## Round 2 — Strong Prompt

### Prompt Used
```
Act as a senior software architect. AstraNotes is a local note-taking 
system for individual users that must protect private notes and remain 
maintainable over a multi-month project. Design a modular storage 
architecture in Python. Think step by step. Define:
- The note model (fields, metadata)
- The storage interface (save, load, update, delete)
- File persistence behavior (how notes are written to disk)
- Error handling (what happens on invalid operations)
- Privacy boundaries for private notes
- How this design remains testable and extensible over time
Avoid unnecessary external dependencies.
```

### AI Response Summary
Copilot produced a full modular architecture with clear separation across six areas:

**1. Note Model** — `@dataclass(frozen=True)` with core fields (id, title, body, timestamps), metadata (tags, author, version), and an explicit privacy field (`visibility: "public" | "unlisted" | "private"` + `encrypted` flag).

**2. Storage Interface** — Abstract class `AbstractNotesRepo` defining `save`, `load`, `list`, `update`, `delete`, `search`, `exists`, and `health_check`. Concrete adapters: `JsonFileNotesRepo`, `InMemoryNotesRepo`, with future `SqliteNotesRepo` and `EncryptedNotesRepo`.

**3. File Persistence** — Atomic writes via temp file + `os.replace()` (POSIX-safe), file locking, backup rotation, and a `lenient/strict` corruption recovery policy.

**4. Error Handling** — Named domain errors: `NoteNotFoundError`, `ValidationError`, `NoteAccessDenied`, `StorageCorruptionError`, `StorageIOError`. Each operation has a defined behavior contract.

**5. Privacy Boundaries** — `NotePrivacyPolicy` class with `can_read/write/delete(note, user)`. Private notes excluded from `list`/`search` unless explicitly authorized. Field-level encryption optional.

**6. Testability & Extensibility** — Dependency injection of `AbstractNotesRepo` into the service layer. `InMemoryNotesRepo` for fast unit tests. Module map:
```
astranotes/model.py | repo/base.py | repo/json_file.py | repo/memory.py
service.py | auth.py | errors.py | utils.py
```

### Key Excerpt from AI Response
> *"Minimal dependencies (stdlib only). Strong separation: model, persistence, policy. Privacy baked into the model and service layer. Easy to test via in-memory adapter. Future-safe for durability with zero-breaking change in API if you preserve the `AbstractNotesRepo` contract."*

### What the Strong Prompt Added vs. Round 1

| Dimension | Round 1 (Weak) | Round 2 (Strong) |
|-----------|----------------|-----------------|
| Logic flow | Single-class chain: one method calls the next with no layer separation | Three-layer flow: `NoteService` → `PrivacyPolicy` → `AbstractNotesRepo`; each layer has a defined entry/exit contract |
| Module boundaries | Single class, everything mixed | 7 separate modules with clear responsibilities |
| Storage interface | Concrete only | Abstract `AbstractNotesRepo` + multiple adapters |
| Error handling | None | 5 named domain errors, per-operation contracts |
| Privacy | None | `visibility` field + `NotePrivacyPolicy` class |
| Testability | Not designed for | `InMemoryNotesRepo` + abstract test mixin |
| Extensibility | Rewrite required | Plug in `SqliteNotesRepo` without touching service layer |
| Realism of design | Not deployable: no atomic writes, no corruption recovery — a single interrupted save corrupts all notes | Production-realistic: atomic write via `os.replace()`, backup rotation, corruption detection, and named error types for every failure mode |

---

## Round 3 — Refined Prompt

### Prompt Used
```
Refine the design so that AstraNotes supports text notes first, but can 
later support voice or image notes without rewriting the storage layer. 
Show the major components, their responsibilities, and where validation, 
privacy, and version history should live.
```

### AI Response Summary
Copilot produced a future-proof, component-based architecture with a `NoteBase` hierarchy:

**Domain Model** — `NoteBase` as the abstract parent; `TextNote`, `VoiceNote`, `ImageNote` as subclasses. A `NoteFactory.from_dict()` handles deserialization by `note_type`. Binary content (voice/image) stored as URIs, not inline.

**Storage Interface** — `AbstractNoteRepository` extended with `history(note_id)` for version tracking. Same adapter pattern as Round 2 (`JsonFile`, `InMemory`, future `Sqlite`/`EncryptedNoteRepository`).

**Validation** — Three-layer: domain-level (inside each `Note` subclass), service-level (`NoteService` runs policy + ownership before calling repo), storage-level (optional `assert note.is_valid()`).

**Privacy** — `PrivacyPolicy` class with `can_read/update/delete(note, user)`. Enforced at every service entry point. Optional audit log.

**Version History** — `NoteVersion` stored in `note_versions.json` or per-note history file. Service workflow: fetch → diff → save `NoteVersion` → commit update. `revert()` creates a new version from old snapshot.

**Module Map:**
```
astranotes/models.py          ← NoteBase, TextNote, VoiceNote, ImageNote, NoteFactory
astranotes/repository/        ← AbstractNoteRepository, JsonFile, InMemory, VersionHistory
astranotes/services/          ← NoteService, PrivacyPolicy
astranotes/exceptions.py      ← ValidationError, AccessDenied, NotFound, StorageError
astranotes/utils/atomic_file.py
tests/                        ← model, repository, privacy, versioning, atomic write
```

### Key Excerpt from AI Response
> *"Start with text note data model + TextNote. Use interface-based repository for storage-location independence. Put privacy logic at service/policy boundary. Enable voice/image later by adding Note types and minimal repo changes. No external dependencies required (stdlib only)."*

---

## Final Verdict

The Round 3 architecture is significantly stronger than Round 1 because it enforces a clear separation between the domain model, storage interface, and privacy policy — allowing each layer to evolve independently without breaking the others. Unlike the single-class design produced by the weak prompt, the interface-based `AbstractNoteRepository` makes the storage backend fully swappable, meaning tests can run against `InMemoryNoteRepository` while production uses `JsonFileNoteRepository`, and a future `SqliteNoteRepository` can be added with zero changes to the service layer. Most critically, privacy and version history are treated as first-class architectural concerns with dedicated components rather than afterthoughts, which is the kind of engineering decision that can actually guide a quarter-long project. I would trust the Round 3 architecture with real user data because privacy is enforced at the service boundary through `PrivacyPolicy` before any repository call is made, private notes are never exposed in list or search results without authorization, and low-level I/O errors are caught and wrapped as named exceptions rather than leaking raw failures to the caller.

---

## Governance Review (2026-04-14)

This section records governance findings and open decisions identified during the Week 3.2 lab review. It is not a design change — it is a formal record of risks, gaps, and decisions that must be resolved before the relevant implementation sprints begin.

### Development Dependency Record

| Dependency | Type | License | Purpose | Version Policy |
|------------|------|---------|---------|----------------|
| pytest | Dev-only (not shipped) | MIT | Unit and integration test runner (GOV-03) | Pin before Sprint 1 |

> Note: pytest was required under GOV-03 but had not been formally recorded here. No runtime dependencies exist as of Week 3.2. This posture must be actively maintained as implementation begins.

---

### Open Decision: SZ-06 — Private Notes Mechanism

**Status:** ✅ RESOLVED — Decision recorded 2026-05-05, before Sprint 1 begins.

**Context:** FR-04 defines a privacy flag enforced at the service layer via `PrivacyPolicy`. The current architecture specifies access-control-only behavior — notes are not encrypted at rest. A user with direct filesystem access to the JSON storage file can read all note content including notes marked private. This is a documented design decision, not an oversight.

**Risk:** If Sprint 5 implementation begins without formally recording the outcome of SZ-06, the system may be released with access-control-only behavior while users assume encryption. The private flag must not imply encryption unless encryption is implemented.

**Decision (2026-05-05): Option A — Access-Control-Only**

Private notes are protected by service-layer access control only. No at-rest encryption is implemented.

**Rationale:**
1. Consistent with the Week 3.1 explicit scope assumption: "No file-system encryption: 'Private' means service-layer access control only."
2. AstraNotes is a single-user, local-first application. The threat model does not include adversarial multi-user access or shared-machine scenarios — encryption adds significant complexity without proportional security benefit at this scope.
3. Adding at-rest encryption (Option B) would require a `cryptography` library dependency, key management design, and a separate FR — none of which are in scope for the current quarter.
4. The access-control mechanism is already designed and tested (PrivacyPolicy + AccessDeniedError).

**Required disclosures (G-02, implemented with FR-04):**
- README must state: "Private notes are protected by application-level access control, not file-system encryption. A user with direct access to `astranotes_data.json` can read all note content."
- CLI help output for the `mark-private` command must include equivalent disclosure.

**Consequence:** FR-04 and GOV-01 can now be implemented in Sprint 1. The `PrivacyPolicy` class enforces the access-control-only model. No `cryptography` dependency will be added unless a new FR explicitly requires it.

---

### Architectural Constraint: Single-User Identity (GOV-B-05, 2026-05-05)

**Status:** Recorded as explicit architectural constraint.

**Constraint:** AstraNotes v1 is a single-user application. The `author_id` field on `Note` and `user_id` parameters on `NoteService` methods are implemented as a hardcoded single-user sentinel (`"local_user"`), not as a multi-user identity system.

**Implications:**
- `PrivacyPolicy.can_read/update/delete(user_id, note)` always receives the same `user_id` value in v1. The policy logic is still correct — private notes require `note.author_id == user_id` — but in practice this always matches.
- Multi-user access is explicitly out of scope (Week 3.1 scope assumption). Adding real user identity would require: an authentication layer, a user registry, and a redesigned PrivacyPolicy — none of which are in scope.
- The `user_id`/`author_id` parameters are retained in the API for future extensibility, not removed, because removing them would be a breaking interface change.

**Single-user sentinel value:** `author_id = "local_user"` — set at note creation; constant throughout application lifetime.

---

### Governance Gaps Identified (Week 3.2)

The following gaps were identified in the Week 3.2 governance review. Each has a recommended action and a target sprint.

| # | Gap | Risk | Action | Target |
|---|-----|------|--------|--------|
| G-01 | SZ-06 unresolved — private notes mechanism undecided | Private flag may mislead users about encryption | Record decision in ADL before Sprint 5 | ✅ Resolved 2026-05-05 — Option A (access-control-only) |
| G-02 | No user-facing disclosure that `private` = access-control-only | Users may assume filesystem-level protection | Add disclosure to README and CLI help output | Sprint 5 |
| G-03 | No audit logging — GOV-01 returns AccessDeniedError but does not record it | Unauthorized access attempts leave no trace | Acknowledge as out-of-scope explicitly; add GOV requirement if needed in future sprint | Sprint 8 review |
| G-04 | No AI code verification checklist for implementation phase | AI-generated code may satisfy surface reading but miss failure paths from refined requirements | Create checklist before Sprint 1: verify requirement mapping, failure paths, and sign-off | Before Sprint 1 |
| G-05 | No formal threat model or attack surface analysis | Architecture specifies where privacy is enforced but not what threats are in/out of scope | Draft single-page threat scope statement before Sprint 5 | Before Sprint 5 |
| G-06 | Single-user assumption hardcoded throughout | Adding multi-user support later would require significant redesign of the privacy layer | Document as explicit architectural constraint in README | Sprint 5 |

---

### AI Data Handling — Implementation Phase Rules (established Week 3.2)

The following rules apply to all AI usage from Sprint 1 onward. They are binding under the Working Agreement and the Definition of Done.

1. All AI prompts must use synthetic placeholder examples. Never paste real note titles, bodies, timestamps, or user-specific content into an AI tool.
2. AI-generated code must be verified against its requirement number before merging. The verification checklist (G-04) must exist before the first Sprint 1 session.
3. Do not claim encryption, at-rest protection, or threat-model coverage in any documentation or README until those capabilities have been implemented and verified against their requirements.
4. Audit logging is explicitly out of current scope. If it becomes necessary in a future sprint, it must be added as a new GOV requirement — not assumed to exist as an extension of GOV-01.

---

## ADR-WEB-01: Architectural Pivot to Web Multi-User REST API

**Date:** 2026-05-06 (Sprint 6, 2026-05-06)
**Status:** Accepted
**Decision maker:** the developer (with AI architectural assistance)

### Context

Through Week 5, AstraNotes was developed as a single-user, local-first CLI tool backed by JSON file storage (JsonFileNoteRepository). The original scope explicitly stated: single-user, local-first, no network access.

In Week 6 (Class 2), the course shifted focus to web development patterns and multi-user SaaS products. The professor explicitly encouraged expanding AstraNotes scope toward a web-accessible multi-user application to make the demo more compelling and the engineering more realistic.

### Decision

Pivot AstraNotes from a local CLI tool to a web-based multi-user REST API backed by SQLite and served by FastAPI. User identity (author_id) is derived from JWT tokens. The existing domain layer (NoteService, PrivacyPolicy, AbstractNoteRepository) remains unchanged — only the delivery mechanism and storage adapter change.

### Alternatives Considered

| Alternative | Reason Rejected |
|-------------|----------------|
| Keep single-user CLI | Acceptable technically, but limits demo appeal and doesn't show web/multi-user skills |
| Django or Flask | FastAPI chosen for native async support, auto-generated OpenAPI docs, and Pydantic integration |
| PostgreSQL | SQLite chosen for Render free-tier deployment compatibility and zero-configuration setup |
| Session-based auth | JWT chosen for stateless scalability; no session storage needed |

### Architecture Changes

| Layer | Before (Week 1-5) | After (Week 6+) |
|-------|-------------------|----------------|
| Delivery | CLI (`main.py`) | FastAPI REST API (`app/`) |
| Auth | None (single-user) | JWT via PyJWT + bcrypt |
| Storage | `JsonFileNoteRepository` (JSON file) | `SqliteNoteRepository` (SQLite via SQLAlchemy Core) |
| User isolation | N/A | PrivacyPolicy enforces per-user note visibility |
| Frontend | None | Single-page HTML/JS app (`app/static/index.html`) |

### Consequences

- **Preserved:** All domain logic (NoteService, PrivacyPolicy, VersionHistory) unchanged — validates the repository pattern decision
- **Updated:** Scope assumptions (single-user → multi-user; local-first → web-accessible)
- **Added:** `author_id` field on all notes (was already in the model, now meaningful for multi-user isolation)
- **Deferred:** Version history full implementation (Sprint 8); bcrypt added in Sprint 7

---

## ADR-WEB-02: SqliteNoteRepository Implementation Strategy

**Date:** 2026-05-12 (Sprint 7, 2026-05-12)
**Status:** Accepted

### Context

With the web pivot (ADR-WEB-01), the `SqliteNoteRepository` stub needed to be implemented. Two implementation approaches were available: SQLAlchemy ORM (declarative models) or SQLAlchemy Core (direct SQL expressions).

### Decision

Use **SQLAlchemy Core** (not ORM) for `SqliteNoteRepository`.

### Rationale

- SQLAlchemy Core is simpler for this scale — no model inheritance, no session management complexity
- Direct SQL gives more control over atomic operations and transaction boundaries
- ORM's advantage (object mapping) is already provided by the `Note` dataclass — adding ORM creates a second mapping layer
- Core is sufficient: the repository pattern already abstracts storage from the domain

### Implementation Notes

- Engine created lazily (not at import time) to allow test isolation via in-memory SQLite
- `add_version_snapshot()` is a no-op (returns None) — required because NoteService.create_note/update_note calls it unconditionally; full implementation deferred to Sprint 8
- `check_same_thread=False` required for FastAPI's thread pool
- Tags stored as JSON string (TEXT column); deserialized on read

---

## ADR-PWD-01 — Note-Level bcrypt Password Protection

**Date:** 2026-05-26 (Sprint 9)
**Status:** Accepted
**Deciders:** Wentao Zhong (human lead) + Claude (AI assistant)

### Context

Account-level JWT authentication isolates notes between users, but does not protect a note if the account itself is compromised. Users wanted an optional second layer of protection for sensitive notes — a per-note password that must be provided even to the authenticated owner.

### Decision

Add an optional `note_password_hash` field (bcrypt via passlib) to the `Note` entity and SQLite `notes` table. When set, `GET /notes/{id}` and `PATCH /notes/{id}` require an `X-Note-Password` request header. The router enforces this via `_require_note_password()` before returning content:
- No header provided → HTTP 401
- Wrong password → HTTP 403
- Correct password → HTTP 200 with full note content

`NoteCreate` and `NoteUpdate` accept an optional `note_password` field that is hashed before storage and never returned in API responses.

### Alternatives Considered

| Option | Reason Rejected |
|--------|----------------|
| Encrypted note content (AES) | Adds key management complexity; out of SZ-06 scope (access-control-only decision) |
| Plaintext password comparison | Security anti-pattern; inconsistent with account password approach |
| Password-protected ZIP export | Not real-time; poor UX for individual note access |

### Consequences

- Emergency unlock endpoint required for password-forgotten recovery (see ADR-UNLOCK-01)
- `is_protected` flag added to `NoteResponse` to signal password-protected status to UI without revealing hash
- PATCH endpoint must also enforce note password before allowing edits
- Test coverage: TNA-10 (401), TNA-11 (403), TNA-12 (200) verify all three branches

---

## ADR-UNLOCK-01 — Emergency Unlock via Account Password

**Date:** 2026-05-26 (Sprint 9)
**Status:** Accepted
**Deciders:** Wentao Zhong (human lead) + Claude (AI assistant)

### Context

ADR-PWD-01 introduced note-level bcrypt passwords. bcrypt is one-way — forgotten note passwords cannot be recovered. Without a recovery mechanism, a user who forgets a note password permanently loses access to that note's content. This is an unacceptable UX outcome for a note-taking application.

### Decision

Add `POST /notes/{id}/emergency-unlock` endpoint. The request body includes the user's **account** password (`account_password`). The endpoint:
1. Verifies the account password via bcrypt comparison against the stored account hash (`verify_user_password()` in `auth.py`)
2. If correct: clears `note_password_hash` to `None` and saves the note
3. Returns the updated note (now accessible without a note password)
4. If incorrect: returns HTTP 403

The note remains accessible without a password until the user sets a new one. The UI prompts the user to set a new note password immediately after emergency unlock.

### Alternatives Considered

| Option | Reason Rejected |
|--------|----------------|
| Email-based password reset | No email infrastructure in AstraNotes v1 |
| Security question | Adds complexity; not implemented |
| Master admin reset | No admin role in current architecture |
| No recovery (accept loss) | Unacceptable UX — users lose data |

### Consequences

- `verify_user_password()` helper added to `app/routers/auth.py` (reused by emergency unlock)
- Unlock clears hash (does not recover original password — impossible with bcrypt)
- Test coverage: deferred to Week 10 security review (noted in collaboration_log.md)

---

## ADR-AUTOSAVE-01 — Auto-Save with 2-Second Debounce

**Date:** 2026-05-26 (Sprint 9)
**Status:** Accepted
**Deciders:** Wentao Zhong (human lead) + Claude (AI assistant)

### Context

User testing (informal) revealed that users frequently forgot to click the Save button after editing notes. Changes were silently lost when navigating away or closing the tab. The explicit save model is appropriate for conflict-sensitive collaborative editing but unnecessary for a single-owner note-taking application.

### Decision

Implement auto-save in the web UI: 2 seconds after the last keystroke in title, body, or tags fields, the client automatically sends a `PATCH /notes/{id}` request with the current content. No new server endpoint is required — this is a client-side UX enhancement only.

Status indicator states:
- `● Unsaved` (amber): content has changed since last save
- `⟳ Saving…` (muted): PATCH request in flight
- `✓ Saved` (green): last PATCH succeeded

Additional behaviors:
- `_isSaving` flag prevents concurrent auto-save requests
- Pending timer cancelled on note switch, editor reset, or logout
- Visibility toggle (public↔private) and password set/remove operations trigger immediate save (no debounce) to prevent state inconsistency

### Alternatives Considered

| Option | Reason Rejected |
|--------|----------------|
| Explicit save only | Poor UX; users lose data |
| Immediate save on every keystroke | Too many API calls; creates unnecessary server load and version history noise |
| Local draft with periodic sync | Adds client-side state management complexity; overkill for current scope |

### Consequences

- Version history now includes frequent auto-save snapshots (each PATCH creates an "update" snapshot)
- If server is unavailable, auto-save fails silently with `● Unsaved` indicator — data not lost in browser until navigation
- `_setSaveStatus()` utility function centralizes all status DOM updates
