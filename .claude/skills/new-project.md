---
name: new-project
description: Bootstrap a new personal project — repo + GitHub + local setup + living doc in ctrl + pointer CLAUDE.md. Also recreates the pointer for an existing project on a new machine.
user_invocable: true
---

# New Project Bootstrap

Set up a personal project per `docs/workflow.md`: code-only repo + living doc in ctrl + machine-local pointer.

## Instructions

Given a project name (ask if not provided; for pointer-only recreation on a new machine, do steps 4–5 only):

1. **Repo** — `mkdir ~/git/hub/alexluong/<name> && git init` (skip if exists).
2. **Living doc** — create `ctrl/docs/projects/<name>.md`: one-line what/why, status line (dated), design principle, plan, open questions. Skip if it exists (it usually will — ideas start in ctrl before the repo).
3. **Local scaffold** — stack-appropriate skeleton (Xcode project, `go mod init`, `npm create`, …) per the living doc's stack decision; ask if undecided. Commit `chore: scaffold project` and create the remote: `gh repo create alexluong/<name> --private --source . --push` (ask before making anything public).
4. **Pointer CLAUDE.md** in the project repo (machine-local, untracked):
   - `echo "CLAUDE.md" >> <repo>/.git/info/exclude`
   - Write `<repo>/CLAUDE.md` covering: repo is code-only; notes live at `~/git/hub/alexluong/ctrl/docs/projects/<name>.md`; read it at session start; write decisions back there and commit in ctrl; never create notes/TODO markdown here; no `~/.claude` memory; conventions at `ctrl/docs/workflow.md`. (Use `~/git/hub/alexluong/fitjournal/CLAUDE.md` as the template.)
5. **Index** — add the project to the `alexluong` org list in `docs/machine.md` if missing; commit in ctrl (`docs(projects): add <name>`).
