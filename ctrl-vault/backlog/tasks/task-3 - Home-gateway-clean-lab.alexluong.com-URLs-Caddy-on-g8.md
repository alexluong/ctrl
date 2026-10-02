---
id: TASK-3
title: 'Home gateway: clean lab.alexluong.com URLs (Caddy on g8)'
status: In Progress
assignee: []
created_date: '2026-10-02 10:08'
updated_date: '2026-10-02 17:02'
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

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-10-02 11:31
---
2026-10-02: built. Container 110 gw on g8 (192.168.1.110), Caddy + Cloudflare DNS module, wildcard certs for *.lab, *.mini.lab, *.g8.lab, token lab-gateway-acme (alexluong.com DNS only) via terraform. Routes: jellyfin, plex, books, books-hannah, audiobooks, qbt, qbt-private, arr apps (mini); pve (g8); short aliases jellyfin/plex/books/books-hannah/audiobooks.lab. All tested from the MBP. Naming settled: <service>.<machine>.lab + short aliases. Config: collielab hosts/gw (3e27e1f). Left: decide the domain (fleet.md §6: collielab.net) before pointing Kobos/TV apps at URLs; hookdeck routes; Tailscale names later.
---

author: @claude
created: 2026-10-02 14:09
---
2026-10-02: 502 on pve.g8.lab (Alex): Caddy looked up the backend name through the router on each new connection; a lookup takes ~1s there and one timed out. Fix: backend machine addresses in gw's /etc/hosts (collielab hosts/gw/machines, installed by push.sh; survives a container restart). Requests now ~20ms. Also since: lab.alexluong.com index page, alex.calibre / hannah.calibre names, private qBittorrent left off, domain stays alexluong.com.
---

author: @claude
created: 2026-10-02 17:02
---
2026-10-02: first hookdeck-ws routes. Site block *.hookdeck-ws.lab in the Caddyfile; dozzle (:8888) and isaiah (:8889) routed, cards on the index page (collielab 5df18d1). Left for hookdeck-ws: core's <ns>.localhost URLs, board, T3.
---
<!-- COMMENTS:END -->
