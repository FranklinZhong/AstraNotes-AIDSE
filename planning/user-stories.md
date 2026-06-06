# AstraNotes User Stories

> Traceability: Each story maps to a Week 1.2 requirement.
> US-01~06: user-facing stories. US-07~10: developer/security stories (added 2026-05-05 to complete backlog coverage).

---

## US-01 — Create Note
**Source:** FR-01

**Story:** As a user, I want to create a new note with a title and body so that I can capture information quickly.

**Acceptance Criteria:**
- A new note can be created by providing a non-empty title and body.
- The note appears in the notes list immediately after it is saved.
- The system shall not save a note with an empty title without displaying a clear warning to the user.

---

## US-02 — Edit Note
**Source:** FR-02

**Story:** As a user, I want to edit an existing note and save my changes so that I can keep my information current.

**Acceptance Criteria:**
- The user can modify the title or body of any existing note.
- Saving an edited note updates the stored version and refreshes the last-modified date.
- If the user attempts to save an edit that removes the title entirely, the system shall warn and refuse the save.

---

## US-03 — Delete Note
**Source:** FR-03

**Story:** As a user, I want to delete a note so that I can remove outdated content from my collection.

**Acceptance Criteria:**
- The user can select a note and delete it.
- The deleted note no longer appears in the notes list after the operation completes.
- The deletion is persisted to SQLite so the note does not reappear on subsequent requests.

---

## US-04 — Private Notes
**Source:** FR-04, GOV-01

**Story:** As a user, I want to mark a note as private so that sensitive information is not exposed to anyone viewing my note list.

**Acceptance Criteria:**
- The user can toggle a note's private flag at creation or during editing.
- A private note's body content is not displayed in plain text in the standard notes list view.
- The privacy state of a note is persisted to SQLite and returned correctly on subsequent API requests.

---

## US-05 — Note Persistence
**Source:** FR-05, FR-06

**Story:** As a user, I want my notes to be saved to the server automatically so that I do not lose my work.

**Acceptance Criteria:**
- All notes created or updated via the API are present when the notes list is fetched again.
- Notes are written to SQLite at the point of save (each POST/PATCH is immediately durable).
- If a note fails to persist due to a storage error, the system shall report a clear error rather than silently losing data.

---

## US-06 — Note Metadata
**Source:** FR-07

**Story:** As a user, I want to see the created date and last-modified date on each note so that I can track when information was added or changed.

**Acceptance Criteria:**
- Each note displays a created-at timestamp set at the moment of first save.
- Each note displays a last-modified timestamp that updates every time the note is edited and saved.
- Timestamps are stored as part of the note data and are restored correctly after application restart.

---

## US-07 — Storage Adapter Isolation
**Source:** NFR-02

**Story:** As a developer, I want the storage backend to be isolated behind `AbstractNoteRepository` so that I can swap storage implementations without changing business logic.

**Acceptance Criteria:**
- `NoteService` is instantiated with an `AbstractNoteRepository` parameter and never imports `SqliteNoteRepository` directly.
- Tests run using an isolated in-memory SQLite instance injected via `app.dependency_overrides` without any changes to `NoteService`.
- The `JsonFileNoteRepository` (v1) was replaced by `SqliteNoteRepository` (v2) with zero changes to `NoteService` or `PrivacyPolicy` — validating this story (ADR-WEB-01).

---

## US-08 — Atomic Write Persistence
**Source:** NFR-02 (atomic write contract)

**Story:** As a user, I want notes written to the database atomically so that my data is not corrupted if the application crashes mid-save.

**Acceptance Criteria:**
- Every write to SQLite is wrapped in a transaction; no partial writes are possible.
- A failed write raises a storage error to the caller rather than silently corrupting data.
- The `version` field increments on every successful PATCH, enabling detection of concurrent update conflicts.

> *Note: The original acceptance criteria (temp→fsync→os.replace, backup rotation) described the v1 `JsonFileNoteRepository`. After ADR-WEB-01, `SqliteNoteRepository` fulfils the atomicity guarantee via SQLAlchemy transactions.*

---

## US-09 — Privacy Policy Enforcement
**Source:** GOV-01, FR-04

**Story:** As a user, I want private notes to be inaccessible to any caller that is not the note's author so that sensitive content is not exposed through the application interface.

**Acceptance Criteria:**
- Every `NoteService` method that reads, updates, or deletes a note calls `PrivacyPolicy.can_*()` before any repository operation.
- Attempting to read, update, or delete a private note with a non-matching `user_id` raises `AccessDeniedError` before the repository is touched.
- The README includes the disclosure: "Private notes are protected by application-level access control, not file-system encryption." (GOV-B-01)

---

## US-10 — Domain Exception Handling
**Source:** NFR-03, SG-2

**Story:** As a user, I want the application to report meaningful error messages instead of crashing so that I can understand what went wrong and recover.

**Acceptance Criteria:**
- No raw Python exception (`FileNotFoundError`, `IntegrityError`, `KeyError`, etc.) escapes any public method of `NoteService` or `SqliteNoteRepository`.
- All storage I/O errors are caught and re-raised as `StorageIOError`; all JSON parse failures as `StorageCorruptionError`.
- Invalid note IDs in get/update/delete raise `NoteNotFoundError`; empty titles raise `ValidationError`; policy violations raise `AccessDeniedError`.
