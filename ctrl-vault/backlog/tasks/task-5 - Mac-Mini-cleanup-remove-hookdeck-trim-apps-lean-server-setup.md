---
id: TASK-5
title: 'Mac Mini cleanup: remove hookdeck, trim apps, lean server setup'
status: To Do
assignee: []
created_date: '2026-10-02 15:07'
updated_date: '2026-10-03 20:56'
labels:
  - machine
dependencies: []
references:
  - ctrl-vault/work/task-5/scan.md
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make the Mini a clean server-like machine. Remove everything hookdeck (Colima profile, repos, credentials, shell config), remove desktop apps and background items it does not need, clear caches. Media stack (gluetun, seedboxapi) is out of scope. Scan results and step list: ctrl-vault/work/task-5/scan.md. Rule (Alex, 2026-10-02): Claude proposes, Alex approves each step before it runs.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 No hookdeck left on the Mini: Colima profile, repos, credentials, zshrc line, editor/Claude project folders
- [ ] #2 Unpushed hookdeck work (outpost branch + stashes, hookdeck-workspace) saved or explicitly dropped by Alex
- [ ] #3 Apps and background items reduced to the agreed keep list
- [ ] #4 Caches and unused Docker images cleared; free disk recorded before and after
- [ ] #5 Media stack still running after the cleanup
- [ ] #6 mac-mini.md and fleet.md updated
<!-- AC:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-10-03 20:56
---
2026-10-04: scan + decisions in work/task-5/scan.md. Hookdeck delete agreed (no save), waiting for go. Apps: not yet. Jump Desktop: no watchdog, cause = silent auto-update. Mini-use brainstorm summarized in docs/fleet.md § The Mini.
---
<!-- COMMENTS:END -->
