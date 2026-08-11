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
- Flow (manual): push to GitHub → `git pull` on VM → `docker build -t eldobot .` → `docker-compose up -d` (v1 binary; VM's Docker is old, no compose plugin)
- compose: container `eldobot`, `restart: unless-stopped`, `./data:/app/data` volume, `.env` (DISCORD_TOKEN, DROPBOX_*)
- **Not registered in collielab** — predates the collielab convention; VM services are split between `collielab/services/` (vaultwarden, glances, portainer) and ad-hoc `~/services/` git clones (eldobot, alexluong.com, caddy, mls)

## Export storage

- `-updatexport` (aliases `-update`, `-updateexport`) uploads the guild's export and returns a public URL; `-load <url>` reads any http URL back. Backend selected by `EXPORT_STORAGE` in the VM `.env` — `dropbox` (current) or `r2`. Code: `storage.py` in the eldobot repo.
- Convention, both backends: **one object per guild**, `{guild_id}-export.json`, overwritten in place. Never timestamped.
- Dropbox account: `lhtanh98@gmail.com`, free Basic, **2 GiB**. App client id `2ffbesv7yp2vtr2`.
- **ibabot shares this Dropbox account** — near-certainly a fork of eldobot: it keeps our `{guild_id}-export` prefix but appends `-YYYYMMDD-HHMMSS`, so every upload is a new object and nothing is ever pruned. The app credentials sat in `.env.example` from `ac8ad2e` (2025-08-22) until the 2026-07-10 scrub, so any clone taken in that window has live write access. Secret still not rotated.
- ibabot's league is **IBA** (`"meta": {"name": "IBA"}` in the export), guild `1346036658616930338` — created 2025-03-03, eldobot is not a member (403 on the guild API), so the name isn't resolvable from our side. eldobot *is* in `Buenos Aires Falcons HQ. IBA`, a team server downstream of it.

## Incidents

- **2026-07-10 — bot hung 1.5 days, container "Up".** `progspredict` command → plotly `write_image` → kaleido's `t.join()` (no timeout) blocked the asyncio event loop → Discord heartbeat stopped → bot offline; container stayed healthy-looking so `restart: unless-stopped` never fired. Fixed with `docker restart eldobot`; root cause patched same day (eldobot `067b2d3`: renders run in a daemon thread with 30s timeout, requirements pinned to prod versions, rebuilt & redeployed). Nothing monitors bot liveness — outage went unnoticed until users reported it.

- **2026-07-22 → ongoing — Dropbox full, all `-updatexport` uploads failing.** ibabot filled the 2 GiB account: on 2026-08-10 alone it wrote 9 IBA exports (234–236 MB each, 08:35→22:51), 2.066 GiB total = the entire account. eldobot's own exports occupy **zero bytes** — the old code deleted its file *before* uploading, so a failed upload left nothing behind and users' links died. 108 `insufficient_space` errors in retained logs, first 2026-07-22. Users saw "Uploading your export to dropbox..." and then silence (failure was an unretrieved task exception, never surfaced). Bot itself was never hung. Mitigation in progress: pluggable storage backend (eldobot `6c01ced`), R2 pending credentials.

## Open items

- Liveness monitoring: healthcheck that detects "up but hung" (heartbeat file + compose healthcheck, or external ping)
- collielab vs `~/services/` split — deliberately ignored for now (Alex, 2026-07-10)
- Repo hygiene (Claude's discretion, Alex OK'd): stray files (`indentation mess.py`, `sdhfgljks.py`, `result.txt` 8MB, `progs.txt` 16MB in git)

- **R2 migration — original plan, now done (see status log).** Plan: own Cloudflare R2 bucket + public custom domain (e.g. `exports.alexluong.com`; the `r2.dev` subdomain is rate-limited and not for production). Free tier 10 GB-month / 1M Class A / 10M Class B, **egress free**; at eldobot's volume this stays free. TTL via native **lifecycle rules** — no cron needed — but granularity is 1 day minimum and deletion lands "typically within 24h" of expiry, so budget ~2 days of retention. If ibabot ever migrates too, give it a **separate bucket + its own scoped token** (R2 tokens scope per-bucket, not per-prefix) so its retention bug can't evict us again.
- Decision needed: talk to the IBA/ibabot owner about pruning, vs rotate the Dropbox app secret and cut them off. Moving eldobot to R2 makes rotation safe to do unilaterally.
- `allowed_servers.txt` has drifted from reality — `1401268831917310097` is labelled "Johannesburg Springboks HQ. IBA" but is now "Buenos Aires Falcons HQ. IBA"; 3 whitelisted guilds eldobot isn't in (Challenger BL, The Ball Pit, DBL-05); 5 joined guilds not whitelisted. Cosmetic (whitelist only gates commands), unreconciled.

## Status log

- 2026-08-11 (later) — **live on R2.** VM `.env` gained `EXPORT_STORAGE=r2` + `R2_*` (old `.env` backed up alongside), image rebuilt for boto3, container recreated; bot reconnected, 9 servers whitelisted, all `data/` state intact. Verified by calling `storage.upload_export` inside the running container against a real 1.6 MB export → `https://exports.alexluong.com/exports/1373305832497741894-export.json` returns 200 `application/json`, byte-identical. Upload ~1.1s. **Dropbox is now unused by eldobot** — links handed out before today are dead (their files were deleted by the old delete-first upload path), so servers need to re-run `-updatexport`. Rotating the Dropbox app secret is now safe for us and would evict ibabot; still Alex's call.
- 2026-08-11 — Dropbox-full diagnosed (see Incidents) and pluggable storage landed in eldobot `6c01ced`: `storage.py` with dropbox|r2 backends behind `EXPORT_STORAGE`, Dropbox switched to overwrite-in-place, upload failures now reported in-channel. Verified against a local S3 (moto) — 17 checks, all pass; live Dropbox path unverified until deploy. **Committed but not pushed and not deployed** — Alex's call, since the Dropbox write path changed.

- 2026-07-10 (later) — history rewrite (git filter-repo): Dropbox app credentials were in `.env.example` and as `basics.py` getenv fallbacks since Aug 2025; scrubbed from working tree and all history, force-pushed, clones reset. Alex chose not to rotate the secret. Note: pre-rewrite objects remain fetchable by SHA on GitHub until their GC (support ticket would purge). All commit SHAs changed — this log uses the new ones.
- 2026-07-10 (later) — system audit & cleanup (`2f857d2`): security dep bumps (aiohttp, Pillow, python-dotenv, simpleeval — all had OSV advisories; new pins verified clean), dead files removed, rebuilt & redeployed, bot healthy. VM: pruned 4.4GB dangling images (disk 74%→59%). Deliberately skipped: kaleido/plotly/pandas upgrades (no security need, churn risk), 4 orphan docker volumes on the VM (portainer/grafana/loki/prometheus data from stopped collielab services — collielab's call, not eldobot's).
- 2026-07-10 — deadlock incident: diagnosed, restarted, root cause fixed & deployed (`067b2d3`); project documented (this doc + repo CLAUDE.md). Prior code change 2026-01-04 (server whitelist).
