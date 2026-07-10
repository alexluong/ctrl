---
name: new-project
description: Bootstrap a new personal project repo (or recreate the pointer CLAUDE.md for an existing one on a new machine) per the code-only/notes-in-ctrl convention
user_invocable: true
---

# New Project Bootstrap

Set up a personal project per `docs/workflow.md`: code-only repo + living doc in ctrl + machine-local pointer.

## Instructions

Given a project name (ask if not provided):

1. **Repo** — `mkdir ~/git/hub/alexluong/<name> && git init` (skip if it exists; for pointer-only recreation on a new machine, skip to step 3).
2. **Living doc** — create `ctrl/docs/projects/<name>.md` with: one-line what/why, status line (dated), design principle, plan, open questions. Skip if it exists.
3. **Pointer CLAUDE.md** in the project repo (machine-local, untracked):
   - `echo "CLAUDE.md" >> <repo>/.git/info/exclude`
   - Write `<repo>/CLAUDE.md` covering: repo is code-only; notes live at `~/git/hub/alexluong/ctrl/docs/projects/<name>.md`; read it at session start; write decisions back there and commit in ctrl; never create notes/TODO markdown here; no `~/.claude` memory; conventions at `ctrl/docs/workflow.md`. (Use `~/git/hub/alexluong/fitjournal/CLAUDE.md` as the template.)
4. **Index** — add the project to the `alexluong` org list in `docs/machine.md` if missing.
5. **Commit in ctrl** (conventional, e.g. `docs(projects): add <name>`). Nothing to commit in the project repo — the pointer is untracked.
