# AstraNotes — Sprint 5 Backlog (Week 6)

**Sprint:** Sprint 5 — First Implementation Slice  
**Date:** 2026-05-05 → 2026-05-13  
**Goal:** Deliver a runnable CLI App Shell with Create Note and List Notes slices; complete Sprint 6 deliverable submission.

---

## Sprint Goal

> Build and demonstrate the first two functional slices of AstraNotes — note creation and note listing — through a runnable CLI shell. Produce the Sprint 6 deliverable Lab submission document.

---

## Sprint 5 Items

| ID | Task | Requirement | Status | Notes |
|----|------|-------------|--------|-------|
| S5-01 | Create CLI App Shell (`main.py`) with main menu | FR-05 | ✅ Done | `AstraNotes/main.py` |
| S5-02 | Implement Slice 1: Create Note (FR-01, US-01) | FR-01 | ✅ Done | `cmd_create()` in main.py |
| S5-03 | Implement Slice 2: List Notes (FR-05, US-05) | FR-05 | ✅ Done | `cmd_list()` in main.py |
| S5-04 | Add StorageCorruptionError startup handler | NFR-03 | ✅ Done | main.py top-level try/except |
| S5-05 | Create `docs/` directory with `functional_spec.md` | GOV | ✅ Done | `AstraNotes/docs/` |
| S5-10 | Create sprint-test-plan.md | P2 | ✅ Done | `planning/sprint-test-plan.md` |
| S5-11 | Create sprint-test-execution.md | P2 | ✅ Done | `planning/sprint-test-execution.md` |
| S5-12 | Create executive-one-pager.md | P2 | ✅ Done | `planning/executive-one-pager.md` |
| S5-13 | Create lucid-diagrams-summary.md | P2 | ✅ Done | `planning/lucid-diagrams-summary.md` |
| S5-14 | Expand docs/functional_spec.md | P3 | ✅ Done | Full slice table + edge cases |
| S5-15 | Create docs/unit_test_plan.md | P3 | ✅ Done | Module-by-module test mapping |
| S5-16 | Create docs/feature_test_plan.md | P3 | ✅ Done | US-01–06 test scenarios |

---

## Definition of Done (applied to this Sprint)

- [x] Code changes pass all 29 existing tests
- [x] New slices manually verified end-to-end (create → list)
- [x] No new third-party dependencies introduced

---

## Sprint Velocity

- **Planned:** 17 tasks
- **Completed:** 16 tasks (S5-17 pending user action)
- **Carry-over to Sprint 6:** None (S5-17 is a user submission action)
