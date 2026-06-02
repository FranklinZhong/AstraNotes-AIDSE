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

Four prompts from the Week 10.1 Prompt Bank were applied to the actual AstraNotes repo state. Results and human decisions are recorded below.

---

### Prompt 1 — CI/CD Plan Draft

> *"Given this AstraNotes repo state, suggest commit, PR, and release checks. Label each as advisory or blocking and explain why."*

**AI output (key suggestions beyond our current plan):**

| Stage | Suggested check | Gate | AI reasoning |
|-------|----------------|------|--------------|
| Commit | `python -m py_compile app/**/*.py` | Blocking | Syntax-only check, zero false positives, catches typos before test runner |
| PR | Import smoke: `python -c "from app.main import app"` | Advisory | Catches import-time config errors not caught by unit tests |
| Release | `bandit -r app/` security scan | Advisory | Good practice; unfamiliar tool baseline needed before making blocking |

**Human decision:**
- `py_compile` check: **deferred**. The existing pytest run already imports all modules, making a separate `py_compile` step redundant at current scale. Will reconsider if test startup time grows significantly.
- Import smoke test: **noted for future**. The `conftest.py` `TestClient` instantiation already validates app startup on every test run.
- `bandit` scan: **agreed — should be added as advisory**. Documented in Operational Risk section; not added to `ci.yml` in Sprint 10 to avoid scope creep.

---

### Prompt 2 — Quality Gate Critique

> *"Critique this proposed AstraNotes CI/CD plan. Identify which gates are too noisy, which important checks are missing, and which checks should not be blocking yet."*

**AI output:**

*Too noisy / misclassified:* None found — `continue-on-error: true` on advisory-checks correctly prevents merge noise. ✅

*Missing checks (AI identified):*
1. **Dependency vulnerability scan** (`safety check` or `pip-audit`) — `requirements.txt` pins exact versions but no CVE check exists. Advisory candidate.
2. **Startup smoke test** — `python -c "from app.main import app"` catches import-time configuration errors. Currently implicit in conftest, not explicit in CI.
3. **Advisory-only on develop pushes** — running advisory-checks on every `develop` push creates noise; should trigger only on PRs to `main`.

*Over-automation risk:* None in current design; two-job structure avoids it.

**Human decision:**
- Vulnerability scan: **accepted as future work**. `pip-audit` is lightweight and should be added as an advisory check in Sprint 11. Documented in sprint backlog.
- Startup smoke: **rejected as redundant** (see Prompt 1 reasoning above).
- Advisory trigger scope: **accepted**. Will narrow advisory-checks to `pull_request` trigger only in a follow-up commit — reduces noise on `develop` branch pushes without affecting PR review signal.

---

### Prompt 8 — Advisory vs Blocking Classification

> *"Given these AstraNotes checks, classify each as advisory or blocking: build check, stable unit tests, flaky UI test, integration smoke test, coverage report, AI summary quality evaluation, security scan."*

**AI classification output:**

| Check | AI Classification | AI Reasoning |
|-------|-----------------|--------------|
| Build / syntax check | Blocking | Binary pass/fail, zero false positives |
| Stable unit tests (81) | Blocking | High signal, consistent, fast, represents DoD |
| Flaky UI test | Advisory | Non-deterministic → alarm fatigue if blocking |
| Integration smoke test | Blocking (if stable) | Our `StaticPool` conftest makes these stable |
| Coverage report | Advisory | Threshold enforcement premature without baseline |
| AI summary quality eval | Advisory | No runtime AI yet; monitoring-only for now |
| Security scan (`bandit`) | Advisory | Unfamiliar tool; false positives likely initially |

**Human decision:** AI classification matches our implemented design exactly for the first five items. The AI correctly identifies that our integration tests are stable (due to `StaticPool`) and thus blocking-worthy — this is a non-obvious judgment that the AI got right because we provided the conftest context. Classification accepted as-is.

---

### Prompt 4 — Operational Risk Identification

> *"Identify the top operational risks for AstraNotes if we add CI/CD and AI-assisted summary features."*

**AI output (top 3 risks):**

1. **Deprecation time-bomb** — `datetime.utcnow()` in `note.py` and `json_file_note_repository.py` will cause test failures on Python 3.13+. Advisory check surfaces it now; must resolve before any Python version upgrade.
2. **Advisory fatigue** — if `advisory-checks` is consistently red, developers learn to ignore it. The advisory signal degrades to background noise. Mitigation: set a target date to promote advisory→blocking after deprecation fix.
3. **AI output drift (future)** — once AI summaries are added, prompt/model changes can silently degrade quality with no automated detector. Mitigation: create a golden-output fixture (`tests/eval/golden_summaries.json`) as a future advisory check.

**Human decision:**
- Risk 1: **already mitigated** by advisory-checks job. Accepted.
- Risk 2: **important new insight**. Added promotion target: advisory-checks should become blocking after `datetime.utcnow()` is replaced (target: before final submission 2026-06-03).
- Risk 3: **out of scope for Sprint 10** — AstraNotes has no runtime AI feature. Documented as a future architectural consideration in `architecture_decision_log.md` backlog.

---

### Summary of Human Refinements

| AI Suggestion | Decision | Reason |
|--------------|----------|--------|
| Add `py_compile` check | Deferred | Redundant with existing pytest import |
| Add import smoke test | Deferred | Already implicit in `TestClient` conftest |
| Add `bandit` security scan (advisory) | Accepted → future work | Added to Sprint 11 backlog |
| Narrow advisory-checks to PR trigger only | Accepted → follow-up commit | Reduces develop-branch noise |
| Advisory fatigue risk | Accepted as new operational risk | Set promotion target date |
| AI summary drift golden fixture | Noted → future architectural item | Out of scope until AI feature exists |
