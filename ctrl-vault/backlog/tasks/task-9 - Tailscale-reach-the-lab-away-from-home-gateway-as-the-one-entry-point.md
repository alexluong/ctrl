---
id: TASK-9
title: >-
  Tailscale: one address set for the lab, home devices reach it through the
  gateway (explore)
status: To Do
assignee: []
created_date: '2026-10-02 18:41'
updated_date: '2026-10-02 21:02'
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
- [ ] #1 Alex: tailnet/account confirmed; stale nodes removed; Tailscale on the MBP and phone
- [ ] #2 Tailscale runs in the gw container and on hookdeck-ws
- [ ] #3 Proof without the router: MBP with Tailscale off and a hand-added route reaches ssh, T3 and a gateway page through gw
- [ ] #4 Router: static route possible and working, or the fallback (design.md) chosen
- [ ] #5 Names point at Tailscale addresses; at home with no app and away with the app: ssh, T3, lab pages, Jellyfin on the phone all work
- [ ] #6 Access rules: gw reaches VMs and the Mini only; VMs cannot start connections to other machines; other people's devices get media only
- [ ] #7 Hardening list in design.md done or explicitly skipped
- [ ] #8 bin/new-vm joins a new VM to the tailnet; docs updated (home-systems.md, fleet.md, t3-code-remote.md, vms/playbook.md)
<!-- AC:END -->
