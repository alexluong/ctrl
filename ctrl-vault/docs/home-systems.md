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
| .10 | `rml-225f38`: "Rainbow Music Led" LED strip controller (ESP chip, web UI on :80) | c8:2b:96:22:5f:38 | DHCP | identified from its web page title |
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
| Services seen | Kobo book sync (port unknown), qBittorrent `:8080` and `:8081`, Jellyfin `:8096`, Plex `:32400`, AirPlay `:5000/:7000`, something on `:53` |
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

## Naming, numbering, URLs (agreed 2026-10-02, not applied yet)

**Names.** Physical machines: `g8` (HP 805 G8, today still hostname `pve1`; rename before the first VM), `mini` (Mac Mini), `mbp`. VMs by purpose: `hookdeck`, `enable`, `solex`, `cs`, `ixchel`, later `media`. The same name is the Proxmox VM name, hostname, Tailscale name and DNS label.

**Home range: stay on `192.168.1.x`** (Alex, 2026-10-02). A move to an uncommon range (e.g. `192.168.77.x`) is deferred; once devices use URLs it is a DNS change plus the fixed addresses, not a per-device chore.

| Range | Use |
|---|---|
| `.1–.9` | network gear |
| `.90–.99` | physical servers, fixed: `mini` = `.90`, `g8` = `.91` |
| `.100–.149` | VMs and containers, fixed. **Proxmox VM ID = last number**: `hookdeck` = VM 110 = `.110` |
| `.150–.254` | DHCP pool (phones, TVs, laptops) |

Templates use VM IDs 9000+.

**URLs.** Zone `lab.alexluong.com` (unused as of 2026-10-02; DNS in Cloudflare via collielab terraform; records DNS-only, so Cloudflare's one-level certificate limit doesn't apply).

- One-of-a-kind services, flat: `jellyfin.lab.alexluong.com`, `plex.lab…`, `qbt.lab…`, `g8.lab…` (Proxmox UI). URL survives a move between hosts.
- Per-workspace services under the workspace: `hookdeck.lab.alexluong.com` (main page, T3), `board.hookdeck.lab…`, `t3.enable.lab…`. A host can't share a name with a flat service.
- **Two name sets, same gateway (a container on g8 running Caddy):** `*.lab.alexluong.com` → the gateway's home address, works at home on every device with no Tailscale (verified: router and Viettel DNS return private addresses for public names). `*.ts.alexluong.com` → the gateway's Tailscale address, works anywhere with Tailscale on, whatever range the other network uses (proposed). Same service names under both: `jellyfin.lab…` / `jellyfin.ts…`. No subnet router needed. Without Tailscale away: nothing connects.
- Caddy gets Let's Encrypt wildcard certificates by DNS check (no open ports); one wildcard per level (`*.lab…`, `*.hookdeck.lab…`). Only the gateway holds the Cloudflare token (scoped to `alexluong.com`); VMs hold none.
- SSH: `ssh g8`, `ssh hookdeck`, `ssh mini` via `~/.ssh/config` aliases.

**If the range changes later:** update the DNS records, the gateway's backend addresses and the fixed addresses on g8, the Mini and VMs; devices that use URLs (Kobo, TV apps) keep working. So point the Kobo (today `192.168.1.90`, typed in its config; service/port on the Mini not found by scan, Mini session to document) and the TV's Jellyfin/Plex apps at URLs once the gateway exists. Other costs: house offline a few minutes; router admin moves; mesh nodes might need re-pairing; a Viettel reset puts the range back. To avoid locking g8 out: give it both addresses first, switch the router, then drop the old one.

## SSH keys on the MBP (2026-10-02)

| Key | Passphrase | In agent | Used for |
|---|---|---|---|
| `github_alexluong` | yes (Keychain) | yes | GitHub, collielab VM (`sshmylab`), **home servers and VMs** |
| `gitlab_alexluong` | yes | no | GitLab |
| `id_ed25519` | yes | no | nothing known (created 2026-08-30) |
| `id_ed_hookdeck` | no | no | Hookdeck jump boxes (`hd_jumpbox`, `hd_jumpbox_stg`) |
| `google_compute_engine` | no | no | gcloud |

One personal key (`github_alexluong`) for all of Alex's own machines: it is the only one loaded in the agent, so it is the only one Claude can use without a prompt. `~/.ssh/config` has no entries for home machines yet; its first line includes `~/.colima/ssh_config`, which no longer exists (harmless).

## Open

- [ ] Router: DHCP pool range; apply the address plan; save router login to Vaultwarden
- [ ] pve1: `ssh-copy-id` from the MBP
- [ ] Mac Mini: Remote Login + MBP key, specs, wired vs Wi-Fi → `mac-mini.md`
- [ ] Later: Tailscale account + install on MBP/phone, `ts` names
- [ ] Identify the unidentified devices (`.57`, `.124`, `.129/.130`)
- [ ] Confirm how the Mini is fixed at `.90` (router reservation vs set on the Mac)
