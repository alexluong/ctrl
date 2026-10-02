---
id: TASK-3
title: 'Home gateway: clean lab.alexluong.com URLs (Caddy on g8)'
status: To Do
assignee: []
created_date: '2026-10-02 10:08'
labels:
  - machine
  - infra
dependencies: []
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Small container on g8 running Caddy so services get https://<name>.lab.alexluong.com with a real certificate, no port, no warning (e.g. jellyfin.lab, g8.lab, qbt.lab, hookdeck.lab). Needs: container in g8's block (.101-.149), a Cloudflare token scoped to alexluong.com DNS (via collielab terraform) for Let's Encrypt DNS checks, wildcard record *.lab.alexluong.com -> the gateway, then move g8.lab/mini.lab to it. After: point the Kobos and TV apps at URLs. Open: flat names (jellyfin.lab) vs host in the name (jellyfin.mini.lab). Scheme and existing records: ctrl-vault/docs/home-systems.md. Later add-on: Tailscale + *.ts.alexluong.com for access away from home.
<!-- SECTION:DESCRIPTION:END -->
