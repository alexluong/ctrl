---
id: TASK-2
title: Set up pve1 (HP 805 G8) + hookdeck workspace VM
status: Done
assignee: []
created_date: '2026-10-02 08:44'
updated_date: '2026-10-02 21:53'
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

author: @claude
created: 2026-10-02 10:26
---
2026-10-02: Mac Mini reachable from the MBP (ssh mini); PR #1 from the Mini's clone merged (media/ domain + docs/mac-mini.md). MBP aliases now use names: g8 -> g8.lab.alexluong.com, mini -> mini.lab.alexluong.com; ssh vultr replaces sshmylab. Left on the Mini: SSH keys only (Alex, sudo), move its clone to main. g8 next: BIOS update, then VM template.
---

author: @claude
created: 2026-10-02 11:02
---
2026-10-02: VM template (9000) and hookdeck VM (101, 192.168.1.101, ssh hookdeck) built from scripts in collielab (hosts/g8, bin/new-vm; new VM in ~40s). T3 server runs in the VM on loopback, reached over SSH. All tools installed; no login or secret on it. Left for Alex: first-run list in work/task-2/hookdeck-vm.md.
---

author: @claude
created: 2026-10-02 21:53
---
Closed 2026-10-03: g8 set up, hookdeck-ws in daily use from T3, playbooks written. Summary: ctrl-vault/work/task-2/summary.md. Follow-ups: TASK-8, 9, 10, 11, 12.
---
<!-- COMMENTS:END -->
