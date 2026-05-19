# AstraNotes — Sprint Test Plan

**Version:** 1.0  
**Date:** 2026-05-06  
**Framework:** pytest 7+

---

## Overview

This document maps each Sprint's implementation items to their intended test coverage. It serves as the test planning record required by GOV-03 (test coverage mandate in requirements baseline).

---

## Sprint 5 Test Plan (Week 6 — First Implementation Slice)

### Module: `note.py`

| Test ID | Scenario | Requirement | File |
|---------|----------|-------------|------|
| TN-01 | Create Note with valid title and body | FR-01 | `test_note_model.py` |
| TN-02 | Create Note with empty title → ValidationError | FR-01 | `test_note_model.py` |
| TN-03 | Create Note with empty body (valid — body is optional) | FR-01 | `test_note_model.py` |
| TN-04 | patch() updates title and increments version | FR-02 | `test_note_model.py` |
| TN-05 | patch() with invalid title → ValidationError | FR-02 | `test_note_model.py` |
| TN-06 | Note.from_dict / to_dict round-trip | FR-05 | `test_note_model.py` |

### Module: `repositories/json_file_note_repository.py`

| Test ID | Scenario | Requirement | File |
|---------|----------|-------------|------|
| TR-01 | create() persists note to JSON | FR-05 | `test_repository.py` |
| TR-02 | get() retrieves persisted note by ID | FR-05 | `test_repository.py` |
| TR-03 | list() returns all stored notes | FR-05 | `test_repository.py` |
| TR-04 | update() overwrites existing note | FR-02 | `test_repository.py` |
| TR-05 | delete() removes note; returns True | FR-03 | `test_repository.py` |
| TR-06 | delete() on non-existent ID → returns False (no exception) | FR-03 | `test_repository.py` |
| TR-07 | Load from missing file → empty collection (no crash) | FR-05 | `test_repository.py` |
| TR-08 | Load from corrupted JSON → StorageCorruptionError | NFR-03 | `test_repository.py` |
| TR-09 | Atomic write: temp file not left behind on success | NFR-02 | `test_repository.py` |

### Module: `services/note_service.py`

| Test ID | Scenario | Requirement | File |
|---------|----------|-------------|------|
| TS-01 | create_note() returns Note with correct fields | FR-01 | `test_service.py` |
| TS-02 | create_note() empty title → ValidationError | FR-01 | `test_service.py` |
| TS-03 | get_note() returns correct note | FR-05 | `test_service.py` |
| TS-04 | get_note() non-existent ID → NoteNotFoundError | FR-05 | `test_service.py` |
| TS-05 | list_notes() filters private notes for wrong user | GOV-01 | `test_service.py` |
| TS-06 | update_note() patches fields, increments version | FR-02 | `test_service.py` |
| TS-07 | delete_note() removes note | FR-03 | `test_service.py` |

### Module: `policies/privacy_policy.py`

| Test ID | Scenario | Requirement | File |
|---------|----------|-------------|------|
| TP-01 | Owner can read own private note | FR-04, GOV-01 | `test_privacy_policy.py` |
| TP-02 | Non-owner cannot read private note → AccessDeniedError | GOV-01 | `test_privacy_policy.py` |
| TP-03 | Any user can read public note | FR-04 | `test_privacy_policy.py` |
| TP-04 | Non-owner cannot update private note → AccessDeniedError | GOV-01 | `test_privacy_policy.py` |
| TP-05 | Non-owner cannot delete private note → AccessDeniedError | GOV-01 | `test_privacy_policy.py` |

### Module: `history/version_history.py`

| Test ID | Scenario | Requirement | File |
|---------|----------|-------------|------|
| TV-01 | add_entry() records create operation | FR-06 | `test_version_history.py` |
| TV-02 | add_entry() records update with incremented version | FR-06 | `test_version_history.py` |
| TV-03 | revert() restores earlier version | FR-06 | `test_version_history.py` |
| TV-04 | revert() to non-existent version → NoteNotFoundError | FR-06 | `test_version_history.py` |

---

## Sprint 6 Test Plan (Week 7 — Test Suite Expansion, Planned)

| Test ID | Scenario | Requirement |
|---------|----------|-------------|
| TF-01 | End-to-end: create → list → verify note appears | FR-01, FR-05 |
| TF-02 | End-to-end: create → update → get → verify updated | FR-02 |
| TF-03 | End-to-end: create → delete → list → verify gone | FR-03 |
| TF-04 | Persistence: create → restart → list → verify note survives | FR-05 |
| TF-05 | Edge: 500 notes stored → list performance acceptable | NFR-01 |

---

## Test Execution Summary (as of 2026-05-05)

```
pytest AstraNotes_v1/tests/ -v
29 passed in < 1s
```

All 29 tests pass. No failures. No skips.
