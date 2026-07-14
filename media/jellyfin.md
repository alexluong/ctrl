# Jellyfin

Media server for **remote streaming** (movies + TV) to phone / laptop / TV.

## Why Jellyfin (and not Plex)

Plex started charging for **remote** playback in 2025 — with no Plex Pass, streaming
from outside the home network hits a paywall, even for the server owner. Jellyfin has
**no such paywall**: remote streaming is free. We reach it privately over Tailscale, so
nothing is exposed to the public internet. Plex is still installed and fine on the LAN;
Jellyfin is the one to use away from home.

## How to access

| Where you are | URL |
| --- | --- |
| Home wifi (no VPN needed) | `http://192.168.1.90:8096` |
| Anywhere (Tailscale on) | `http://100.91.137.41:8096` |
| Anywhere (Tailscale, by name) | `http://alexs-mac-mini.tail2b958c.ts.net:8096` |

**Login:** user `alex` — password is in `media/.env` (`JELLYFIN_ADMIN_PASS`).

### Recommended: just leave Tailscale on

Simplest setup — leave Tailscale **on** on the phone/laptop and always use the tailnet
address `100.91.137.41:8096`. When you're home, Tailscale connects the two devices
**directly over the LAN** (full local speed, no internet hop); when you're out, it routes
over the internet. One address, works everywhere, negligible battery.

- The **tailnet IP `100.91.137.41` is stable** — prefer it.
- The **LAN IP `192.168.1.90` can change** on DHCP lease renewal. If you rely on it, set a
  DHCP reservation for the Mac Mini in the router, or just use the tailnet address.

### Tailscale

- Tailscale runs on the Mac Mini (host, not in the VM). CLI lives at
  `/Applications/Tailscale.app/Contents/MacOS/Tailscale`.
- Check state: `/Applications/Tailscale.app/Contents/MacOS/Tailscale status`
- Account: `lhtanh98@`. Devices: `alexs-mac-mini` (this box), `iphone-15-pro`.
- To add a device: install Tailscale, log in with the **same account**.

## Clients

No hardware transcoding is available inside the Linux VM (the M4's VideoToolbox isn't
passed through), so **transcoding is software/CPU-only**. The library is mostly x265
10-bit — pick clients that **direct-play** so the server just streams the file untouched
(lighter + best quality). Avoid remote 4K (heavy software transcode).

| Platform | Client | Notes |
| --- | --- | --- |
| iOS | **Swiftfin** (free, official) | Direct-plays HEVC 10-bit. *Infuse* (paid) for a nicer UI. |
| macOS | **Jellyfin Media Player** (MPV) | Plays everything. Swiftfin also runs on Apple Silicon. |
| Android TV | **Jellyfin for Android TV** | *Findroid* is a nice native alternative. |

## Libraries

Container paths come from the drive mounts (`/Volumes/Blue4/arr -> /Blue4`,
`/Volumes/Red4/arr -> /Red4`).

- **Movies** → `/Red4/media/movies`, `/Blue4/media/movies` (+ `movies4k` on both)
- **TV Shows** → `/Red4/media/tv`, `/Blue4/media/tv` (+ `tv4k` on both)

New content added by the catalog pipeline lands in these folders and is picked up by the
next library scan.

## Operations

Jellyfin is part of the **always-on** stack (see `README.md` → Stacks & always-on policy).

```sh
./scripts/up.sh jellyfin      # start
./scripts/down.sh jellyfin    # stop
docker --context colima-arr logs jellyfin
```

### Force a scan

Dashboard → Libraries → "Scan All Libraries", or via API:

```sh
# authenticate -> token
J=http://localhost:8096
AUTH='Authorization: MediaBrowser Client="cli", Device="cli", DeviceId="cli", Version="1.0"'
TOKEN=$(curl -s -X POST "$J/Users/AuthenticateByName" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"Username":"alex","Pw":"<pass from .env>"}' | grep -o '"AccessToken":"[^"]*"' | cut -d'"' -f4)

# scan everything
curl -s -X POST "$J/Library/Refresh" -H "X-Emby-Token: $TOKEN"
```

### API cookbook

All calls need the token above (`H="X-Emby-Token: $TOKEN"`). Query-param `?X-Emby-Token=`
auth is unreliable — **use the header**. Get the user id and library ids first:

```sh
JFUID=$(curl -s "$J/Users" -H "$H" | grep -o '"Id":"[^"]*"' | head -1 | cut -d'"' -f4)
curl -s "$J/Library/VirtualFolders" -H "$H" | python3 -c \
  "import sys,json;[print(f['Name'],f['ItemId']) for f in json.load(sys.stdin)]"
# item counts
curl -s "$J/Items?Recursive=true&IncludeItemTypes=Movie&Limit=0&userId=$JFUID" -H "$H" \
  | grep -o '"TotalRecordCount":[0-9]*'
# scan a single library (fast, no metadata): use its ItemId
curl -s -X POST "$J/Items/<LIB_ID>/Refresh?Recursive=true&MetadataRefreshMode=None&ImageRefreshMode=None" -H "$H"
# force full metadata + artwork re-fetch (see gotcha below)
curl -s -X POST "$J/Items/<LIB_ID>/Refresh?Recursive=true&MetadataRefreshMode=FullRefresh&ImageRefreshMode=FullRefresh&ReplaceAllMetadata=true&ReplaceAllImages=true" -H "$H"
# stop a running scan
curl -s "$J/ScheduledTasks" -H "$H" | grep -o '"Id":"[^"]*"'   # find "Scan Media Library"
curl -s -X DELETE "$J/ScheduledTasks/Running/<TASK_ID>" -H "$H"
```

### Gotchas / lessons (learned the hard way, 2026-07-14/15)

1. **Scan speed is disk-I/O-bound, not CPU/RAM.** Jellyfin `ffprobe`s every file, and the
   library is on external USB drives via the virtiofs mount (~2s/file). A first scan of the
   whole library is ~25 min for TV + similar for movies. More RAM does not speed this up
   (the 8 GB bump was to stop OOM, a separate issue). Future incremental scans are fast.
2. **A combined "Scan All" does Movies fully, then TV.** To get shows sooner, scan the TV
   library alone via `/Items/<TVID>/Refresh` rather than `/Library/Refresh`.
3. **Metadata/artwork requires fetchers to be configured — and creating a library via the
   API leaves them EMPTY.** Symptom: posters never populate no matter how many refreshes you
   run (`TypeOptions: []`, only embedded art appears). Fix: set `EnableInternetProviders=true`
   AND populate `TypeOptions` with `TheMovieDb` per type (Movie / Series / Season / Episode),
   then `FullRefresh`. Get valid fetcher names from
   `GET /Libraries/AvailableOptions?libraryContentType=movies|tvshows`.
4. **`MetadataRefreshMode=Default` skips items already marked "refreshed"** — even if they
   have no art. After a metadata-free scan you must use `FullRefresh` + `ReplaceAll*=true` to
   force fetching.
5. **`POST /Library/Media/Updated` (targeted path scan) does nothing here** even with the
   library monitor on — don't rely on it to scan a single show.
6. **Changing the admin password invalidates existing API tokens** — re-authenticate after.
7. No hardware transcoding in the VM — see Clients; keep clients direct-playing.

A full first scan of the whole library takes ~25+ min per library (I/O bound). Metadata and
artwork are a separate, network-bound pass on top (TMDB, ~10 items/min).

## Setup notes (how it was built)

- Fresh setup on 2026-07-14. An earlier abandoned setup (users `admin`/`alex`, no
  libraries) was moved aside to `$DATA_PATH/jellyfin.bak-<timestamp>` and a clean instance
  was configured via the startup API.
- Admin user `alex` created; remote access enabled; UPnP off (we don't port-forward —
  Tailscale handles remote).
- **VM was resized from 2 GB / 2 CPU to 8 GB / 6 CPU** (`scripts/vm-start.sh`) because the
  library scan was starving the 2 GB VM and OOM-killing containers. See
  `README.md` → VM management.
