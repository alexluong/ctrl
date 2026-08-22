# Project: eldobot

Discord bot for Basketball GM (BBGM) fantasy leagues — loads BBGM export files and runs league operations in Discord: drafts, free agency, re-signings, trades, rosters, player stats/progression charts, plus a points/inventory economy. Live in 9 whitelisted servers (VBA, NABL, etc.). Repo: `hub/alexluong/eldobot`.

**Status: live in production**, unlike most project docs here — this one is running with real users.

## Stack

- Python 3.11, discord.py, single-process bot (`python main.py`)
- plotly + kaleido (headless Chromium) for chart images
- Cloudflare R2 (S3 API via boto3) for storing/serving league export files; Dropbox backend retained but unused
- State = JSON files in `data/` (points, inventory, daily, tracking, servers), volume-mounted
- `dropbox-ui/` in the same repo = a **separate Cloudflare Worker** (TypeScript), no shared code or runtime with the bot — see "Dropbox UI" below

## Deployment

- Runs on the homelab VM (`sshmylab`, 149.28.40.6) alongside vaultwarden, alexluong.com, glances
- Deploy dir: `/home/alex/services/eldobot` — a git clone of the repo
- Flow (manual): push to GitHub → `git pull` on VM → `docker build -t eldobot .` → `docker-compose up -d` (v1 binary; VM's Docker is old, no compose plugin)
- compose: container `eldobot`, `restart: unless-stopped`, `./data:/app/data` volume, `.env` (DISCORD_TOKEN, EXPORT_STORAGE, R2_*, DROPBOX_* unused)
- **Not registered in collielab** — predates the collielab convention; VM services are split between `collielab/services/` (vaultwarden, glances, portainer) and ad-hoc `~/services/` git clones (eldobot, alexluong.com, caddy, mls)

## Export storage

- `-updatexport` (aliases `-update`, `-updateexport`) uploads the guild's export and returns a public URL; `-load <url>` reads any http URL back. Backend selected by `EXPORT_STORAGE` in the VM `.env` — **`r2` since 2026-08-11**; `dropbox` still works as a fallback. Code: `storage.py` in the eldobot repo.
- **Live URL shape:** `https://pub-a00ede68ec534ed6a68018b276d7fb34.r2.dev/exports/{guild_id}-export.json` — Cloudflare's managed r2.dev hostname, deliberately not a custom domain so league-facing links carry none of Alex's own domains. Bucket `eldobot-exports`; infra in `collielab/terraform/r2.tf`, details in `../collielab.md`.
- Convention, both backends: **one object per guild**, `{guild_id}-export.json`, overwritten in place. Never timestamped.
- Dropbox account: `lhtanh98@gmail.com`, free Basic, **2 GiB**. App client id `2ffbesv7yp2vtr2`.
- **ibabot shares this Dropbox account** — near-certainly a fork of eldobot: it keeps our `{guild_id}-export` prefix but appends `-YYYYMMDD-HHMMSS`, so every upload is a new object and nothing is ever pruned. The app credentials sat in `.env.example` from `ac8ad2e` (2025-08-22) until the 2026-07-10 scrub, so any clone taken in that window has live write access. Secret still not rotated.
- ibabot's league is **IBA** (`"meta": {"name": "IBA"}` in the export), guild `1346036658616930338` — created 2025-03-03, eldobot is not a member (403 on the guild API), so the name isn't resolvable from our side. eldobot *is* in `Buenos Aires Falcons HQ. IBA`, a team server downstream of it.

## Dropbox UI

- **https://dropbox.builders.so** — list / open / delete for the shared Dropbox account. Built 2026-08-22 so whoever runs IBA can clear ibabot's exports themselves instead of Alex hand-wiping the account each time it fills.
- Cloudflare Worker, TypeScript, server-rendered HTML + plain CSS, no build step, no framework, mobile-friendly. Code: `dropbox-ui/` **in the eldobot repo** (Alex's call — no new repo), but it is an **independent deploy**: `cd dropbox-ui && npm run deploy`. Never needs the bot restarted, shares nothing with it.
- **Domain choice:** the workers.dev subdomain is account-wide and already `alexluong`, and changing it would break 6 existing workers (scribbble-gateway, mbr-gateway-prd, nilventures-clubs, …) — so a neutral zone Alex already owns was used instead. Same reasoning as the r2.dev export hostname: nothing league-facing carries Alex's name.
- **Auth:** one shared password in the `APP_PASSWORD` secret; login form is the first screen. Session cookie = `<expiry>.<HMAC-SHA256(expiry)>`, 30 days, `HttpOnly; Secure; SameSite=Strict` (which is also what covers CSRF — every mutating route is a same-site form POST). **The HMAC key is derived from `APP_PASSWORD` itself, so changing the password signs everyone out** — deliberate for a shared credential. Current password is a weak throwaway (Alex: "not the most critical in terms of security, we can change later"); it lives only in wrangler secrets, not in the repo.
- **Deletes** use `files/delete_v2` — `files/permanently_delete` needs the `files.permanent_delete` scope, which Dropbox app 4558019 does not have. Fine: verified 2026-08-22 that trash does not count against this account's quota, so space frees immediately and files are recoverable ~30 days.
- Secrets: `APP_PASSWORD`, `DROPBOX_REFRESH_TOKEN`, `DROPBOX_CLIENT_ID`, `DROPBOX_CLIENT_SECRET` via `wrangler secret put`. Dropbox values are the same ones in the VM `.env`.
- **Deploy gotcha:** the collielab CF API token (`collielab/terraform/.env` → `TF_VAR_cloudflare_api_token`, account `3f6713b6…`) has R2/DNS scopes but **not Workers Routes**, so a `[[routes]]` block in `wrangler.toml` makes every deploy fail *after* uploading. The custom domain was bound once out-of-band via `PUT /accounts/{acct}/workers/domains` (that endpoint the token *can* call) and persists across deploys; `wrangler.toml` deliberately declares no route. `wrangler deploy` prints **"No targets deployed"** — that is expected and misleading: verified by probe that deploys do reach the live domain.
- Not in collielab terraform (the Worker and its domain binding were created imperatively). Consistent with eldobot's existing "not registered in collielab" status.

## Incidents

- **2026-07-10 — bot hung 1.5 days, container "Up".** `progspredict` command → plotly `write_image` → kaleido's `t.join()` (no timeout) blocked the asyncio event loop → Discord heartbeat stopped → bot offline; container stayed healthy-looking so `restart: unless-stopped` never fired. Fixed with `docker restart eldobot`; root cause patched same day (eldobot `067b2d3`: renders run in a daemon thread with 30s timeout, requirements pinned to prod versions, rebuilt & redeployed). Nothing monitors bot liveness — outage went unnoticed until users reported it.

- **2026-07-22 → 2026-08-11 — Dropbox full, all `-updatexport` uploads failing.** ibabot filled the 2 GiB account: on 2026-08-10 alone it wrote 9 IBA exports (234–236 MB each, 08:35→22:51), 2.066 GiB total = the entire account. eldobot's own exports occupy **zero bytes** — the old code deleted its file *before* uploading, so a failed upload left nothing behind and users' links died. 108 `insufficient_space` errors in retained logs, first 2026-07-22. Users saw "Uploading your export to dropbox..." and then silence (failure was an unretrieved task exception, never surfaced). Bot itself was never hung. **Resolved 2026-08-11** by moving to R2 (see status log); the Dropbox account is still ibabot-full but no longer eldobot's problem.

## Open items

- Liveness monitoring: healthcheck that detects "up but hung" (heartbeat file + compose healthcheck, or external ping)
- collielab vs `~/services/` split — deliberately ignored for now (Alex, 2026-07-10)
- Repo hygiene (Claude's discretion, Alex OK'd): stray files (`indentation mess.py`, `sdhfgljks.py`, `result.txt` 8MB, `progs.txt` 16MB in git)

- **Tell the leagues to re-run `-updatexport`** — every Dropbox link issued before 2026-08-11 is dead.
- R2 free tier is 10 GB-month / 1M Class A / 10M Class B with **egress free**; at eldobot's volume (one overwritten object per guild) this stays free. Watch it only if a bot ever starts writing timestamped objects. If ibabot ever migrates here, give it a **separate bucket + its own scoped token** (R2 tokens scope per-bucket, not per-prefix) so its retention bug can't evict us again.
- Decision needed: talk to the IBA/ibabot owner about pruning, vs rotate the Dropbox app secret and cut them off. Moving eldobot to R2 makes rotation safe to do unilaterally. **Still open as of 2026-08-22** — ibabot is actively uploading and the account is over quota (see status log).
- `allowed_servers.txt` has drifted from reality — `1401268831917310097` is labelled "Johannesburg Springboks HQ. IBA" but is now "Buenos Aires Falcons HQ. IBA"; 3 whitelisted guilds eldobot isn't in (Challenger BL, The Ball Pit, DBL-05); 5 joined guilds not whitelisted. Cosmetic (whitelist only gates commands), unreconciled.

## Status log

- 2026-08-22 (later still) — **Dropbox UI built and live at https://dropbox.builders.so** (`dropbox-ui/` in the eldobot repo, commit `3a3670f`, pushed). List / open / delete only, shared-password auth. Verified end-to-end against the live site: unauthenticated request shows only the login form, wrong password rejected, tampered and expired cookies rejected, and list → open (temporary link) → delete exercised with a throwaway file that was cleaned up. See "Dropbox UI" above for the deploy gotchas.
- 2026-08-22 (later) — **Dropbox cleared** (Alex's call). All 9 ibabot IBA exports deleted: **2,374,984,455 B → 9,762,906 B used (110.6% → 0.5%)**, 2,365,221,549 B freed, 0 live files. `files/permanently_delete` is **not available to this app** (missing `files.permanent_delete` scope, app ID 4558019) — fell back to `files/delete_v2` (trash). Space freed immediately and in full, so **trash does not count against the quota** on this account; files recoverable from web trash ~30 days. IBA's export links issued before this are dead. Script: `dbx_clear.py` pattern — read VM `.env`, refresh-token, `list_folder` recursive, delete each. **Not durable:** ibabot still has working credentials, still writes ~263 MB per upload, still never prunes — refills to full in ~33 h at last week's cadence. Rotating the app secret is the only fix that holds; still Alex's call, still zero-cost to eldobot.
- 2026-08-22 — **Dropbox re-checked (live API, VM creds; script pattern: read `/home/alex/services/eldobot/.env` on the VM, refresh-token → `users/get_space_usage` + `files/list_folder` recursive with `include_deleted`).** **Over quota: 2,374,984,455 B used / 2,147,483,648 B allocated = 110.6%.** Live contents: **9 files, all ibabot IBA exports** (`/exports/1346036658616930338-export-YYYYMMDD-HHMMSS.json`, 262.6–262.9 MB each, 2026-08-20 06:51 → 2026-08-21 15:46 UTC), 2,365,221,549 B — i.e. the entire account. **eldobot: zero bytes.** R2 migration confirmed clean.
  - **Full path history: 4,826 entries — 9 live, 4,816 deleted tombstones.** Names ever seen: 4,799 ibabot-style timestamped IBA exports, 11 for guild `1408169726466850817` (so ibabot serves ≥2 leagues), 14 plain `{guild_id}-export.json` (eldobot's convention), 1 `test-upload.json`.
  - **Corrects the 2026-08-22 first read ("something prunes") and the Incidents note on how eldobot's files vanished.** Nothing prunes automatically — ibabot never deletes. The account jams, then is **hand-wiped**: last pre-jam upload 2026-08-10 22:50, then **9 days of nothing**; `files/list_revisions` shows the backlog deleted at **2026-08-20T06:48:34Z**, first new upload **06:51:03Z — 2.5 min later**. It refilled to over-quota in ~33 h. Same pattern earlier: eldobot's own `{guild_id}-export.json` files last had content in late 2025 and were deleted **2026-02-19T07:16:5x, seconds apart** — an owner mass-wipe, *not* eldobot's old delete-before-upload path.
  - **Trajectory: terminal.** Export size grows with the league (62 MB Oct 2025 → 226 MB Aug 1 → 263 MB Aug 21). At 263 MB, **8 uploads fill 2 GiB** — under one day of ibabot's traffic (~5–15/day, peaks 40–63/day in Nov 2025). It will jam again within days and stay jammed unless they prune or upgrade. ibabot is **actively in use**, not abandoned.
  - Secret still not rotated; rotating remains zero-cost to eldobot.
- 2026-08-11 (later) — **live on R2.** VM `.env` gained `EXPORT_STORAGE=r2` + `R2_*` (old `.env` backed up alongside), image rebuilt for boto3, container recreated; bot reconnected, 9 servers whitelisted, all `data/` state intact. Verified by calling `storage.upload_export` inside the running container against a real 1.6 MB export → the public bucket URL returns 200 `application/json`, byte-identical. Upload ~1.1s. **Dropbox is now unused by eldobot** — links handed out before today are dead (their files were deleted by the old delete-first upload path), so servers need to re-run `-updatexport`. Rotating the Dropbox app secret is now safe for us and would evict ibabot; still Alex's call.
- 2026-08-11 — Dropbox-full diagnosed (see Incidents) and pluggable storage landed in eldobot `6c01ced`: `storage.py` with dropbox|r2 backends behind `EXPORT_STORAGE`, Dropbox switched to overwrite-in-place, upload failures now reported in-channel. Verified against a local S3 (moto) — 17 checks, all pass; live Dropbox path unverified until deploy. **Committed but not pushed and not deployed** — Alex's call, since the Dropbox write path changed.

- 2026-07-10 (later) — history rewrite (git filter-repo): Dropbox app credentials were in `.env.example` and as `basics.py` getenv fallbacks since Aug 2025; scrubbed from working tree and all history, force-pushed, clones reset. Alex chose not to rotate the secret. Note: pre-rewrite objects remain fetchable by SHA on GitHub until their GC (support ticket would purge). All commit SHAs changed — this log uses the new ones.
- 2026-07-10 (later) — system audit & cleanup (`2f857d2`): security dep bumps (aiohttp, Pillow, python-dotenv, simpleeval — all had OSV advisories; new pins verified clean), dead files removed, rebuilt & redeployed, bot healthy. VM: pruned 4.4GB dangling images (disk 74%→59%). Deliberately skipped: kaleido/plotly/pandas upgrades (no security need, churn risk), 4 orphan docker volumes on the VM (portainer/grafana/loki/prometheus data from stopped collielab services — collielab's call, not eldobot's).
- 2026-07-10 — deadlock incident: diagnosed, restarted, root cause fixed & deployed (`067b2d3`); project documented (this doc + repo CLAUDE.md). Prior code change 2026-01-04 (server whitelist).
