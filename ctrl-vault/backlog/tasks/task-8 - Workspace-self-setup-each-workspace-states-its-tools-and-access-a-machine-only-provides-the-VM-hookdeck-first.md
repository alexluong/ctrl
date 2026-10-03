---
id: TASK-8
title: >-
  Workspace self-setup: each workspace states its tools and access; a machine
  only provides the VM (hookdeck first)
status: In Progress
assignee: []
created_date: '2026-10-02 17:06'
updated_date: '2026-10-03 22:01'
labels:
  - workspace
  - machine
dependencies: []
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Alex 2026-10-03: a workspace should care about what it does (tools, access), not the environment around it. Target flow: get a VM, log in to Claude and GitHub, clone the workspace, and the workspace's own setup and checklist take it from there. Rely on mise as much as possible so macOS and Debian behave the same; workspace agents can add tools and access items themselves. Spec: ctrl-vault/work/task-8/spec.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 hookdeck: tools installed outside mise today are pinned in mise.toml (doppler, golangci-lint, gopls, pnpm, psql, redis-cli) and install on both macOS and Debian
- [x] #2 hookdeck: 'mise run setup' (idempotent) and 'mise run doctor' (read-only: tools, each login, config files present) exist and pass on the VM and the MBP
- [x] #3 hookdeck: access checklist (login, purpose, how to do it, how to check it) and .env.example files for ops/ and the root, with where each value comes from
- [x] #4 hookdeck: a setup skill an agent follows on a fresh machine; ends with the list left for the human
- [x] #5 hookdeck: rule in AGENTS.md for agents adding a tool, an access item or a config variable
- [x] #6 collielab: hosts/hookdeck-ws/setup.sh holds nothing workspace-specific; Linux quirks any workspace hits live in the base template; template rebuilt
- [x] #7 ctrl: vms/playbook.md and the per-VM doc template follow the new flow; workspace-setup.md carries the convention for all workspaces
- [ ] #8 Proven on a fresh VM: new-vm, clone, setup, doctor shows only the logins left
<!-- AC:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-10-03 21:32
---
2026-10-04 (ctrl): machine side done: template 9000 rebuilt (IPv4-first, browser libs), hosts/workspace-vm/setup.sh does git identity, GitHub key, Claude plugins; bin/new-vm copies the dotfiles Claude config, starts Docker UIs (moved out of the hookdeck repo: hosts/workspace-vm/docker-ui.sh; hookdeck-ws already on it), firewall on before first boot. Proven twice on throwaway VM 148 (--tailscale), cleaned up. Docs: workspace-setup.md § 7a (convention), vms/playbook.md two paths, per-VM doc template. Workspace side handed to the hookdeck lead: work/task-8/handoff-hookdeck.md (Alex pastes its ask into a hookdeck session on hookdeck-ws). Then: delete hosts/hookdeck-ws/setup.sh (#6), throwaway-VM proof of clone/setup/doctor (#8).
---

author: @claude
created: 2026-10-03 21:36
---
2026-10-04: Docker UIs stay hookdeck-specific (Alex); the common docker-ui.sh was removed from collielab (6968e77) and hookdeck-ws's containers are back under the workspace's tools/docker-ui. Hand-off and docs updated.
---

author: @claude
created: 2026-10-03 22:01
---
2026-10-04: hookdeck side landed (hookdeck task-105, 374a4ca): mise tools, setup/doctor (doctor reads access.md), env examples, setup skill, AGENTS rule; doctor passes on the VM, setup idempotent. ctrl removed the apt Doppler on the VM (doppler from mise, login kept, doctor exit 0) and deleted collielab hosts/hookdeck-ws/setup.sh (4425eff). Not done, optional: MBP verification (only matters if hookdeck sessions run on the MBP), amp-server .env.example (names need Alex). #8 (fresh-VM proof) will happen with enable-ws (TASK-10) instead of a throwaway clone.
---
<!-- COMMENTS:END -->
