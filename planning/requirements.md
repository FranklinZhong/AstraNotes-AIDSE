# AstraNotes Requirements Baseline

---

## Original Baseline (Week 1.2 — 2026-04-08)

*Preserved for traceability. Refined version is below.*

### Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-01 | The system shall allow a user to create a text note with a title and body. |
| FR-02 | The system shall allow a user to edit an existing note and save the updated content. |
| FR-03 | The system shall allow a user to delete a note from the local collection. |
| FR-04 | The system shall allow a user to mark a note as private. |
| FR-05 | The system shall persist notes to local storage so they are available after restart. |
| FR-06 | The system shall load previously saved notes when the application starts. |
| FR-07 | The system shall support note metadata: created date, last modified date, and note identifier. |

### Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | The system shall remain responsive when managing a large local collection of notes. |
| NFR-02 | The system architecture shall separate core logic from storage and presentation concerns so components can be reviewed or tested independently. |

### Security, Reliability, and Governance Requirements

| ID | Requirement |
|----|-------------|
| GOV-01 | Private notes shall be protected using a privacy or encryption mechanism appropriate to the Python technical path. |
| GOV-02 | The system shall handle invalid save, load, or delete operations gracefully and report clear errors instead of crashing. |
| GOV-03 | The project shall be structured so that major components can be reviewed or tested using pytest. |
| GOV-04 | The system shall avoid unverified third-party dependencies unless their purpose and risk are clearly justified. |

---

## Refined Baseline (Week 3.1 — 2026-04-13)

*Enhanced via ambiguity review, edge case analysis, and AI-assisted pressure testing.*
*Key change: GOV-02 reclassified as NFR-03 (reliability quality attribute, not a governance rule).*

### Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-01 | The system shall allow a user to create a text note with a non-empty title and an optional body. If the title is empty, the system shall reject the operation and return a validation error without creating a partial record. The system shall assign a unique identifier to each note at creation time. |
| FR-02 | The system shall allow a user to edit the title or body of an existing note and save the updated version to local storage. If the title is cleared, the system shall reject the save and return a validation error. If the note identifier no longer exists at save time, the system shall return a not-found error and shall not crash. The last-modified timestamp shall update on every successful save. |
| FR-03 | The system shall allow a user to delete a note by its unique identifier. If the identifier does not exist, the system shall return a not-found error and shall not crash. Deletion shall remove the note from both the in-memory collection and local storage. |
| FR-04 | The system shall allow a user to set a privacy flag on an individual note. Notes marked as private shall not display their body content in list or summary views. The privacy policy shall be enforced at the service layer before any read, update, or delete operation on a private note. The privacy flag shall persist across application restarts. In this version, private means hidden by application logic — notes are not encrypted at rest. |
| FR-05 | The system shall persist notes to local storage when a create, edit, or delete operation completes. If a persistence operation fails, the system shall return a storage error to the caller and shall not silently report success. The specific storage format is a design decision and is not prescribed by this requirement. |
| FR-06 | The system shall load previously saved notes from local storage when the application starts. If no storage file exists, the system shall initialize with an empty collection without error. If the storage file is corrupted or unreadable, the system shall report a storage error and start with a safe empty state rather than crashing. |
| FR-07 | The system shall store and return a unique identifier, a created timestamp, and a last-modified timestamp for each note. The identifier shall be a UUID assigned at creation and immutable thereafter. The last-modified timestamp shall update automatically whenever the note title or body is successfully saved. |

### Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | The system shall complete note list operations within an acceptable response time for a local collection at the scale of a quarter-long student project — typically fewer than 500 notes. Loading the full collection into memory at startup is acceptable at this scale. |
| NFR-02 | The system architecture shall organize note domain logic, storage operations, and privacy policy into distinct modules, each independently testable using pytest. No module shall directly depend on the internals of another — interactions shall occur through defined interfaces. This separation shall allow the storage backend to be swapped without changes to the domain or service layer. |
| NFR-03 | The system shall not raise unhandled exceptions or terminate unexpectedly when encountering invalid note identifiers, failed storage operations, or corrupted storage files. All error conditions shall surface as domain-specific exception types rather than raw system exceptions. *(Reclassified from GOV-02: this is a reliability quality attribute, not a governance rule.)* |

### Security, Reliability, and Governance Requirements

| ID | Requirement |
|----|-------------|
| GOV-01 | Private notes shall be protected by an access control policy enforced at the service layer. If access is not permitted, the system shall return an access-denied error. The specific implementation mechanism shall be recorded as an explicit decision in the architecture decision log before implementation begins. |
| GOV-03 | The project shall include pytest test files for the note domain model, the repository adapter, the note service, and the privacy policy. Each test file shall cover at least one success path and one failure path for its component. |
| GOV-04 | The system shall use Python standard library modules for all core functionality. Any third-party package added to the project shall be documented in the architecture decision log with its stated purpose and version. |

### Scope Assumptions (made explicit in Week 3.1)

- **Single-user**: AstraNotes is designed for one user. Multi-user access is out of scope.
- **Text-only**: Only text notes in this version. Images, voice, and attachments are deferred.
- **Local-first**: No network access, cloud sync, or remote sharing in this version.
- **In-memory collection**: All notes are loaded at startup. Lazy loading is not required at this scale.
- **Storage format is a design decision**: Current choice (JSON) is recorded in the architecture decision log, not mandated by requirements.
- **No file-system encryption**: "Private" means service-layer access control only.

### Scope Update: Web Multi-User Pivot (Week 6 Decision — ADR-WEB-01)

The original scope assumptions (single-user, local-first) were updated in Week 6 following an architectural pivot decision. See `planning/architecture_decision_log.md` ADR-WEB-01 for full rationale.

**Updated Scope (Sprint 7+):**

| Dimension | Original Scope (Week 3.1) | Updated Scope (Week 6+) |
|-----------|--------------------------|------------------------|
| User model | Single-user | Multi-user (JWT authentication) |
| Access | Local CLI | Web REST API + Browser UI |
| Storage | Local JSON file | SQLite (server-side) |
| Privacy | Local access control | Per-user isolation via JWT + PrivacyPolicy |
| Deployment | Local only | Cloud-deployable (Render) |

**Preserved constraints:**
- Text-only notes (no images, attachments)
- No real-time collaboration
- No end-to-end encryption (notes stored plaintext in SQLite)
- No external third-party services (no email, no SMS)

---

## Design Validation Findings (Week 5.1 — 2026-04-27)

*From the requirements-to-UML requirements-to-UML traceability audit. These are cross-week inconsistencies between this requirements baseline and the Week 4 UML package. Full details in `planning/TRACEABILITY.md`.*

### Contradiction Found — FR-01 Body Validation

**FR-01 (this document):** "...a non-empty title and an **optional** body."

**Week 4 Activity Diagram (UML Activity Diagram, line 13):** Raises `ValidationError` when `title empty OR body empty` — treating body as required.

**Resolution for Sprint 1 implementation:** Validate title only. An empty body is valid per FR-01. The activity diagram must be corrected.

### Scope Concern — author_id / user_id Parameters ✅ Resolved (2026-05-05)

The Week 4 class diagram adds `author_id` to `Note` and `user_id` to all `NoteService` methods. This implies multi-user identity, which contradicts the single-user scope above.

**Decision:** Retain parameters with hardcoded single-user sentinel `"local_user"`. This preserves the interface for future extensibility without building a multi-user identity system. See DESIGN.md Issue 2 and `architecture_decision_log.md` GOV-B-05 for full rationale.

### Gold-Plating Items Without Requirement Backing

| Element | Location | Resolution Needed |
|---------|----------|-------------------|
| `Note.tags` field | Class diagram | Add requirement or remove field |
| `VersionHistory` user-facing access (UC7/UC8) | Use Case diagram | Add explicit FR or scope to internal-only |
| `author_id` / `user_id` parameters | Class + Service | Resolve per scope concern above |
