# AstraNotes — Sprint Test Execution Record

**Version:** 1.0  
**Date:** 2026-05-06  

---

## Sprint 5 Execution (2026-05-05)

### Environment

```
Python:  3.12.x
OS:      macOS Darwin 25.3.0
Tool:    pytest 7+
Command: python -m pytest AstraNotes_v1/tests/ -v
```

### Results

```
AstraNotes_v1/tests/test_note_model.py       ........ (8 tests)   PASSED
AstraNotes_v1/tests/test_repository.py       ....... (7 tests)    PASSED
AstraNotes_v1/tests/test_service.py          ....... (7 tests)    PASSED
AstraNotes_v1/tests/test_privacy_policy.py   ..... (5 tests)      PASSED
AstraNotes_v1/tests/test_version_history.py  .... (4 tests)       PASSED

========== 29 passed in 0.XXs ==========
```

**All 29 tests: PASS**

### Bug Fixed During Sprint 5

| Bug | Symptom | Root Cause | Fix |
|-----|---------|-----------|-----|
| FR-01 body regression | `body=""` raised ValidationError | `note.py` had `not self.body` guard that treated empty string as invalid | Removed guard; body is optional (comment added: `FR-01: body is optional`) |
| note_service.py body | `create_note()` required body | Default parameter was missing | Changed to `body: str = ""` |

---

## Manual Smoke Test (CLI Shell, 2026-05-06)

```
$ cd AstraNotes/
$ python main.py

  ╔══════════════════════════════════╗
  ║        AstraNotes  v1            ║
  ║  1  Create note                  ║
  ║  2  List notes                   ║
  ║  0  Exit                         ║
  ╚══════════════════════════════════╝

  Choice: 1

  Title: Sprint 5 Test Note
  Body  (Enter to skip): Testing CLI shell

  Created [d557e358] "Sprint 5 Test Note"

  Choice: 2

  ID          TITLE                           VER   UPDATED
  ──────────────────────────────────────────────────────────
  [P] d557e358  Sprint 5 Test Note              v1    2026-05-06T...

  Choice: 0
  Goodbye.
```

**Result:** PASS — Create Note and List Notes both work correctly.

---

## Sprint 6 Execution (Planned — Week 7)

| Test | Target | Expected |
|------|--------|----------|
| End-to-end create → list | TF-01 | Notes survive across sessions |
| End-to-end edit flow | TF-02 | version increments; updated_at changes |
| End-to-end delete flow | TF-03 | note absent from list after delete |
| Persistence restart test | TF-04 | ~/.astranotes/notes.json survives restart |
| 500-note performance | TF-05 | list_notes() < 1s |
