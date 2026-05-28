# AstraNotes — Collaboration and Version Control Log


## Overview

This log documents the version control workflow, branching strategy, and AI-human collaboration process used throughout AstraNotes development.

## Repository Information

- **Platform:** GitHub
- **Branch strategy:** Single `main` branch (student solo project)
- **Commit convention:** Descriptive messages with sprint/week context

## AI-Native Development Workflow

AstraNotes was built using an AI-native workflow where Claude (Claude) acted as a collaborative pair-programmer across all development phases.

### Roles

| Role | Human (Project Lead) | AI (Claude) |
|------|---------------------|-------------|
| Requirements | Final approval | Draft + ambiguity detection |
| Architecture | Decision authority | Options + tradeoff analysis |
| Implementation | Code review + approval | Draft implementation |
| Testing | Test design approval | Test scaffold generation |
| Documentation | Final content review | Draft generation |

### AI Output Review Process (GOV-04 Compliance)

Before accepting any AI-generated code or content:
1. Read and understand the output (not just accept blindly)
2. Check against requirements (TRACEABILITY.md reference)
3. Run tests to verify behavior
4. Document what was kept, changed, or rejected (see `planning/week7-testing-strategy.md` for example)

## Sprint Collaboration Log

| Sprint | Week | Key AI Assistance | Human Judgment Applied |
|--------|------|-------------------|----------------------|
| Sprint Zero | Week 2 | Generated initial backlog and Sprint Zero plan | Prioritized removed overcomplicated items |
| Sprint 1-5 | Week 4-6 | Implemented all domain layer (NoteService, repositories, policies) | Reviewed test coverage; fixed body validation bug (FR-01) |
| Sprint 6 | Week 6 | Generated FastAPI scaffold + FastAPI app structure | Decided on FastAPI over Flask; chose SQLite over PostgreSQL for free-tier deploy |
| Sprint 7 | Week 7 | Generated SqliteNoteRepository + notes API TDD tests | Rejected ORM approach; fixed in-memory SQLite test isolation issue (StaticPool) |
| Sprint 8 (1.0) | Week 11 | Generated web UI + auth persistence | Reviewed all API endpoint handling; verified end-to-end smoke test |

## Code Review Summary

### What Was Accepted Without Change
- Abstract repository interface (`AbstractNoteRepository`) — clean, minimal
- JWT token creation/verification (`app/auth/jwt.py`) — straightforward HS256
- Pydantic schemas (`app/schemas/`) — match domain model precisely

### What Was Changed After AI Generation
- `note.py` body validation: AI initially made body required; corrected to optional (FR-01)
- `SqliteNoteRepository` test isolation: AI used `sqlite:///:memory:` which creates new DB per connection; changed to `StaticPool` for consistent in-memory DB
- Auth engine initialization: AI created module-level engine (pollutes tests); changed to lazy init

### What Was Rejected
- SQLAlchemy ORM (replaced with Core — simpler at this scale)
- bcrypt password hashing in Sprint 7 (deferred to Sprint 8 to avoid breaking auth tests)
- Module-level engine singleton in auth.py (breaks test isolation)

## Refactoring History

| Date | Refactoring | Reason |
|------|-------------|--------|
| 2026-05-05 | Fixed body=None bug in Note | FR-01 violation found via test |
| 2026-05-06 | Replaced JSON file storage with FastAPI scaffold | Web multi-user pivot (ADR-WEB-01) |
| 2026-05-12 | Replaced in-memory `_users` dict with SQLite + bcrypt | Production readiness for 1.0 |
| 2026-05-12 | Moved health check from `/` to `/health` | Free `/` for web UI serving |

---

## Week 8 — Collaborative Git Workflow (2026-05-18)

> Week 8.1 topic: Version control, branching, PR summaries, AI-assisted review, merge conflict discipline.
> Week 8.2: Midterm 2 + CI/CD automation mindset introduction.

### Branching and PR Strategy

Starting state: `main` branch, 58 tests passing, Sprint 7 fully merged.

Two independent branches were created to simulate parallel development streams:

| Branch | Purpose | Requirement |
|--------|---------|-------------|
| `feature/search-filter` | Expose `tags` field in API schemas; add `?tags=` query filtering to `GET /notes/` | US-03, FR-03 |
| `test/title-validation` | Fix whitespace-only title gap in `Note.__post_init__`; add 3 domain tests | FR-01, US-01 |

**Workflow followed:**

1. Pulled latest `main` — confirmed 58 tests passing
2. Created `feature/search-filter` from `main`; added tags to `NoteCreate`, `NoteUpdate`, `NoteResponse` schemas and `?tags=` filtering to `GET /notes/`; all 9 API tests passed; committed and pushed
3. Switched back to `main`; created `test/title-validation`
4. Discovered real domain validation gap: `Note("   ")` was accepted by `Note.__post_init__` (which only checked `not self.title`) but rejected by the API-layer `NoteCreate` validator (which used `.strip()`); fixed `__post_init__` to use `.strip()` check; added 3 new tests
5. 61 tests passing locally — committed and pushed

**CI Failure and Root Cause:**

Both PRs triggered GitHub Actions (Python 3.11 + 3.12). Both failed with:

```
FAILED app/tests/test_auth.py::test_notes_without_token_returns_401
assert resp.status_code == 401
       403 == 401
```

Root cause: `HTTPBearer()` (default `auto_error=True`) intercepts missing `Authorization` headers before the route handler and raises HTTP 403, not 401. This was invisible locally because the local environment ran FastAPI 0.136 while CI ran FastAPI 0.115, which has different behavior.

Resolution: Changed to `HTTPBearer(auto_error=False)` in `app/auth/dependencies.py`. This passes `None` as credentials, letting the handler raise 401 explicitly — semantically correct (401 = not authenticated, 403 = authenticated but not authorized).

```python
# Before
_bearer = HTTPBearer()

# After
_bearer = HTTPBearer(auto_error=False)
# handler explicitly raises HTTPException(status_code=401) when credentials is None
```

CI passed on both Python 3.11 and 3.12 after this fix. Both PRs merged into `main`. Final state: 61 tests passing.

**PR summary discipline:**

Each PR included: Change, Why, Risks, and Evidence sections (per Week 8.1 class format). `test/title-validation` was approved on first review. `feature/search-filter` received a `Request changes` decision — tag matching semantics (case-sensitive, AND logic) needed to be documented in the endpoint docstring before merge. One-line docstring update unblocked it.

### AI Code Review Experience

Five AI prompts were used across the two PRs; all produced useful output.

| Prompt | What AI Was Asked | Outcome |
|--------|------------------|---------|
| PR Summary Draft | Draft `feature/search-filter` PR with Change/Why/Risks/Evidence | Accepted with minor edits — used as PR description base |
| Review Assistant | Generate 4 review questions (architecture, edge cases, backward compat, test coverage) | 3 of 4 questions surfaced real issues; Q4 (missing filter test) added to review comment |
| Bug Detection | Check for validation inconsistencies between `Note` domain class and `NoteCreate` schema | Accepted entirely — directly identified the whitespace-title gap that became the `test/title-validation` branch |
| Merge Readiness Check | Assess whether `feature/search-filter` PR is ready to merge | Accepted — identified missing docstring as blocker; drove the `Request changes` decision |
| CI Failure Diagnosis | Explain 403 vs 401 behavior difference with FastAPI `HTTPBearer` | Accepted — applied fix directly to `app/auth/dependencies.py` |

**One AI suggestion rejected:**

AI suggested making tag filtering case-insensitive by default (`tag.lower()`). Rejected because: tag canonicalization belongs at creation time, not at query time; the domain model stores tags as-is and query behavior should be consistent with storage behavior. Kept case-sensitive with a note in the PR description.

**Key boundary observed:**

AI review surfaced the right questions but did not make merge decisions. The `Request changes` judgment on `feature/search-filter` and the `Approve` on `test/title-validation` were human decisions based on scope, risk, and requirement linkage. AI comments were treated as a checklist to evaluate, not as approval.

### Refactoring Decisions

- `feature/search-filter` kept filtering logic in the router (`notes.py`) rather than moving it into `NoteService`. Intentional: the service layer already accepts a `filters` dict, so a future sprint can push filtering down if needed. Moving it now would change tested service contracts for no current benefit.
- `test/title-validation` was a one-line tightening of an existing guard in `Note.__post_init__`. No structural refactoring needed — the fix belongs where the constraint originates.

### CI/CD Mindset (Week 8.2 Transition)

Week 8.2 introduced the transition from "build and review" to "build, review, and automate." Key principle from class: repeated quality checks should become a reliable workflow habit, not a memory exercise.

The existing GitHub Actions CI (`ci.yml`) already gates on: `pytest` passing on Python 3.11 and 3.12 on every push to `main` and every PR. The CI failure in this sprint (HTTPBearer 403/401) demonstrated exactly why this gate matters — the bug was real, caught before merge, and required a semantically correct fix rather than a workaround.

Next step (Week 9/10): evaluate adding `pytest-cov` to the CI pipeline to track test coverage trends.

---

## Week 9 — Prompt Bank Analysis and Test Quality Improvement (2026-05-27)

> Week 9 topics: Advanced testing, test coverage analysis, mock strategies, validation optimization.
> Lab exercise: Apply the professor's 7-prompt Prompt Bank to the AstraNotes test suite; identify and fix weak tests and behavioral coverage gaps.

### Prompt Bank Exercise

The 7 prompts were applied to the existing test suite (70 tests, Sprint 8 state). Each prompt guided a different angle of test quality analysis.

#### Findings and Actions

| Prompt | Finding | Action |
|--------|---------|--------|
| 1 — Test Quality Critique | TVH-02 used `versions[1]` (positional index) — same brittle assumption as the pre-fix TSQ-14 | **Fixed**: replaced with `by_version = {v["version"]: v ...}` keyed assertion |
| 2 — Coverage Gap | `?tags=a&tags=b` AND semantics (`set.issubset()`) completely untested — changing to OR logic would be undetected | **Added TNA-09**: verifies AND semantics by confirming a one-tag note is excluded from a two-tag filter |
| 2 — Coverage Gap | `_require_note_password()` has 3 branches (missing pw → 401, wrong pw → 403, correct pw → 200); none tested via HTTP | **Added TNA-10/11/12**: tests all three branches |
| 2 — Coverage Gap | `AccessDeniedError → 403` path untested for both PATCH and DELETE endpoints | **Added TNA-13/14**: registers a second user and attempts non-owner PATCH/DELETE |
| 3 — Mocking Critique | Zero mocking in integration tests; in-memory SQLite isolation in unit tests — both appropriate | No change — assessment confirmed existing approach is correct |
| 4 — Flaky Test Repair | TVH-02 positional index creates latent flakiness risk | Fixed (see Prompt 1 fix above) |
| 5 — Stronger Assertion | `_require_note_password` success path never tested | Fixed via TNA-12 |
| 6 — Validation Refinement | `str.strip()` in Pydantic validator and domain model does not handle U+00A0 (non-breaking space) — a title of `" "` passes validation silently | **Fixed validator** in `app/schemas/note.py` and `AstraNotes_v1/note.py` to use `re.search(r'\S', v)`; **Added TNA-15** |
| 7 — Test Improvement Log | Lab9_WentaoZhong.docx records the full narrative from this session | See `Week9/HW9/Lab9_WentaoZhong.docx` |

#### AI Suggestions Accepted

- TVH-02 positional index fix: verified by reading `history.py` — the API returns a list sorted oldest-first by implementation detail, not by requirement. Keyed assertion is requirement-aligned.
- AND tags gap (TNA-09): verified by reading `notes.py:59` — `tag_set.issubset()` is AND logic. A missing test means changing it to `any()` (OR logic) would go undetected.
- Note password branches (TNA-10/11/12): verified by reading `notes.py:16-27` — three distinct code branches, all reachable, none previously exercised.
- PATCH/DELETE non-owner 403 (TNA-13/14): verified by reading `PrivacyPolicy.can_update()` and `can_delete()` — both raise `AccessDeniedError`, mapped to 403 in router.
- Unicode validation fix (TNA-15): verified with Python REPL — `" ".strip()` returns `" "` (non-empty), confirming the bug. `re.search(r'\S', " ")` correctly returns `None`.

#### AI Suggestions Rejected

- Add `test_create_note_response_validates_uuid_format`: UUID format is already implicitly tested — if `note.id` were non-UUID, multiple downstream ID lookups would fail. Adding a `uuid.UUID(data["id"])` assertion is useful but not priority for this sprint.
- Add tests for the `emergency-unlock` endpoint: the endpoint is real but out of scope for the Week 9 test quality lab. Coverage note recorded; deferred to Week 10 security review.
- Add a PATCH version of the note password test (TNA-10 style): PATCH also calls `_require_note_password`, but this code path is already covered because PATCH fetches the note via `service.get_note()` which goes through the same function. Adding a redundant PATCH-specific password test would add complexity without covering new behavior.

### Test Count After Week 9

Starting count: **74 tests** (Sprint 8 + HW9 state: 68 passed, 6 pre-existing failures)
- Fixed: TVH-02 (assertion improvement, no new test)
- Added: TNA-09, TNA-10, TNA-11, TNA-12, TNA-13, TNA-14, TNA-15 (7 new tests)

**Final count: 81 tests, 75 passed, 6 pre-existing failures**

> Note: The 6 pre-existing failures (`test_note_creation_defaults`, `test_note_default_visibility_is_private`, `test_privacy_can_read_public`, `test_privacy_can_read_none_user_public_note`, `test_service_list_hides_private_from_other_user`, `test_us01_create_note_with_valid_title_returns_201`) reflect a design drift: those tests were written when default visibility was "private" and public notes were visible to other users. The current implementation sets default visibility to "public" at the schema layer and enforces owner-only access in `PrivacyPolicy` for all notes. These failures are tracked and not caused by Week 9 changes.

### Coverage Improvement Summary

| Area | Before Week 9 | After Week 9 |
|------|--------------|-------------|
| Tags AND semantics | 0 tests | TNA-09 |
| Note password branches | 0 tests (all 3 branches) | TNA-10, TNA-11, TNA-12 |
| PATCH by non-owner → 403 | 0 tests | TNA-13 |
| DELETE by non-owner → 403 | 0 tests | TNA-14 |
| Unicode whitespace title | 0 tests (real bug) | TNA-15 + validator fix |
| TVH-02 ordering robustness | Brittle positional assertion | Version-number keyed assertion |

---

## Week 10 — CI/CD, Security, Release, and Maintenance (2026-06-01 / 2026-06-03)

> Week 10.1 (June 1): CI/CD, DevOps, MLOps basics, operational risk
> Week 10.2 (June 3): SAST/DAST, security, release preparation, deployment, maintenance strategy

---

### Week 10.1 — CI/CD and Operational Risk Assessment (2026-06-01)

#### CI/CD Pipeline Status

The GitHub Actions CI pipeline (`ci.yml`) was implemented during Sprint 8 and has been operational since. Status as of final submission:

| Check | Configuration | Status |
|-------|--------------|--------|
| Python versions | 3.11 + 3.12 (matrix) | ✅ Passing |
| Test runner | `pytest -q --tb=short` | ✅ 75 passing |
| Artifact upload | Test results, 7-day retention | ✅ Configured |
| Trigger | Push to `main`; PR to `main` | ✅ Active |

**CD configuration (Render):**
- Platform: Render Web Service (free tier)
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variable: `JWT_SECRET` (set in Render dashboard)
- Database: SQLite file on ephemeral disk (acceptable for demo; data lost on redeploy)

**AI role in CI/CD:**
- CI configuration generated by AI in Sprint 8; human verified trigger conditions and Python version matrix
- CI caught the real HTTPBearer 401/403 bug (Python 3.11 vs 3.12 FastAPI behavior difference) — validated the value of the CI gate

#### Operational Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| SQLite data loss on Render redeploy | High (free tier) | Medium (demo data only) | Document in README; demo video uses fresh data |
| Render free-tier cold start (~30s) | High | Low | Start demo after warming up; note in video |
| JWT_SECRET change invalidates all tokens | Low | High | Coordinated logout + re-login required; document in maintenance_plan.md |
| Python `datetime.utcnow()` deprecation (3.12+) | Certain | Low | 189 tracked warnings; non-blocking; tracked for future sprint |
| Dependency CVE | Low | Medium | Dependencies pinned in requirements.txt; manual review performed Week 10 |

**MLOps assessment:** AstraNotes v1.0 contains no ML/AI model components. MLOps concerns (model drift, retraining pipelines, feature stores) are not applicable to this version. Noted as future consideration if NLP-based search (semantic note retrieval) is added in a future sprint.

---

### Week 10.2 — Security Audit and Release (2026-06-03)

#### SAST Assessment (Manual Code Review)

Performed manual static analysis equivalent to running `bandit` on the codebase:

| Security Check | Finding | Status |
|----------------|---------|--------|
| Raw SQL string interpolation | None found — SQLAlchemy parameterized queries throughout `sqlite_repository.py` | ✅ Pass |
| Hardcoded secrets | `JWT_SECRET` read from `os.environ` via `config.py`; not committed | ✅ Pass |
| Password in API response | `note_password_hash` never in `NoteResponse`; account password never returned | ✅ Pass |
| `eval()` / `exec()` | None found in application code | ✅ Pass |
| SQLite file path | Configurable via `DATABASE_URL` env var; not hardcoded | ✅ Pass |
| bcrypt work factor | passlib default (~12 rounds); not configurable via env var | ⚠️ Acceptable for demo |
| HTTPS enforcement | Delegated to Render platform; not enforced at application level | ⚠️ Acceptable for demo |

**AI role in SAST:**
- AI generated the checklist of security checks to perform
- Human verified each finding by reading the actual source code (`config.py`, `sqlite_repository.py`, `auth.py`, `notes.py`)
- No automated scanning tool used; all findings are based on manual code reading

#### DAST Assessment (Manual API Testing)

Behavioral security testing against running application:

| Test Scenario | Method | Result |
|---------------|--------|--------|
| Auth bypass: no token | GET /notes/ without Authorization | 401 ✅ (test_notes_without_token_returns_401) |
| Auth bypass: invalid token | GET /notes/ with `Bearer invalid` | 401 ✅ |
| Cross-user note access (GET) | User B reads User A's private note | 403 ✅ (PrivacyPolicy) |
| Cross-user PATCH | User B PATCHes User A's note | 403 ✅ (TNA-13) |
| Cross-user DELETE | User B DELETEs User A's note | 403 ✅ (TNA-14) |
| Note password bypass (missing) | GET private note without X-Note-Password | 401 ✅ (TNA-10) |
| Note password bypass (wrong) | GET private note with wrong X-Note-Password | 403 ✅ (TNA-11) |
| SQL injection (title field) | POST /notes/ with `title: "'; DROP TABLE notes; --"` | 201 — stored as literal string; no SQL execution ✅ |

**AI role in DAST:**
- AI suggested the test scenario list
- Human executed each scenario against the running application and verified responses
- SQL injection test result confirmed by checking SQLAlchemy query generation (parameterized)

#### Release Checklist

| Item | Status |
|------|--------|
| README updated with correct API reference and test counts | ✅ |
| All SDLC planning artifacts present in `planning/` | ✅ |
| CI passing on Python 3.11 and 3.12 | ✅ |
| GitHub repository public and accessible | ✅ |
| Architecture Decision Log covers all major pivots (ADR-WEB-01, ADR-WEB-02, ADR-PWD-01, ADR-UNLOCK-01, ADR-AUTOSAVE-01) | ✅ |
| Traceability matrix updated through Sprint 9 | ✅ |
| Threat scope statement updated for web architecture | ✅ |
| Sprint log covers Sprint 0 through Sprint 9 | ✅ |
| Demo video recorded | ⏳ Weekend of June 1-2 |
| Render deployment live | ⏳ Weekend of June 1-2 |
| Canvas submission (GitHub link + video) | ⏳ June 3, before 11:59pm |

#### Maintenance Notes

See `planning/maintenance_plan.md` for full maintenance strategy. Key decisions:
- SQLite acceptable for demo; production would require PostgreSQL or managed SQLite (Turso)
- Dependency versions pinned; no known CVEs in current dependency set (FastAPI 0.115, SQLAlchemy 2.0, PyJWT 2.9, passlib 1.7) as of May 2026
- `/health` endpoint available for uptime monitoring integration

**Key boundary observed (AI vs human in Week 10):**
AI generated the security checklist templates and operational risk categories based on course syllabus topics. Human verified all claims against actual source code. No security assessment was accepted without corresponding manual code verification. The SAST and DAST results above reflect actual code behavior, not AI-generated speculation.
