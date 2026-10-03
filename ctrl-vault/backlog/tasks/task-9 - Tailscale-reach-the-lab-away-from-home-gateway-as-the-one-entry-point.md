---
id: TASK-9
title: >-
  Tailscale: one address set for the lab, home devices reach it through the
  gateway (explore)
status: In Progress
assignee: []
created_date: '2026-10-02 18:41'
updated_date: '2026-10-03 19:41'
labels:
  - infra
  - machine
dependencies: []
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Direction Alex likes (2026-10-03), to prove before deciding: every lab machine on the tailnet, all names point at Tailscale addresses, one static route on the home router sends the tailnet range to the gateway so devices at home need no app; away it works with the app on. Same URL, same ssh, same T3 environment everywhere. Design, checks in order, weak points, hardening list and fallbacks: ctrl-vault/work/task-9/design.md. Nothing is installed yet. Touches gw (coordinate with TASK-3) and the router (Alex's say-so).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Alex: tailnet/account confirmed; stale nodes removed; Tailscale on the MBP and phone
- [ ] #2 Tailscale runs in the gw container and on hookdeck-ws
- [x] #3 Proof without the router: MBP with Tailscale off and a hand-added route reaches ssh, T3 and a gateway page through gw
- [x] #4 Router: static route possible and working, or the fallback (design.md) chosen
- [ ] #5 Names point at Tailscale addresses; at home with no app and away with the app: ssh, T3, lab pages, Jellyfin on the phone all work
- [ ] #6 Access rules: gw reaches VMs and the Mini only; VMs cannot start connections to other machines; other people's devices get media only
- [ ] #7 Hardening list in design.md done or explicitly skipped
- [ ] #8 bin/new-vm joins a new VM to the tailnet; docs updated (home-systems.md, fleet.md, t3-code-remote.md, vms/playbook.md)
<!-- AC:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-10-02 22:05
---
2026-10-03: gw has the tun device (no restart needed) and Tailscale (100.126.136.120). Forwarding proof passed from the MBP with a hand-added route, target = the Mini: ping, ssh, Jellyfin, lab pages on gw's 100.x. gw forwarding + masquerade and the MBP route are runtime only. Left for #3: T3, needs Tailscale on hookdeck-ws. Details: work/task-9/log.md
---

author: @claude
created: 2026-10-03 19:06
---
2026-10-04: router static route 100.64.0.0/255.192.0.0 → 192.168.1.110 (egress LAN) works: g8 and MBP without Tailscale reach the Mini and gw's 100.x (ssh, Jellyfin, lab page; ~200 Mbit/s). MBP's PIA needed a split-tunnel exception. Every setting: docs/tailscale.md.
---

author: @claude
created: 2026-10-03 19:41
---
2026-10-04 (Alex afk, go-ahead given): policy applied by Terraform (collielab terraform/tailscale.tf); DNS switched: gw names + mini.lab → 100.x, tested by name from MBP and g8; bin/vm-tailnet + bin/new-vm --tailscale (opt-in) written; gw check.sh extended. Waiting on Alex: tag gw/Mini in the admin console, vm-join OAuth client → then hookdeck-ws joins (T3 test, #2, #5, #6). Calibre-Web 500s on the Mini itself (not this change).
---
<!-- COMMENTS:END -->
