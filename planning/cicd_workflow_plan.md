# AstraNotes CI/CD Workflow Plan

**Course:** CSEN 296B-2 AI-Driven Software Development  
**Week:** 10.1 — CI/CD, DevOps, and MLOps Foundations  
**Lab deliverable:** CI/CD workflow plan and operational risk note  
**Date:** 2026-06-01  

---

## 1. Repo State Summary

| Item | Status |
|------|--------|
| GitHub repository | Public, accessible |
| Local build | `uvicorn app.main:app --reload` — functional |
| Test suite | 81 tests: 81 passing, 0 failures, 213 deprecation warnings |
| Existing CI | GitHub Actions (`.github/workflows/ci.yml`), Python 3.11 + 3.12 matrix |
| Branches | `main` (primary), `develop` (feature integration) |
| Known technical debt | `datetime.utcnow()` deprecated in Python 3.12+; 213 warnings surfaced by pytest |
| AI-assisted features | AI used for test critique (Sprint 9 Prompt Bank); no AI inference at runtime yet |
| Recent changes | Sprint 9: note-level bcrypt password protection, emergency unlock, auto-save UI, unicode fix |

---

## 2. Selected Scenario

**Scenario B — Flaky test noise / known technical debt gate**

**Why this scenario fits AstraNotes:**  
The project had 6 pre-existing test failures through Sprint 9 caused by a visibility model drift (tests expected `visibility="private"` default; implementation uses `visibility="public"` with access-control-only privacy). These were documented and eventually resolved.

More actively today: the test suite produces **213 deprecation warnings** from `datetime.utcnow()` calls in `AstraNotes_v1/note.py` and `json_file_note_repository.py`. In Python 3.12+, these will escalate. Running with `-W error::DeprecationWarning` causes widespread test failures — a useful signal, but not stable enough to be a merge blocker today.

**This is the canonical Scenario B situation:** a check that gives genuine useful information, but is not yet stable enough to be a blocking gate.

---

## 3. Check Table

| Stage | Check | Advisory or Blocking? | Why | Evidence Produced |
|-------|-------|-----------------------|-----|-------------------|
| Commit | Build / startup check (import validation) | Blocking | Catches obvious syntax and import errors before any test runs | Exit code 0/1 in CI log |
| Commit | Stable unit + integration tests (`AstraNotes_v1/tests/` + `app/tests/`) | Blocking | 81 stable, high-signal tests; consistently pass; represent the agreed DoD | JUnit XML (`test-results-py3.11.xml`, `test-results-py3.12.xml`), uploaded as artifact |
| Pull Request | Same stable test suite as commit (both Python versions) | Blocking | PR cannot introduce regressions; both Python versions must pass | Artifact: stable-test-results-py3.11 / py3.12 |
| Pull Request | Deprecation-warning check (`-W error::DeprecationWarning`) | Advisory | 213 current warnings = known technical debt; useful signal but not stable enough to block | Advisory JUnit XML artifact; job uses `continue-on-error: true` |
| Release | Manual release checklist (README, SDLC artifacts, CI green, demo recorded) | Blocking | Ensures release evidence exists before submission; no automated equivalent | `collaboration_log.md` Release Checklist section |

**Rationale for advisory vs blocking classification:**

- **Stable tests are blocking** because they are fast (< 8 seconds), consistently pass, cover all core business logic, and have stable signal since Sprint 7.
- **Deprecation check is advisory** because it currently fails (213 warnings become errors), making it technically a "flaky gate" — it would block valid work if set as a hard gate. It should become blocking only after `datetime.utcnow()` is replaced with `datetime.now(datetime.UTC)` across the codebase.
- **Release checklist is manual-blocking** because no automated tool can verify demo video quality or deployment success; human judgment is required.

---

## 4. Pipeline Outline

The updated `.github/workflows/ci.yml` implements two jobs:

```yaml
# Trigger: push to main/develop, PR to main

jobs:

  stable-checks:          # BLOCKING — never merge if this fails
    matrix: [3.11, 3.12]
    steps:
      - checkout
      - setup-python
      - cache pip
      - install requirements.txt + requirements-dev.txt
      - pytest AstraNotes_v1/tests/ app/tests/ -q --tb=short --junitxml=...
      - upload JUnit XML as artifact (14-day retention)

  advisory-checks:        # ADVISORY — continue-on-error: true; never blocks merge
    matrix: [3.11, 3.12]
    steps:
      - checkout
      - setup-python
      - cache pip
      - install dependencies
      - pytest ... -W error::DeprecationWarning --junitxml=... || true
      - upload advisory JUnit XML as artifact
```

**Gate decisions:**

| Check | Blocks merge? | Reasoning |
|-------|--------------|-----------|
| `stable-checks` passes | Yes | Core signal — stable, fast, high-value |
| `advisory-checks` passes | No | Currently failing by design; tracks technical debt without friction |
| Both Python versions pass | Yes (for stable) | Prevents Python version-specific regressions |

**What should wait until later:**
- Security scan (e.g., `bandit`, `safety`) — not yet integrated; should be advisory first
- Coverage threshold gate — useful metric but too early to enforce a minimum
- End-to-end workflow tests (`user_scenario_tests.py`) — requires a live server; too complex for current CI scope

---

## 5. Operational Risk Note

**Risk:** Deprecation warnings become blocking failures in a future Python version upgrade.

**Why it matters:**  
`datetime.utcnow()` is deprecated as of Python 3.12 and will be removed in a future release. The codebase currently generates 213 such warnings. If the project upgrades to Python 3.13+ without addressing these, the stable unit tests will fail unexpectedly — breaking the blocking gate and stopping all merges until resolved. This is a time-bomb in the current codebase.

**Control:**  
The advisory-checks job already surfaces this risk on every PR via `-W error::DeprecationWarning`. The artifact output (`advisory-results-py3.1x.xml`) documents how many tests are affected. When the advisory check passes consistently (i.e., after `datetime.utcnow()` is replaced with `datetime.now(datetime.UTC)`), the advisory check can be promoted to a blocking gate.

**Owner:**  
Any developer modifying `AstraNotes_v1/note.py` or `json_file_note_repository.py` should address the deprecation in the same PR. The CI advisory report makes this visible on every PR review.

---

## 6. AI Critique and Human Refinement

**Prompt used (Prompt 2 from Week 10.1 Prompt Bank):**
> "Critique this AstraNotes CI/CD plan. Identify which gates are too noisy, which important checks are missing, and which checks should not be blocking yet."

**AI suggestion 1 (accepted):**  
AI suggested that running `pytest` with `-x` (stop on first failure) in the blocking job would provide faster feedback on commits. Accepted: adding `-x` to the stable-checks run would halve the feedback loop when a test breaks, making the gate more actionable.

*Human decision:* `-x` not added in this version because the test suite is fast enough (< 8 seconds total). Worth reconsidering if the suite grows beyond 30 seconds. Documented for future consideration.

**AI suggestion 2 (rejected):**  
AI suggested adding a `coverage` gate requiring minimum 80% line coverage as a blocking check.

*Human decision:* Rejected. Coverage thresholds are premature at this stage — the project has comprehensive business logic coverage but intentionally minimal coverage of the legacy `AstraNotes_v1/repositories/json_file_note_repository.py` (JSON-based legacy storage, no longer primary). A blanket 80% requirement would penalize deliberate architectural decisions. Coverage should be advisory, not blocking, until we define which modules are in scope.

**Final human decision:**  
Two-job design (stable-checks blocking, advisory-checks non-blocking) is the correct approach for the current project maturity. The deprecation check is the right candidate for the advisory job because it is genuinely informative, currently unstable as a gate, and has a clear path to becoming a blocking gate after the `datetime.utcnow()` fix.
