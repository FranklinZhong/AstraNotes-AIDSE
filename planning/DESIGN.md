# AstraNotes — Design Package Reference

> **Source:** UML design package — PlantUML (Phase 1) + Draw.io (Phase 2)
> **Last validated:** Week 5.1 traceability audit (2026-04-27)
> **Last updated:** 2026-05-05 (all Known Design Issues resolved; code FR-01 bug fixed)
> **Status:** Design complete; backend code fully implemented (29 tests passing); App Shell implemented in Sprint 6

This document is the authoritative design reference for Copilot and all Sprint 1 implementation work. It describes the intended class structure, relationships, exception contracts, and known design gaps that must be resolved before or during implementation.

---

## Architecture Overview

AstraNotes uses a three-layer architecture with strict dependency direction:

```
User / CLI
    │
    ▼
NoteService          ← orchestrates all operations; enforces privacy policy
    │         │
    ▼         ▼
PrivacyPolicy   VersionHistory   ← cross-cutting concerns
    │
    ▼
AbstractNoteRepository   ← interface; NoteService depends on this, not concrete class
    │
    ▼
JsonFileNoteRepository   ← concrete adapter; atomic writes to local JSON file
    │
    ▼
Local Filesystem (astranotes_data.json + 3 rolling backups)
```

**Key architectural rules:**
- `NoteService` depends on `AbstractNoteRepository` (interface), not `JsonFileNoteRepository` directly — storage backend is swappable
- `PrivacyPolicy` is enforced at the service layer, not at the repository layer
- No module imports from sibling modules except through defined interfaces
- All errors surface as domain-specific exception types (never raw Python exceptions)

---

## Class Definitions

### `Note` (domain model)

```python
@dataclass
class Note:
    id: str                  # UUID, assigned at creation, immutable
    title: str               # non-empty required
    body: str                # OPTIONAL — may be empty string
    tags: list[str]          # ⚠ NO REQUIREMENT — gold-plating, see Design Issues
    visibility: str          # "public" | "private"  (NOT a boolean is_private flag)
    author_id: str           # ⚠ SCOPE CONCERN — see Design Issues
    created_at: datetime     # set at creation, immutable
    updated_at: datetime     # updated on every successful save
    version: int             # incremented on each edit

    def patch(self, fields: dict) -> None: ...
    def to_dict(self) -> dict: ...
    @staticmethod
    def from_dict(data: dict) -> Note: ...
```

**Important:** `visibility` is a string enum (`"public"` or `"private"`), not a boolean. Use `note.visibility == "private"` in policy checks.

---

### `AbstractNoteRepository` (interface)

```python
class AbstractNoteRepository(ABC):
    @abstractmethod
    def create(self, note: Note) -> Note: ...
    @abstractmethod
    def get(self, note_id: str) -> Note: ...         # raises NoteNotFoundError if missing
    @abstractmethod
    def list(self, filters: dict) -> list[Note]: ...
    @abstractmethod
    def update(self, note: Note) -> Note: ...        # raises NoteNotFoundError if missing
    @abstractmethod
    def delete(self, note_id: str) -> bool: ...      # raises NoteNotFoundError if missing
    @abstractmethod
    def add_version_snapshot(self, note: Note) -> None: ...
    @abstractmethod
    def get_versions(self, note_id: str) -> list[VersionEntry]: ...
    @abstractmethod
    def revert_to_version(self, note_id: str, version: int) -> Note: ...
```

---

### `JsonFileNoteRepository` (concrete adapter)

```python
class JsonFileNoteRepository(AbstractNoteRepository):
    _filepath: str
    _lock: threading.Lock

    # Public: all AbstractNoteRepository methods implemented

    # Private internals:
    def _load(self) -> dict: ...             # reads JSON from disk
    def _save(self, data: dict) -> None: ... # atomic write: temp → fsync → os.replace
    def _rotate_backups(self) -> None: ...   # keeps 3 rolling backups (.bak.1/.bak.2/.bak.3)
    def _recover(self) -> dict: ...          # fallback if primary file is corrupted
```

**Atomic write contract:** Every write goes through `_save()` which writes to a temp file, calls `fsync`, then uses `os.replace()` to atomically swap in. This guarantees no partial writes. Failures raise `StorageIOError`.

**Backup files:** `astranotes_data.json.bak.1`, `.bak.2`, `.bak.3` — rotated on every successful write.

---

### `NoteService` (orchestration layer)

```python
class NoteService:
    _repo: AbstractNoteRepository    # injected — never instantiate directly inside
    _policy: PrivacyPolicy
    _history: VersionHistory

    def create_note(self, author_id: str, title: str, body: str,
                    tags: list, visibility: str) -> Note: ...
    def get_note(self, user_id: str, note_id: str) -> Note: ...
    def list_notes(self, user_id: str, filters: dict) -> list[Note]: ...
    def update_note(self, user_id: str, note_id: str, fields: dict) -> Note: ...
    def delete_note(self, user_id: str, note_id: str) -> bool: ...
    def revert_note(self, user_id: str, note_id: str, version: int) -> Note: ...
```

**Operation contract for all methods:**
1. Check `PrivacyPolicy.can_read/update/delete(user_id, note)` — raise `AccessDeniedError` if denied
2. Perform operation via `self._repo`
3. Record in `self._history` via `add_entry(note, actor_id)`
4. Return result or raise domain exception

---

### `PrivacyPolicy` (access control)

```python
class PrivacyPolicy:
    @staticmethod
    def can_read(user_id: str, note: Note) -> bool: ...
    @staticmethod
    def can_update(user_id: str, note: Note) -> bool: ...
    @staticmethod
    def can_delete(user_id: str, note: Note) -> bool: ...
```

**Current policy (access-control-only, no encryption):**
- Public note: any user can read/update/delete
- Private note (`visibility == "private"`): only `author_id == user_id` can access
- Returns `False` if denied; `NoteService` raises `AccessDeniedError` on `False`

**SZ-06 Decision (2026-05-05):** Option A — access-control-only. No at-rest encryption. Formal decision recorded in `architecture_decision_log.md`. Sprint 1 may implement `PrivacyPolicy` using this model.

---

### `VersionHistory`

```python
class VersionHistory:
    _repo: AbstractNoteRepository

    def add_entry(self, note: Note, actor_id: str) -> None: ...
    def get_history(self, note_id: str) -> list[VersionEntry]: ...
    def revert(self, user_id: str, note_id: str, version: int) -> Note: ...
```

**Decision (2026-05-05):** `VersionHistory` is **internal-only** for Sprint 1. `add_entry()` is called by `NoteService` after every successful mutation. `get_history()` and `revert()` are implemented but not exposed via any user-facing CLI command or service endpoint. UC7 (View Version History) and UC8 (Revert Note) are **out of Sprint 1 scope** — they will be re-evaluated if an explicit FR is added in a future sprint. This removes the gold-plating risk while keeping the internal implementation available.

---

### `VersionEntry`

```python
@dataclass
class VersionEntry:
    note_id: str
    version: int
    snapshot: dict    # full Note state at that version
    actor_id: str
    timestamp: datetime
```

---

## Exception Hierarchy

```
AstraNotesError (base)
├── NoteNotFoundError      — note_id does not exist in get/update/delete
├── ValidationError        — empty title, or other input validation failure
├── AccessDeniedError      — PrivacyPolicy returned False
├── StorageIOError         — file write/read failed (disk full, permissions, etc.)
└── StorageCorruptionError — JSON file unreadable or structurally invalid
```

**Contract:** No raw Python exceptions (`FileNotFoundError`, `JSONDecodeError`, `KeyError`, etc.) should escape any public method. All must be wrapped in one of the five domain exception types above.

---

## UML Diagram Coverage (v4.1 artifact / v4.2 artifact)

| Diagram | Format | What It Shows |
|---------|--------|---------------|
| Class Diagram | PlantUML + Draw.io | All 6 classes, fields, methods, exception hierarchy, relationships |
| Object Diagram | PlantUML + Draw.io | Runtime snapshot of a Create Note operation (instance names: service1, policy1, history1, repo1, note1, entry1) |
| Use Case Diagram | PlantUML + Draw.io | 8 use cases: Create/View/Edit/Delete Note, Mark as Private, List Notes, View Version History, Revert Note |
| Activity Diagram | PlantUML + Draw.io | **Create Note only** — full swimlane: User → NoteService → PrivacyPolicy → JsonFileNoteRepository → VersionHistory |
| Deployment Diagram | PlantUML + Draw.io | Developer Workstation > Python 3.12 Runtime > Application components > Local Filesystem (data + 3 backups) |

---

## Known Design Issues (from Week 5.1 Traceability Audit)

These issues were identified during the requirements-to-UML traceability review (v5.1 artifact, 2026-04-27). They must be resolved before Sprint 1 implementation begins.

### Issue 1 — FR-01 Body Validation Contradiction (HIGH)

**Requirement (v3.1 artifact, FR-01):** "...a non-empty title and an **optional** body."

**Activity Diagram (v4.1 artifact, line 13):** `if (title empty OR body empty?) then (yes) → Raise ValidationError`

The diagram incorrectly rejects notes with empty body. Sprint 1 implementation must only validate the title. The activity diagram should be corrected.

**Fix:** In `NoteService.create_note()`, raise `ValidationError` only when `title` is empty, not when `body` is empty.

---

### Issue 2 — author_id / user_id Scope Creep (HIGH)

**Requirement (v3.1 artifact, Scope):** "Single-user: AstraNotes is designed for one user. Multi-user access is out of scope."

**Design (v4.1 artifact, Class Diagram):** Every `NoteService` method accepts `user_id` or `author_id` parameter, and `Note` stores `author_id`. This implies a multi-user identity system.

**Decision (2026-05-05): Option B — Hardcoded single-user sentinel**

`author_id` is retained in `Note` and `user_id` is retained in `NoteService` method signatures, but both are fixed at the value `"local_user"` throughout the application. Removing them would be a breaking interface change; keeping them with a documented sentinel preserves future extensibility without implementing multi-user features.

**Sprint 1 implementation rule:** Set `author_id = "local_user"` at note creation. Pass `user_id = "local_user"` in all service calls. Document this convention in code comments and README. Do not build a user registry or authentication system. Formal constraint recorded in `architecture_decision_log.md` (GOV-B-05, 2026-05-05).

---

### Issue 3 — Tags Field (LOW)

`Note.tags: list[str]` and `NoteService.create_note(tags=...)` exist in the design but no requirement mentions tags.

**Decision (2026-05-05):** Retain `Note.tags` as a field (defaulting to empty list `[]`) but **remove the `tags` parameter from all `NoteService` method signatures** in Sprint 1. Tags are not exposed via the service API and not serialized as a meaningful feature. No tag-related functionality will be implemented until an explicit FR is added. This avoids gold-plating while keeping the data model extensible.

---

### Issue 4 — VersionHistory User-Facing Access (MEDIUM)

Covered above in the VersionHistory class description. UC7 (View Version History) and UC8 (Revert Note) exist in the use case diagram without a backing FR.

---

### Issue 5 — Missing Activity Diagrams (MEDIUM)

Only the Create Note activity diagram exists. Edit Note (FR-02) and Mark as Private (FR-04) have no activity-level specification. Developers need to infer the flow from the use case diagram and class structure alone.

**Known Gap (not blocking Sprint 1):** The Create Note activity diagram is sufficient to guide the first implementation slice. Edit Note and Mark as Private flows are derivable from the class contracts and FR-02/FR-04 text. Formal activity diagrams for these two operations are deferred and should be added if ambiguity arises during implementation.

**Inferred Edit Note flow:** User → NoteService.update_note(user_id, note_id, fields) → PrivacyPolicy.can_update() → repo.get() → note.patch(fields) → repo.update() → history.add_entry() → return updated Note.

**Inferred Mark as Private flow:** User → NoteService.update_note(user_id, note_id, {visibility: "private"}) → [same as Edit Note path] → FR-04 satisfied when visibility field persists.

---

## AI-Generated Design Critique (Week 5.1 Validation)

**Round 1 — Weak prompt output (rejected entirely):** Single-class `AstraNotesStorage` with no module boundaries, no error handling, no privacy layer, no testability design.

**Round 2 — Strong prompt output (accepted elements):**
- Three-layer architecture: NoteService → AbstractNoteRepository ← JsonFileNoteRepository
- Named exception hierarchy: 5 types inheriting from AstraNotesError
- Atomic write pattern: temp → fsync → os.replace with 3 rolling backups
- PrivacyPolicy as a separate service-layer concern enforced before repository access

**AI-generated elements that were accepted without sufficient scrutiny — require resolution before Sprint 1:**

| Element | Problem | Resolution |
|---------|---------|------------|
| `author_id`/`user_id` on all NoteService methods | Multi-user pattern; contradicts explicit single-user scope | ✅ **Decided 2026-05-05**: Retained as hardcoded sentinel `"local_user"` (GOV-B-05) |
| `tags: list[str]` on Note and NoteService | No requirement backing | ✅ **Decided 2026-05-05**: `Note.tags` kept as empty list default; removed from NoteService API |
| UC7/UC8 (View Version History, Revert Note) | User-facing version access not specified in any FR | ✅ **Decided 2026-05-05**: VersionHistory internal-only; UC7/UC8 out of Sprint 1 scope |
| Activity diagram body validation (`title OR body empty`) | Contradicts FR-01 which states body is optional | ✅ **Fix confirmed**: Sprint 1 validates title only (body empty = valid) |

---

## Identity vs. Value Analysis (Week 5.1 Validation)

Per the OOAD validation framework, design elements fall into two categories:

| Element | Category | Reasoning |
|---------|----------|-----------|
| `Note` | **Identity-bearing** | UUID assigned at creation (immutable), tracked over time with version counter and timestamps |
| `VersionEntry` | **Identity-bearing** | Captures a specific historical state of a Note; stored and retrievable by version number |
| `created_at` / `updated_at` | Value-like | Datetime attributes of Note; not independently tracked entities |
| `visibility` | Value-like | String attribute ("public"/"private") on Note; not a tracked object |
| `filters` in `list(filters)` | Value-like | Transient query criteria; discarded after use |
| `tags: list[str]` | Value-like | Simple string metadata; ⚠ no requirement backing; should not be treated as tracked entities |
| `VersionHistory` class | Service (not entity) | Stateless coordinator that delegates to the repository; correctly not identity-bearing |

**Key judgment:** `Note` is correctly designed as an entity. The problematic elements (`tags`, `author_id`) are value-like or scope-creep items. `VersionHistory` is correctly a service, not an entity — but its user-facing use cases (UC7/UC8) require a decision before Sprint 1.

---

## Cross-Diagram Consistency (Week 5.1 Validation)

| Check | Result |
|-------|--------|
| Class names consistent across all 5 diagrams | ✅ Consistent |
| Single-user scope reflected in deployment | ✅ Deployment has no network node |
| Body validation: activity diagram vs. FR-01 | ❌ CONTRADICTION — activity diagram requires body; FR-01 says optional |
| author_id in class diagram vs. single-user scope | ❌ INCONSISTENCY — class diagram implies multi-user; deployment says single-user |
| UC7/UC8 (Version History) vs. FR requirements | ❌ NO BACKING — use cases exist; no FR requires user-facing version access |
| Activity diagram coverage: 1/8 use cases covered | ⚠ INCOMPLETE — only Create Note has activity-level specification |

---

## Maintainability Assessment (Week 5.1 Validation)

**Positive signals:**
- Three-layer separation makes responsibilities clear
- `AbstractNoteRepository` interface provides a testability seam
- Named exception hierarchy makes error handling predictable
- Atomic write is well-encapsulated in `_save()`

**Warning signs (must resolve before Sprint 1):**
| Warning | Severity | Resolution |
|---------|----------|------------|
| `NoteService` directly references `PrivacyPolicy` and `VersionHistory` (not via interfaces) | Low | Acceptable for student project scale; note the coupling |
| UC7/UC8 (Version History) have no requirement owner — cannot be scoped, tested, or pruned | Medium | Add explicit FR or remove use cases |
| `author_id`/`user_id` on every method adds noise for a single-user system | Medium | Remove or replace with hardcoded sentinel |
| `tags` field adds data complexity without requirement | Low | Remove or add requirement |

---

## Scope Constraints (from v3.1 artifact)

| Constraint | Detail |
|------------|--------|
| Single-user | No multi-user access, no authentication system |
| Text-only | No images, voice, or attachments in v1 |
| Local-first | No network, cloud sync, or remote access |
| In-memory collection | All notes loaded at startup; lazy loading not required |
| Storage format | JSON (design decision, not a requirement — backend is swappable) |
| No at-rest encryption | "Private" = service-layer access control only ✅ SZ-06 decided 2026-05-05: Option A |
