---
id: TASK-13
title: 'Backups for g8 guests: where they go, how often, how to restore'
status: To Do
assignee: []
created_date: '2026-10-02 21:56'
updated_date: '2026-10-03 20:32'
labels:
  - infra
  - machine
dependencies: []
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Nothing on g8 is backed up (fleet.md open item 2). Snapshots of 101 (clean-setup, ready) live in the same thin pool on the same NVMe, so they are for rollback only and die with the disk. Decide where backups are stored and set it up.

Measured 2026-10-03:
- 101 hookdeck-ws: 250GB disk, 53GB written (Docker images 25, build cache 7, volumes 6, home 19 of which workspaces 7.2, .cache 5.8, .local 2.6, go 2.2). About 40GB can be downloaded again; under 10GB is hard to replace (workspace clones, logins, secret files). Estimated backup file 20-30GB compressed (not run yet).
- 110 gw: 4GB disk, 1.1GB written; rebuilt from collielab in four commands.
- 9000 template: rebuilt from the Debian cloud image + collielab scripts; no backup needed.
- Space: local (dir) 86GB free on g8; Blue4 on the Mini 817GB free (USB, Mini on Wi-Fi, stays off after a power cut); R2 about 0.015 USD/GB/month, no download fee.

Options:
A. Proxmox backup job (vzdump, VM stays up) -> file on g8 'local' -> rclone to R2. Simple; every run is a full copy; keep few.
B. Same job writing to Blue4 on the Mini over NFS/SMB. Off the NVMe but in the same house; depends on the Mini being on.
C. Proxmox Backup Server (in a VM/CT on g8 or on another machine): changed chunks only, so nightly runs are small; its S3 datastore is a preview feature, untested against R2.
D. Back up only what is hard to replace from inside the VM (restic to R2 of workspaces, logins, secret files; exclude caches and Docker) and rebuild the rest with new-vm + the playbook. Smallest; restore is slower and needs the playbook to be right.

To decide: which of A-D (or a mix, e.g. A weekly + D nightly); how many copies to keep; one copy at home + one in R2 or R2 only; encryption of what goes to R2 (the VM holds logins and secrets); who alerts when a job fails (ties to TASK-7).

Done when: a schedule runs without anyone starting it, one restore has been done for real (restore 101 to a new id, boot it, check logins), and the steps are in collielab hosts/g8/README.md and docs/fleet.md.

First step: run one vzdump of 101 to 'local' to get the real size and duration.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Backup target reachable from g8 with enough space; speed measured
- [ ] #2 Scheduled backup of VM 101 (and later VMs) with retention; a failed run is visible
- [ ] #3 Restore tested once to a throwaway VM ID (boot it, check logins)
- [ ] #4 Docs: collielab hosts/g8/README.md, fleet.md, vms/playbook.md
<!-- AC:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-10-03 19:07
---
2026-10-04: include the schedule and retention (Proxmox backup job, e.g. keep 7 daily / 4 weekly, prune automatic). Snapshots stay manual (vms/maintenance.md); a stale-snapshot check (>30 days) fits TASK-7.
---

author: @claude
created: 2026-10-03 20:32
---
Merged TASK-12 into this one (same goal; 12 was the earlier, shorter version). Its criteria are now here.
---
<!-- COMMENTS:END -->
