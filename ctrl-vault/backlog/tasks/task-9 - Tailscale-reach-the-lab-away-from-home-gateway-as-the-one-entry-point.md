---
id: TASK-9
title: 'Tailscale: reach the lab away from home (gateway as the one entry point)'
status: To Do
assignee: []
created_date: '2026-10-02 18:41'
labels:
  - infra
  - machine
dependencies: []
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hookdeck sessions now run only on the VM (2026-10-03), so away from home there is no hookdeck work until this exists. Design already proposed in docs/home-systems.md § URLs: Tailscale on the gateway (gw) only; *.ts.alexluong.com -> the gateway's Tailscale address, same service names as *.lab; no subnet router, no Tailscale on VMs, so it does not depend on how many VMs exist. Gap in that design: SSH (T3 connects to a workspace VM over SSH, not HTTP). Proposed: the gateway as SSH jump host when not at home (ProxyJump in collielab/ssh/config, chosen automatically), so VMs still need nothing. Alternatives if that fails: Tailscale on each workspace VM (baked into the template; one login per VM) or a subnet router advertising only g8's block as narrow routes (192.168.1.x clashes with cafe/hotel networks otherwise). Touches gw: coordinate with TASK-3.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Alex: Tailscale account chosen (the Mini is on lhtanh98@ today; MBP has none), installed on the MBP and phone
- [ ] #2 gw joined to the tailnet (container needs /dev/net/tun or userspace mode); *.ts.alexluong.com records and certificates
- [ ] #3 Away from home with Tailscale on: lab URLs open under *.ts, including hookdeck-ws services
- [ ] #4 Away from home: ssh hookdeck-ws and the T3 app connect with no manual step; at home nothing changes with Tailscale on or off
- [ ] #5 Works from a network that itself uses 192.168.1.x
- [ ] #6 Docs: home-systems.md, fleet.md, t3-code-remote.md, vms/playbook.md (nothing per VM, or the per-VM step)
<!-- AC:END -->
