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

Torrent files (`.torrent`) are stored locally, organized by target drive:

```
~/Documents/pt/
├── blue4/         # Torrents whose downloads go to Blue4
└── red4/          # Torrents whose downloads go to Red4
```

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
| **qBittorrent Private** | 8081 | private.yaml | Secondary torrent client (behind PIA VPN, DE Berlin) |
| **Gluetun** | — | download.yaml | VPN container (PIA, Singapore) |
| **Gluetun Private** | — | private.yaml | Secondary VPN (PIA, DE Berlin) |
| **Seedbox API** | — | download.yaml | MAM dynamic seedbox registration (see below) |
| **Prowlarr** | 9696 | arr.yaml | Indexer manager (not actively used) |

### VM management

```bash
# In scripts/
./vm-start.sh        # Start Colima VM, mount both drives
./vm-stop.sh         # Stop VM
./up.sh <stack>      # Start containers (download|arr|jellyfin|calibre|audiobookshelf|private|all)
./down.sh <stack>    # Stop containers
./port-status.sh     # Check/sync VPN port forwarding
./server-mode.sh     # Toggle macOS sleep settings for always-on
```

### Colima VM startup

If the VM fails to start with "failed to run attach disk", the previous instance left stale state. Fix with:

```bash
colima delete arr --force
# Then start fresh:
./scripts/vm-start.sh
```

This recreates the VM from scratch. Container data persists on the HDDs (`/Volumes/Blue4/arr/data/`), so nothing is lost.

### Gluetun (VPN) troubleshooting

Both gluetun containers use PIA. If one shows unhealthy with TLS handshake failures:

1. The region may be down. Check logs: `docker --context colima-arr logs <container> --tail 20`
2. Clear stale server cache: `docker --context colima-arr exec <container> rm /gluetun/servers.json`
3. If port forwarding fails, clear stale data: `docker --context colima-arr exec <container> rm /gluetun/piaportforward.json`
4. Restart: `docker --context colima-arr restart <container>`
5. If the region is consistently failing, change `SERVER_REGIONS` in `.env` (main) or `compose/private.yaml` (private)

### MyAnonamouse (MAM) seedbox API

The `seedboxapi` container registers the VPN IP with MAM as a dynamic seedbox. It runs through the main gluetun (Singapore) and pings MAM every 60 minutes.

**When MAM_ID expires** (the container will restart-loop with "mam_id passed on command line is invalid"):

1. Log into myanonamouse.net
2. Go to **Preferences → Security**
3. Under "Create session":
   - **IP**: Current VPN IP (`docker --context colima-arr exec gluetun cat /tmp/gluetun/ip`)
   - **IP vs ASN locked session**: **ASN** (better for VPN — IP may change but ASN stays the same)
   - **Allow Session to set Dynamic Seedbox**: **Yes**
   - **Label**: `gluetun-singapore` or similar
4. Submit and copy the new session ID
5. Update `MAM_ID` in `.env`
6. Clear old cookies: `rm /Volumes/Blue4/arr/data/seedboxapi/MAM.cookies`
7. Restart: `DOCKER_CONTEXT=colima-arr docker-compose -f compose/download.yaml --env-file .env up -d seedboxapi`
8. Verify: `docker --context colima-arr logs seedboxapi --tail 5` — should show `"Success":true`

## Catalog scripts

The `catalog.py` script in `catalog/scripts/` automates the tracking pipeline:

```bash
./catalog.py scan torrents      # Find new .torrent files → downloads.json
./catalog.py scan downloads     # Match completed downloads to torrents
./catalog.py import             # Parse metadata from filenames → catalog.json
./catalog.py link               # Create hardlinks to media library
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
