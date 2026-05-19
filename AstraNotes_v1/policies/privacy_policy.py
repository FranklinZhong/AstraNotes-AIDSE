from typing import Optional

from ..note import Note
from ..exceptions import AccessDeniedError


class PrivacyPolicy:
    """Enforces access control rules for note operations."""

    @staticmethod
    def can_read(user_id: Optional[str], note: Note) -> bool:
        if note.visibility == "public":
            return True
        if user_id is not None and user_id == note.author_id:
            return True
        raise AccessDeniedError("Read access denied")

    @staticmethod
    def can_update(user_id: Optional[str], note: Note) -> bool:
        if user_id is not None and user_id == note.author_id:
            return True
        raise AccessDeniedError("Update access denied")

    @staticmethod
    def can_delete(user_id: Optional[str], note: Note) -> bool:
        if user_id is not None and user_id == note.author_id:
            return True
        raise AccessDeniedError("Delete access denied")
