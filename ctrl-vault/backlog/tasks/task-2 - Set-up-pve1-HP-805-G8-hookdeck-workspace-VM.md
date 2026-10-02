---
id: TASK-2
title: Set up pve1 (HP 805 G8) + hookdeck workspace VM
status: In Progress
assignee: []
created_date: '2026-10-02 08:44'
updated_date: '2026-10-02 09:58'
labels:
  - machine
  - infra
dependencies: []
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Host basics, VM template, hookdeck workspace VM. Plan: ctrl-vault/work/task-2/plan.md. Home map: ctrl-vault/docs/home-systems.md.
<!-- SECTION:DESCRIPTION:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-10-02 09:37
---
2026-10-02: SSH access from the MBP works (id_ed25519). Discovery done: clean shop install, PVE 9.0.3, 181 updates pending, BIOS from 2021. Agreed: name g8, address .91, VMs .100+ (VM ID = last number), URLs under lab.alexluong.com, stay on 192.168.1.x, Tailscale later. Change log: work/task-2/log.md.
---

author: @claude
created: 2026-10-02 09:58
---
2026-10-02: router pool now .2-.99; box renamed pve1 -> g8 and moved .21 -> .100; ssh g8 works from the MBP. Next: host updates (181), SSH keys only, BIOS update, then VM template.
---
<!-- COMMENTS:END -->
