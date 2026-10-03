---
id: TASK-15
title: 'MBP as control point: snapshot and check of its setup outside git (deferred)'
status: To Do
assignee: []
created_date: '2026-10-03 21:02'
labels:
  - machine
  - workspace
dependencies: []
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Deferred (Alex 2026-10-04): the MBP stays the control point for now; no action until a second or replacement Mac is on the table. Goal then: one small script (sync / check / snapshot) that lists and verifies everything the MBP holds that is not in git, so a new Mac can be brought up from it and drift is visible.

What it would cover (today written down by hand in ctrl-vault/docs/tailscale.md § Adding a device, case B):
- ~/.ssh/config: the Include line for collielab/ssh/config (not in dotfiles); fleet key id_ed25519 in the agent
- collielab/terraform/.env: R2, Cloudflare, Vultr, Tailscale terraform OAuth client
- ctrl/secrets/: gw/caddy.env, tailscale/vm-join.key (both regenerable from terraform output), others per project
- VPN exceptions: PIA split tunnel 100.64.0.0/10 (piactl -u dump daemon-settings); WARP if turned on
- Vaultwarden copies of each secret (Alex)
- Possibly: Brewfile/dotfiles drift, bin/svc services, T3 environments

Done when: the script reports each item ok/missing on the MBP, runs read-only by default, and the runbook points at it.
<!-- SECTION:DESCRIPTION:END -->
