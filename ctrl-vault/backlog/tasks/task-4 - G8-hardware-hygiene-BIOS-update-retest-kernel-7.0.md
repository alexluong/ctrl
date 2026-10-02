---
id: TASK-4
title: 'G8 hardware hygiene: BIOS update, retest kernel 7.0'
status: To Do
assignee: []
created_date: '2026-10-02 10:39'
labels:
  - machine
  - infra
dependencies: []
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
g8 is pinned to kernel 6.14.11-9-pve because 7.0.14 on this box (BIOS T26 02.02.00, 2021) marks the TSC unstable and falls back to the slow HPET timer (clock read ~1400 ns vs ~70 ns), and never attaches the hardware-clock driver. Details: ctrl-vault/work/task-2/kernel-7-clock-issues.md. To do at the box (monitor + keyboard): 1) BIOS update (HP network update from the BIOS menu); 2) unpin (proxmox-boot-tool kernel unpin), boot the newest kernel, check current_clocksource = tsc and /dev/rtc0 exists; if not, re-pin 6.14 or try 6.17 / tsc=reliable; 3) check the hardware clock survives a long unplug (clock battery). Until done: pinned kernel gets no automatic move to newer lines; re-check when Proxmox ships kernel updates.
<!-- SECTION:DESCRIPTION:END -->
