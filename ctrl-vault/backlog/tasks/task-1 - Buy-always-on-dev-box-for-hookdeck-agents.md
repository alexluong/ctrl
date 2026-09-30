---
id: TASK-1
title: Buy always-on dev box for hookdeck agents
status: In Progress
assignee: []
created_date: '2026-09-29 19:45'
updated_date: '2026-09-30 11:10'
labels:
  - machine
  - infra
dependencies: []
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Dedicated always-on machine to run agentic local dev for hookdeck (core ~24-container stack + outpost + parallel worktree builds). Mac Mini (base M4) stays on arrstack + enable/solex. Research notes: ctrl-vault/work/task-1/research.md
<!-- SECTION:DESCRIPTION:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-30 09:22
---
Decided: HP EliteDesk 805 G8 Mini 95W (R7 5700G, 64GB DDR4, 1TB) from xeon.vn, 19.8M VND, Proxmox VE 9.2 one-VM-per-project. Spec note sent to shop. See work/task-1/decision.md
---

author: @claude
created: 2026-09-30 11:10
---
Box received; Proxmox pre-installed at 192.168.1.21, BIOS power-on-after-loss set, memtest running. Next: management setup discussion (see decision.md Status).
---
<!-- COMMENTS:END -->
