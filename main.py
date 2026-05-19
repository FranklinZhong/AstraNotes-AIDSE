"""AstraNotes CLI — App Shell

Functional Slices implemented:
  Slice 1 — Create Note  (FR-01, US-01)
  Slice 2 — List Notes   (FR-05, US-05)
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow `python main.py` from the AstraNotes/ root
sys.path.insert(0, str(Path(__file__).parent))

from AstraNotes_v1 import (
    JsonFileNoteRepository,
    NoteService,
    ValidationError,
    StorageIOError,
    StorageCorruptionError,
)

DATA_FILE = Path.home() / ".astranotes" / "notes.json"
DEFAULT_USER = "local_user"


# ── service factory ─────────────────────────────────────────────────────────

def _build_service() -> NoteService:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    repo = JsonFileNoteRepository(str(DATA_FILE))
    return NoteService(repo)


# ── Slice 1: Create Note (FR-01, US-01) ─────────────────────────────────────

def cmd_create(service: NoteService) -> None:
    """Prompt the user for title + body, then persist a new note."""
    title = input("  Title: ").strip()
    if not title:                               # early guard — avoids a round-trip to the service
        print("  Error: title cannot be empty.")
        return
    body = input("  Body  (Enter to skip): ").strip()
    try:
        note = service.create_note(author_id=DEFAULT_USER, title=title, body=body)
        print(f"  Created [{note.id[:8]}] \"{note.title}\"")
    except ValidationError as exc:
        print(f"  Validation error: {exc}")
    except StorageIOError as exc:
        print(f"  Storage write failed: {exc}")


# ── Slice 2: List Notes (FR-05, US-05) ──────────────────────────────────────

def cmd_list(service: NoteService) -> None:
    """Display all notes visible to the current user."""
    notes = service.list_notes(user_id=DEFAULT_USER)
    if not notes:
        print("  (no notes yet)")
        return
    print(f"\n  {'ID':10}  {'TITLE':30}  {'VER':4}  UPDATED")
    print("  " + "-" * 62)
    for n in notes:
        icon = "[P]" if n.visibility == "private" else "[O]"
        print(f"  {icon} {n.id[:8]:<8}  {n.title[:30]:<30}  v{n.version:<3}  {n.updated_at}")


# ── main menu ────────────────────────────────────────────────────────────────

MENU = """
  ╔══════════════════════════════════╗
  ║        AstraNotes  v1            ║
  ║  1  Create note                  ║
  ║  2  List notes                   ║
  ║  0  Exit                         ║
  ╚══════════════════════════════════╝"""


def main() -> None:
    try:
        service = _build_service()
    except StorageCorruptionError as exc:
        print(f"FATAL: notes data is corrupted — {exc}")
        sys.exit(1)

    while True:
        print(MENU)
        choice = input("  Choice: ").strip()
        print()
        if choice == "1":
            cmd_create(service)
        elif choice == "2":
            cmd_list(service)
        elif choice == "0":
            print("  Goodbye.")
            break
        else:
            print("  Unknown option — enter 1, 2, or 0.")


if __name__ == "__main__":
    main()
