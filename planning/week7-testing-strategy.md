# AstraNotes Week 7.2 Testing Strategy

## Features Selected for TDD

Feature 1: Create Note (FR-01, US-01) — POST /notes/ → 201
Feature 2: List Notes (FR-05, US-05) — GET /notes/ → 200 with user isolation

Reason: These are the two most foundational behaviors. Create enables all other tests;
List demonstrates user isolation which is critical for the web multi-user architecture.

## Test Classification

| Test File | Count | Level | Description |
|-----------|-------|-------|-------------|
| test_sqlite_repository.py | 13 | Unit | Repository in isolation, in-memory SQLite |
| test_notes_api.py | 9 | Integration | HTTP+service+repository via FastAPI TestClient |
| AstraNotes_v1/tests/ | 36 | Unit | Domain model, service, policy (existing) |

## Test Timing (Development Flow Alignment)

- test_sqlite_repository.py: written at Step A1-1, before sqlite_repository.py existed
- test_notes_api.py: written at Step A2-2, before notes.py was implemented
- Both test files ran RED first, then implementation made them GREEN (TDD gate confirmed)

## Requirements Traceability

| Test | FR/US | What It Validates |
|------|-------|-------------------|
| test_create_returns_same_note | FR-01 | Repository creates and returns note |
| test_us01_create_note | FR-01 / US-01 | API creates note, returns 201 |
| test_list_empty | FR-05 / US-05 | Empty list before any notes |
| test_list_only_returns_own_notes | FR-05 / US-05 | User isolation via PrivacyPolicy |
| test_get_note_by_id | FR-01 | Single note retrieval |
| test_get_nonexistent_returns_404 | FR-01 | Error boundary handling |
| test_update_note_increments_version | FR-02 / US-02 | Version tracking on update |
| test_delete_note_returns_204 | FR-03 / US-03 | Soft boundary: note gone after delete |

## Fixture Design: Named In-Memory SQLite

`reset_note_service` fixture uses a UUID-named SQLite URI with `mode=memory&cache=shared`
instead of the default `sqlite:///:memory:`. This is required because SQLAlchemy opens a
new connection per query — with a plain `:memory:` URL each connection gets an empty
database, causing "no such table" errors. The named shared cache ensures all connections
within a test see the same in-memory database. The UUID suffix guarantees test isolation
(each test gets its own named DB that disappears when the process ends).

## Scripted Automation vs AI-Native Testing

**Scripted (pytest):** Deterministic, repeatable, CI-ready. Used for all tests here.
Ideal for verifying exact contracts, regression checks, and boundary conditions.

**AI-native:** Used to generate initial test scaffolding and suggest edge cases.
Claude drafted the test structure; human review removed redundant tests and verified
assertion logic against the actual domain model behavior.

## AI Use Log

**Claude generated:** test fixture pattern (named shared-cache in-memory SQLite per test),
dependency_overrides pattern for conftest, router implementation with proper exception mapping

**Kept as-is:** SQLAlchemy Core table definition, fixture isolation strategy, NoteService
constructor signature (repository + policy)

**Changed:** In-memory SQLite URL from `sqlite:///:memory:` to named URI with
`mode=memory&cache=shared` — needed because SQLAlchemy opens a new connection per
operation, which loses the in-memory schema. Named shared cache solves this without
requiring StaticPool.

**Rejected:** SQLAlchemy ORM Session (replaced with Core for simplicity), module-level
engine singleton (breaks test isolation)
