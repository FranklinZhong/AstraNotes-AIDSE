# AstraNotes — Sprint Log

**Project:** AstraNotes — A Secure, Modular Note-Taking System  

> One entry per Sprint. Add Planning, Review, and Retrospective at the appropriate time.
> Use `backlog.md` to track individual task status.

---

## Sprint 0 — Week 1 (2026-03-30 to 2026-04-01)

**Focus:** Project setup — architecture decisions, initial requirements baseline

### Sprint Goal
Establish the AstraNotes architecture and produce a requirements baseline that can guide
the rest of the quarter.

### Completed
- Architecture Decision Log (3 prompt rounds: weak → strong → refined)
- Initial requirements baseline: FR-1–FR-6, NFR-1–NFR-2, SG-1–SG-2 (10 requirements)
- Code scaffold: `AstraNotes_v1/` with note model, repository interface, service,
  privacy policy, version history, and 5 test files

### Session Logs
| Date | Planned | Completed | Blocked |
|------|---------|-----------|---------|
| 2026-03-30 | Waterfall Gantt + FBI Sentinel analysis | Both done | — |
| 2026-04-01 | ADL + requirements baseline + v1 scaffold | All done | — |

### Sprint Review
All Sprint 0 deliverables pass the Definition of Done:
- ADL traces each design decision to a prompt round with explicit reasoning
- All 10 requirements are in testable "The system shall..." form with backlog/test links
- Code scaffold compiles and all 5 test files run (may not all pass yet)

### Retrospective
+ **What worked:** Iterating prompts (weak → strong → refined) produced a significantly
  better architecture than a single prompt would have.
- **Improve next Sprint:** Requirements need more specificity on access-control rules
  before implementation can begin (gap identified in Sprint 1 planning).

---

## Sprint 1 — Week 2.1 (2026-04-06)

**Focus:** Project governance — Working Agreement, Definition of Done, Product Backlog

### Sprint Goal
Establish the working process for the rest of the project — how work is planned, how AI
is used, and what "done" means for every task.

### Completed
- `working_agreement.md` — 7 agreements covering Sprint cadence, AI usage, prompt logging,
  backlog discipline, duplication prevention, and quality gate
- `definition_of_done.md` — 7 conditions with AstraNotes-specific acceptance criteria
- `backlog.md` — 10 user stories mapped from requirements, prioritized, Sprint-allocated
- `sprint_log.md` — this file (Sprint 0 retrospective + Sprint 1 entry)
- s: Working Agreement (Part 1) + Definition of Done (Part 2)

### Session Logs
| Date | Planned | Completed | Blocked |
|------|---------|-----------|---------|
| 2026-04-06 | 
### Sprint Review
- Working Agreement: 7 conditions, all AstraNotes-specific, zero copied from template
- Definition of Done: 7 conditions, all traceable to architecture layers and requirement IDs
- Backlog: 10 stories, prioritized, Sprint-allocated through Week 10

### Retrospective
+ **What worked:** Writing tests for the lab content before finalizing caught gaps early
  (missing Sprint/Retro terms, word count issues, copied content from sample).
- **Improve next Sprint:** Need to add specificity to SG-1 before Sprint 8 — the access
  control rules (what counts as unauthorized, which error type, where the check lives)
  are not yet written down precisely enough to implement.

---

## Sprint 2 — Week 2.2 (2026-04-08) — COMPLETED

**Focus:** AI-native planning — user stories, backlog, Sprint Zero plan

### Sprint Goal
Produce the full planning baseline: user stories with acceptance criteria, prioritized backlog, and Sprint Zero execution plan.

### Completed
- `planning/user-stories.md` — US-01 to US-06, each with 3 acceptance criteria
- `planning/backlog.md` — prioritized backlog (High/Medium/Low), Sprint allocation
- `planning/sprint-zero-plan.md` — SZ-01 to SZ-07, each with "Done when" condition

### Session Logs
| Date | Planned | Completed | Blocked |
|------|---------|-----------|---------|
| 2026-04-08 | User stories + backlog + sprint zero plan | All done | — |

### Sprint Review
- 6 user stories, all traceable to FR/GOV requirement IDs
- Backlog has explicit prioritization rationale (persistence before edit; privacy design before storage code)
- Sprint Zero plan has zero feature implementation items — setup only

### Retrospective
+ **What worked:** Tracing each user story to a requirement ID made the backlog defensible and easy to review.
- **Improve next Sprint:** Requirements still have ambiguous terms (quickly, responsive, appropriate) — Week 3.1 will address this.

---

## Sprint 3 — Week 3.1 (2026-04-13) — COMPLETED

**Focus:** Requirements Engineering — ambiguity review, edge case analysis, refined requirement baseline

### Sprint Goal
Strengthen the Week 1.2 / 2.2 requirement set by identifying vague language, separating functional from non-functional requirements, and pressure-testing with edge cases using AI assistance.

### Completed
- `planning/requirements.md` — updated with refined baseline alongside preserved original (Week 3.1 section added)
- Key changes to requirements:
  - FR-01 to FR-07: failure behaviors and validation rules made explicit
  - NFR-01: scoped to <500 notes (previously undefined "large")
  - NFR-02: interface boundaries specified
  - NFR-03: new — GOV-02 reclassified as reliability non-functional requirement
  - GOV-01: enforcement point (service layer) and mechanism (ADL) specified
  - GOV-03 / GOV-04: coverage and record-keeping requirements made specific
  - 6 explicit scope assumptions added (single-user, text-only, local-first, etc.)

### Session Logs
| Date | Planned | Completed | Blocked |
|------|---------|-----------|---------|
| 2026-04-13 | Ambiguity review + refined requirements + lab submission | All done | — |

### Sprint Review
All 7 Definition of Done conditions satisfied:
1. Traceability — all refined requirements retain FR/NFR/GOV IDs
2. Self-explainable — every change has a documented reason
3. Architecture fit — requirements still map to service/policy/repository layers
4. Validated — 6 AI sessions pressure-tested ambiguity and edge cases
5. Security/privacy — GOV-01 and NFR-03 failure paths explicitly specified
6. Buildable foundation — refined baseline ready to guide Week 4 UML design
7. Sprint Review ready — each requirement change can be explained from memory

### Retrospective
+ **What worked:** Using AI specifically as a critic ("would two engineers build the same thing?") surfaced ambiguities that weren't obvious from reading the requirements alone.
- **Improve next Sprint:** Some requirements (especially GOV-01 privacy mechanism) still defer to the ADL — the actual design decision needs to be locked down before Week 4 UML work begins.

---

## Sprint 4 — Week 3.2 + Week 4 (2026-04-14 to 2026-04-22) — COMPLETED

**Focus:** Governance review + UML design package

### Sprint Goal
Complete the governance and ethics review, apply its conclusions to project artifacts, and produce a full UML design package (class / object / use case / activity / deployment diagrams).

### Completed
- `architecture_decision_log.md` — Week 3.2 additions: pytest dev dependency, SZ-06 open decision, G-01~G-06 governance gaps, 4 AI data handling rules
- `working_agreement.md` — Agreement 8-10 added (AI synthetic data, code verification checklist, privacy disclosure discipline)
- `backlog.md` — GOV-B-01~05 governance backlog items added
- `planning/DESIGN.md` — authoritative design reference created from UML package

### Session Logs
| Date | Planned | Completed | Blocked |
|------|---------|-----------|---------|
| 2026-04-14 | Governance review memo + ADL/WA/Backlog updates | All done | — |
| 2026-04-21 | v4.1 artifact PlantUML + Draw.io + Written Rationale | All done | — |
| 2026-04-22 | v4.2 artifact Draw.io v2 (html=0 rendering fix) | All done | — |

### Sprint Review
All Definition of Done conditions satisfied:
1. Each UML diagram traces back to specific FR/NFR/GOV requirement IDs
2. Written Rationale explains design choices (atomic write, interface separation, privacy-at-service-layer) without referencing the AI session
3. All diagrams are cross-consistent (class names match across all 5 diagram types)
4. Governance gaps G-01~G-06 documented with target sprints
5. SZ-06 open decision formally recorded in ADL

### Retrospective
+ **What worked:** The 3-layer architecture (Service → Policy/History → Repository) proved stable across all 5 diagram types — no contradictions found during v4.2 artifact review.
- **Improve next Sprint:** 3 gold-plating items identified (`author_id`, `tags`, UC7/UC8) need explicit decisions before implementation — carried into Week 5 traceability audit.

---

## Sprint 5 — Week 5 (2026-04-26 to 2026-04-29) — COMPLETED

**Focus:** Design validation, requirements-to-UML traceability audit, Midterm 1

### Sprint Goal
Validate that the Week 4 UML design actually supports the Week 3.1 refined requirements. Identify gaps before implementation begins.

### Completed
- `planning/TRACEABILITY.md` — full traceability audit results stored in project
- `planning/DESIGN.md` — "Known Design Issues" section added: Issues 1-5 from audit
- Midterm 1 completed 2026-04-29 (25 questions, Week 1.1–5.1 scope)
- 90-question practice bank generated (`Mid-Term1/practice_questions.md`)

### Session Logs
| Date | Planned | Completed | Blocked |
|------|---------|-----------|---------|
| 2026-04-27 | Traceability matrix + TRACEABILITY.md | All done | — |
| 2026-04-28 | Midterm 1 practice questions (90 items) | All done | — |
| 2026-04-29 | Midterm 1 exam | Completed | — |

### Sprint Review
Traceability audit findings:
- FR-05, NFR-02: **Fully Traced** — atomic write and interface separation well-supported
- FR-01, FR-02, NFR-03, GOV-01: **Partially Traced** — structural support strong; behavioral coverage incomplete
- FR-04: **Weakly Traced** — SZ-06 still open at time of audit
- 3 gold-plating UML elements identified (author_id, tags, UC7/UC8)

### Retrospective
+ **What worked:** Systematically checking each requirement against all 4 diagram types caught the FR-01 body-validation contradiction that would have caused a bug in Sprint 1 implementation.
- **Improve next Sprint:** SZ-06 must be resolved before any FR-04 / GOV-01 implementation. Also need GOV-B-02 checklist and GOV-B-04 threat scope before Sprint 1 coding begins.

---

## Sprint 6 — Week 6 (2026-05-03 to present) — IN PROGRESS

**Focus:** Pre-implementation cleanup + first implementation slice (Class 2)

### Sprint Goal
Close all Sprint 1 prerequisites (SZ-06, GOV-B-02~05, design issue decisions), then build the App Shell and first 1-2 feature slices as Sprint6 deliverable deliverable.

### Completed (Class 1 pre-work, 2026-05-05)
- **SZ-06 decision**: Option A — access-control-only; formal entry in `architecture_decision_log.md`
- **DESIGN.md**: All 4 open design issues resolved (author_id → hardcoded sentinel; tags → not in service API; VersionHistory → internal-only; activity diagram gaps → flows inferred)
- **GOV-B-02**: `planning/ai_code_validation_checklist.md` created (25-item checklist)
- **GOV-B-03**: SZ-06 decision written into ADL
- **GOV-B-04**: `planning/threat_scope_statement.md` created
- **GOV-B-05**: Single-user constraint recorded in ADL + DESIGN.md
- **FR-01 bug fix**: `note.py` body validation corrected — empty body now valid (2026-05-05)
- **`note_service.py`**: `body` parameter default set to `""` (optional per FR-01)
- All planning files moved to `planning/` directory; per-week summary MDs created (Week 1-6)
- 29 tests passing after FR-01 fix

### Pending (Class 2)
- [ ] Confirm app direction (CLI recommended — consistent with existing Python stack)
- [ ] Build App Shell (entry point, menu, command dispatcher)
- [ ] Implement feature slice 1: `create_note` end-to-end with CLI
- [ ] Implement feature slice 2: `list_notes` or `get_note` with CLI
- [ ] Write Sprint6 deliverable PDF (6 sections: direction, structure, shell, slices, traceability, AI reflection)

### Session Logs
| Date | Planned | Completed | Blocked |
|------|---------|-----------|---------|
| 2026-05-03 | Week 6.1 translation | Done | — |
| 2026-05-05 | Pre-implementation doc cleanup + code fix | Done | — |
| Class 2 | App Shell + Sprint6 deliverable slices | Pending | — |

### Sprint Review
*To be completed after Class 2.*

### Retrospective
*To be completed after Class 2.*

---

## Sprint 7 — SqliteNoteRepository + FastAPI Notes API (Week 7, 2026-05-11)

**Goal:** Implement the full notes REST API using TDD; replace JSON file storage with SQLite for the web layer.

**Sprint Backlog:**
- [x] `SqliteNoteRepository` implementing `AbstractNoteRepository` via SQLAlchemy Core
- [x] `POST /notes/`, `GET /notes/`, `GET /notes/{id}`, `PATCH /notes/{id}`, `DELETE /notes/` endpoints
- [x] `NoteCreate`, `NoteUpdate`, `NoteResponse`, `NoteListResponse` Pydantic schemas
- [x] Integration tests (test_notes_api.py): US-01~05 test coverage, TNA-01~04
- [x] Repository unit tests (test_sqlite_repository.py): TSQ-01~12 (CRUD + tags + version field)
- [x] `?tags=` query filter (AND semantics via `set.issubset()`)

**Key Decisions:**
- SQLAlchemy Core chosen over ORM (simpler for current scale; direct SQL control)
- Test isolation: named in-memory SQLite URI (`file:{uuid}?mode=memory&cache=shared`) per test — StaticPool approach rejected after discovering it caused cross-test contamination
- `HTTPBearer(auto_error=False)` to get 401 (not 403) for missing tokens

**AI Role:**
- Generated `SqliteNoteRepository` scaffold and schema definitions
- Human identified StaticPool isolation bug; fixed via named in-memory URI approach
- Human verified all Pydantic validators against domain model behavior before accepting

**Outcome:** 58 tests passing (29 domain + 17 repository + 5 auth + 5 notes API + 2 health); CI green on Python 3.11 and 3.12.

**Lessons Learned:**
- SQLite in-memory isolation is non-trivial in multi-connection test environments
- `HTTPBearer` default behavior differs between FastAPI versions — pin and test against both 3.11 and 3.12 early

---

## Sprint 8 — Version History + Collaborative Git Workflow (Week 8, 2026-05-18)

**Goal:** Add version history with revert capability; practice collaborative branching and PR workflow; improve UI.

**Sprint Backlog:**
- [x] `note_versions` table in SQLite; `add_version_snapshot()`, `get_versions()`, `revert_to_version()` in `SqliteNoteRepository`
- [x] `GET /notes/{id}/versions` and `POST /notes/{id}/revert/{version}` endpoints (`routers/history.py`)
- [x] `NoteService.revert_note()` method
- [x] TSQ-13~17: repository unit tests for version history
- [x] TVH-01~05: API integration tests for version history endpoints
- [x] UI: version history panel (collapsible), toast error system (replaces console.error), tags input
- [x] Branching workflow: `feature/search-filter` PR (tags schema + filter) + `test/title-validation` PR (whitespace title fix + 3 tests)
- [x] CI fixed: `HTTPBearer(auto_error=False)` resolves 401/403 discrepancy between FastAPI versions

**Key Decisions:**
- Version snapshots stored in separate `note_versions` table (not as JSON blob in notes table) — cleaner schema, easier to query
- UI toast system preferred over `alert()` — non-blocking, dismissible, consistent with web UX patterns
- `feature/search-filter` PR required `Request changes` review — missing docstring for AND semantics; human judgment call

**AI Role:**
- Generated version history table schema and repository methods
- Generated PR descriptions and review question templates
- Human identified HTTPBearer CI failure; human made final merge decision on both PRs
- Human rejected AI suggestion to make tag filter case-insensitive (canonicalization belongs at creation time)

**Outcome:** 70 tests passing; version history fully functional; 2 PRs merged via formal review workflow; CI passing.

**Lessons Learned:**
- CI matrix (3.11 + 3.12) caught a real version-specific behavior difference (FastAPI HTTPBearer)
- PR review process catches scope and documentation gaps that code review alone misses

---

## Sprint 9 — Note Passwords, Auto-Save, Test Quality (Week 9, 2026-05-27)

**Goal:** Add note-level password protection and emergency unlock; implement auto-save UX; apply Prompt Bank test quality improvements.

**Sprint Backlog:**
- [x] Note-level bcrypt password: `note_password_hash` field in `Note` + SQLite; `X-Note-Password` header enforcement in `GET /notes/{id}` and `PATCH /notes/{id}` via `_require_note_password()`
- [x] `POST /notes/{id}/emergency-unlock` endpoint: verify account password, clear `note_password_hash`
- [x] Auto-save UI: 2-second debounce on title/body/tags changes; `● Unsaved` / `⟳ Saving…` / `✓ Saved` status indicator; `_isSaving` concurrency guard; timer cleanup on note switch/logout
- [x] Visibility toggle auto-save: Public→Private and Private→Public transitions save immediately after confirmation
- [x] Unicode title validation fix: `re.search(r'\S', v)` replaces `v.strip()` in both Pydantic validator and domain model (catches U+00A0 non-breaking spaces)
- [x] Prompt Bank exercise (7 prompts applied to test suite):
  - TVH-02 fix: `versions[1]` positional index → `by_version` version-number keyed assertion
  - TNA-09: AND tags semantics test
  - TNA-10/11/12: note password 401/403/200 branches
  - TNA-13/14: PATCH/DELETE non-owner → 403
  - TNA-15: unicode title validation

**Key Decisions (see ADR-PWD-01, ADR-UNLOCK-01, ADR-AUTOSAVE-01):**
- bcrypt for note passwords (consistent with account password approach; no plaintext ever stored)
- 2-second debounce for auto-save (balance between responsiveness and API call volume)
- Emergency unlock clears hash rather than recovering password (impossible with bcrypt)

**AI Role:**
- Prompt Bank: AI critiqued test suite across 7 dimensions; human verified every finding against source code before accepting
- AI-generated TVH-02 fix, AND tags test, unicode fix all accepted after verification
- AI suggestion to add emergency-unlock tests rejected for Week 9 scope; deferred to Week 10 security review
- AI suggestion to split TSQ-14 into separate tests rejected (unnecessary complexity)

**Outcome:** 81 tests at Sprint 9 close (visibility-drift failures resolved in Sprint 10 cleanup); all Sprint 9 features functional; Week 9 collaboration log completed. Final count after Sprint 10: 84 passing, 0 failures.

**Lessons Learned:**
- Prompt Bank is a structured critique tool: AI finds patterns, human verifies against code
- Pre-existing test failures must be documented (not hidden) — they represent design decisions, not bugs
- Unicode edge cases (` `) are not caught by Python's `str.strip()` — use `re.search(r'\S', v)`

---

## Sprint 10 — CI/CD Workflow Design and Pipeline Improvement (Week 10, 2026-06-01)

**Goal:** Apply Week 10.1 CI/CD lab concepts to AstraNotes; implement advisory vs blocking gate design; create formal CI/CD workflow deliverable.

**Sprint Backlog:**
- [x] Verify all 81 tests passing locally after Sprint 9 visibility-drift resolution
- [x] Redesign `.github/workflows/ci.yml` with two-job structure: `stable-checks` (blocking) + `advisory-checks` (non-blocking, `continue-on-error: true`)
- [x] Add JUnit XML artifact upload (`--junitxml`) for proper test result evidence
- [x] Advisory job: `-W error::DeprecationWarning` check surfaces 213 `datetime.utcnow()` deprecation warnings as technical debt signal
- [x] Create `planning/cicd_workflow_plan.md` — complete lab deliverable (6 sections)
- [x] Scenario B selected: flaky/known technical debt gate (pre-existing visibility-drift tests + deprecation warnings)

**Key Decisions:**
- `stable-checks` job is blocking: 81 stable unit + integration tests, fast (< 8 sec), consistent signal since Sprint 7
- `advisory-checks` job is non-blocking: deprecation-warnings-as-errors is a real signal but currently fails by design; `continue-on-error: true` ensures it never stops valid merges
- JUnit XML replaces `.pytest_cache/` artifact: structured test results are more useful evidence for reviewers
- Coverage threshold gate rejected: premature — legacy `json_file_note_repository.py` intentionally has lower coverage (architectural decision, not a gap)

**AI Role:**
- AI proposed two-job YAML structure based on lab prompt bank
- AI suggested `-x` flag and 80% coverage gate; human reviewed both
- `-x` deferred (suite < 8 sec; worth revisiting if suite grows); coverage gate rejected (penalizes intentional architectural scope decisions)
- All CI changes verified locally before push

**Outcome:** CI pipeline updated with advisory vs blocking gate design; `cicd_workflow_plan.md` covers all 6 lab sections; 81 tests still passing; deprecation technical debt surfaced as advisory signal.

**Lessons Learned:**
- `continue-on-error: true` is the key YAML setting that makes a job advisory without requiring a separate workflow file
- Advisory checks are most valuable when they have a clear path to becoming blocking (the deprecation check becomes blocking after `datetime.utcnow()` replacement)
- JUnit XML artifacts provide better evidence than cache directories — structured data is reviewable in GitHub PR summaries

---

## Sprint Template (copy for each new Sprint)

```markdown
## Sprint N — Week X (YYYY-MM-DD to YYYY-MM-DD)

**Focus:** 

### Sprint Goal

### Completed
-

### Session Logs
| Date | Planned | Completed | Blocked |
|------|---------|-----------|---------|
| | | | |

### Sprint Review

### Retrospective
+ **What worked:** 
- **Improve next Sprint:** 
```
