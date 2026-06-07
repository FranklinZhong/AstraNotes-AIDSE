# AstraNotes — Final Submission Checklist

**Course:** CSEN 296B-2 AI-Driven Software Development · Santa Clara University · Spring 2026  
**Student:** Wentao (Franklin) Zhong  
**Repository:** https://github.com/FranklinZhong/AstraNotes-AIDSE

This document maps each grading criterion to the specific artifacts in this repository.

---

## 1. Requirements & Planning Artifacts ✅

| Artifact | File |
|----------|------|
| Initial requirements baseline (FR/NFR/GOV) | `planning/initial_requirements.md` |
| Refined requirements baseline (Week 3.1) | `planning/requirements.md` |
| Scope summary & web pivot decision | `planning/Scope_Summary.md` |
| User stories (US-01 – US-10) | `planning/user-stories.md` |
| Product backlog (prioritized, Sprint-allocated) | `planning/backlog.md` · `planning/backlog_v1_week2.md` |
| Sprint backlogs | `planning/sprint-backlog.md` · `planning/sprint7-backlog.md` |
| Sprint log (Sprint 0 – Sprint 10 with retrospectives) | `planning/sprint_log.md` |
| Sprint Zero plan | `planning/sprint-zero-plan.md` |
| Working Agreement (14 agreements) | `planning/working_agreement.md` |
| Definition of Done | `planning/definition_of_done.md` |
| Executive one-pager | `planning/executive-one-pager.md` |
| Functional specification (v2.0 web) | `planning/functional_spec.md` |
| PRD outline | `planning/PRD_Outline.md` |
| Design outline | `planning/Design_Outline.md` |

---

## 2. Architecture & UML Artifacts ✅

| Artifact | File |
|----------|------|
| Class diagram | `UML/01_class_diagram.drawio` |
| Object diagram | `UML/02_object_diagram.drawio` |
| Use case diagram | `UML/03_usecase_diagram.drawio` |
| Activity diagram | `UML/04_activity_diagram.drawio` |
| Deployment diagram | `UML/05_deployment_diagram.drawio` |
| Architecture Decision Log (ADR-WEB-01/02, ADR-PWD-01, ADR-UNLOCK-01, ADR-AUTOSAVE-01 + governance) | `planning/architecture_decision_log.md` |
| Full design package | `planning/DESIGN.md` |
| UML diagram summary (Lucidchart export notes) | `planning/lucid-diagrams-summary.md` |
| README architecture section (three-layer diagram + decision table) | `README.md` |

> **Note:** UML files are in draw.io (`.drawio`) format. Open at https://app.diagrams.net or use the VS Code draw.io extension to view.

---

## 3. Traceability & Verification Materials ✅

| Artifact | File |
|----------|------|
| Requirements-to-UML traceability matrix (pre-Sprint 1 audit + Sprint 7/8/9 post-implementation update) | `planning/TRACEABILITY.md` |
| AI code validation checklist | `planning/ai_code_validation_checklist.md` |
| AI interaction log (28 interactions, W1–W10, accepted / refined / rejected outcomes) | `planning/ai_interaction_log.md` |
| Collaboration log (human–AI workflow, SAST/DAST, release checklist) | `planning/collaboration_log.md` |

---

## 4. Source Code ✅

| Component | Location |
|-----------|----------|
| FastAPI web layer (auth, notes, history routers; schemas; SQLite adapter; JWT; static UI) | `app/` |
| Domain layer — pure Python, framework-free (Note model, NoteService, PrivacyPolicy, VersionHistory, AbstractNoteRepository, JsonFileNoteRepository) | `AstraNotes_v1/` |
| Application entry point | `app/main.py` · `main.py` |
| Single-page web UI (HTML/CSS/JS) | `app/static/index.html` |
| CI/CD pipeline | `.github/workflows/ci.yml` |
| Dependencies | `requirements.txt` · `requirements-dev.txt` |

**Key features implemented:** JWT multi-user auth · full note CRUD · owner-only access control (PrivacyPolicy) · note-level bcrypt password · emergency unlock · version history · auto-save · sidebar search · tags AND filter · unicode title validation

---

## 5. Test Artifacts ✅

**84 automated tests — 0 failures (Python 3.11 + 3.12, CI green)**

| Test File | Count | Level | Coverage |
|-----------|-------|-------|----------|
| `AstraNotes_v1/tests/test_note_model.py` | 11 | Unit | Note entity, unicode validation |
| `AstraNotes_v1/tests/test_service.py` | 5 | Unit | NoteService CRUD + error paths |
| `AstraNotes_v1/tests/test_privacy_policy.py` | 6 | Unit | Access control rules |
| `AstraNotes_v1/tests/test_repository.py` | 7 | Unit | JsonFile repository adapter |
| `AstraNotes_v1/tests/test_version_history.py` | 3 | Unit | Version snapshot model |
| `app/tests/test_sqlite_repository.py` | 17 | Integration | SQLite adapter CRUD + version history (TSQ-01–17) |
| `app/tests/test_notes_api.py` | 23 | Integration | HTTP endpoints, passwords, access control (TNA-01–18) |
| `app/tests/test_version_history_api.py` | 5 | Integration | Version history API (TVH-01–05) |
| `app/tests/test_auth.py` | 5 | Integration | Register / login flows |
| `app/tests/test_health.py` | 2 | Integration | Health endpoint |

| Planning Document | File |
|-------------------|------|
| Unit test plan | `planning/unit_test_plan.md` |
| Feature test plan | `planning/feature_test_plan.md` |
| Sprint test plan | `planning/sprint-test-plan.md` |
| Sprint test execution reports | `planning/sprint-test-execution.md` · `planning/sprint7-test-execution.md` |
| Testing strategy | `planning/week7-testing-strategy.md` |
| Scenario tests (150 live-server scenarios) | `app/tests/scenario_tests.py` · `app/tests/scenario_tests_extended.py` |

Run all tests:
```bash
python -m pytest -q
# 84 passed, 0 failed
```

---

## 6. Security, Deployment & Maintenance Notes ✅

| Artifact | File |
|----------|------|
| Threat scope statement (in-scope / out-of-scope threats, SAST summary) | `planning/threat_scope_statement.md` |
| Deployment plan (Render, environment variables, build/start commands, rollback) | `planning/deployment_plan.md` |
| Maintenance plan (monitoring, bug response, dependency audit, security hardening) | `planning/maintenance_plan.md` |
| CI/CD workflow plan (blocking vs. advisory gate design, prompt bank findings) | `planning/cicd_workflow_plan.md` |
| CI/CD pipeline implementation | `.github/workflows/ci.yml` |
| Environment variable template | `.env.example` |

---

## 7. README with Setup & Usage Instructions ✅

**File:** `README.md`

Sections covered:
- **Features** — full feature list
- **Quick Start** — prerequisites, install, run locally (`uvicorn app.main:app --reload`)
- **Architecture** — three-layer diagram, key decision table, links to ADL
- **API Reference** — all 11 endpoints with method, path, and description
- **Testing** — how to run tests, test result table, scenario test instructions
- **Project Artifacts** — table of all 20+ SDLC planning documents with week references
- **AI-Native Development Process** — accepted / refined / rejected outcome examples
