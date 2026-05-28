# AstraNotes — AI Code Validation Checklist

> **Governance item:** GOV-B-02 (from Week 3.2 governance review, G-04)
> **Required before:** First Sprint 1 implementation session
> **Referenced by:** `backlog.md` GOV-B-02, `working_agreement.md` Agreement 9

This checklist must be completed for every AI-generated code block before it is merged into the AstraNotes codebase. It satisfies the Definition of Done requirement that AI-generated code is verified — not just accepted — before merge.

---

## How to Use

For each AI-generated function, class, or module:
1. Read through every item in the checklist below
2. Check each box that passes; note any failures with a short comment
3. Do not merge until all items pass or have a documented exception

---

## Checklist

### 1. Requirement Alignment

- [ ] **FR mapping:** Every method or behavior in the generated code maps to a numbered requirement (FR, NFR, or GOV). List the requirement IDs.
- [ ] **No ghost features:** The generated code does not implement functionality that has no requirement (no extra endpoints, no undocumented flags, no unrequested data transformations).
- [ ] **Scope compliance:** The code does not introduce multi-user identity, network calls, external dependencies, or encryption unless an explicit requirement permits it.
- [ ] **Body validation rule:** `create_note()` raises `ValidationError` only when `title` is empty — not when `body` is empty (FR-01: body is optional).

### 2. Interface Consistency

- [ ] **author_id / user_id sentinel:** All code passes `author_id=<JWT-derived user_id from get_current_user() dependency>`. No user registry or authentication logic is present.
- [ ] **No tags in service API:** `NoteService` methods do not expose a `tags` parameter (tags field exists on `Note` but is not surfaced in service layer per Issue 3 decision).
- [ ] **Exception types only:** No raw Python exceptions (`FileNotFoundError`, `KeyError`, `JSONDecodeError`, etc.) escape any public method. All wrapped in `AstraNotesError` hierarchy.
- [ ] **Dependency injection:** `NoteService` receives `AbstractNoteRepository`, `PrivacyPolicy`, and `VersionHistory` as constructor arguments — never instantiates them internally.

### 3. Test Coverage

- [ ] **New test added:** At least one test file updated or created covering the generated code's success path.
- [ ] **Failure path covered:** At least one test verifies the expected exception or error for an invalid input or failure condition.
- [ ] **Tests pass:** `pytest` runs green after the change (81 tests total (75 passing, 6 pre-existing visibility-drift failures tracked); run `python -m pytest -q` to verify).
- [ ] **No test mocks that hide real behavior:** `SqliteNoteRepository` is used in API integration tests (production path); `JsonFileNoteRepository` retained for domain layer unit tests only. Tests that touch storage must use real repositories backed by in-memory or temp storage, not mocks that bypass I/O.

### 4. Privacy and Governance

- [ ] **PrivacyPolicy enforced first:** Any service method that reads, updates, or deletes a note calls `PrivacyPolicy.can_*()` before calling the repository. Access is denied before any data operation.
- [ ] **No encryption claims:** No comment, docstring, or README text claims at-rest encryption unless it has been implemented and tested (SZ-06 decision: access-control-only).
- [ ] **Synthetic data only in AI prompts:** No real note content, real file paths, or real user data was submitted to the AI tool during this session.

### 5. Code Quality

- [ ] **Naming consistent with DESIGN.md:** Class names, method names, parameter names, and exception names match `planning/DESIGN.md` exactly.
- [ ] **No dead code or TODO stubs committed:** Generated scaffolding with `pass` or `raise NotImplementedError` is only acceptable in designated stub files during Sprint Zero; Sprint 1+ implementations must be complete.
- [ ] **No new third-party imports:** Only Python standard library modules imported unless a dependency has been formally recorded in `architecture_decision_log.md`.

---

## Sign-Off

After completing the checklist, record the session:

| Date | File(s) Changed | AI Tool Used | Req IDs Covered | Reviewer Sign-Off |
|------|----------------|--------------|----------------|-------------------|
| | | | | |

---

## Common Failure Patterns (from Week 5.1 audit)

| Pattern | What to Watch For |
|---------|------------------|
| Body validation regression | AI often adds `if not body` to validation; must only check `if not title` |
| Multi-user creep | AI may add `user_id` as a dynamic parameter; must always be hardcoded `"local_user"` |
| Tags parameter | AI may re-introduce `tags=[]` in service method signatures; must be absent |
| Raw exceptions | AI may not wrap `json.JSONDecodeError` — verify all I/O is in try/except with named exceptions |
| UC7/UC8 features | AI may implement `get_history()` or `revert()` as user-facing commands; internal only for Sprint 1 |

## JWT Authentication Checklist (Sprint 6+)

Added when project pivoted to web multi-user architecture (ADR-WEB-01).

- [ ] JWT token not stored in `localStorage` (use `sessionStorage` to reduce XSS risk)
- [ ] `Authorization: Bearer <token>` header format used correctly in all authenticated requests
- [ ] 401 returned for missing/invalid/expired token (not 403)
- [ ] 403 returned for authenticated user accessing another user's resource (not 401)
- [ ] `JWT_SECRET` read from environment variable, never hardcoded
- [ ] Token payload contains only `user_id` and `exp` — no sensitive data
- [ ] `get_current_user()` dependency used consistently across all protected endpoints

## Note Password Checklist (Sprint 9)

- [ ] `note_password_hash` never included in `NoteResponse` (only `is_protected` boolean)
- [ ] `X-Note-Password` header verified via bcrypt before returning private note content
- [ ] Missing password → 401, wrong password → 403, correct password → 200
- [ ] `note_password` field in `NoteCreate`/`NoteUpdate` hashed before storage, never logged
- [ ] Emergency unlock verifies account password, does not reveal original note password
