# AstraNotes Prioritized Backlog

## High Priority

| Item | Links To | Notes |
|------|----------|-------|
| Project setup — repo structure, Python env, planning folder | Sprint Zero | Must exist before any work begins |
| Confirm and document architecture from Week 1.2 | Sprint Zero | Locks module boundaries before coding |
| Privacy design decision — encryption vs. access control | US-04, GOV-01 | **Blocks** note storage implementation; must be resolved first |
| Note creation and save flow | US-01 | Core value; all other note operations depend on this existing |
| Note persistence to local storage | US-05 | Persistence must work before editing or deletion can be verified |

## Medium Priority

| Item | Links To | Notes |
|------|----------|-------|
| Note editing | US-02 | Depends on persistence (US-05) being in place |
| Note deletion | US-03 | Depends on persistence and the notes list being reliable |
| Note metadata display (created date, last-modified date) | US-06 | Useful, but not blocking for early realization |

## Low Priority

| Item | Links To | Notes |
|------|----------|-------|
| Keyword search across notes | (not yet a formal requirement) | Useful feature; deferred until core CRUD is stable |
| Future note type extensibility (voice, image plugins) | Project Charter | Architecture supports it; implementation deferred to later quarter |

---

## Priority Decision Rationale

**Decision 1 — Persistence before editing:**
Note editing (US-02) and deletion (US-03) are ranked below note persistence (US-05) because editing or deleting a note that cannot be reliably stored creates misleading behavior. It is not useful to confirm an edit if the note reverts on next startup. Persistence is the prerequisite, not a parallel track.

**Decision 2 — Privacy decision before storage implementation:**
The privacy design question (US-04) is ranked as high priority and placed before any storage code is written. If the decision is made after the storage layer exists, the privacy mechanism becomes a retrofit rather than a design choice. Security that is bolted on after the fact is harder to reason about, test, and defend — which conflicts directly with the Week 2.1 Definition of Done.
