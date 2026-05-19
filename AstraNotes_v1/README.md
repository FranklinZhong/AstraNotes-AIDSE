# AstraNotes v1

A secure, modular note-taking system (Python 3.12). Implements the `Note` model, repository abstraction with JSON storage, `NoteService` orchestration, `PrivacyPolicy`, and `VersionHistory`.

## Features

- CRUD operations for notes
- Filtered listing with visibility an author-based controls
- Privacy policies for read/update/delete
- Version history with create/update/revert semantics
- Atomic JSON writes (`tmp + fsync + replace`) and backup rotation
- Error wrapping for I/O and corruption

## Structure

- `note.py`: `Note` entity with validation
- `exceptions.py`: custom exception classes
- `repositories/`: repository abstractions and `JsonFileNoteRepository`
- `policies/privacy_policy.py`: access control checks
- `history/version_history.py`: version audit and rollback
- `services/note_service.py`: business logic and orchestration
- `tests/`: pytest suite

## Install & Test

```bash
python -m pip install -U pytest
cd AstraNotes_v1
pytest -q tests
```

## Usage

```python
from AstraNotes_v1.repositories.json_file_note_repository import JsonFileNoteRepository
from AstraNotes_v1.services.note_service import NoteService

repo = JsonFileNoteRepository("my_notes.json")
service = NoteService(repo)

n = service.create_note("user1", "Hello", "World", visibility="public")
print(service.get_note("user1", n.id))
```

## Backlog & mapping

- FR-1...FR-6 implemented in `services/note_service.py` & `repositories/json_file_note_repository.py`
- NFR-1 by abstraction with `AbstractNoteRepository` and test harness
- NFR-2 via `_atomic_save` and backup rotation
- SG-1 via `PrivacyPolicy` checks
- SG-2 via `StorageIOError` and `StorageCorruptionError`
