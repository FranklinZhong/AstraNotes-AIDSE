# AstraNotes — Maintenance Plan

> **Status:** Complete — security assessment performed Week 10; dependency audit current as of May 2026.

## Overview

This plan describes how AstraNotes v1.0 will be maintained after initial deployment. It covers monitoring, bug response, dependency updates, and planned Sprint 8+ enhancements.

## Monitoring

### Health Checks

| Check | Method | Frequency | Action on Failure |
|-------|--------|-----------|------------------|
| API availability | GET /health → 200 | Every 5 min (Render built-in) | Alert; check Render logs |
| Test suite | CI pipeline on push | Every commit | Block merge; investigate failure |

### Key Metrics to Watch

- Response time: health check should respond < 500ms
- Test pass rate: must remain 84/84 (100%)
- SQLite file size: monitor for unexpected growth

### Log Locations

- **Render:** Dashboard → Service → Logs tab
- **Local:** `uvicorn` stdout

## Bug Response Process

### Severity Levels

| Level | Definition | Response Time |
|-------|-----------|---------------|
| Critical | App crashes or auth broken | Fix within 24h |
| High | CRUD operations fail | Fix within 48h |
| Medium | UI issues, minor errors | Fix within 1 week |
| Low | Cosmetic issues | Next sprint |

### Bug Fix Workflow

1. Reproduce locally with failing test
2. Write a regression test (TDD — test first)
3. Fix the bug
4. Verify all 84+ tests pass
5. Commit with descriptive message
6. Push to main (triggers CI)

## Dependency Management

### Current Dependencies and Update Policy

| Package | Current | Update Trigger |
|---------|---------|---------------|
| `fastapi` | 0.115.0 | Security patches |
| `sqlalchemy` | 2.0.35 | Minor versions quarterly |
| `pyjwt` | 2.9.0 | Security patches immediately |
| `passlib[bcrypt]` | 1.7.4 | Security patches immediately |
| `pydantic` | 2.9.2 | Minor versions quarterly |

**Policy:** Security-related packages (pyjwt, passlib) are updated immediately on CVE disclosure. All updates require passing the full test suite before deployment.

### Known Technical Debt (Sprint 7 baseline — resolved in Sprint 8+)

| Item | Location | Status |
|------|----------|--------|
| `add_version_snapshot()` is a no-op | `app/db/sqlite_repository.py` | ✅ Resolved Sprint 8 |
| Auth users stored in same SQLite file as notes | `app/routers/auth.py` | ✅ Resolved Sprint 7 |
| No password reset flow | `app/routers/auth.py` | Out of scope v1 |
| bcrypt warning (passlib/bcrypt version compat) | `requirements.txt` | Low priority |
| `datetime.utcnow()` deprecation warnings | `AstraNotes_v1/note.py` | Low priority (advisory CI only) |

## Completed Enhancements (Sprint 8-9)

| Feature | Priority | Status |
|---------|----------|--------|
| Full version history | P0 | ✅ Done Sprint 8 — `add_version_snapshot()` + API + UI |
| Note-level bcrypt password | P0 | ✅ Done Sprint 9 — TNA-10/11/12 |
| Emergency unlock | P0 | ✅ Done Sprint 9 — TNA-16/17/18 |
| Tags filtering (AND semantics) | P1 | ✅ Done Sprint 9 — TNA-09 |
| Auto-save (client-side debounce) | P1 | ✅ Done Sprint 9 |
| CI/CD pipeline (blocking + advisory) | P0 | ✅ Done Sprint 10 |

## Future Enhancements (post-course)

| Feature | Priority | Description |
|---------|----------|-------------|
| Note search | P1 | Full-text search across notes |
| Note export | P2 | Export notes as Markdown or plain text |
| Automated CVE scanning | P1 | Add Dependabot or `pip-audit` to CI |

## Data Backup (Local Development)

```bash
# Backup SQLite database
cp notes.db notes_backup_$(date +%Y%m%d).db

# Restore from backup
cp notes_backup_YYYYMMDD.db notes.db
```

## Security Maintenance

- Rotate `JWT_SECRET` quarterly (invalidates all existing sessions)
- Review `planning/threat_scope_statement.md` before each major release
- Run `pip audit` monthly for known vulnerabilities
- Review `planning/ai_code_validation_checklist.md` before merging AI-generated code

## Security Assessment (Week 10)

Performed as part of Week 10.2 release preparation. See `planning/collaboration_log.md` Week 10.2 for full details.

### Dependency Audit (May 2026)

| Package | Pinned Version | Known CVEs (May 2026) | Notes |
|---------|---------------|----------------------|-------|
| fastapi | 0.115.0 | None | Stable; ASGI framework |
| sqlalchemy | 2.0.35 | None | Core only (no ORM) |
| pyjwt | 2.9.0 | None | HS256 signing |
| passlib[bcrypt] | 1.7.4 | None | bcrypt cost ~12 rounds |
| pydantic | 2.9.2 | None | v2 API |
| uvicorn | (pinned) | None | ASGI server |

### Security Hardening Notes

| Item | Current State | Production Recommendation |
|------|--------------|--------------------------|
| bcrypt work factor | passlib default (~12) | Configurable via env var; increase to 14+ for production |
| JWT TTL | 24 hours (default) | Reduce to 1-4 hours for production |
| HTTPS enforcement | Delegated to Render | Enforce at application level (`SECURE_SSL_REDIRECT` or middleware) |
| Rate limiting | None | Add `slowapi` middleware for login endpoint |
| SQLite storage | Ephemeral on Render | Replace with PostgreSQL or Turso (managed SQLite) for production |
| Automated CVE scanning | None | Add GitHub Dependabot or `pip-audit` to CI pipeline |

### Known Technical Debt (Updated Sprint 9)

| Item | File | Priority | Notes |
|------|------|----------|-------|
| `datetime.utcnow()` deprecation | `note.py`, `json_file_note_repository.py` | Low | 189 warnings in test run; replace with `datetime.now(datetime.UTC)` |
| 6 pre-existing visibility-drift test failures | `test_note_model.py`, `test_privacy_policy.py`, `test_service.py` | Low | Document design decision (owner-only access); update or remove outdated tests |
| Emergency unlock test coverage | — | ✅ Resolved | TNA-16/17/18 added Sprint 10 |
| SQLite ephemeral storage | Render deployment | High (production) | Acceptable for demo; requires managed DB for real deployment |
