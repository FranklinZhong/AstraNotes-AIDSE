from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any

from .exceptions import ValidationError


def _now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


@dataclass
class Note:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    body: str = ""
    tags: List[str] = field(default_factory=list)
    visibility: str = "public"  # public=no extra password; private=password-protected
    metadata: Dict[str, Any] = field(default_factory=dict)
    author_id: Optional[str] = None
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)
    version: int = 1
    note_password_hash: Optional[str] = None  # bcrypt hash; only set when visibility=="private"

    def __post_init__(self):
        # re.search(r'\S') catches all Unicode whitespace, not just ASCII (str.strip() misses U+00A0)
        if not isinstance(self.title, str) or not re.search(r'\S', self.title):
            raise ValidationError("title must be a non-empty string")
        if not isinstance(self.body, str):  # FR-01: body is optional; empty string is valid
            raise ValidationError("body must be a string")
        if self.visibility not in {"private", "public"}:
            raise ValidationError("visibility must be 'private' or 'public'")
        if self.author_id is not None and not isinstance(self.author_id, str):
            raise ValidationError("author_id must be a string if provided")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Note":
        return cls(
            id=data["id"],
            title=data["title"],
            body=data["body"],
            tags=list(data.get("tags", [])),
            visibility=data.get("visibility", "public"),
            metadata=data.get("metadata", {}),
            author_id=data.get("author_id"),
            created_at=data.get("created_at", _now_iso()),
            updated_at=data.get("updated_at", _now_iso()),
            version=int(data.get("version", 1)),
            note_password_hash=data.get("note_password_hash"),
        )

    def patch(self, **fields: Any) -> "Note":
        if "title" in fields and fields["title"] is not None:
            if not isinstance(fields["title"], str) or not re.search(r'\S', fields["title"]):
                raise ValidationError("title must be a non-empty string")
            self.title = fields["title"]
        if "body" in fields and fields["body"] is not None:
            if not isinstance(fields["body"], str):  # FR-01: empty body is valid
                raise ValidationError("body must be a string")
            self.body = fields["body"]
        if "tags" in fields and fields["tags"] is not None:
            if not isinstance(fields["tags"], list):
                raise ValidationError("tags must be a list of strings")
            self.tags = fields["tags"]
        if "metadata" in fields and fields["metadata"] is not None:
            if not isinstance(fields["metadata"], dict):
                raise ValidationError("metadata must be a dict")
            self.metadata = fields["metadata"]
        if "visibility" in fields and fields["visibility"] is not None:
            if fields["visibility"] not in {"private", "public"}:
                raise ValidationError("visibility must be 'private' or 'public'")
            self.visibility = fields["visibility"]

        self.version += 1
        self.updated_at = _now_iso()
        return self
