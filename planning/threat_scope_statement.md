# AstraNotes — Threat Scope Statement

> **Governance item:** GOV-B-04 (from Week 3.2 governance review, G-05)
> **Related:** ADL SZ-06 decision, `planning/DESIGN.md` Scope Constraints, `requirements.md` FR-04/GOV-01

This document defines the threat surface for AstraNotes v1. It is not a full threat model — it is a one-page scope statement that clarifies what the system is and is not designed to protect against. This prevents scope creep during implementation and sets honest expectations for users.

---

## What AstraNotes Is

AstraNotes is a **single-user, local-first, text-only note-taking application** that stores notes in a JSON file on the developer's local machine. It is a student project built over one academic quarter with a stdlib-only Python stack. No network access, no remote storage, no authentication system.

---

## In-Scope Threats

These are the threats the current design is intended to address:

| Threat | Mechanism | How AstraNotes Mitigates It |
|--------|-----------|----------------------------|
| **Application-layer unauthorized access to private notes** | A second user or process calling `NoteService` methods | `PrivacyPolicy` checks `author_id == user_id` at the service layer before every read/update/delete on a private note. Returns `AccessDeniedError` if not authorized. |
| **Data corruption from interrupted writes** | Process killed mid-write; disk failure during save | `JsonFileNoteRepository._save()` uses atomic write: temp file → `fsync` → `os.replace()`. 3 rolling backups maintained. `StorageCorruptionError` triggers recovery. |
| **Silent failures on invalid operations** | Empty title, missing note ID, failed storage I/O | All invalid operations raise named domain exceptions (`ValidationError`, `NoteNotFoundError`, `StorageIOError`) rather than returning `None` or crashing silently. |
| **Gold-plating that expands attack surface** | Unused features, unrequested dependencies | Scope constraints enforced: no third-party dependencies, no network stack, no encryption library, no user registry. |

---

## Out-of-Scope Threats

These threats are **explicitly not addressed** in v1. This is a design choice, not an oversight.

| Threat | Why Out of Scope |
|--------|----------------|
| **Direct filesystem access to `astranotes_data.json`** | Any user with filesystem access to the data file can read all note content, including notes marked private. AstraNotes does not encrypt data at rest (SZ-06, Option A). The private flag is application-logic only. **Users must be informed of this limitation.** |
| **At-rest encryption** | No `cryptography` dependency. No key management. Not in scope unless a new SG requirement is added and SZ-06 is revisited. |
| **Multi-user isolation** | No authentication, no user registry. All notes belong to a single `author_id = "local_user"`. A second OS-level user with file access can read all notes. |
| **Network-based attacks** | No network stack, no remote API. Not applicable in v1. |
| **Memory-based attacks** | Notes are loaded in memory at startup. No protection against process inspection or memory dumps. Out of scope for a local student project. |
| **Concurrent write conflicts** | `threading.Lock` is present in `JsonFileNoteRepository` but concurrent multi-process access is not a supported use case. |
| **Audit logging of access attempts** | `AccessDeniedError` is raised but not logged. Audit trails are explicitly out of scope (see ADL G-03). |

---

## Required User Disclosure (linked to GOV-B-01)

The following disclosure must appear in the AstraNotes README and in the CLI `--help` output before Sprint 1 ships:

> **Privacy notice:** Notes marked as "private" are hidden from list and summary views within the application. They are **not encrypted on disk**. Anyone with access to `astranotes_data.json` on your local machine can read all note content. Do not store sensitive credentials, financial data, or personal information in AstraNotes.

---

## Scope Change Process

If a new threat enters scope (e.g., at-rest encryption becomes required), the following must happen **before** implementation begins:

1. Write a new SG requirement in `planning/requirements.md`
2. Record a new ADL entry with the dependency, license, and rationale
3. Update this threat scope statement
4. Update the AI code validation checklist with new verification items
