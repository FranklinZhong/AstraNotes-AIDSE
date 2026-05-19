# AstraNotes PRD Outline
> **Source:** Week 5.2 PRD prompt workflow exercise | **Created:** ~2026-04-28 | **Updated:** 2026-05-05
> **Note:** SZ-06 references as 'open decision' resolved 2026-05-05 (Option A).

## 1. Product Scope Summary
- AstraNotes is a single-user local note-taking system with a modular Python architecture, JSON persistence, and service-layer privacy enforcement. [Source: `planning/requirements.md`, `backlog.md`, `architecture_decision_log.md`]
- The current product scope covers note CRUD, listing/filtering, privacy policy, version history, swappable storage, atomic persistence, and domain-specific error handling. [Source: `planning/requirements.md`, `backlog.md`, `architecture_decision_log.md`]
- Governance discipline is required: AI output must map to numbered requirements, privacy claims must be accurate, and scope creep must be controlled. [Source: `working_agreement.md`, `backlog.md`, `architecture_decision_log.md`]

## 2. Problem Statement
- AstraNotes is a local Python note-taking system for one user that must be modular, traceable, and safe. [Source: `planning/requirements.md`, `working_agreement.md`, `architecture_decision_log.md`]
- Simple note apps often conflate storage and business logic, lack privacy controls, and fail to document requirements or risks. [Source: `architecture_decision_log.md`, `working_agreement.md`]
- AstraNotes must enforce access control for private notes and handle storage failures with domain-specific exceptions rather than crashing. [Source: `planning/requirements.md` FR-04, NFR-03, SG-2]

## 3. Target Users
- Primary: a single local desktop or laptop user. [Source: `planning/requirements.md` scope assumptions]
- Secondary: course reviewers and developers requiring a traceable, testable implementation. [Source: `working_agreement.md`, `backlog.md`]
- User needs:
  - capture and organize notes with title, body, tags, and visibility. [Source: `backlog.md` US-01]
  - retrieve and update saved notes reliably. [Source: `backlog.md` US-02, US-04]
  - keep private notes hidden from unauthorized reads/edits/deletes. [Source: `backlog.md` US-09, `planning/requirements.md` FR-04]
  - recover cleanly from storage failures without crashing. [Source: `backlog.md` US-10, `planning/requirements.md` NFR-03]

## 4. Core Features
- FR-01: Create a note with title, body, tags, visibility, UUID, timestamps, and version metadata. [Source: `planning/requirements.md`, `backlog.md` US-01]
- FR-02: Retrieve a note by ID and return all persisted fields; missing IDs raise `NoteNotFoundError`. [Source: `planning/requirements.md`, `backlog.md` US-02]
- FR-03: List/filter notes by tags, visibility, or author, excluding unauthorized private notes. [Source: `planning/requirements.md`, `backlog.md` US-03]
- FR-04: Update a note with patch semantics, version increment, validation, and privacy enforcement. [Source: `planning/requirements.md`, `backlog.md` US-04]
- FR-05: Delete a note by ID with safe handling of missing notes. [Source: `planning/requirements.md`, `backlog.md` US-05]
- FR-06: Maintain version history for note snapshots and rollback support. [Source: `planning/requirements.md`, `backlog.md` US-06]
- NFR-02: Isolate storage behind `AbstractNoteRepository` with a concrete JSON adapter. [Source: `planning/requirements.md`, `backlog.md` US-07]
- SG-1: Enforce `PrivacyPolicy` checks before repository operations. [Source: `planning/requirements.md` GOV-01, `architecture_decision_log.md`]

## 5. Non-Functional Constraints
- NFR-01: Keep the system responsive for a local collection of about 500 notes. [Source: `planning/requirements.md`]
- NFR-02: Separate domain, storage, and privacy into independently testable modules. [Source: `planning/requirements.md`, `backlog.md` US-07]
- NFR-03: Surface all failures as domain-specific exception types; do not leak raw Python exceptions. [Source: `planning/requirements.md`]
- Must use atomic JSON persistence: temp file → `fsync` → `os.replace()`. [Source: `backlog.md` US-08, `architecture_decision_log.md`]
- Must remain stdlib-only for core functionality; track dev-only dependencies like `pytest` in governance artifacts. [Source: `planning/requirements.md` GOV-04, `architecture_decision_log.md`]

## 6. Risks
- Misleading privacy claims if private notes are treated as encrypted when they are access-control-only. [Source: `architecture_decision_log.md` SZ-06, `working_agreement.md` Agreement 10]
- Scope creep from `author_id`/`user_id` and `tags` appearing in the design without explicit requirement backing. [Source: `planning/TRACEABILITY.md`, `planning/DESIGN.md`]
- Incomplete behavioral design for edit/update and private-note flows. [Source: `planning/TRACEABILITY.md`]
- Governance gaps: missing disclosure, threat scope statement, AI verification checklist, and single-user documentation. [Source: `backlog.md` GOV-B-01..GOV-B-05, `architecture_decision_log.md`]

## 7. Out of Scope
- Multi-user collaboration, network sync, cloud storage, or remote sharing. [Source: `planning/requirements.md` scope assumptions]
- Filesystem encryption / at-rest encryption unless a formal GOV requirement is added. [Source: `planning/requirements.md` FR-04, `architecture_decision_log.md` SZ-06]
- Attachments, images, audio, or rich media note content. [Source: `planning/requirements.md` scope assumptions]
- Audit logging for unauthorized access attempts unless a future GOV requirement includes it. [Source: `architecture_decision_log.md` G-03]
- Large-scale optimization beyond a small local note collection. [Source: `planning/requirements.md` NFR-01]

## 8. Structural and Behavioral Support
- Structural views define the key system components and their relationships.
  - `AbstractNoteRepository` + `JsonFileNoteRepository` support atomic persistence and backend swapability. [Source: `planning/DESIGN.md`, `planning/TRACEABILITY.md`]
  - `NoteService`, `PrivacyPolicy`, and exception hierarchy support service-layer privacy and explicit error handling. [Source: `planning/DESIGN.md`, `planning/TRACEABILITY.md`]
  - `Note` model supports creation, retrieval, update, and metadata semantics. [Source: `planning/DESIGN.md`]
- Behavioral views define runtime flow and failure handling.
  - Create Note activity shows validation, privacy check, atomic write, and version recording. [Source: `planning/TRACEABILITY.md`]
  - The privacy lane in the activity diagram supports enforcement before repository access. [Source: `planning/TRACEABILITY.md`]
  - Missing Edit Note and private-note failure activity diagrams are identified as gaps. [Source: `planning/TRACEABILITY.md`]
- Combined structural and behavioral support strengthens top requirements such as FR-05, FR-04, and NFR-03.

## 9. Weaknesses and Scoped-Down Design
- Weak or partial design areas:
  - FR-04 has weak behavioral coverage for private-note denial and access flow. [Source: `planning/TRACEABILITY.md`]
  - FR-02 lacks a dedicated Edit Note activity diagram. [Source: `planning/TRACEABILITY.md`]
  - NFR-03 and SG-2 need broader delete/update failure path coverage. [Source: `planning/TRACEABILITY.md`]
  - VersionHistory has user-facing use cases without an explicit backing requirement. [Source: `planning/TRACEABILITY.md`, `planning/DESIGN.md`]
  - `tags` and `author_id` are design items without clear requirement justification. [Source: `planning/TRACEABILITY.md`]
- Scoped-down design decisions:
  - Single-user only; no multi-user identity unless scope is updated. [Source: `planning/requirements.md`]
  - Privacy is access-control-only until SZ-06 is resolved and documented. [Source: `architecture_decision_log.md`]
  - Audit logging is out of scope unless a future GOV requirement adds it. [Source: `architecture_decision_log.md`]
  - Sprint 1 focuses on `JsonFileNoteRepository` while preserving `AbstractNoteRepository` for future adapter support. [Source: `backlog.md` US-07]

## 10. Traceability
- Requirements baseline: `planning/requirements.md`
- Backlog and user stories: `backlog.md`
- UML/design package: `planning/DESIGN.md`
- Traceability audit: `planning/TRACEABILITY.md`
- Governance decisions: `architecture_decision_log.md`, `working_agreement.md`

## 11. Implementation Notes
- Map every implementation change to a numbered requirement before accepting it. [Source: `working_agreement.md`]
- Inject `AbstractNoteRepository` into `NoteService`; avoid concrete coupling. [Source: `planning/DESIGN.md`]
- Wrap low-level exceptions in domain-specific error types. [Source: `planning/requirements.md` NFR-03]
- Use `pytest` for unit tests of model, repository, service, and policy layers. [Source: `architecture_decision_log.md`]
- Do not claim encryption until it is explicitly implemented and approved. [Source: `architecture_decision_log.md` G-02, `working_agreement.md` Agreement 10]
- Document the single-user assumption in README and system documentation. [Source: `architecture_decision_log.md` G-06]

## 12. Appendix
- Artifact list:
  - `planning/requirements.md`
  - `backlog.md`
  - `planning/DESIGN.md`
  - `planning/TRACEABILITY.md`
  - `architecture_decision_log.md`
- Pre-Sprint 1 unresolved items:
  - FR-01 validation behavior vs. activity diagram
  - author_id/user_id scope decision
  - VersionHistory requirement scope
  - tags requirement justification
  - privacy flow activity coverage
