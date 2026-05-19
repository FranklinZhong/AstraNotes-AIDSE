# AstraNotes — Requirements-to-UML Traceability Matrix

> **Source:** Requirements-to-UML Traceability Audit (2026-04-27)
> **Requirements Baseline:** Refined requirements baseline (2026-04-13)
> **UML Package:** PlantUML diagrams (Phase 1) + Draw.io diagrams (Phase 2)
> **Status:** Pre-Sprint 1 validation — gaps identified, resolution required

---

## Purpose

This matrix verifies whether the Week 4 UML design package actually supports the refined requirements from Week 3. It was produced as part of a systematic cross-week consistency audit before Sprint 1 implementation begins. Copilot should consult this document to understand which design elements are well-specified and which require clarification before implementing a feature.

---

## Requirements Selected (7 of 13 — highest priority for Sprint 1)

| ID | Requirement Summary | Full Text (see planning/requirements.md) |
|----|--------------------|-----------------------------------------|
| FR-01 | Create note: UUID, non-empty title, **optional body**, ValidationError on empty title | Refined Baseline, FR-01 |
| FR-02 | Edit note: update timestamp, NoteNotFoundError if not found | Refined Baseline, FR-02 |
| FR-04 | Privacy flag (visibility field): hide body in list, service-layer enforcement | Refined Baseline, FR-04 |
| FR-05 | Persist on create/edit/delete: atomic write, StorageIOError on failure | Refined Baseline, FR-05 |
| NFR-02 | Module separation: domain / storage / policy independently testable, swappable backend | Refined Baseline, NFR-02 |
| NFR-03 | No unhandled exceptions: all errors as domain exception types | Refined Baseline, NFR-03 |
| GOV-01 | PrivacyPolicy enforces access control at service layer; AccessDeniedError | Refined Baseline, GOV-01 |

---

## Traceability Matrix

| Req ID | Requirement Summary | Class/Object Evidence | Use Case/Activity Evidence | Deployment Evidence | Status | Gap Note |
|--------|--------------------|-----------------------|---------------------------|--------------------|---------|---------| 
| **FR-01** | Create note with UUID; body is optional; ValidationError on empty title only | Note, NoteService, AbstractNoteRepository, JsonFileNoteRepository | Create Note use case; Create Note activity (full swimlane: User→NoteService→PrivacyPolicy→JsonFileNoteRepository→VersionHistory) | Local filesystem write path shown in deployment diagram | **Partially Traced** | ⚠ CONTRADICTION: Activity diagram (line 13) raises ValidationError when `title empty OR body empty`, but FR-01 explicitly states body is optional. Behavioral evidence directly contradicts the requirement. Fix: validate title only. |
| **FR-02** | Edit note; update `updated_at`; NoteNotFoundError if not found | Note (`updated_at` field), NoteService, NoteNotFoundError | Edit Note use case exists; **no dedicated edit activity diagram** | Local filesystem write (inferred from Create pattern) | **Partially Traced** | Edit use case present but no activity diagram shows the edit flow or error handling. Behavioral specification is incomplete. |
| **FR-04** | Privacy flag (`visibility` field); hide body in list; service-layer enforcement; SZ-06 pending | `Note.visibility: str` ("public"\|"private"), PrivacyPolicy class, AccessDeniedError | Mark Note as Private use case (with SZ-06 annotation); **no unlock/lock activity flow** | Not deployment-specific | **Weakly Traced** | PrivacyPolicy and visibility field exist in class diagram; SZ-06 still open in ADL; no activity diagram shows what happens when access is denied or how lock/unlock changes the user path. |
| **FR-05** | Atomic write on create/edit/delete; StorageIOError on failure | JsonFileNoteRepository (`_save()` atomic: temp→fsync→os.replace, `_rotate_backups()`), StorageIOError | Storage write step shown in Create Note activity | Local Filesystem node in deployment diagram ("atomic read/write", 3 backup artifacts) | **Fully Traced** | Atomic write mechanism consistently documented across class diagram, activity diagram, and deployment diagram. StorageIOError named explicitly. |
| **NFR-02** | Module separation; each layer independently testable; swappable storage backend | NoteService→AbstractNoteRepository←JsonFileNoteRepository; DI pattern in class diagram | Activity swimlanes visually show layer boundaries (User/NoteService/PrivacyPolicy/JsonFileNoteRepository/VersionHistory) | Deployment diagram shows distinct Application, Repository, and Filesystem components | **Fully Traced** | Interface-based design supports testability; swimlane decomposition confirms layer independence. Minor concern: NoteService holds direct references to PrivacyPolicy and VersionHistory (not via interfaces). |
| **NFR-03** | No unhandled exceptions; domain-specific error types | Exception hierarchy: AstraNotesError → NoteNotFoundError, ValidationError, AccessDeniedError, StorageIOError, StorageCorruptionError | Error paths in Create Note activity (ValidationError branch shown) | Not deployment-specific | **Partially Traced** | Exception types are well-defined structurally. Activity diagram only shows Create Note error paths; edit and delete error handling not shown behaviorally. |
| **GOV-01** | PrivacyPolicy enforces access at service layer; AccessDeniedError; SZ-06 decision in ADL | PrivacyPolicy (static `can_read`/`can_update`/`can_delete`), AccessDeniedError | Mark Note as Private use case (with annotation); PrivacyPolicy swimlane in Create Note activity | Not deployment-specific | **Partially Traced** | Structural enforcement point clear. SZ-06 decision still open in ADL; no activity shows what the user experiences when `can_read()` returns False. |

**Status definitions:**
- **Fully Traced** — requirement supported by consistent evidence across all applicable diagram types
- **Partially Traced** — structural evidence strong; behavioral specification incomplete or missing
- **Weakly Traced** — only one evidence category; significant gaps in design specification
- **Not Traced** — no design evidence for this requirement

---

## Metrics Summary

| Metric | Count |
|--------|-------|
| Total requirements reviewed | 7 |
| Fully Traced | 1 (FR-05) |
| Partially Traced | 4 (FR-01, FR-02, NFR-03, GOV-01) |
| Weakly Traced | 1 (FR-04) |
| Not Traced | 0 |
| UML elements without clear requirement backing | 3 (see below) |

### UML Elements Without Requirement Backing

| Element | Location | Issue |
|---------|----------|-------|
| `VersionHistory.get_history()`, `revert()` + UC7/UC8 | Class diagram + Use Case diagram | No FR specifies user-facing version history access. `add_entry()` is internally justified; the user-facing use cases are not. |
| `Note.tags: list[str]` + `NoteService.create_note(tags=...)` | Class diagram | No requirement mentions tags. |
| `user_id` / `author_id` parameters on all NoteService methods | Class diagram | Implies multi-user identity; contradicts explicit single-user scope. |

---

## Gap Analysis

### 1. Structural vs. Behavioral Completeness

The design package is structurally stronger than behaviorally complete. The class diagram precisely specifies the three-layer architecture, the five-exception hierarchy, and the PrivacyPolicy enforcement point — all of which trace to FR-05 and NFR-02. The deployment diagram reinforces the atomic write story. However, only one activity diagram exists (Create Note); Edit Note (FR-02) and Mark as Private (FR-04) have no behavioral specification.

### 2. Cross-Week Inconsistency: FR-01 Body Validation

**This is a direct contradiction between Week 3 requirements and Week 4 design.**

- Refined requirements (FR-01): "...a non-empty title and an **optional** body."
- UML Activity Diagram (line 13): `if (title empty OR body empty?) → Raise ValidationError`

The activity diagram makes body required. Sprint 1 must implement title-only validation per the requirement, not the diagram. The activity diagram should be corrected to match FR-01.

### 3. Scope Creep: author_id / user_id

All NoteService methods accept `user_id` or `author_id`, and `Note` stores `author_id`. This implies a multi-user identity system. The Week 3 scope statement is explicit: "Single-user: AstraNotes is designed for one user." In a true single-user system, user identity is implicit and no `author_id` field is needed. This must be resolved before implementation: either remove the field (Option A) or update the scope to acknowledge a design-level user_id that defaults to a hardcoded single user (Option B).

### 4. Gold-Plating Risk

Three design elements exist without requirement backing: version history use cases (UC7/UC8), the `tags` field, and `author_id`. Each requires a resolution decision (add a requirement or remove the element) before Sprint 1 to avoid implementing features that are not specified.

---

## Pre-Sprint 1 Action Items

| Priority | Action | Blocks |
|----------|--------|--------|
| HIGH | Fix activity diagram: body validation should not raise ValidationError | FR-01 implementation |
| HIGH | Decide on author_id/user_id: remove or justify with explicit scope update | All NoteService methods |
| HIGH | Resolve SZ-06: access-control-only vs. encryption | PrivacyPolicy implementation |
| MEDIUM | Add activity diagrams for Edit Note and Mark/Unmark Private | FR-02, FR-04 implementation |
| MEDIUM | Resolve VersionHistory scope: internal-only or add user-facing FR | Sprint 1 scope |
| LOW | Decide on tags: add requirement or remove field | Note model implementation |

---

## Post-Implementation Update — Sprint 7 (2026-05-12)

> **Context:** The traceability matrix above was produced in Week 5 (pre-Sprint 1) as a design validation exercise. The following section documents the actual implementation status after Sprint 7 completion.

### Implementation Status

| Req ID | Original Status (Week 5) | Sprint 7 Status | Evidence |
|--------|--------------------------|-----------------|---------|
| FR-01 | Partially Traced | ✅ IMPLEMENTED | `NoteService.create_note()` enforces non-empty title; returns `ValidationError`; UUID assigned |
| FR-02 | Partially Traced | ✅ IMPLEMENTED | `NoteService.update_note()` patches note, increments version, updates `updated_at` |
| FR-03 | Not in matrix | ✅ IMPLEMENTED | `NoteService.delete_note()` → `SqliteNoteRepository.delete()` |
| FR-04 | Weakly Traced | ✅ IMPLEMENTED | `Note.visibility` field; `PrivacyPolicy.can_read/update/delete()` enforced at service layer |
| FR-05 | Fully Traced | ✅ IMPLEMENTED | `SqliteNoteRepository` persists to SQLite; survives restart |
| FR-06 | Not in matrix | ✅ IMPLEMENTED | Repository loads all notes via `list()` on each request |
| FR-07 | Not in matrix | ✅ IMPLEMENTED | `created_at`, `updated_at`, `id` in every `NoteResponse` |
| NFR-01 | Not in matrix | ✅ IMPLEMENTED | SQLite handles 500+ notes; memory-friendly |
| NFR-02 | Fully Traced | ✅ IMPLEMENTED | `AbstractNoteRepository` interface; `NoteService` has no import of concrete storage |
| NFR-03 | Partially Traced | ✅ IMPLEMENTED | All domain exceptions surfaced; HTTP 404/403/422 mapped at router |
| GOV-01 | Partially Traced | ✅ IMPLEMENTED | `PrivacyPolicy` enforced before every read/update/delete; `AccessDeniedError` → HTTP 403 |
| GOV-03 | Not in matrix | ✅ IMPLEMENTED | 58 tests: 29 domain unit + 13 repository unit + 9 API integration + 7 auth/health |
| GOV-04 | Not in matrix | ✅ IMPLEMENTED | All deps pinned in `requirements.txt`; passlib, sqlalchemy, pyjwt documented in ADL |

### Previously Identified Gaps — Resolution

| Gap (Week 5) | Resolution |
|-------------|-----------|
| FR-01: Body validation contradiction in activity diagram | Resolved: `Note.__post_init__` validates title only (body is optional) |
| FR-02: No edit activity diagram | Resolved: `NoteService.update_note()` is the authoritative behavioral spec; `test_us02_update_note_increments_version` validates the flow |
| FR-04: No lock/unlock activity | Resolved: `PrivacyPolicy.can_read()` raises `AccessDeniedError`; API returns 403; `test_list_only_returns_own_notes` validates multi-user isolation |
| `author_id` implies multi-user (scope contradiction) | Resolved: ADR-WEB-01 formally documents the single-user → multi-user scope pivot |
| `VersionHistory` user-facing use cases not in requirements | Status: `add_version_snapshot()` is a no-op in Sprint 7; full version history deferred to Sprint 8 |

### Test-to-Requirement Traceability (Sprint 7)

| Test | File | Requirement |
|------|------|-------------|
| test_create_returns_same_note | test_sqlite_repository.py | FR-01 |
| test_get_nonexistent_raises | test_sqlite_repository.py | FR-01, NFR-03 |
| test_list_with_author_id_filter | test_sqlite_repository.py | FR-05 |
| test_delete_returns_true/false | test_sqlite_repository.py | FR-03, NFR-03 |
| test_tags_round_trip | test_sqlite_repository.py | FR-07 |
| test_us01_create_note_returns_201 | test_notes_api.py | FR-01, US-01 |
| test_us02_update_note_increments_version | test_notes_api.py | FR-02, US-02 |
| test_us03_delete_note_returns_204 | test_notes_api.py | FR-03, US-03 |
| test_us05_list_notes_returns_empty | test_notes_api.py | FR-05, US-05 |
| test_create_note_response_has_author_id | test_notes_api.py | FR-07, US-06 |
| test_list_only_returns_own_notes | test_notes_api.py | GOV-01, US-04, FR-04 |
| test_get_nonexistent_returns_404 | test_notes_api.py | NFR-03 |
