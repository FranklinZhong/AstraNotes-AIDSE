# AstraNotes — Working Agreement

**Project:** AstraNotes — A Secure, Modular Note-Taking System  
**Established:** 2026-04-06  

---

## How This Project Is Governed

AstraNotes runs in weekly Sprints. At the start of each Sprint, the developer selects 2–3 tasks from
the backlog that match the week's learning objective. At the end, run a Sprint Review
against the Definition of Done and write a two-sentence retrospective.

---

## Agreements

1. **Sprint cadence and tracking**  
   Each session opens with a one-line goal and closes with a three-line log:
   what I planned, what I completed, and what is blocked.
   This is the stand-up equivalent for a solo project.

2. **AI as a starting point, not a decision**  
   Every AI suggestion must connect to a specific AstraNotes requirement (FR, NFR, or SG)
   before it moves forward. General-purpose output that does not map to the project
   is not accepted.

3. **AI acceptance gate**  
   Before any AI-generated code enters AstraNotes, I must be able to trace it through
   the relevant modules — NoteService, PrivacyPolicy, repository — without re-reading
   the original prompt. If I cannot, I re-prompt rather than accept.

4. **Prompt log**  
   Every significant AI session is recorded in `prompt_log.md`:
   `[Date] [Module] [what I asked] → [accepted / changed / rejected — one-line reason]`.
   Decisions made in Week 2 must still be traceable in Week 10.

5. **Backlog discipline**  
   If AI proposes something outside the current backlog (FR-1–FR-6, NFR-1–NFR-2, SG-1–SG-2),
   it is logged as a candidate for a future Sprint — not added to the current one.

6. **No parallel modules**  
   Before building anything new, I check whether an existing AstraNotes module already
   handles it. If so, I extend it rather than creating a parallel version.

7. **Done means done**  
   A task is not complete because it compiles or reads well.
   It must pass every condition in the Definition of Done before leaving the Sprint.

---

## Sprint Retrospective Format

At the end of each Sprint, append one entry to `sprint_log.md`:

```
Sprint N Retrospective — YYYY-MM-DD
+ What worked:
- What to improve next Sprint:
```

---

*This agreement applies to all AstraNotes work across the project lifecycle.*

---

## Week 3.2 Governance Addendum (2026-04-14)

The following rules were added after the Week 3.2 governance and ethics review. They extend the original agreements and are equally binding.

### Agreement 8 — AI Data Handling

All AI prompts during the implementation phase must use synthetic placeholder examples. Real note titles, note bodies, timestamps, user-specific content, passwords, and personal details must never be pasted into an AI tool. This rule applies regardless of which AI tool is used or whether the session is recorded in the prompt log.

### Agreement 9 — AI Code Verification Checklist

Before Sprint 1 begins, a lightweight checklist must be established. For each function or module proposed by AI, the following must be confirmed before the code is merged:
- Which requirement number (FR, NFR, GOV) does this function satisfy?
- Are all failure paths specified in the refined requirements baseline covered?
- Has a human reviewed and signed off on the output?

A checklist entry that cannot be completed means the AI output is not ready to merge — re-prompt or revise manually.

### Agreement 10 — Privacy Claim Discipline

No documentation, README, or CLI output may claim that AstraNotes is secure, encrypted, or privacy-compliant unless the underlying design actually delivers that property. The private flag is access-control-only until SZ-06 resolves otherwise. Any claim beyond that must be traceable to an implemented and tested requirement.

---

## Sprint 8-10 Governance Addendum (2026-05-18 through 2026-06-03)

The following agreements were added as the project progressed into implementation and release phases.

### Agreement 11 — Branch Naming and PR Format (Sprint 8, 2026-05-18)

All branches follow the `<type>/<short-description>` convention: `feature/`, `test/`, `fix/`, `docs/`. Every pull request must include four sections before requesting review: **Change** (what is being added), **Why** (requirement or problem being solved), **Risks** (what could break), **Evidence** (test results or CI link). PRs without this structure receive a `Request changes` review.

*Rationale:* Established during Week 8 collaborative Git workflow exercise; the `feature/search-filter` PR was blocked until missing AND-semantics docstring was added, demonstrating the value of explicit PR structure.

### Agreement 12 — CI Gate on Both Python Versions (Sprint 8, 2026-05-18)

No branch is merged to `main` without CI passing on both Python 3.11 and 3.12. This gate is non-negotiable even for documentation-only changes.

*Rationale:* The HTTPBearer 401/403 bug was caught by the 3.11/3.12 matrix — the bug was real, not a false alarm. The cost of enforcing both versions is low; the value of catching version-specific behavior is demonstrated.

### Agreement 13 — AI Test Suggestions Require Source Verification (Sprint 9, 2026-05-27)

All AI-suggested tests must be verified against the actual source code before being added to the test suite. Each accepted test must have a documented requirement linkage (FR/NFR/GOV ID). Rejected suggestions must be documented with the reason for rejection in `collaboration_log.md`.

*Rationale:* Applied during Week 9 Prompt Bank exercise. AI identified 7 gaps; 7 were accepted (all verified against code); 3 suggestions were rejected (already covered, Python truthiness behavior not application behavior, unnecessary complexity). The verification step prevented adding tests that would have had no real behavioral meaning.

### Agreement 14 — Human Review of Security-Sensitive Code (Sprint 9, 2026-05-27)

Any code involving password hashing, JWT token generation/verification, or access control enforcement must be read and understood by the human developer before committing. AI output in these areas is accepted only after the human has traced the execution path from input to storage/response.

*Rationale:* bcrypt and JWT implementations have subtle correctness requirements (cost factor, algorithm selection, `exp` claim handling). Accepting AI output without reading the implementation creates invisible security debt.
