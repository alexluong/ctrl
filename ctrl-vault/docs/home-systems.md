# Home systems

Map of the home network: devices, addresses, what runs where, how each is reached.
Machine conventions (repo layout, MBP tooling): `machine.md`. Cloud homelab VM: `collielab.md`.
Scanned from the MBP 2026-10-02 (ping sweep, mDNS, port probes); re-scan before trusting a DHCP address.

## Network

- ISP: Viettel (fiber). LAN `192.168.1.0/24`, gateway `192.168.1.1`, DNS = Viettel's (handed out by the router).
- Router: **ZTE F6601P** (Viettel ONT + router + Wi-Fi), `192.168.1.1`, admin UI `http://192.168.1.1`.
- Mesh nodes: 2 × **ZTE H3601P**, `192.168.1.3` and `192.168.1.5` (admin UI on each).
- DHCP pool range: **unknown, check in router**. Leases seen from `.3` to `.131`, so the pool likely starts near `.2` and `.21` sits inside it.
- No Tailscale anywhere yet. No port forwards known.

## Devices

| IP | Device | MAC | Address type | Notes |
|---|---|---|---|---|
| .1 | ZTE F6601P router | 68:9e:29:a2:a1:d6 | fixed | gateway, DHCP, DNS relay |
| .3 | ZTE H3601P mesh node | 80:2d:1a:0c:16:70 | DHCP? | |
| .5 | ZTE H3601P mesh node | 80:2d:1a:0c:13:74 | DHCP? | |
| .4 | Chromecast | 90:ca:fa:b1:7c:6e | DHCP | |
| .7 | Chromecast | 90:ca:fa:ad:e9:ee | DHCP | |
| .10 | `rml-225f38` (Espressif IoT, web UI on :80) | c8:2b:96:22:5f:38 | DHCP | what is it? |
| **.21** | **`pve1`: HP EliteDesk 805 G8 Mini (Proxmox)** | 84:69:93:4f:fe:41 | **static, set on the box** | wired to router |
| .39 | Hannah's iPad | private MAC | DHCP | |
| **.90** | **Mac Mini (`alexs-Mac-mini.local`)** | a6:54:90:62:c6:fe (private → Wi-Fi?) | DHCP | media host |
| .91 | MacBook Pro (`Alexs-MacBook-Pro`) | private MAC | DHCP | Wi-Fi (`en0`) |
| .131 | `HNNHPHM-PC` (Windows, SMB open) | f0:57:a6:cf:9c:7f | DHCP | |
| .57, .124, .129/.130 | unidentified, private MACs, no open ports | | DHCP | phones/watches likely |

Private (randomized) MACs change if the device's Wi-Fi setting is "Rotating"; a router reservation only holds when it is "Fixed" or the device is wired.

## Servers

### pve1 (HP EliteDesk 805 G8 Mini)

Ryzen 7 5700G (8c/16t), 64GB DDR4, 1TB NVMe. Proxmox VE, installed by the shop (xeon.vn). Buying trail: `work/task-1/decision.md`. Setup: TASK-2, `work/task-2/plan.md`.

| | |
|---|---|
| Address | `192.168.1.21/24`, gw `.1`, bridge `vmbr0` on `eno1` |
| Web UI | `https://192.168.1.21:8006`, user `root`, realm Linux PAM (self-signed cert) |
| SSH | `root@192.168.1.21`: **MBP key not installed yet** (password login only) |
| Root password | Vaultwarden, item `pve1 root (Proxmox)` |
| BIOS | SVM on; After Power Loss = Power On (Advanced → Boot Options) |
| Console | none remote; needs monitor (DisplayPort) + USB keyboard at the box |
| VMs | none yet. First: hookdeck workspace |

### Mac Mini (base M4)

| | |
|---|---|
| Address | `192.168.1.90` (DHCP), `alexs-Mac-mini.local` |
| SSH | **off** (Remote Login disabled; port 22 closed) |
| Services seen | qBittorrent `:8080`, Jellyfin `:8096`, Plex `:32400`, AirPlay `:5000/:7000`, something on `:53` |
| Arrstack | `hub/alexluong/arr` (gluetun, qbittorrent, prowlarr, radarr, sonarr) on Colima; data on Samsung T7 (`/Volumes/T7/arr`) |
| Unknown | exact specs, macOS version, wired vs Wi-Fi, T7 filesystem. Details go in `mac-mini.md` (written from a session on the Mini) |

### collielab VM (cloud, Vultr)

`sshmylab` → `alex@149.28.40.6`. Vaultwarden etc. See `collielab.md`.

## Access (from the MBP)

| Target | Web | SSH | Status |
|---|---|---|---|
| Router | `http://192.168.1.1` | n/a | login on the router's sticker (save to Vaultwarden) |
| pve1 host | `https://192.168.1.21:8006` | `root@192.168.1.21` | web works; SSH key pending |
| pve1 VMs | n/a | `alex@<vm>` | none yet |
| Mac Mini | Jellyfin/Plex/qBittorrent ports above | off | Remote Login to enable |
| collielab VM | `vault.collie.studio` etc. | `sshmylab` | works |

Home-only today: everything on `192.168.1.x` is reachable only on home Wi-Fi. Tailscale (planned) makes pve1, its VMs and the Mini reachable from anywhere.

## Address plan (proposed, not applied)

- `.1–.9` network gear (as is)
- `.20–.49` servers and VMs, static: pve1 `.21`, hookdeck VM `.22`, later VMs `.23+`
- `.50–.254` DHCP pool
- Mac Mini: router reservation to keep `.90`

Applying it = one router change (DHCP pool start → `.50`) plus one reservation.

## Open

- [ ] Router: DHCP pool range; apply the address plan; save router login to Vaultwarden
- [ ] pve1: `ssh-copy-id` from the MBP
- [ ] Mac Mini: Remote Login + MBP key, specs, wired vs Wi-Fi → `mac-mini.md`
- [ ] Tailscale account + install on MBP/phone
- [ ] Identify `.10` (`rml-225f38`) and the unidentified devices
