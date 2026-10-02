---
id: TASK-10
title: 'enable-ws: Enable workspace on its own VM (102)'
status: To Do
assignee: []
created_date: '2026-10-02 18:41'
labels:
  - workspace
  - machine
dependencies: []
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Plan only for now (Alex 2026-10-03: finalize hookdeck first). Own VM because it holds another company's production access (gcloud stg/prd/prd-rw, Mongo read and write, Cloudflare, Metabase). Follow docs/vms/playbook.md in its TASK-8 form: new-vm, Claude + GitHub login, clone, the workspace's own setup and doctor. Size estimate (not measured): 4 vCPU, 8-12GB, 80GB; measure on the MBP first (playbook step 1). Depends on TASK-8 (the self-setup convention ported to the enable workspace). Planned grouping: docs/vms/README.md § Planned.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 enable workspace has the self-setup pieces (mise tools, setup, doctor, access checklist, env examples)
- [ ] #2 VM 102 created, setup run, doctor shows only logins left; Alex logs in
- [ ] #3 T3 environment connected, a session runs; gateway routes if it serves anything
- [ ] #4 docs/vms/enable-ws.md; the Enable workspace's own machines note; MBP no longer runs Enable sessions
<!-- AC:END -->
