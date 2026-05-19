# AstraNotes — Product Backlog

**Project:** AstraNotes — A Secure, Modular Note-Taking System  
**Last Updated:** 2026-05-05  

---

## Priority Legend

| Symbol | Meaning |
|--------|---------|
| 🔴 High | Core functionality or security — must ship |
| 🟡 Medium | Important but can follow after core is stable |
| 🟢 Low | Valuable but deferrable |

## Status Legend

| Status | Meaning |
|--------|---------|
| `Backlog` | Not yet started |
| `In Progress` | Active in current Sprint |
| `Done` | Passed all DoD conditions |
| `Deferred` | Moved out of scope for now |

---

## Product Backlog

| ID | User Story | Req | Priority | Status | Sprint |
|----|------------|-----|----------|--------|--------|
| US-01 | As a user, I want to create a note with title, body, tags, and visibility so that I can capture and organize content. | FR-1 | 🔴 High | `Backlog` | Sprint 5 |
| US-02 | As a user, I want to retrieve a note by ID so that I can read previously saved content. | FR-2 | 🔴 High | `Backlog` | Sprint 5 |
| US-03 | As a user, I want to list and filter notes by tags, visibility, or author so that I can find relevant notes quickly. | FR-3 | 🟡 Medium | `Backlog` | Sprint 7 |
| US-04 | As a user, I want to update a note's fields so that I can revise content without losing the original record. | FR-4 | 🟡 Medium | `Backlog` | Sprint 7 |
| US-05 | As a user, I want to delete a note by ID so that I can remove content I no longer need. | FR-5 | 🟡 Medium | `Backlog` | Sprint 7 |
| US-06 | As a user, I want to view a note's version history and revert to a prior version so that I can recover earlier content. | FR-6 | 🟢 Low | `Backlog` | Sprint 9 |
| US-07 | As a developer, I want storage adapters isolated behind AbstractNoteRepository so that the backend can be swapped without changing business logic. | NFR-1 | 🔴 High | `Backlog` | Sprint 5 |
| US-08 | As a user, I want notes written atomically (temp → fsync → replace) so that my data survives a crash or interrupted save. | NFR-2 | 🔴 High | `Backlog` | Sprint 9 |
| US-09 | As a user, I want private notes protected by PrivacyPolicy so that unauthorized users cannot read, modify, or delete them. | SG-1 | 🔴 High | `Backlog` | Sprint 8 |
| US-10 | As a user, I want storage errors caught and wrapped as named exceptions so that a corrupted file or I/O failure does not crash the application. | SG-2 | 🔴 High | `Backlog` | Sprint 8 |

---

## Sprint Allocation Overview

| Sprint | Week | Focus | Items |
|--------|------|-------|-------|
| Sprint 0 | Week 1 | Architecture + Requirements | — (planning only) |
| Sprint 1 | Week 2 | Working Agreement, DoD, Backlog, Sprint Zero plan | — (planning only) |
| Sprint 2 | Week 3 | Requirements refinement + governance review | — (documents) |
| Sprint 3 | Week 4 | UML class diagram + behavioral design | — (design) |
| Sprint 4 | Week 5 | Design validation + Midterm 1 | — (design) |
| Sprint 5 | Week 6 | First implementation slice | US-01, US-02, US-07 |
| Sprint 6 | Week 7 | Testing strategy + first test suite | Tests for US-01, US-02 |
| Sprint 7 | Week 8 | CRUD completion + refactor | US-03, US-04, US-05 |
| Sprint 8 | Week 9 | Security + error handling | US-09, US-10 |
| Sprint 9 | Week 10 | Atomic write + version history + CI/CD | US-06, US-08 |

---

## Candidate Items (not yet in backlog)

> Items proposed during AI sessions that have no current requirement behind them.
> Review at the start of each Sprint; promote to backlog only if a requirement is written first.

| Candidate | Proposed By | Date | Decision |
|-----------|-------------|------|----------|
| Local encryption for private note bodies | AI session | 2026-04-06 | ✅ Resolved 2026-05-05 — SZ-06 decided: Option A (access-control-only). Encryption will not be implemented unless a new SG requirement is added. |

---

*Add new candidate items here. Do not move to backlog without a numbered requirement.*

---

## Week 3.2 Governance Backlog Items (added 2026-04-14)

These items were identified during the Week 3.2 governance and ethics review. They are tracked here until formal GOV requirements are written and they can be promoted to the main backlog.

| ID | Item | Source Gap | Blocking Sprint | Notes |
|----|------|-----------|-----------------|-------|
| GOV-B-01 | Add user-facing disclosure to README and CLI help: private flag = service-layer access control only, not filesystem encryption | G-02 | Sprint 5 | `Backlog` — Must ship before or alongside FR-04 implementation; disclosure text specified in ADL SZ-06 decision |
| GOV-B-02 | Create Sprint 1 AI code verification checklist (requirement mapping, failure path coverage, sign-off) | G-04 | Sprint 1 | ✅ `Done` 2026-05-05 — Created in `planning/ai_code_validation_checklist.md` |
| GOV-B-03 | Record SZ-06 outcome (access-control-only vs. at-rest encryption) in architecture decision log | G-01 | Sprint 5 | ✅ `Done` 2026-05-05 — Option A recorded in ADL; FR-04 implementation unblocked |
| GOV-B-04 | Draft single-page threat scope statement: what threats are in scope, what are explicitly out of scope by design | G-05 | Sprint 5 | ✅ `Done` 2026-05-05 — Created in `planning/threat_scope_statement.md` |
| GOV-B-05 | Document single-user assumption as explicit architectural constraint in README | G-06 | Sprint 5 | ✅ `Done` 2026-05-05 — Recorded in ADL (Architectural Constraint section) + DESIGN.md Issue 2 resolution |

> To promote any item above to the main backlog, write a numbered GOV requirement first and add it to the requirements baseline. Do not move directly to Sprint without a requirement.
