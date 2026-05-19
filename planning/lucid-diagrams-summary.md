# AstraNotes — UML Diagrams Summary

**Version:** 1.0  
**Date:** 2026-05-06  
**Diagrams location:** `AstraNotes/UML/` (draw.io files)  
**PlantUML source:** `UML/` directory and `UML/` directory

---

## Diagram Inventory

| # | Diagram | File | Description |
|---|---------|------|-------------|
| 1 | Class Diagram | `UML/01_class_diagram.drawio` | Core domain: Note, NoteService, repositories, privacy, history |
| 2 | Object Diagram | `UML/02_object_diagram.drawio` | Runtime snapshot: one Note instance with two NoteVersion objects |
| 3 | Use Case Diagram | `UML/03_usecase_diagram.drawio` | Actor: User; 6 use cases (UC1–UC6) mapping to FR-01–FR-07 |
| 4 | Activity Diagram | `UML/04_activity_diagram.drawio` | Edit Note flow: validate → patch → persist → version-log |
| 5 | Deployment Diagram | `UML/05_deployment_diagram.drawio` | Single node: local machine → Python process → ~/.astranotes/notes.json |

---

## Class Diagram Summary

```
Note (dataclass)
  id: str (UUID)
  title: str  ← required, non-empty (FR-01)
  body: str   ← optional (FR-01 fix: 2026-05-05)
  visibility: "private" | "public"
  author_id: str | None  ← "local_user" in Phase 1
  created_at, updated_at: ISO timestamps (FR-07)
  version: int

AbstractNoteRepository (ABC)
  + create(note) → Note
  + get(note_id) → Note
  + list(filters) → List[Note]
  + update(note) → Note
  + delete(note_id) → bool

JsonFileNoteRepository(AbstractNoteRepository)
  path: str  ← ~/.astranotes/notes.json
  Atomic write: temp → fsync → os.replace (NFR-02)

NoteService
  repository: AbstractNoteRepository
  policy: PrivacyPolicy
  version_history: VersionHistory
  + create_note, get_note, list_notes, update_note, delete_note, revert_note

PrivacyPolicy
  + can_read(user_id, note) → None | AccessDeniedError  (GOV-01)
  + can_update, can_delete

VersionHistory
  + add_entry(note, op, actor_id)
  + revert(note_id, version, actor_id) → Note
```

---

## Use Case Mapping

| Use Case | User Story | Requirement | Implemented? |
|----------|-----------|-------------|--------------|
| UC1: Create Note | US-01 | FR-01 | ✅ Sprint 5 |
| UC2: List Notes | US-05 | FR-05 | ✅ Sprint 5 |
| UC3: Edit Note | US-02 | FR-02 | ⏳ Sprint 7 |
| UC4: Delete Note | US-03 | FR-03 | ⏳ Sprint 7 |
| UC5: Private Note | US-04 | FR-04, GOV-01 | ⏳ Sprint 8 |
| UC6: View Timestamps | US-06 | FR-07 | ✅ (in List Notes output) |

---

## AI Prompt Used (Lucid AI / draw.io)

```
Prompt 1 (Class Diagram):
Generate a UML class diagram for AstraNotes with these classes:
Note (id, title, body, visibility, author_id, created_at, updated_at, version),
AbstractNoteRepository (interface: create, get, list, update, delete),
JsonFileNoteRepository (implements AbstractNoteRepository),
NoteService (create_note, get_note, list_notes, update_note, delete_note, revert_note),
PrivacyPolicy (can_read, can_update, can_delete),
VersionHistory (add_entry, revert).
Show inheritance, composition, and dependency arrows.

Prompt 5 (Deployment Diagram):
Generate a UML deployment diagram for AstraNotes.
Single local machine node. Python 3.12 process runs main.py.
Reads/writes ~/.astranotes/notes.json via JsonFileNoteRepository.
No network connections. No external services.
```

Full prompt set (5 prompts): `UML/` directory  
Refined prompt set (v2): `UML/` directory

---

## How to Open

1. Browser: go to [app.diagrams.net](https://app.diagrams.net)
2. Open from Device → select `.drawio` file from `AstraNotes/UML/`
3. Each file has one diagram page

PlantUML alternative: install PlantUML → render `.puml` files in `UML/` directory
