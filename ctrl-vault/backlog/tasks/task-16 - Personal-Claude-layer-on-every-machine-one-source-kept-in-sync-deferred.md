---
id: TASK-16
title: 'Personal Claude layer on every machine: one source, kept in sync (deferred)'
status: To Do
assignee: []
created_date: '2026-10-03 21:50'
labels:
  - machine
  - workspace
dependencies: []
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Deferred (Alex 2026-10-04): long term a personal skill pack / plugin; for now nothing to do.

Today: the user-level Claude layer (dotfiles dot/.claude/CLAUDE.md = communication style, settings.json = model, effort, broad allow/deny permissions, all plugins installed but disabled; no hooks, no MCP) is on the MBP via dotfiles and is copied once into each new VM by collielab bin/new-vm (plugins by hosts/workspace-vm/setup.sh). Nothing keeps the copies in sync: a change in dotfiles reaches the MBP only, and VMs keep the version from the day they were built (hookdeck-ws: 2026-10-02). Workspace-specific config (tools, MCP, hooks, skills) stays in each workspace repo (docs/claude-config.md) and is not part of this.

To decide later: a personal plugin/skill pack (installed per machine, updated in one place) vs. a sync step (e.g. a check in the TASK-15 MBP script that diffs each VM's ~/.claude/{CLAUDE.md,settings.json} against dotfiles and pushes on OK); what belongs in it (communication style, permissions, personal skills).

Done when: one source for the personal layer, every machine (MBP, each VM) on it, and a way to see drift.
<!-- SECTION:DESCRIPTION:END -->
