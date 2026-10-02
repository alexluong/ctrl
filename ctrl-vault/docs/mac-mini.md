# Mac mini (home server)

The always-on box at home that runs the `media/` stack (Plex + the arr/Jellyfin
containers) and is managed remotely over SSH from the MacBook Pro. This documents
what the machine is, what runs on it, how to reach it, and what would block moving
the stack to a Linux VM on Proxmox later.

_No secrets live in this file — only where they live. Captured 2026-10-02._

## Specs

| | |
|---|---|
| Model | Mac mini (`Mac16,10`), Apple **M4**, 10-core (4P/6E) |
| RAM | 16 GB |
| Internal disk | 245 GB APFS (`disk0`), ~61 GB free |
| macOS | 15.5 (build 24F74) |
| Serial | `XV2L2GK9K7` |
| ComputerName | "alex's Mac mini" / mDNS `alexs-Mac-mini.local` |
| Only user account | `alex` |

## Network

- **On Wi-Fi, not wired.** Ethernet `en0` is inactive (no cable plugged).
- Active interface: **Wi-Fi `en1` → `192.168.1.90`** (netmask /24).
  - MAC `a6:54:90:62:c6:fe` — a **private/randomized** Wi-Fi address (locally
    administered). The IP has been stable but *could* drift; prefer the mDNS or
    Tailscale name below over the raw IP.
- **Tailscale** (host app): this node = `alexs-mac-mini` → **`100.91.137.41`**,
  reachable from anywhere on the tailnet (account `lhtanh98@`).
- Three ways to reach it, most → least robust to IP changes:
  1. `alex@100.91.137.41` (Tailscale — works off-LAN)
  2. `alex@alexs-Mac-mini.local` (mDNS — survives DHCP changes on-LAN)
  3. `alex@192.168.1.90` (raw LAN IP)

> `*:53` is held by `limactl usernet` (Colima's internal user-mode networking) —
> **not** a DNS server you run. Ignore it.

## Storage

| Volume | Device | Size (vol) | Free | FS | Role |
|---|---|---|---|---|---|
| Macintosh HD | internal `disk0` | 245 GB | ~61 GB | APFS | OS + apps + Plex/Colima config |
| **Blue4** | external USB `disk4` (4 TB) | 3.1 TB | ~817 GB | APFS | media + downloads |
| **Red4** | external USB `disk5` (4 TB) | 3.8 TB | ~191 GB | APFS | media + downloads |

- Both externals are **APFS** (each has its own EFI partition; GPT). Mounted at
  `/Volumes/Blue4` and `/Volumes/Red4`; the stack uses the `arr/` subdir on each.
- Downloads and the Plex/Jellyfin library are **hardlinked within the same drive**
  (download ↔ library share inodes) — this is why both must stay on one filesystem.

## Services

### Plex — native macOS app (not containerized)
- `/Applications/Plex Media Server.app`, v1.43.3, ports **32400** (main), 32401,
  32600 (tuner). Config + token under
  `~/Library/Application Support/Plex Media Server/`.

### Colima VM `arr` → the container stack
- Docker context **`colima-arr`** (`export DOCKER_CONTEXT=colima-arr`).
- VM sized **8 GB / 6 CPU / 30 GB disk** (`media/scripts/vm-start.sh`), virtiofs.
- External drives mounted into the VM read-write: `/Volumes/Blue4/arr` → `/Blue4`,
  `/Volumes/Red4/arr` → `/Red4`.

| Container | Host port | Notes |
|---|---|---|
| `gluetun` | 8080, 9696 | PIA VPN (Netherlands); shares netns with qbittorrent + prowlarr |
| `qbittorrent` | (via gluetun :8080) | main downloader |
| `gluetun-private` + `qbittorrent-private` | 8081 | second VPN'd downloader |
| `jellyfin` | **8096** | primary remote-streaming app (over Tailscale) |
| `audiobookshelf` | 13378 | audiobooks |
| `calibre-web-alex` / `calibre-web-hannah` | 8074 / 8073 | ebooks (shared calibre library) |
| `prowlarr` | 9696 (via gluetun) | indexers — **on-demand (`arr` profile)** |
| `radarr` / `sonarr` / `bazarr` | 7878 / 8989 / 6767 | **on-demand (`arr` profile)** |
| `flaresolverr` | — | cloudflare solver — on-demand |
| `seedboxapi` | — | MAM session keepalive (currently crash-looping on a dead `MAM_ID`) |
| `autoheal` | — | restarts containers labelled `autoheal=true` |

- **Always-on set** (`scripts/up.sh core`): download (gluetun+qbit), private,
  calibre, audiobookshelf, jellyfin. Only the **`arr`** profile is on-demand.
- Stack control: `media/scripts/up.sh <stack>` / `down.sh <stack>`; VM lifecycle
  `vm-start.sh` / `vm-stop.sh`.

### Other host software
Tailscale, Jump Desktop daemon (`com.p5sys.jump.connect`), PIA VPN daemon,
iStat Menus, Setapp, Logi G HUB.

## Startup & power

- **Sleep is disabled** (`pmset sleep 0`, plus a `caffeinate` running); display
  sleeps at 10 min; Wake-on-LAN (`womp`) on.
- **Auto-restart after power failure is OFF** (`autorestart 0`) — by choice. After
  a power loss the Mac stays off until powered on by hand.
- **Colima does NOT auto-start on boot** (no launch agent). After any
  reboot/power-on the containers are down until you run `media/scripts/vm-start.sh`
  then `scripts/up.sh core`. **Plex (native app) does come back on login.**
  → Reaching the box via SSH works immediately after power-on (see below); the
  *media containers* need the manual VM start.

## SSH access (manage from the MacBook Pro)

- **Remote Login is enabled** and **restricted to `alex`** via the
  `com.apple.access_ssh` group. Service is launched on-demand by `launchd`
  (persists across reboots — no re-enabling needed).
- The MacBook Pro's public key (`alexluong@Alexs-MacBook-Pro.local`) is installed
  in `~/.ssh/authorized_keys` (dir `700`, file `600`).
- Host key fingerprint (ED25519) to verify on first connect:
  `SHA256:W06CBmqKhXnLrnUqkKQJ/bYV05tLrDc3vxcjI0O6W3E`
- Connect: `ssh alex@100.91.137.41` (Tailscale) · `ssh alex@alexs-Mac-mini.local`
  · `ssh alex@192.168.1.90`.

**Keys-only hardening** (recommended; apply after confirming key login works):
```sh
sudo tee /etc/ssh/sshd_config.d/100-keys-only.conf >/dev/null <<'EOF'
PasswordAuthentication no
KbdInteractiveAuthentication no
ChallengeResponseAuthentication no
EOF
sudo sshd -t && echo "config valid"
```
macOS spawns `sshd` per-connection, so this applies to new connections with no
restart and no risk to an existing session.

## Secrets — locations only (never commit)

- `media/.env` (gitignored): `DC_API_KEY`, PIA/OpenVPN creds, `MAM_ID`,
  `DATA_PATH`, `JELLYFIN_ADMIN_USER/PASS`.
- Plex token: `~/Library/Application Support/Plex Media Server/.LocalAdminToken`.
- SSH host keys: `/etc/ssh/ssh_host_*`. User SSH keys: `~/.ssh/`.

## Migration blockers → Linux VM on Proxmox

- **APFS externals.** Linux can't mount APFS read-write. Either copy ~6 TB of media
  to ext4/XFS or reformat the drives (destructive) — the biggest lift.
- **Plex is a native macOS app.** On Linux it becomes the `plexinc/pms-docker`
  container; re-claim the server + migrate `Application Support` library DB.
- **Hardlink layout** must stay same-filesystem after the move (download ↔ library).
- **Hardware transcoding.** Mac uses VideoToolbox; on Proxmox you'd pass through an
  Intel iGPU (QSV) or NVIDIA GPU to the guest, or run CPU-only.
- **Portable already:** gluetun/PIA, qBittorrent, Jellyfin, calibre, audiobookshelf
  are all containers — they lift-and-shift once storage + paths are sorted.
  virtiofs mounts (`/Blue4`, `/Red4`) just become real Linux bind mounts.
- **Tailscale** needs re-auth on the new host (or use an auth key).
