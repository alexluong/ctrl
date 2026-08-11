# Project: alexluong.com

Alex's personal site — writing (posts/articles/notes) plus an RSS feed. Live at https://alexluong.com. Repo: `hub/alexluong/alexluong.com`, remote `git@github.com:alexluong/alexluong.com.git`.

**Status: live in production**, and largely untouched since Sept 2024 — last commit `2fc9dac` (2024-09-02), running version 5.7.

## Stack

- **Go 1.23** (`.tool-versions`), single binary
- **PocketBase** as the whole backend — embedded SQLite, admin UI, auth, migrations (`internal/migrations`, automigrate on in local dev only)
- **templ** for views (`internal/views`), **echo v5** routing (comes via PocketBase)
- **Tailwind** standalone binary (`bin/tailwindcss/…`) → `build/assets/styles.css`
- `internal/feed` renders the RSS feed, `internal/models` the content types

## Local dev

```bash
make dev     # plain `go run main.go serve`
make live    # -j3: templ --watch, air rebuilding the server, tailwind --watch
```

No README setup section beyond a link to the site — the Makefile is the real documentation. Doesn't meet the `workflow.md` setup-doc bar; see Open items.

## Build & deploy

Version-tagged Docker images on Docker Hub, deployed by hand. `version.txt` is the source of truth.

```bash
make release   # scripts/release.sh: bump version.txt, docker build --platform linux/amd64,
               # docker push alexluong/personal:alexluong.com-<version>, git commit the bump
# then on the VM:
cd /home/alex/services/alexluong.com && git pull && make up   # scripts/up.sh reads version.txt → VERSION env
```

- Image: `alexluong/personal:alexluong.com-5.7`. Dockerfile is two-stage, final stage is `scratch`.
- Built `--platform linux/amd64` from the ARM Mac — required, the VM is x86.
- compose: `restart: unless-stopped`, `127.0.0.1:8090:8090` (localhost-only on purpose — `2fc9dac` fixed Docker bypassing the firewall by binding all interfaces), bind mount `./data` → `/pb_data`.
- The VM clone sits one commit behind (`709e002`), but its `docker-compose.yml` already has the 127.0.0.1 binding, so the running config is correct. `git pull` there is safe and overdue.

## Serving

`alexluong.com` and `www` are AAAA records → the VM's IPv6, proxied by Cloudflare (terraform-managed in `collielab/terraform/alexluong_com.tf`). On the box, **host-level Caddy** (systemd, `/usr/bin/caddy`, config `/etc/caddy/Caddyfile`) terminates TLS and reverse-proxies to `localhost:8090`; `www.alexluong.com` 301s to the apex. `alexluong.com` uses `tls internal` since Cloudflare fronts it.

Note the trap: `~/services/caddy/` on the VM is a **dead docker-compose Caddy** — no container, and its `Caddyfile` bind source is an empty *directory*. Editing anything there does nothing. See `../collielab.md`.

## State

PocketBase SQLite in `/home/alex/services/alexluong.com/data/` — `data.db` (~570 KB, all site content) and `logs.db`. **This is the only copy.** It is not in git, not backed up to object storage; the only protection is the Vultr instance's weekly Thursday snapshot. Losing the VM between snapshots loses up to a week of writes.

## Open items

- **`data.db` has no backup of its own** — weekly VM snapshots are the entire safety net for all site content. A periodic dump to R2 would be cheap and would fit the existing `eldobot-exports` pattern.
- **`/etc/caddy/Caddyfile` is unversioned** — the routing table for every public service on the VM exists only on the box, root-owned. See `../collielab.md`.
- README has no "Local setup" section (`workflow.md` convention); the Makefile carries it implicitly.
- VM clone is a commit behind; harmless today, but `make up` there uses whatever `version.txt` says, so a stale clone can silently deploy an old image.
- Repo hygiene: `.DS_Store` and `tmp/` are in the working tree.

## Status log

- 2026-08-12 — documented (this doc); no code changes. Verified live: apex 200, `www` 302 → apex, container `alexluongcom_app_1` up 2 weeks on image 5.7, PocketBase writing (`data.db-wal` active).
