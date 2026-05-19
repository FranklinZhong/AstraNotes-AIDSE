# AstraNotes Scope Summary
> **Source:** Week 5.2 PRD prompt workflow exercise | **Created:** ~2026-04-28 | **Updated:** 2026-05-05

## Product Vision
AstraNotes is a single-user, local note-taking system with a secure, modular architecture. The product is built around a Python backend with JSON file storage, an abstract repository interface, service-layer orchestration, privacy policy enforcement, and version-history support.

## In-Scope
- Create, read, update, and delete notes.
- Persist notes to local storage with a JSON-based adapter behind `AbstractNoteRepository`.
- Support note fields including `title`, `body`, `tags`, and `visibility`.
- Enforce privacy policy through `PrivacyPolicy` at the service layer.
- Provide robust error handling for storage failures and invalid operations.
- Maintain a product backlog that is traceable to numbered requirements.
- Follow governance rules for AI-generated output, prompt logging, and testable design.

## Core Requirements
- FR-1: Create a note with title, body, tags, visibility, UUID, created/updated timestamps, and version metadata.
- FR-2: Retrieve a note by ID and return all persisted fields; missing IDs raise `NoteNotFoundError`.
- FR-3: List/filter notes by tags, visibility, or author, excluding unauthorized private notes.
- FR-4: Update note fields with patch semantics, version increment, and validation errors for invalid values.
- FR-5: Delete a note by ID without raising an error for non-existing notes.
- FR-6: Maintain version history for notes, including snapshots, timestamps, and rollback support.

## Non-Functional Requirements
- NFR-1: Isolate storage adapters behind `AbstractNoteRepository` so backend swaps require no business logic changes.
- NFR-2: Use atomic write semantics for persistence (temp file → `fsync` → replace) to prevent partial saves and data loss.

## Security and Governance Requirements
- SG-1: Enforce `can_read`, `can_update`, and `can_delete` through `PrivacyPolicy`; unauthorized operations fail before repository access.
- SG-2: Catch and wrap low-level I/O and corruption errors as domain-specific storage exceptions, with observable logging and recovery behavior.

## Scope Constraints and Assumptions
- Single-user only; multi-user support is out of scope.
- Notes are text-only; attachments, media, and network sync are out of scope.
- Private notes are protected by access control only, not by filesystem encryption.
- The current storage format is JSON by design; no external packages are required for core functionality.
- All notes may be loaded into memory at startup, as the project scale is small.

## Governance and Process Notes
- AI output must map to specific numbered requirements before acceptance.
- Prompt log entries are required for significant AI sessions.
- No unverified third-party dependencies may be added without ADL documentation and review.
- Privacy claims must reflect actual implemented properties; the private flag is not a guarantee of encryption.
- The project uses a weekly sprint cadence with defined backlog and review checkpoints.

## Current Backlog Focus
- Sprint 5: US-01, US-02, US-07 (create note, read note, adapter isolation).
- Sprint 7: US-03, US-04, US-05 (list/filter, update, delete).
- Sprint 8: US-09, US-10 (privacy enforcement, error handling).
- Sprint 9: US-06, US-08 (version history, atomic writes).

## Governance Backlog Items
- GOV-B-01: Disclose privacy scope clearly in user-facing docs.
- GOV-B-02: Establish an AI code verification checklist.
- GOV-B-03: Record the access-control vs encryption decision in the architecture log.
- GOV-B-04: Publish a threat scope statement.
- GOV-B-05: Document the single-user assumption explicitly.
