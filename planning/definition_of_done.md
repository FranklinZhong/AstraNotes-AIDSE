# AstraNotes — Definition of Done

**Project:** AstraNotes — A Secure, Modular Note-Taking System  
**Established:** 2026-04-06  

---

## When Is a Task Done?

A task, feature, or artifact exits the Sprint only when **all** of the following are true:

| # | Condition | What "met" looks like for AstraNotes |
|---|-----------|--------------------------------------|
| 1 | **Requirement traceability** | The work is traceable to a numbered requirement (FR-1–FR-6, NFR-1–NFR-2, or SG-1–SG-2). No backlog item = scope creep, not done. |
| 2 | **Self-explainable** | I can explain the module behavior and design decision from memory, without re-reading the AI session that produced it. |
| 3 | **Architecture fit** | The output belongs to the correct layer (model / repository / service / policy), with no boundary violations between NoteService, PrivacyPolicy, and the repository. |
| 4 | **Tested or validated** | For code: at least one test covers the new behavior and I can explain each assertion. For documents: a review note names the requirement it addresses. |
| 5 | **Security and privacy addressed** | Any change touching note visibility, file I/O, or access control has been checked for failure-path behavior — not just the success path. |
| 6 | **Buildable foundation** | The work is clean enough that the next Sprint can start from it without reverse-engineering how it was built. |
| 7 | **Sprint Review ready** | I can present this work, name the requirement it satisfies, and state what it leaves open for the next Sprint. |

---

## Scope

This DoD applies to **all work items** in AstraNotes:

- Code (new features, bug fixes, refactors)
- Design documents (UML, ADRs)
- Requirement artifacts (user stories, acceptance criteria)
- AI-generated output promoted into the project

---

## How to Apply

At the end of each session, run through conditions 1–7 before marking any task as complete
in `backlog.md`. If any condition fails, the task stays `In Progress` in the current Sprint
or carries over to the next one.

A task that passes all 7 conditions is marked `Done` in `backlog.md` with the date.

---

*This DoD applies to all AstraNotes work across the project lifecycle.*
