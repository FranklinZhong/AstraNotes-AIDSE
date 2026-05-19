# AstraNotes — Executive One-Pager

**Version:** 1.0  
**Date:** 2026-05-06  

---

## What

AstraNotes is a secure, modular, local-first note-taking application built with Python 3.12. It allows a single user to create, edit, delete, and privately manage text notes with full persistence across restarts.

## Why

Traditional note apps expose all notes equally and rely on OS-level access control. AstraNotes demonstrates that privacy and access control can be enforced at the application layer — a key software engineering principle.

## Who

- **Primary user:** One local user (single-user scope, Phase 1)
- **Developer/reviewer:** the development team

## How

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Model | `note.py` (dataclass) | UUID, title, body, visibility, timestamps |
| Storage | `JsonFileNoteRepository` | Atomic write (temp → fsync → os.replace) |
| Business logic | `NoteService` | CRUD orchestration, FR-01–FR-07 |
| Access control | `PrivacyPolicy` | Blocks unauthorized reads/writes (GOV-01) |
| Audit | `VersionHistory` | Version trail per note (FR-06) |
| CLI shell | `main.py` | Menu-driven terminal interface (Week 6.1) |

## Current Status (Week 6)

| Area | Status |
|------|--------|
| Planning & requirements | ✅ Complete (Sprint 0–4) |
| UML design | ✅ Complete (5 diagrams, Week 4) |
| Design validation | ✅ Complete (traceability audit, Week 5) |
| Core implementation | ✅ 29/29 tests passing |
| CLI App Shell | ✅ Created (Week 6.1) |
| Sprint 2 CRUD (edit/delete) | ⏳ Pending |
| GitHub remote setup | ⏳ Pending |

## Key Constraints

- Stdlib only — no third-party runtime dependencies
- Single-user, local JSON storage (Phase 1)
- No encryption (access-control-only per SZ-06 decision, ADL)
- Python 3.12+

## Deliverable Timeline

| Sprint | Week | Deliverable |
|--------|------|-------------|
| Sprint 0–4 | Weeks 1–5 | Planning, UML, requirements baseline |
| Sprint 5 (Sprint 6) | Week 6 | App shell + Create/List slices |
| Sprint 6+ | Weeks 7–10 | Full CRUD, tests, GitHub CI |
