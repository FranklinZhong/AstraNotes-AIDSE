# Sprint 7 — Test Execution Record

## Environment
- Python: 3.13.5
- pytest: 8.3.4
- sqlalchemy: 2.0.x
- Run: `python -m pytest -q` from AstraNotes/

## TDD Gate Log

| Step | Action | Result |
|------|--------|--------|
| A1-1 | Write test_sqlite_repository.py (13 tests) | 13 FAIL (NotImplementedError) ✅ gate confirmed |
| A1-2 | Implement SqliteNoteRepository | 13 PASS |
| A2-1 | Extend conftest.py with reset_note_service fixture | fixture added |
| A2-2 | Update test_notes_api.py (remove 4 skips + 4 new tests) | 8 FAIL (501 responses) ✅ gate confirmed |
| A2-3 | Implement notes.py router (full CRUD with exception mapping) | 8 PASS |
| A2-4 | Fix conftest SQLite isolation (named shared-cache URI) | 9 PASS (incl. pydantic test) |

## Before Sprint 7
37 passed, 4 skipped, 0 failed

## After Sprint 7
```
58 passed, 0 skipped, 0 failed
```

Breakdown:
- AstraNotes_v1/tests/ (domain): 36 passed
- app/tests/test_sqlite_repository.py: 13 passed
- app/tests/test_notes_api.py: 9 passed (1 existing pydantic + 4 de-skipped + 4 new)

## Test-to-Requirement Mapping (Sprint 7 additions)

| Test ID | Test Name | Level | FR/US |
|---------|-----------|-------|-------|
| TSQ-01~13 | SqliteNoteRepository unit tests | Unit | FR-01~07 |
| TNA-00 | test_us01_create_note_with_empty_title_returns_422 | Integration | FR-01 (pydantic) |
| TNA-US01 | test_us01_create_note_with_valid_title_returns_201 | Integration | FR-01/US-01 |
| TNA-US05 | test_us05_list_notes_returns_empty_list_initially | Integration | FR-05/US-05 |
| TNA-US02 | test_us02_update_note_increments_version | Integration | FR-02/US-02 |
| TNA-US03 | test_us03_delete_note_returns_204 | Integration | FR-03/US-03 |
| TNA-01 | test_create_note_response_has_author_id | Integration | FR-01/US-01 |
| TNA-02 | test_get_note_by_id_returns_200 | Integration | FR-01/US-01 |
| TNA-03 | test_get_nonexistent_note_returns_404 | Integration | FR-01 |
| TNA-04 | test_list_only_returns_own_notes | Integration | FR-05/US-05 |

## Key Technical Decision

**Named shared-cache SQLite URI for test isolation:**

Problem: `sqlite:///:memory:` gives a fresh empty database per SQLAlchemy connection.
Since CRUD operations each open a new connection via `with engine.connect()`, the table
created during `__init__` is invisible to subsequent queries → `no such table: notes`.

Solution: Use SQLite URI with `mode=memory&cache=shared` and a UUID-based name per test:
```
sqlite+pysqlite:///file:test_{uuid}?mode=memory&cache=shared&uri=true
```

This keeps all connections within a test pointing to the same named in-memory DB while
guaranteeing isolation between tests (each UUID is unique and the memory is released
when the process ends).
