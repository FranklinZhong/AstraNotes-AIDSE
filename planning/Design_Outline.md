# AstraNotes Design Document Outline
> **Source:** Week 5.2 Design Document prompt workflow | **Created:** ~2026-04-28 | **Updated:** 2026-05-05
> **Note:** All open decisions referenced here resolved on 2026-05-05.

## 1. Introduction
- Purpose: Document AstraNotes design using the UML package, traceability matrix, and architecture decision log.
- Scope: Sprint 1 implementation of the core architecture, with clear mapping to course requirements and known design decisions.
- This document consolidates three design prompt outcomes:
  1. Use the UML package, traceability matrix, and architecture decisions to outline the design document.
  2. Explain how structural and behavioral views support the most important requirements.
  3. Identify where the design is still weak, partial, or intentionally scoped down before implementation.
- Artifact references:
  - `planning/DESIGN.md` (UML package reference)
  - `planning/TRACEABILITY.md` (requirements-to-UML traceability matrix)
  - `architecture_decision_log.md` (governance decisions and open issues)

## 2. Architecture Overview
- Three-layer architecture:
  - `NoteService` orchestration layer
  - `PrivacyPolicy` and `VersionHistory` cross-cutting services
  - `AbstractNoteRepository` storage interface
  - `JsonFileNoteRepository` concrete adapter writing to local JSON file with atomic persistence
- Dependency rule: `NoteService` depends on the repository interface, not concrete storage.
- Design goals: modularity, testability, local-first operation, and explicit error handling.
- UML evidence:
  - Class diagram: interface/adapter separation, service and policy classes, exception hierarchy
  - Activity diagram: Create Note swimlane flow
  - Deployment diagram: local filesystem, atomic write path, backup artifacts

## 3. Key Design Elements
### 3.1 Note Model
- `Note` fields: `id`, `title`, `body`, `tags`, `visibility`, `author_id`, `created_at`, `updated_at`, `version`
- Important constraints:
  - `title` must be non-empty
  - `body` is optional
  - `visibility` is enum-like string (`public` or `private`)
- Traceability:
  - FR-01, FR-07 (requirements baseline)
  - `planning/DESIGN.md` class definition
- Known issue: `tags` and `author_id` are present in the design but need requirement justification.

### 3.2 Storage Interface and Adapter
- `AbstractNoteRepository` methods: `create`, `get`, `list`, `update`, `delete`, `add_version_snapshot`, `get_versions`, `revert_to_version`
- `JsonFileNoteRepository` responsibilities:
  - load/write JSON data
  - atomic write via temp file + `fsync` + `os.replace()`
  - backup rotation and corruption recovery
- Traceability:
  - NFR-02, FR-05, NFR-03
  - `planning/DESIGN.md` repository definitions
  - `planning/TRACEABILITY.md` matrix shows FR-05 fully traced

### 3.3 Service Layer and Privacy Policy
- `NoteService` orchestrates business operations and enforces privacy.
- `PrivacyPolicy` methods: `can_read`, `can_update`, `can_delete`
- Operation contract:
  1. authorize via `PrivacyPolicy`
  2. perform repository call
  3. record version history if applicable
  4. return result or raise domain exception
- Traceability:
  - FR-04, GOV-01
  - `planning/DESIGN.md` service and policy structure
  - `planning/TRACEABILITY.md` shows FR-04 weakly traced due to incomplete behavior modeling
- Open decision: SZ-06 access-control-only vs. encryption must be resolved before Sprint 5.

### 3.4 Version History
- `VersionHistory` stores snapshots and supports rollback.
- `VersionEntry` includes `note_id`, `version`, `snapshot`, `actor_id`, `timestamp`
- Traceability issue: no explicit FR backs user-facing version history use cases.
- Option: treat version history as internal implementation support until a requirement is added.

### 3.5 Exception Handling
- Domain exception hierarchy:
  - `AstraNotesError`
  - `NoteNotFoundError`
  - `ValidationError`
  - `AccessDeniedError`
  - `StorageIOError`
  - `StorageCorruptionError`
- Contract: no raw Python or system exceptions escape public interfaces.
- Traceability:
  - NFR-03, SG-2
  - Supported by architecture decision log and design document.

## 4. Traceability Summary
- Uses the traceability matrix to confirm design coverage for Sprint 1 requirements.
- Summary findings from `planning/TRACEABILITY.md`:
  - FR-05 is fully traced across architecture and UML artifacts.
  - FR-01, FR-02, NFR-03, GOV-01 are partially traced.
  - FR-04 is weakly traced and needs better behavioral modeling.
- Gap items requiring action:
  - correct FR-01 body validation contradiction
  - add edit and privacy activity diagrams
  - resolve `author_id`/`user_id` scope creep
  - justify or remove `tags`
  - clarify version history scope

## 4.1 Structural and Behavioral Support for Key Requirements
- Structural views (class diagrams, deployment diagrams) define the static system organization needed for the top requirements.
  - FR-05 / NFR-02: `AbstractNoteRepository` plus `JsonFileNoteRepository` show repository abstraction and concrete persistence. The deployment diagram confirms the local JSON storage path and backup artifacts needed for atomic writes.
  - FR-04 / GOV-01: `PrivacyPolicy` and `NoteService` classes show the access-control enforcement point at the service layer. The class structure makes privacy a first-class component rather than an ad hoc check inside storage.
  - NFR-03 / SG-2: the exception hierarchy in the class diagram makes domain-specific error handling explicit. This structure supports the requirement that no raw system exceptions leak from public APIs.
  - FR-01 / FR-02: the `Note` model fields and `NoteService` operations support creation, update, and note identity semantics.
- Behavioral views (activity/use case diagrams) demonstrate how key operations should execute and where failure conditions are handled.
  - FR-05: the Create Note activity shows atomic persistence, policy enforcement, and version history recording in one end-to-end workflow.
  - FR-01: the Create Note swimlane documents the title validation step and error path; this is critical to prevent the body-from-required contradiction.
  - FR-04: the activity swimlane includes `PrivacyPolicy` as a separate lane, supporting the requirement that privacy checks occur before repository access.
  - FR-02: while the Edit Note use case exists structurally, the lack of a dedicated activity diagram is a gap; adding it would complete behavioral evidence for update and not-found handling.
- Combined structural and behavioral support:
  - Structural views define what components exist and how they relate.
  - Behavioral views define how those components interact to satisfy use cases and error conditions.
  - For the most important requirements, the system is strongest when both views align: e.g., atomic write behavior in the activity diagram must match the repository design in the class diagram.

## 4.2 Weaknesses, Partial Support, and Scoped-Down Design
- Weak or partial design areas:
  - FR-04 privacy enforcement is structurally supported, but behavioral evidence is weak because there is no dedicated activity diagram for access-denied or private-note read/update/delete flows. [Source: `planning/TRACEABILITY.md`]
  - FR-02 edit/update behavior is only partially modeled: the class diagram defines update operations, but there is no separate Edit Note activity diagram to show error handling and policy checks. [Source: `planning/TRACEABILITY.md`]
  - NFR-03 and SG-2 have structural exception coverage, but there is incomplete behavioral coverage for delete and edit failure paths beyond the Create Note activity. [Source: `planning/TRACEABILITY.md`]
  - VersionHistory has user-facing use cases in the UML but no explicit requirement backing, making its scope partial and potentially oversized for Sprint 1. [Source: `planning/TRACEABILITY.md`, `planning/DESIGN.md`]
  - `tags` and `author_id` are present in the design, but their requirement justification is unclear; these are potential scope creep items. [Source: `planning/TRACEABILITY.md`, `planning/DESIGN.md`]
- Intentionally scoped-down areas before implementation:
  - Single-user only: the system is explicitly not designed for multi-user collaboration or identity management beyond a possible hardcoded user sentinel. [Source: `planning/requirements.md` scope assumptions]
  - Privacy is currently access-control-only, not encrypted at rest, until SZ-06 is resolved and documented. [Source: `architecture_decision_log.md` SZ-06]
  - Audit logging for unauthorized access is out of scope unless a future GOV requirement adds it. [Source: `architecture_decision_log.md` G-03]
  - No networking, cloud sync, or attachment/media support is included in Sprint 1 design. [Source: `planning/requirements.md` scope assumptions]
  - The storage backend is designed to be swappable, but the current implementation focus is on `JsonFileNoteRepository` with the interface preserved for future adapters. [Source: `planning/requirements.md` NFR-02, `backlog.md` US-07]
- Implementation guidance:
  - Keep the Sprint 1 design bounded to the requirements and design gaps identified in the traceability audit.
  - Do not add user-facing version history or multi-user identity unless corresponding requirements are written first.
  - Document any deviation from this scoped-down baseline as an explicit design decision in `architecture_decision_log.md`.

## 5. Architecture Decisions and Risks
- Reference key decisions from `architecture_decision_log.md`:
  - atomic JSON persistence and backup strategy
  - privacy policy enforcement at the service layer
  - local JSON storage with optional future adapters
  - governance of dependencies and AI code verification
- Risks and open decisions:
  - SZ-06 private notes mechanism and disclosure obligations
  - G-01..G-06 governance gaps
  - misaligned activity diagram behavior vs. requirements

## 6. Implementation Notes
- Follow the working agreement: every implementation change must map to a numbered requirement.
- Keep `NoteService` dependency-injected with `AbstractNoteRepository`.
- Implement error wrapping in every public method.
- Use `pytest` for all unit tests, especially repository and policy layers.
- Do not claim encryption unless `cryptography` is added with review and ADL entry.
- Document the single-user assumption explicitly in README and system documentation.

## 7. Appendix
- Artifact list:
  - `planning/DESIGN.md`
  - `planning/TRACEABILITY.md`
  - `architecture_decision_log.md`
  - `backlog.md`
  - `planning/requirements.md`
- List of unresolved design items to close before Sprint 1.
