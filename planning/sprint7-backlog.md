---
sprint: 7
title: "Sprint 7 — SQLite Persistence & REST API"
status: in-progress
started: 2026-05-12
agents: [Agent1-Repository, Agent2-API]
---

# Sprint 7 Backlog

## Sprint Goal

Replace in-memory JSON stubs with a real SQLite persistence layer
(`SqliteNoteRepository`) and expose fully-tested CRUD REST endpoints,
making AstraNotes production-ready for local single-user deployment.

---

## Task Table

| ID    | Task Description                                        | Agent   | Req Ref       | Status |
|-------|---------------------------------------------------------|---------|---------------|--------|
| S7-01 | Write `test_sqlite_repository.py` (13 unit tests)       | Agent1  | US-07         | ✅     |
| S7-02 | Implement `SqliteNoteRepository.create`                 | Agent1  | FR-01         | ✅     |
| S7-03 | Implement `SqliteNoteRepository.get`                    | Agent1  | FR-01         | ✅     |
| S7-04 | Implement `SqliteNoteRepository.list` (+ filter)        | Agent1  | FR-05         | ✅     |
| S7-05 | Implement `SqliteNoteRepository.update`                 | Agent1  | FR-02         | ✅     |
| S7-06 | Implement `SqliteNoteRepository.delete`                 | Agent1  | FR-03         | ✅     |
| S7-07 | `add_version_snapshot` no-op (Sprint 8 placeholder)     | Agent1  | FR-07         | ✅     |
| S7-08 | Wire `service_deps.py` with real repo + policy          | Agent1  | NFR-02        | ✅     |
| S7-09 | Extend `app/tests/conftest.py` with API test fixtures   | Agent2  | GOV-03        | [Agent2] |
| S7-10 | Remove `@pytest.mark.skip` + add REST integration tests | Agent2  | US-01~05      | [Agent2] |
| S7-11 | Implement `POST /notes/`                                | Agent2  | FR-01         | [Agent2] |
| S7-12 | Implement `GET /notes/`                                 | Agent2  | FR-05         | [Agent2] |
| S7-13 | Implement `GET /notes/{id}`                             | Agent2  | FR-01         | [Agent2] |
| S7-14 | Implement `PATCH /notes/{id}`                           | Agent2  | FR-02         | [Agent2] |
| S7-15 | Implement `DELETE /notes/{id}`                          | Agent2  | FR-03         | [Agent2] |
| S7-16 | Write Sprint 7 planning/design document                 | Agent2  | Canvas        | [Agent2] |

---

## Definition of Done (Sprint 7)

- [ ] All 13 `test_sqlite_repository.py` tests pass
- [ ] All pre-existing tests continue to pass (no regressions)
- [ ] REST endpoints return correct HTTP status codes (201, 200, 204, 404)
- [ ] `get_note_service()` uses real `SqliteNoteRepository` (not stub)
- [ ] `add_version_snapshot` does **not** raise (required by `NoteService.create_note`)
- [ ] Full pytest suite: 50+ passed, 0 failed

---

## Notes

- `SqliteNoteRepository` uses **SQLAlchemy Core** (no ORM) for minimal overhead
- In-memory SQLite (`sqlite:///:memory:`) is used in all unit tests for isolation
- `add_version_snapshot` is intentionally a no-op until Sprint 8 (version history table)
- `revert_to_version` raises `NotImplementedError` — deferred to Sprint 8
