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

A full first scan of the whole library takes a few minutes. Series metadata/images fill in
after the episode files are indexed.

## Setup notes (how it was built)

- Fresh setup on 2026-07-14. An earlier abandoned setup (users `admin`/`alex`, no
  libraries) was moved aside to `$DATA_PATH/jellyfin.bak-<timestamp>` and a clean instance
  was configured via the startup API.
- Admin user `alex` created; remote access enabled; UPnP off (we don't port-forward —
  Tailscale handles remote).
- **VM was resized from 2 GB / 2 CPU to 8 GB / 6 CPU** (`scripts/vm-start.sh`) because the
  library scan was starving the 2 GB VM and OOM-killing containers. See
  `README.md` → VM management.
