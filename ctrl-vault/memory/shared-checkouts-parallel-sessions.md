---
name: shared-checkouts-parallel-sessions
description: ctrl and collielab checkouts are shared by several Claude sessions (pull first, never git add -A); a workspace repo is written only from its home machine, not from ctrl
metadata:
  type: feedback
---

Several Claude sessions often work at the same time in the same checkouts (`~/workspaces/ctrl`, `~/git/hub/alexluong/collielab`). On 2026-10-02 another session built the hookdeck VM in `collielab` while this one built the gateway there.

**Why:** `git add -A` would sweep another session's half-done files into your commit, and stale reads make edits fail or clobber.

**How to apply:** `git pull --rebase` before editing, `git add <specific paths>`, commit and push promptly, re-read a file before rewriting it. If a machine suddenly has things you did not make (a VM, a branch), check `git log` for the other session before assuming a problem.

**Workspace repos have one home machine.** Each `~/workspaces/<name>` keeps its board, memory and digest as files in git, which assumes one writer. On 2026-10-02 hookdeck sessions ran on the MBP and on the `hookdeck-ws` VM at once: both created `task-86` within 34 minutes and the checkouts diverged. Since 2026-10-03 the VM is the home of hookdeck sessions; MBP sessions are still allowed when needed (Alex, 2026-10-04): pull first, push promptly, and not while VM sessions are writing the board or memory. From a ctrl session, do not commit to another workspace's repo or create tasks on its board while it has live sessions; write the ask into a ctrl task and hand it to that workspace's lead. Details: `ctrl-vault/docs/vms/hookdeck-ws.md` § Open points, `~/workspaces/cs/cs-vault/notes/studio/multi-writer.md`. Related: [[build-as-board-task]].
