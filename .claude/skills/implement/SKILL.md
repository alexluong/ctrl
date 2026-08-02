---
name: implement
description: Plan → implement → review → test a feature for a personal project (e.g. "/implement fitjournal: add ghost overlay to progress-pic camera"). Runs from a ctrl cockpit session; delegates impl to agents in the project repo.
---

# Implement a Feature

Full pipeline for landing a feature in a project repo while keeping notes in ctrl. Conventions: `docs/workflow.md`.

## Instructions

1. **Context** — parse project + feature from args (ask if unclear). Read `docs/projects/<project>.md` and `docs/workflow.md`. Repo is at `~/git/hub/alexluong/<project>`.
2. **Plan** — draft the approach against the living doc's design stance. If it conflicts with a recorded decision, or a genuine design fork exists, raise it with Alex (AskUserQuestion) before coding. Record the agreed plan in the living doc. If Alex said "plan only", stop here.
3. **Pick the flow** (per workflow.md): small/mechanical → direct to main; large or Alex-wants-review → branch + GitHub PR. Delegated impl defaults to branch + PR.
4. **Implement** — in the project repo:
   - Single scoped task: delegate to one agent; the prompt must inline the relevant design constraints from the living doc (agents start with zero context) and state the branch/commit expectations. Trivial edits can be done directly.
   - Multiple independent tasks on the same repo: parallel agents with `isolation: "worktree"` so they don't clobber each other.
5. **Fix + check + test** — run the project's `fix` (auto-format/lint-fix), then `check` (lint, type-check — read-only), then build + tests (unit for tricky logic, e2e for flows). Add/update `qa/` specs in the same commit as the behavior change. Delegated agents run this before reporting done.
6. **Review** — run /code-review on the diff; fix confirmed findings.
7. **Land** — conventional commits. Branch flow: push, open PR (`gh pr create`), hand Alex the link for review. Direct flow: commit to main.
8. **Log** — update the living doc (status line, decisions made, open questions raised) and commit in ctrl.
