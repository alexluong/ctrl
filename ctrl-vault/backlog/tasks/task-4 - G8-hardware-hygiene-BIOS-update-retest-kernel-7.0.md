---
id: TASK-4
title: 'G8 hardware hygiene: BIOS update, retest kernel 7.0'
status: To Do
assignee: []
created_date: '2026-10-02 10:39'
updated_date: '2026-10-03 18:26'
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

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-10-02 16:31
---
Add-on (2026-10-02): while 101 is down for the g8 reboots, turn on memory reporting. new-vm.sh sets --balloon 0, so the Proxmox UI shows 100% memory for the VM (guest really ~15G used / 15G cache). Do: ssh g8 'qm set 101 --balloon 32768' before the stop (balloon = memory: stats reported, RAM never shrinks; applies on a full stop/start, not a reboot from inside the VM), and change --balloon 0 to --balloon "$MEMORY" in collielab hosts/g8/new-vm.sh. Check after: VM Summary memory graph shows real use. Stopping 101 ends running T3 turns, PM2 and Docker processes; do it with no agent work in flight.
---

author: @claude
created: 2026-10-03 18:26
---
2026-10-04: memory-reporting add-on done. qm set 101 --balloon 32768 + full stop/start; Proxmox shows real use (1.7 of 32GB after boot). collielab d23a24d: new-vm.sh uses --balloon "$MEMORY". Left: BIOS update + kernel 7.0 retest (at the box).
---
<!-- COMMENTS:END -->
