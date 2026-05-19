# AstraNotes — Initial Requirements Set


---

## Prompt Evolution

### Weak Prompt (Round 1)

```
Generate requirements for a note-taking app in Python.
```

**What the weak prompt produced:**
- Generic bullet points ("users can create, edit, delete notes")
- No testability — statements like "the app should be fast" or "notes should be saved"
- No format or structure — mixed functional and non-functional items with no labeling
- No connection to the architecture — requirements floated in isolation from the design decisions

**Why it was insufficient:**
The output could apply to any note-taking app ever written. Nothing in the response was traceable
to a specific module, interface, or design decision. It could not guide a backlog, a test, or an
acceptance criterion.

---

### Strong Prompt (Round 2 — Structured Template)

```
[Tech Stack]Python 3.12 + local JSON file storage (stdlib only)

[Requirements]Please generate the initial requirements baseline for AstraNotes:
1. At least 6 functional requirements (CRUD for notes, privacy, version history)
2. At least 2 non-functional requirements (testability, reliability)
3. At least 2 security/privacy/governance requirements (access control, error handling)
4. Total >= 10 requirements

[Context]
AstraNotes is a secure, modular note-taking system in Python.
Architecture: NoteBase model -> AbstractNoteRepository interface -> JsonFileNoteRepository adapter
-> NoteService (orchestration) -> PrivacyPolicy (access control) -> VersionHistory (audit)

[Output Requirements]
- Write each requirement as: "The system shall..."
- Number them FR-1...FR-6, NFR-1...NFR-2, SG-1...SG-2
- After each requirement, add one line: "-> [Backlog item / Test / Acceptance Criterion]: ..."
- Be specific enough to directly guide implementation or testing
- No explanations, just the requirements
```

**Why the strong prompt produced better output:**
- Specifying the tech stack (Python 3.12 + stdlib JSON) prevented the AI from suggesting
  irrelevant frameworks or external dependencies
- Numbered categories forced the AI to cover all requirement types — it could not skip
  security or non-functional requirements
- Providing the architecture context caused the AI to reference actual module names
  (`AbstractNoteRepository`, `PrivacyPolicy`, `NoteService`) instead of vague abstractions
- The output format instruction (`"The system shall..."` + traceability line) made every
  requirement directly usable as a backlog item, test, or acceptance criterion
- The result is an architecture-grounded requirements baseline, not a generic wish list

---

## Functional Requirements (6)

**FR-1.** The system shall allow a user to create a text note with `title`, `body`, `tags`, and `visibility`, and persist it as a new `Note` entity with unique UUID, `created_at`, `updated_at`, and `version` fields.
> → [Backlog item]: Implement `NoteService.create_note()` with validation and repository save.

**FR-2.** The system shall allow a user to fetch a note by its `id` and return all persisted fields, failing with `NoteNotFoundError` if no matching note exists.
> → [Test]: Unit test for `AbstractNoteRepository.get()` with valid and invalid IDs.

**FR-3.** The system shall allow a user to list notes with optional filtering (`tags`, `visibility`, `author_id`), and it shall exclude private notes unless the requester is authorized for those notes.
> → [Acceptance Criterion]: List operation returns filtered results excluding unauthorized private notes.

**FR-4.** The system shall allow a user to update a note's content fields (`title`, `body`, `tags`, `metadata`, `visibility`) via patch semantics, increment `version`, set `updated_at`, and reject invalid field values with `ValidationError`.
> → [Backlog item]: Add `NoteService.update_note()` with patch logic and version increment.

**FR-5.** The system shall allow a user to delete a note by `id` and return success status (`true/false`); deleting a non-existing note must safely return `false` without raising an error.
> → [Test]: Integration test for `AbstractNoteRepository.delete()` on existing and non-existing notes.

**FR-6.** The system shall maintain version history for each note in a separate history store (`NoteVersion` entries), including prior snapshot, author, timestamp, and change diff, and provide a retrieval API for rollbacks.
> → [Acceptance Criterion]: `VersionHistory.get(note_id)` returns version list; `revert()` creates new version from prior snapshot.

---

## Non-Functional Requirements (2)

**NFR-1.** The system shall isolate storage adapters behind `AbstractNoteRepository` and include a comprehensive adapter test suite so that any backend swap (JSON file, in-memory, SQLite) requires no changes to business logic or service layer.
> → [Test]: Shared test suite mixin applied to both `JsonFileNoteRepository` and `InMemoryNoteRepository` — both must pass identically.

**NFR-2.** The system shall persist notes in a JSON file with an atomic write strategy — write to temp file, `fsync`, then `os.replace()` to target — with backup rotation and corruption detection to prevent partial writes or data loss.
> → [Backlog item]: Implement atomic write in `JsonFileNoteRepository` with error recovery and backup fallback.

---

## Security, Privacy, and Governance Requirements (2)

**SG-1.** The system shall enforce access control by validating `can_read`, `can_update`, and `can_delete` for each request through `PrivacyPolicy`, and raise `AccessDenied` for any unauthorized operation before reaching the repository layer.
> → [Test]: Unit test for `PrivacyPolicy` methods with authorized and unauthorized user scenarios.

**SG-2.** The system shall catch and wrap low-level I/O errors as `StorageIOError` and corrupt data errors as `StorageCorruptionError`, emit observable logs, and fall back to the most recent valid backup without crashing the process.
> → [Acceptance Criterion]: Error simulation tests confirm graceful handling, correct error types raised, and backup restoration.

---

## Summary

| Category | Count | Minimum Required |
|----------|-------|-----------------|
| Functional | 6 | ≥ 6 ✓ |
| Non-Functional | 2 | ≥ 2 ✓ |
| Security / Privacy / Governance | 2 | ≥ 2 ✓ |
| **Total** | **10** | **≥ 10 ✓** |

All requirements are written in testable "The system shall..." form and are directly traceable
to a specific module, interface, or service in the AstraNotes architecture. Each requirement
includes an explicit conversion path to a backlog item, unit test, or acceptance criterion,
making this baseline actionable for the full quarter project.
