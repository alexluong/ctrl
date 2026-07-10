# Project: eldobot

Discord bot for Basketball GM (BBGM) fantasy leagues — loads BBGM export files and runs league operations in Discord: drafts, free agency, re-signings, trades, rosters, player stats/progression charts, plus a points/inventory economy. Live in 9 whitelisted servers (VBA, NABL, etc.). Repo: `hub/alexluong/eldobot`.

**Status: live in production**, unlike most project docs here — this one is running with real users.

## Stack

- Python 3.11, discord.py, single-process bot (`python main.py`)
- plotly + kaleido (headless Chromium) for chart images
- Dropbox API for storing/loading league export files
- State = JSON files in `data/` (points, inventory, daily, tracking, servers), volume-mounted

## Deployment

- Runs on the homelab VM (`sshmylab`, 149.28.40.6) alongside vaultwarden, alexluong.com, glances
- Deploy dir: `/home/alex/services/eldobot` — a git clone of the repo
- Flow (manual): push to GitHub → `git pull` on VM → `docker build -t eldobot .` → `docker compose up -d`
- compose: container `eldobot`, `restart: unless-stopped`, `./data:/app/data` volume, `.env` (DISCORD_TOKEN, DROPBOX_*)
- **Not registered in collielab** — predates the collielab convention; VM services are split between `collielab/services/` (vaultwarden, glances, portainer) and ad-hoc `~/services/` git clones (eldobot, alexluong.com, caddy, mls)

## Incidents

- **2026-07-10 — bot hung 1.5 days, container "Up".** `progspredict` command → plotly `write_image` → kaleido's `t.join()` (no timeout) blocked the asyncio event loop → Discord heartbeat stopped → bot offline; container stayed healthy-looking so `restart: unless-stopped` never fired. Fixed with `docker restart eldobot`. Root cause unpatched: kaleido render runs synchronously on the event loop (`figure_utils.py`). Nothing monitors bot liveness — outage went unnoticed until users reported it.

## Open items

- Fix the deadlock class: run kaleido render off the event loop with a timeout; consider pinning/upgrading kaleido
- Liveness monitoring: healthcheck that detects "up but hung" (heartbeat file + compose healthcheck, or external ping)
- Decide: migrate eldobot under collielab's `services/` convention, or document the `~/services/` split as intentional
- Repo hygiene: no README; stray files (`indentation mess.py`, `sdhfgljks.py`, `result.txt` 8MB, `progs.txt` 16MB in git)

## Status log

- 2026-07-10 — deadlock incident diagnosed & restarted; project documented (this doc + repo CLAUDE.md). Last code change 2026-01-04 (server whitelist).
