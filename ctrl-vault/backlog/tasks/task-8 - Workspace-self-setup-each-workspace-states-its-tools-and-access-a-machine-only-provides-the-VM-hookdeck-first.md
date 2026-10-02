---
id: TASK-8
title: >-
  Workspace self-setup: each workspace states its tools and access; a machine
  only provides the VM (hookdeck first)
status: To Do
assignee: []
created_date: '2026-10-02 17:06'
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
- [ ] #1 hookdeck: tools installed outside mise today are pinned in mise.toml (doppler, golangci-lint, gopls, pnpm, psql, redis-cli) and install on both macOS and Debian
- [ ] #2 hookdeck: 'mise run setup' (idempotent) and 'mise run doctor' (read-only: tools, each login, config files present) exist and pass on the VM and the MBP
- [ ] #3 hookdeck: access checklist (login, purpose, how to do it, how to check it) and .env.example files for ops/ and the root, with where each value comes from
- [ ] #4 hookdeck: a setup skill an agent follows on a fresh machine; ends with the list left for the human
- [ ] #5 hookdeck: rule in AGENTS.md for agents adding a tool, an access item or a config variable
- [ ] #6 collielab: hosts/hookdeck-ws/setup.sh holds nothing workspace-specific; Linux quirks any workspace hits live in the base template; template rebuilt
- [ ] #7 ctrl: vms/playbook.md and the per-VM doc template follow the new flow; workspace-setup.md carries the convention for all workspaces
- [ ] #8 Proven on a fresh VM: new-vm, clone, setup, doctor shows only the logins left
<!-- AC:END -->
