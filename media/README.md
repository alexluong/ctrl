# Media

Home media management — movies, TV, audiobooks, and ebooks.

## What this is

We manually curate and manage a media library across two external hard drives, served via Jellyfin (video), Audiobookshelf (audiobooks), and Calibre-Web (ebooks). There is no automated download pipeline (Radarr/Sonarr are not in active use) — content is sourced manually, and tracked in structured JSON files.

The priority is **correctness**: the files on disk and the tracking data must agree. The Python catalog scripts (`catalog.py` in the arr repo) are helpers but not authoritative — when they produce wrong results, we fix the data to match reality.

## Physical storage

Two external HDDs connected to the Mac mini:

| Drive | Model | Size | Mount | Role |
|-------|-------|------|-------|------|
| **Blue4** | WD Blue | 4TB | `/Volumes/Blue4` | General media storage |
| **Red4** | WD Red | 4TB | `/Volumes/Red4` | General media storage (added later) |

## Folder structure

Both drives follow the same layout under `/Volumes/{Blue4,Red4}/arr/`:

```
arr/
├── data/                    # Service configs & databases
│   ├── jellyfin/
│   ├── audiobookshelf/
│   ├── calibre-web-alex/
│   ├── calibre-web-hannah/
│   ├── gluetun/
│   ├── qbittorrent/
│   ├── prowlarr/
│   ├── radarr/
│   ├── sonarr/
│   └── bazarr/
├── downloads/               # Torrent downloads (active + seeding)
└── media/                   # Organized library (hardlinked from downloads)
    ├── movies/              # 1080p movies
    ├── movies4k/            # 4K/UHD movies
    ├── tv/                  # 1080p TV shows
    ├── tv4k/                # 4K/UHD TV shows
    ├── audiobooks/          # Audiobook library (Blue4 only)
    └── books/
        └── library/         # Ebook library for Calibre-Web (Blue4 only)
```

**Hardlinks**: Downloads and media library point to the same data on disk. Deleting from one location doesn't affect the other. This only works within the same drive.

## Torrent files

Torrent files (`.torrent`/`.magnet`) are archived locally, organized **by target drive,
then by source tracker**:

```
~/Documents/pt/
├── blue4/         # Torrents whose downloads go to Blue4
└── red4/          # Torrents whose downloads go to Red4
    ├── dc/        # DigitalCore (private)
    ├── mam/       # MyAnonaMouse (private, books)
    ├── hf/        # HD-Forever / other private
    └── public/    # public trackers (YTS, RARBG-style release groups, etc.)
```

The drive (`blue4`/`red4`) picks which disk the download lands on; the source subfolder
(`dc`/`mam`/`hf`/`public`) is just how we file the `.torrent` — **ask if unsure which
source**, it's not always guessable from the filename (a public-looking `x265-LAMA`
release can still come from DC).

### Adding a torrent to qBittorrent (manual)

Standing rule is Alex runs downloads himself — but when asked to add one, this is the
verified path. **Only ever interact with the *main* qBittorrent** (behind `gluetun`);
`qbittorrent-private` is left alone.

1. **Archive the `.torrent`** to `~/Documents/pt/<drive>/<source>/` (see above).
2. **Copy it into the container.** The file is on the host; qbit runs in the VM sharing
   gluetun's network namespace, and `~/Documents` isn't mounted into the VM — so `docker cp`
   it in (curl *is* present in the qbittorrent image):
   ```bash
   docker --context colima-arr cp <file>.torrent qbittorrent:/tmp/add.torrent
   ```
3. **POST it to the WebUI API** from *inside* the qbittorrent container (its localhost:8080
   is gluetun's namespace; auth-free via `WebUI\LocalHostAuth=false`). Default `save_path`
   is `/Red4/downloads` (= `/Volumes/Red4/arr/downloads`); use `/Blue4/downloads` for a
   Blue4 target. autoTMM is **off** and the `radarr`/`tv-sonarr` categories are unused —
   add with an explicit `savepath`, no category:
   ```bash
   docker --context colima-arr exec qbittorrent \
     curl -s -F "torrents=@/tmp/add.torrent" -F "savepath=/Red4/downloads" \
     "http://localhost:8080/api/v2/torrents/add"    # returns "Ok."
   ```
4. **Force-start it** — a fresh add often sits in `queuedDL` behind the queue limit. Grab
   the hash and force-start so it downloads immediately:
   ```bash
   H=$(docker --context colima-arr exec gluetun wget -qO- \
       "http://localhost:8080/api/v2/torrents/info" | \
       python3 -c "import sys,json;print(next(t['hash'] for t in json.load(sys.stdin) if 'grease' in t['name'].lower()))")
   docker --context colima-arr exec gluetun wget -qO- \
     --post-data="hashes=$H&value=true" "http://localhost:8080/api/v2/torrents/setForceStart"
   ```
5. **Verify** state moved to `downloading`/`forcedDL` with peers via `torrents/info?hashes=$H`,
   then `docker --context colima-arr exec qbittorrent /bin/rm -f /tmp/add.torrent`.

> Reads from qbit go through `gluetun` (`docker exec gluetun wget -qO- .../api/v2/...`);
> the file *upload* must run from inside `qbittorrent` (it's where the `docker cp`'d file
> lives, and it shares gluetun's netns). Both hit the same WebUI.
> After the download completes, catalog it (`catalog.py`: scan → import → link).

## Tracking data

Lives in `catalog/`:

| File | Purpose |
|------|---------|
| `downloads.json` | Torrent-to-download path mapping. Source of "what we've downloaded." |
| `catalog.json` | Full library: title, year, resolution, codec, HDR, source, status. The main tracking file. |
| `wishlist.json` | Movies and TV shows we want but don't have yet. |
| `media.json` | Extended media metadata. |
| `LIST.md` | Human-readable inventory (generated). |

### Catalog entry lifecycle

```
torrent added → downloads.json (download: null)
             → download completes → downloads.json (download: "blue4/...")
             → imported → catalog.json (status: "pending")
             → hardlinked to media/ → catalog.json (status: "linked")
```

Status values: `pending` (imported, not linked), `linked` (hardlinked to library), `external` (not from a torrent — no download path).

### Resolution routing

| Filename pattern | Treated as | Library folder |
|-----------------|-----------|---------------|
| `2160p`, `4K` + `HDR`, `UHD` | 4K | `movies4k/` or `tv4k/` |
| `DS4K`, `RM4K` | 1080p (downscaled/remastered) | `movies/` or `tv/` |
| `1080p`, `720p` | 1080p | `movies/` or `tv/` |

### Library naming

- **Movies**: `Title (Year)` — e.g., `Blade Runner 2049 (2017)`
- **TV**: `Title` — e.g., `Breaking Bad`, `The Office (US)`

## Services

Run via Docker on a Colima VM (`colima-arr` context). Compose files in `compose/`. Uses standalone `docker-compose` (not `docker compose` plugin).

| Service | Port | Compose file | What it does |
|---------|------|-------------|-------------|
| **Jellyfin** | 8096 | jellyfin.yaml | Video streaming (movies + TV) |
| **Audiobookshelf** | 13378 | audiobookshelf.yaml | Audiobook + podcast player |
| **Calibre-Web (Hannah)** | 8073 | calibre.yaml | Ebook reader |
| **Calibre-Web (Alex)** | 8074 | calibre.yaml | Ebook reader |
| **qBittorrent** | 8080 | download.yaml | Torrent client (behind PIA VPN) |
| **qBittorrent Private** | 8081 | private.yaml | Secondary torrent client (behind PIA VPN, Netherlands) |
| **Gluetun** | — | download.yaml | VPN container (PIA, Singapore) |
| **Gluetun Private** | — | private.yaml | Secondary VPN (PIA, Netherlands) |
| **Seedbox API** | — | download.yaml | MAM dynamic seedbox registration (see below) |
| **Prowlarr** | 9696 | arr.yaml | Indexer manager (not actively used) |

**Jellyfin remote access, clients, and login → see [`jellyfin.md`](jellyfin.md).** Reached
privately over Tailscale (`http://100.91.137.41:8096`); no public exposure, no Plex paywall.

**Ebook library (Calibre-Web) + cataloging → see [`books.md`](books.md).** The shared calibre
library is managed via `catalog/scripts/books.py` (scan/import/normalize/archive) — never
hand-file into the library.

### Stacks & always-on policy

The VM is provisioned with **8 GB / 6 CPU** (see VM management below), enough to run the
core services plus Jellyfin 24/7. Only `arr` is left off by default — it's rarely needed
and heavy. Historically this VM was 2 GB and running everything OOM-killed qBittorrent;
the RAM bump resolved that.

| Stack | Services | ~RAM | Policy |
|-------|----------|------|--------|
| **download** | gluetun, qbittorrent, autoheal, seedboxapi | ~250 MB | **always-on** — torrent engine + seeding + catalog pipeline |
| **private** | gluetun-private, qbittorrent-private | ~125 MB | **always-on** |
| **calibre** | calibre-web (alex + hannah) | ~310 MB | **always-on** |
| **audiobookshelf** | audiobookshelf | ~40 MB | **always-on** |
| **jellyfin** | jellyfin | ~155 MB (more while scanning/transcoding) | **always-on** — remote streaming must be reachable anytime (see `jellyfin.md`) |
| **arr** | prowlarr, radarr, sonarr, bazarr, flaresolverr | ~550 MB | **on-demand** — downloads are mostly manual; start when managing indexers |

`./scripts/up.sh core` brings up the always-on set (download + private + calibre +
audiobookshelf + jellyfin). Start `arr` only when needed:

```bash
./scripts/up.sh core       # the always-on set (incl. jellyfin)
./scripts/up.sh arr        # when you need indexer search / automation
./scripts/down.sh arr      # frees ~550 MB when done
```

### VM management

The VM is sized in `scripts/vm-start.sh` — currently **8 GB RAM / 6 CPU / 30 GB disk**
on the 16 GB M4 Mac Mini. To change resources, edit that script and restart the VM
(`./vm-stop.sh && ./vm-start.sh`); Colima applies the new limits on next start.

```bash
# In scripts/
./vm-start.sh        # Start Colima VM (8 GB / 6 CPU), mount both drives
./vm-stop.sh         # Stop VM
./up.sh <stack>      # Start containers (download|arr|jellyfin|calibre|audiobookshelf|private|all)
./down.sh <stack>    # Stop containers
./port-status.sh     # Check/sync VPN port forwarding
./server-mode.sh     # Toggle macOS sleep settings for always-on
```

### Colima VM startup

After an **unclean host shutdown/crash**, `vm-start.sh` may fail with
`failed to run attach disk "colima-arr", in use by instance "colima-arr"` — an orphaned
`colima daemon start arr` / `limactl usernet` process (from the aborted start) still holds
the disk lock, even though `colima status` reports the VM as *Stopped*. **Try the gentle fix
first** (no VM recreation):

```bash
colima stop arr -f      # releases the lock + reaps the orphan procs
./scripts/vm-start.sh   # then start normally
```

Only if that doesn't clear it (or the error is specifically `failed to run attach disk`
with no orphan process) fall back to recreating the VM:

```bash
colima delete arr --force
./scripts/vm-start.sh
```

Either way, container data persists on the HDDs (`/Volumes/Blue4/arr/data/`) and in the
native config volumes (`qbit_config`, `jellyfin_config`), so nothing is lost. On boot the
containers auto-restart with the VM (`restart: unless-stopped`); running `./scripts/up.sh core`
afterward is still worth it to confirm they're on the current compose config.

### Gluetun (VPN) troubleshooting

Both gluetun containers use PIA. If one shows unhealthy with TLS handshake failures:

1. The region may be down. Check logs: `docker --context colima-arr logs <container> --tail 20`
2. Clear stale server cache: `docker --context colima-arr exec <container> rm /gluetun/servers.json`
3. If port forwarding fails, clear stale data: `docker --context colima-arr exec <container> rm /gluetun/piaportforward.json`
4. Restart: `docker --context colima-arr restart <container>`
5. If the region is consistently failing, change `SERVER_REGIONS` in `.env` (main) or `compose/private.yaml` (private)

> **2026-07-15:** `gluetun-private` flapped ~every 15s — PIA's **German** endpoints (both
> DE Frankfurt *and* DE Berlin) were failing the OpenVPN TLS handshake, while the main stack
> (Singapore) was fine on the same credentials/server list. Restarts and switching cities
> didn't help (PIA-side outage, not our config). Fix was `SERVER_REGIONS=Netherlands` in
> `compose/private.yaml` — connected healthy immediately. Retry a DE region later if a German
> exit is needed. A flapping VPN is not cosmetic: each reconnect re-announces torrents and can
> trigger tracker "duplicate peer" bans (see MAM section).

### VPN port forwarding (auto-synced)

PIA hands gluetun a **new** forwarded port every time the tunnel fully re-establishes (restart, health-restart, or PIA lease expiry). qBittorrent's listening port is static, so historically it would silently desync → incoming peers fail → slow downloads until noticed.

This is now **automatic**: gluetun's `VPN_PORT_FORWARDING_UP_COMMAND` hook (in `compose/download.yaml`) fires on every port-forward event and pushes the new port into qBittorrent via its WebUI API. It works credential-free because qbit has `WebUI\LocalHostAuth=false` and the call comes from *inside* gluetun's shared network namespace.

- To verify or force a manual re-sync: `./scripts/port-status.sh` (add `--sync`).
- Requires the qbit config flag `WebUI\LocalHostAuth=false` (in `${DATA_PATH}/qbittorrent/qBittorrent/qBittorrent.conf`). If the config is ever wiped, re-add that line or the hook can't push the port.

### qBittorrent WebUI flakiness (auto-healed)

qbit's WebUI occasionally wedges or flaps on a stale single-instance lock socket (an artifact of `/config` on the virtiofs-mounted drive — the `QLocalServer::listen: Unknown error 22` log line), and gets orphaned when gluetun restarts. A Docker **healthcheck** on qbit + the **autoheal** container (both in `compose/download.yaml`) now detect this and restart qbit automatically. autoheal is scoped by the `autoheal=true` label so it only ever touches qbittorrent.

- If qbit still seems down, check `docker --context colima-arr ps` (look for `unhealthy`) and `docker --context colima-arr logs autoheal`.
- **Config-on-virtiofs status:** the **main** qbit was migrated to a native Docker volume
  (`qbit_config`) and Jellyfin likewise (`jellyfin_config`), so they no longer hit this. **`qbittorrent-private` is the last container still on virtiofs** (`${DATA_PATH}/qbittorrent-private`) and it has **no** healthcheck/autoheal — so if it wedges, nothing restarts it. **Backlog:** migrate it to a `qbit_private_config` native volume + add the autoheal healthcheck (same recipe as `compose/download.yaml`). See memory `project_lsio_config_virtiofs`.

### MyAnonamouse (MAM) seedbox API

The `seedboxapi` container registers the VPN IP with MAM as a dynamic seedbox. It runs
through the main gluetun (Singapore, `network_mode: service:gluetun`) and pings MAM every
60 minutes. Because it shares gluetun's network namespace, it can **only** egress through
the VPN — it never uses the host's default route.

> **Boot-race (fixed 2026-07-22):** `depends_on` was a plain `- gluetun`, which only waits
> for the container to *start*, not for the tunnel to be *healthy*. On a cold VM boot,
> seedboxapi's first registration ping fired in the sub-second window before OpenVPN
> established, so MAM saw the host's real egress IP (a Viettel/VN residential IP → ASN 7552)
> and rejected the session with `"Invalid session - ASN mismatch"`. Fixed by making the
> dependency `condition: service_healthy` (gluetun ships a built-in healthcheck). It now
> waits for the tunnel before pinging. If you ever see a non-Singapore IP in the MAM
> response, check that this condition is still in `compose/download.yaml`.

**When MAM_ID expires** (the container logs `"mam_id passed on command line is invalid"`):

1. Log into myanonamouse.net
2. Go to **Preferences → Security**
3. Under "Create session":
   - **IP**: Current VPN IP (`docker --context colima-arr exec gluetun cat /tmp/gluetun/ip`)
   - **IP vs ASN locked session**: **ASN** (better for VPN — IP may change but ASN stays the same)
   - **Allow Session to set Dynamic Seedbox**: **Yes** ← *easy to miss; without it the new
     session registers but seedboxapi is rejected with* `"Incorrect session type - not
     allowed this function"` *(hit 2026-07-22). You can toggle this on the existing session
     and just clear the cookie + restart — no need to mint a whole new ID.*
   - **Label**: `gluetun-singapore` or similar
4. Submit and copy the new session ID
5. Update `MAM_ID` in `.env`
6. Clear old cookies: `rm /Volumes/Blue4/arr/data/seedboxapi/MAM.cookies`
7. Restart: `DOCKER_CONTEXT=colima-arr docker-compose -f compose/download.yaml --env-file .env up -d seedboxapi`
   (or `docker --context colima-arr restart seedboxapi` if `MAM_ID` is unchanged)
8. Verify: `docker --context colima-arr logs seedboxapi --tail 5` — should show `"Success":true`

#### Ban-safety: duplicate peer entries (learned 2026-07-08)

MAM **disabled tracker access** after detecting "duplicate peer entries" — 10 copies each of 3
torrents from the single VPN IP within ~11 minutes. Root cause: the main qBittorrent was in a
**crash loop** (OOM-killed on the then-2 GB VM, auto-restarted by `restart: unless-stopped` +
autoheal, over and over), and **every restart re-announces all torrents**. 10 restarts → 10
"peers" per torrent → MAM's abuse detection tripped.

- **The trigger is any rapid re-announce loop:** client crash-looping (OOM), or a **flapping VPN**
  (each reconnect re-announces — see the Gluetun 2026-07-15 note above).
- **Fixed by** the VM bump to 8 GB / 6 CPU (no more OOM; main qbit stable). We already follow
  MAM's recommended layout — the client is bound to the VPN's network namespace
  (`network_mode: service:gluetun`), not an external killswitch script.
- **If it happens again:** stabilize the client/VPN first (`docker inspect <c> --format '{{.RestartCount}} {{.State.OOMKilled}}'`, check gluetun for TLS-flap loops), *then* reply to the
  MAM ticket explaining the cause + fix. Don't just delete the torrents (MAM says that doesn't
  fix the root cause). Keep torrents **seeding** to maintain ratio.

#### Searching / downloading from MAM

- The **search API works** from inside the VPN with our session cookie (the endpoint the site's
  own search + Prowlarr use):
  `curl -b "mam_id=$MAM_ID" https://www.myanonamouse.net/tor/js/loadSearchJSONbasic.php --data-raw '{"tor":{"text":"<query>","srchIn":{"title":true,"author":true},"searchType":"all","main_cat":[14],"sortType":"seedersDesc"},"perpage":8}'`
  (run it via `docker exec qbittorrent` so it goes out the registered VPN IP; `main_cat` 14=ebooks,
  13=audiobooks). Keep it to a few human-paced queries — MAM bans abusive scraping.
- **Downloading the `.torrent` does NOT work** with the seedbox session — `download.php` returns
  *"Invalid download link, or not signed in"*, and the search JSON carries no download token. The
  seedbox `mam_id` is scoped for search + announce, not `.torrent` downloads (those need a full
  web-login session). **So: grab the `.torrent` from the browser**, drop it in
  `~/Documents/pt/red4/mam/`, add it to qBittorrent (behind the VPN), and it downloads + seeds.
  The proper automated path (if wanted) is the **MAM indexer in Prowlarr** (already installed,
  dormant), which handles the download token correctly.

## DigitalCore (DC)

Primary source for movies and TV. API key stored in `.env` as `DC_API_KEY`.

### API usage

```bash
# Search
curl -s -H "X-API-KEY: $DC_API_KEY" \
  "https://digitalcore.club/api/v1/torrents?searchText=QUERY&limit=20"

# Download .torrent file
curl -s -H "X-API-KEY: $DC_API_KEY" \
  "https://digitalcore.club/api/v1/torrents/download/TORRENT_ID" \
  -o ~/Documents/pt/red4/filename.torrent
```

Response fields: `id`, `name`, `size`, `seeders`, `leechers`, `category`, `added`, `frileech`, `language`.

### Selecting releases

**Library preferences** (derived from existing 600-item catalog):

1. **Codec priority**: AV1 > x265 > x264. We prefer efficient encodes — quality-per-GB matters more than maximum bitrate.
2. **Resolution**: 1080p is the default. 4K only for showcase titles (epic visuals, HDR/DV content).
3. **Audio**: Opus or DD+ is fine for most content. Atmos/TrueHD/DTS-HD for 4K showcase titles.
4. **Source**: BluRay preferred, WEB-DL when BluRay unavailable.
5. **Groups**: KIMJI (AV1+Opus, dominant in library), LAMA, OFT, dAV1nci are trusted. FLUX, NTb for WEB-DL.
6. **Packs**: Prefer complete season/series packs over individual episodes when available.
7. **Size guidance**: For a full TV series, an x265 or AV1 encode is preferred over a raw H.264 WEB-DL that's 2-3x larger. A sitcom doesn't need 1.4 GB/episode.

**Storage**: Blue4 is nearly full (97%). **Default new downloads to Red4** (`~/Documents/pt/red4/`).

### Download workflow

1. Search DC API for the title
2. Pick release based on preferences above
3. Download `.torrent` to `~/Documents/pt/red4/` (or `blue4/` if space permits)
4. qBittorrent picks it up via watch folder or manual add
5. After download completes, run catalog pipeline to track and link

## Catalog scripts

The `catalog.py` script in `catalog/scripts/` automates the tracking pipeline:

```bash
./catalog.py scan torrents      # Find new .torrent files → downloads.json
./catalog.py scan downloads     # Match completed downloads to torrents
./catalog.py import             # Parse metadata from filenames → catalog.json
./catalog.py link               # Create hardlinks to media library
./catalog.py refresh            # Trigger Plex + Jellyfin library scans (--server, --type)
./catalog.py status             # Show pending/linked counts
./catalog.py prune              # Remove entries for deleted torrents
```

**Important**: These scripts are helpers, not the source of truth. They parse metadata from filenames which can be wrong. Always verify the end state — files on disk must match what the tracking data says. When there's a discrepancy, investigate and fix whichever side is wrong.

## What Hannah can ask for

- **"Do we have [movie/show]?"** — search catalog.json
- **"Add [movie/show] to the wishlist"** — update wishlist.json
- **"What's on the wishlist?"** — read wishlist.json
- **"What's downloading / pending?"** — check download and catalog status
- **"Is Jellyfin up?"** — check service status
- **Audiobook/ebook questions** — check what's in the library
