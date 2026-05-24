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

## [TODO — Week 9 Content]

> Week 9 topics: Advanced testing, test coverage analysis, Mock strategies, validation optimization.
> Scheduled: ~2026-05-27 (Week 9 Wed; Mon is Memorial Day holiday).

### Test Coverage Analysis (Week 9 Lab)
*[To be completed after Week 9 class — will add coverage report (pytest-cov) and document any new tests added to improve coverage.]*

### Mock Strategy Review (Week 9 Lab)
*[To be completed after Week 9 class — will document where mocks were used or considered in the test suite and why.]*

---

## [TODO — Week 10 Content]

> Week 10 topics: CI/CD, DevOps, MLOps basics; Security/SAST/DAST; Release preparation; Deployment; Maintenance.

### CI/CD Deployment Log (Week 10 Lab)
*[To be completed after Week 10 class — will record actual Render deployment URL, GitHub Actions CI results, and any deployment issues encountered.]*

### Security Audit Results (Week 10 Lab)
*[To be completed after Week 10 class — will supplement `planning/threat_scope_statement.md` with SAST/DAST findings if applicable.]*
