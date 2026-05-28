class AstraNotesError(Exception):
    """Base exception for AstraNotes."""


class NoteNotFoundError(AstraNotesError):
    """Raised when a note cannot be found."""


class ValidationError(AstraNotesError):
    """Raised when client data fails validation."""


class AccessDeniedError(AstraNotesError):
    """Raised when an operation violates privacy policy."""


class StorageIOError(AstraNotesError, IOError):
    """Raised for low-level I/O failures in repository."""


class StorageCorruptionError(AstraNotesError, ValueError):
    """Raised when storage data appears corrupted."""


class WrongNotePasswordError(AstraNotesError):
    """Raised when the provided note password does not match the stored hash."""
