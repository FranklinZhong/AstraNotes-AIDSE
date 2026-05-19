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

## [TODO — Week 8 Content]

> The following sections will be filled in after Week 8 class (scheduled ~2026-05-18).
> Week 8 topics: Version control workflows, branching strategies, PR review, AI-assisted code review, CI/CD introduction.

### Branching and PR Strategy (Week 8 Lab)
*[To be completed after Week 8 class — will document branch naming conventions, PR template, and merge strategy adopted for this project.]*

### AI Code Review Experience (Week 8 Lab)
*[To be completed after Week 8 class — will document how AI-assisted code review was applied to AstraNotes PRs and what was found.]*

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
