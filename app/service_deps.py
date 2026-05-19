"""NoteService factory — Sprint 7.

Wires SqliteNoteRepository + PrivacyPolicy into a ready-to-use NoteService.
FastAPI routers should declare ``Depends(get_note_service)`` to obtain an instance.

Usage:
    from app.service_deps import get_note_service

    @router.post("/notes/")
    def create_note(body: NoteCreate,
                    user_id: str = Depends(get_current_user),
                    service: NoteService = Depends(get_note_service)):
        note = service.create_note(author_id=user_id, title=body.title, body=body.body)
        return NoteResponse.from_domain(note)
"""
from app.db.sqlite_repository import SqliteNoteRepository
from app.config import settings
from AstraNotes_v1.services.note_service import NoteService
from AstraNotes_v1.policies.privacy_policy import PrivacyPolicy


def get_note_service() -> NoteService:
    """Return an application-scoped NoteService backed by SQLite."""
    repo = SqliteNoteRepository(settings.database_url)
    return NoteService(repository=repo, policy=PrivacyPolicy())
