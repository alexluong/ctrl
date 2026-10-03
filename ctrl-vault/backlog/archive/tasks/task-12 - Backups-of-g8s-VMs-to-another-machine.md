---
id: TASK-12
title: Backups of g8's VMs to another machine
status: To Do
assignee: []
created_date: '2026-10-02 18:41'
updated_date: '2026-10-03 20:32'
labels:
  - infra
  - machine
dependencies: []
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Nothing is backed up. Snapshots (clean-setup, ready) sit on the same disk as the VM, and since 2026-10-03 hookdeck-ws is the only home of hookdeck sessions: unpushed work and the logged-in setup exist on one NVMe. Target named in fleet.md: the Mini's Blue4 drive (817GB free, APFS over USB, the Mini is on Wi-Fi: speed to measure). Decide: Proxmox vzdump to a share on the Mini vs Proxmox Backup Server; schedule and retention; whether secrets inside VM backups are acceptable on that drive (encryption); a restore test.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Backup target reachable from g8 with enough space; speed measured
- [ ] #2 Scheduled backup of VM 101 (and later VMs) with retention; failure is visible
- [ ] #3 Restore tested once to a throwaway VM ID
- [ ] #4 Docs: fleet.md, vms/playbook.md
<!-- AC:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-10-03 20:32
---
Duplicate of TASK-13, merged there 2026-10-04 (criteria moved).
---
<!-- COMMENTS:END -->
