---
id: TASK-11
title: 'cs-ws: shared VM for personal workspaces (cs, solex, later ones) (103)'
status: To Do
assignee: []
created_date: '2026-10-02 18:41'
labels:
  - workspace
  - machine
dependencies: []
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Plan only for now (Alex 2026-10-03). One VM for Alex's own projects, which hold no client secrets: cs and solex at ~/workspaces/<name>, later personal projects join. Name to confirm (cs-ws proposed; Alex said cs-vm). ctrl does not move: it is headquarters on the MBP (Alex), drives the machines and a VM never holds keys to the host or other machines. Shared-VM points: one T3 environment with a project per workspace; one GitHub key (orgs alexluong, colliestudio); machine-wide logins are shared by all workspaces on it; distinct ports per workspace for dev servers and boards. Size estimate: 4 vCPU, 8GB, 80-100GB. Cheapest proof of the TASK-8 flow (no prod access); could go before enable-ws.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Name confirmed; VM 103 created from the shared template
- [ ] #2 cs and solex cloned, each passes its own doctor; solex e2e tests (Playwright) run
- [ ] #3 T3: one environment, both projects; boards and dev servers on distinct ports, reachable through the gateway
- [ ] #4 docs/vms/cs-ws.md; playbook notes for a VM holding several workspaces
<!-- AC:END -->
