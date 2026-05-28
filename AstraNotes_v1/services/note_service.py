from typing import Dict, List, Optional

from ..repositories.abstract_note_repository import AbstractNoteRepository
from ..policies.privacy_policy import PrivacyPolicy
from ..history.version_history import VersionHistory
from ..note import Note
from ..exceptions import NoteNotFoundError


class NoteService:
    def __init__(
        self,
        repository: AbstractNoteRepository,
        policy: Optional[PrivacyPolicy] = None,
        version_history: Optional[VersionHistory] = None,
    ):
        self.repository = repository
        self.policy = policy or PrivacyPolicy()
        self.version_history = version_history or VersionHistory(repository)

    def create_note(
        self,
        author_id: str,
        title: str,
        body: str = "",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
        visibility: str = "public",
        note_password_hash: Optional[str] = None,
    ) -> Note:
        note = Note(
            title=title,
            body=body,
            tags=tags or [],
            metadata=metadata or {},
            visibility=visibility,
            author_id=author_id,
            note_password_hash=note_password_hash,
        )
        created = self.repository.create(note)
        self.version_history.add_entry(created, "create", actor_id=author_id)
        return created

    def get_note(self, user_id: Optional[str], note_id: str) -> Note:
        note = self.repository.get(note_id)
        self.policy.can_read(user_id, note)
        return note

    def list_notes(self, user_id: Optional[str], filters: Optional[Dict] = None) -> List[Note]:
        # Always filter to owner's notes only; merge with any extra filters.
        all_filters: Dict = {"author_id": user_id}
        if filters:
            all_filters.update(filters)
        return self.repository.list(all_filters)

    def update_note(self, user_id: Optional[str], note_id: str, **patch_data) -> Note:
        note = self.repository.get(note_id)
        self.policy.can_update(user_id, note)
        old_version = note.version
        note.patch(
            title=patch_data.get("title"),
            body=patch_data.get("body"),
            tags=patch_data.get("tags"),
            metadata=patch_data.get("metadata"),
            visibility=patch_data.get("visibility"),
        )
        # note_password_hash is not part of Note.patch(); set directly when present.
        if "note_password_hash" in patch_data:
            note.note_password_hash = patch_data["note_password_hash"]
        note.version = old_version + 1
        updated = self.repository.update(note)
        self.version_history.add_entry(updated, "update", actor_id=user_id)
        return updated

    def delete_note(self, user_id: Optional[str], note_id: str) -> bool:
        note = self.repository.get(note_id)
        self.policy.can_delete(user_id, note)
        return self.repository.delete(note_id)

    def revert_note(self, user_id: Optional[str], note_id: str, version: int) -> Note:
        note = self.repository.get(note_id)
        self.policy.can_update(user_id, note)
        reverted = self.version_history.revert(note_id, version, actor_id=user_id)
        return reverted
