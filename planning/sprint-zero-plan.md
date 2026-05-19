# AstraNotes Sprint Zero Plan

> Sprint Zero covers setup, planning, and risk reduction only. No feature implementation belongs here.

## Sprint Zero Items

### SZ-01 — Repository and Folder Structure
Create the AstraNotes project folder with the following layout:
```
AstraNotes/
├── planning/          ← this folder (already in progress)
├── src/
│   ├── note.py
│   ├── repository.py
│   ├── storage.py
│   └── privacy.py
└── tests/
    └── test_smoke.py
```
**Done when:** Folder structure exists and is committed to version control.

### SZ-02 — Python Environment Confirmation
Confirm Python 3.12 is the runtime. Document any planned dependencies (e.g., `pytest` for testing, standard library only for storage). No unverified third-party packages added yet (GOV-04).

**Done when:** A `requirements.txt` or equivalent note documents the environment baseline.

### SZ-03 — Architecture Confirmation
Review the Week 1.2 architecture decision and confirm the six modules still apply:
- `note.py` — Note entity and metadata
- `repository.py` — Repository interface (abstract)
- `storage.py` — File storage adapter (concrete)
- `privacy.py` — Privacy/encryption service
- Validation logic — embedded in repository or a separate validator
- App service / note manager — coordinates workflow

**Done when:** Architecture is documented in `planning/` or confirmed unchanged from Week 1.2.

### SZ-04 — Empty Module Stubs
Create placeholder files in `src/` with module-level docstrings only. No logic yet. This gives the project a skeleton that future code will fill in.

**Done when:** All four `.py` files exist and are importable without errors.

### SZ-05 — Pytest Smoke Test
Create `tests/test_smoke.py` with one trivially passing test to confirm the test runner works.

```python
def test_environment():
    assert True
```

**Done when:** `pytest` runs and reports 1 passed.

### SZ-06 — Privacy Design Decision ✅ COMPLETE (2026-05-05)

Before writing any storage code, decide: will private notes use encryption (e.g., symmetric key derived from a passphrase) or access-control-only (flag stored in metadata, body readable on disk)? Document the decision and the tradeoff.

**Decision:** Option A — Access-control-only. Private flag is enforced at the service layer by `PrivacyPolicy`. No at-rest encryption. Required user-facing disclosure added to README per G-02.

**Rationale (one paragraph):** AstraNotes is a single-user, local-first application. The Week 3.1 scope assumptions explicitly state "No file-system encryption." At-rest encryption would require a `cryptography` dependency, a key derivation and management design, and a new FR — none of which are in scope. The access-control-only model is consistent with all existing requirements and the constraint that only stdlib dependencies are permitted. The risk of user confusion (assuming encryption) is mitigated by mandatory disclosure in the README and CLI.

**Formal record:** `architecture_decision_log.md` — "SZ-06 Resolution" section (2026-05-05).

**Done when:** Decision is written in `planning/` with a one-paragraph rationale. ✅ Satisfied — decision is recorded in ADL and this entry.

### SZ-07 — Apply Definition of Done to Planning Artifacts
Review all four planning files against the Week 2.1 Definition of Done. Confirm each artifact:
- Maps to a specific AstraNotes objective or requirement
- Can be explained without referring back to the AI session
- Has been checked for clarity, realism, and fit with existing design

**Done when:** A brief review note exists (even inline in this file) confirming all four planning artifacts pass DoD.

---

## What Sprint Zero Is NOT

Sprint Zero does not include implementing note creation, editing, deletion, or any user-facing feature. Those items belong in the backlog and will be picked up in Sprint 1 and beyond. Adding feature work to Sprint Zero would undermine its purpose as a risk-reduction and planning phase.
