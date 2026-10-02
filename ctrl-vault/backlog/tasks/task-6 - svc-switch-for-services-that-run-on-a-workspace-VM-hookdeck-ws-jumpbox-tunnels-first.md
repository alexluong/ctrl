---
id: TASK-6
title: >-
  svc: switch for services that run on a workspace VM (hookdeck-ws jumpbox
  tunnels first)
status: To Do
assignee: []
created_date: '2026-10-02 15:44'
updated_date: '2026-10-02 16:25'
labels:
  - machine
  - workspace
dependencies: []
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Sessions on hookdeck-ws need the jumpbox tunnel on the VM's own localhost; the Mac's tunnel does not reach them. Goal: a menubar item on the MBP that switches a service on or off on the VM, where the service keeps running with the MBP asleep or away, and the definition stays in ctrl's services.conf. Work in progress is parked on branch svc-remote (worktree local/svc-remote), not merged: Alex was using the menubar. Handoff: ctrl-vault/work/task-6/handoff.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Menubar shows hookdeck-ws tunnel-prd and tunnel-stg as switches; state read from the VM
- [ ] #2 A tunnel started from the menubar survives the MBP sleeping; it stops only when switched off
- [ ] #3 VM unreachable: items greyed, menubar refresh stays fast
- [ ] #4 Staging tunnel port clash with the outpost stack (26379) resolved or documented
- [ ] #5 Alex has decided: auto-off for the prod tunnel, and whether the Mac-side tunnel rows stay
- [ ] #6 Existing local services (caffeinate, boards, Mac tunnels) behave as before
- [ ] #7 Docs: services.conf header, vms/playbook.md (what a workspace runs from the menubar), hookdeck machines note
<!-- AC:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-10-02 16:25
---
Paused 2026-10-02 (Alex): the wider idea is a per-workspace control panel running on the VM, noted as a Collie Studio idea to evaluate (~/workspaces/cs/cs-vault/notes/studio/workspace-control.md). Finish this only if a stopgap is wanted before that.
---
<!-- COMMENTS:END -->
