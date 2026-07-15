---
name: media-ops
description: >-
  Operate Alex's self-hosted media stack in the `media/` domain — Jellyfin
  (remote streaming), qBittorrent downloading + the catalog pipeline, and the
  calibre/audiobookshelf book stack. Use whenever the task involves streaming,
  downloading/cataloging media, library scans/metadata, the Colima "arr" VM, or
  the media Docker services.
---

# media-ops

Playbook for running the `media/` domain. **Read the detailed docs before acting** —
this file routes; the docs have the specifics.

- `media/README.md` — storage layout, folder structure, services, stacks & always-on
  policy, VM management, DigitalCore (DC) API, catalog scripts, VPN.
- `media/jellyfin.md` — Jellyfin access, clients, API cookbook, **gotchas** (read these
  before touching scans/metadata).
- `media/catalog/scripts/catalog.py` — the download→library pipeline.

## Environment

- Repo root: `/Users/alex/git/hub/alexluong/ctrl`. Monorepo; media lives in `media/`.
- Containers run in the Colima **`arr`** VM → Docker context **`colima-arr`**
  (`export DOCKER_CONTEXT=colima-arr`, or `docker --context colima-arr ...`).
- VM sized in `scripts/vm-start.sh` (**8 GB / 6 CPU**). Host is a 16 GB M4 Mac Mini.
- Drives mounted into the VM: `/Volumes/Blue4/arr` and `/Volumes/Red4/arr`
  (as `/Blue4` and `/Red4` inside containers).
- Secrets in `media/.env` (**gitignored — never commit**): `DC_API_KEY`, PIA/OpenVPN
  creds, `MAM_ID`, `DATA_PATH`, `JELLYFIN_ADMIN_USER/PASS`.
- Stack control: `scripts/up.sh <stack>` / `scripts/down.sh <stack>`; `up.sh core` =
  always-on set (download + private + calibre + audiobookshelf + **jellyfin**). Only
  `arr` is on-demand.

## Common tasks

**Stream remotely (Jellyfin).** Reached over Tailscale — no public exposure, no Plex
paywall. LAN `http://192.168.1.90:8096`, Tailscale `http://100.91.137.41:8096`, login in
`.env`. Clients: Swiftfin (Apple), Jellyfin for Android TV. Full details + API +
gotchas → `media/jellyfin.md`. Tailscale runs on the **host**, CLI at
`/Applications/Tailscale.app/Contents/MacOS/Tailscale`.

**Download + catalog.** Alex drops a `.torrent`/magnet; standing rule is **save it, he runs
the download himself** (saves to `~/Documents/pt/red4/`, sorted `dc/` vs `public/`). DC
(DigitalCore) is the primary source — search/download via its API (`media/README.md`).
qBittorrent WebUI is reached inside the VM: `docker exec gluetun wget -qO- "http://localhost:8080/api/v2/..."` (no creds, POST for toggles). After downloads finish, catalog with
`catalog.py` (scan → import → link) — see README "Catalog scripts". Hand-author catalog
entries when folder names are verbose/misparsed.

- **MAM (MyAnonaMouse):** search API works from the box (via `docker exec qbittorrent curl -b mam_id=…`,
  through the VPN) — good for *finding* books; but the **`.torrent` download must be done in the
  browser** (seedbox session can't fetch torrent files). MAM is on the **main/Singapore** stack.
  **Ban-safety is real** — a crash-looping client or flapping VPN re-announces repeatedly and
  triggers "duplicate peer" bans (it happened 2026-07-08). Keep seeding; don't let it crash-loop.
  Details + search payload → `media/README.md` (MAM section). For books specifically → `books.md`.
- **Audiobooks ≠ ebooks:** audiobooks (mp3/m4b) go to **audiobookshelf** (`/media/audiobooks`),
  not calibre. Reacher + GoT audiobooks are downloaded but were sitting uncataloged (2026-07-15).

**Books (calibre / audiobookshelf).** Always-on. calibre-web alex `:8074` / hannah `:8073` share
one calibre library at `/Volumes/Blue4/arr/media/books/library`; audiobookshelf `:13378` for
audiobooks. **Full playbook + standing workflow + design decisions → `media/books.md`** (a living
doc — extend it as the setup evolves).

- **Goal:** keep the calibre **catalog** (`metadata.db`) current + clean (no dupes/ghosts/split
  authors/Unknown junk). Per-user calibre-web `app.db` (shelves/progress) is disposable.
- **On-demand workflow (not scheduled):** when books land in `downloads/`, run
  `books.py status → scan → import → archive → status`, **with eyes on the output** — that
  review is deliberate (a blind cron or CWA auto-import erodes "clean"; see books.md decisions).
- **Ebook cataloging is scripted:** `catalog/scripts/books.py` (`status` / `scan` / `import` /
  `normalize` / `archive`). It de-dupes downloads against the library (they're usually already
  imported), enriches metadata online, and normalizes author names. Treat it as a codified helper,
  not a crutch — operate `calibredb` directly and adapt when needed. **Never hand-file into the
  library** — go through `calibredb` (it owns `metadata.db`).
- `calibredb` isn't in calibre-web; run it one-shot from the full-calibre image:
  `docker --context colima-arr run --rm -v /Volumes/Blue4/arr/media/books:/books --entrypoint /usr/bin/calibredb lscr.io/linuxserver/calibre:latest --library-path /books/library <cmd>`
  (mount must be read-write even for `list`).
- **Writes must stop calibre-web first** — `metadata.db` is on virtiofs, so concurrent writers
  hit `database is locked` (same class as the Jellyfin DB). `books.py` does this automatically.
- Manga/comics (cbz) are **out of scope** for `books.py` and pollute the library as "Unknown"
  authors — deferred to a future Komga/Kavita pass.

## Critical gotchas (full list in the docs)

- **qBit WebUI flapping = OOM**, historically (2 GB VM). Now on 8 GB it's fine; if it
  recurs, check `colima ssh -p arr -- free -h` and `docker inspect -f '{{.State.OOMKilled}}' qbittorrent` FIRST. See `media/README.md` and memory `project_qbit_oom`. **A crash-loop (OOM) or a
  flapping VPN re-announces torrents on every restart → tracker "duplicate peer" bans** (MAM
  disabled access 2026-07-08 this way). Stabilize the client/VPN before replying to a tracker ticket.
- **LSIO container `/config` (qBit, Jellyfin) MUST be on a native docker volume, not the
  virtiofs external drive.** SQLite/lock files on virtiofs → `database is locked` storms,
  readonly-DB errors, WebUI flapping (`QLocalServer::listen: Unknown error 22`), and (Jellyfin,
  2026-07-15) a 6m49s wedged boot that never binds. Main qBit uses `qbit_config`, Jellyfin uses
  `jellyfin_config`. **`qbittorrent-private` is the last one still on virtiofs (backlog — migrate
  to `qbit_private_config`).** If you recreate a config volume, chown it to `PUID:PGID` (`501:20`).
  Media stays on the external drives.
- **Jellyfin metadata won't populate if `TypeOptions` is empty** (happens when a library is
  created via API) — must configure `TheMovieDb` fetchers + `FullRefresh`. Scans are
  **disk-I/O-bound** (external USB), not RAM-bound. A combined movie+TV `FullRefresh` does
  movies first and starves TV — refresh TV alone to populate shows sooner. Full gotcha list
  → `media/jellyfin.md`.
- **Shell `rm -rf` is wrapped/rejected** on this Mac — use Python `shutil.rmtree` or
  `/bin/rm`.
- Household: Hannah uses the stack too, mostly via Discord; don't narrate Discord actions.

## Related memory

`project_media_infra`, `reference_colima`, `project_qbit_oom`, `project_jellyfin_remote`,
`user_household`, `feedback_no_narration`.
