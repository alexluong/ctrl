---
name: shared-checkouts-parallel-sessions
description: ctrl and collielab working copies are shared by several Claude sessions at once; pull first and never git add -A
metadata:
  type: feedback
---

Several Claude sessions often work at the same time in the same checkouts (`~/workspaces/ctrl`, `~/git/hub/alexluong/collielab`). On 2026-10-02 another session built the hookdeck VM in `collielab` while this one built the gateway there.

**Why:** `git add -A` would sweep another session's half-done files into your commit, and stale reads make edits fail or clobber.

**How to apply:** `git pull --rebase` before editing, `git add <specific paths>`, commit and push promptly, re-read a file before rewriting it. If a machine suddenly has things you did not make (a VM, a branch), check `git log` for the other session before assuming a problem.
