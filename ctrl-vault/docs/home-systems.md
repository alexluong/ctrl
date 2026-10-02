# Home systems

Map of the home network: devices, addresses, what runs where, how each is reached.
Machine conventions (repo layout, MBP tooling): `machine.md`. Cloud homelab VM: `collielab.md`.
Earlier router work (existing reservations, router menus, DNS notes): `home-network-handoff.md`, reconciled below.
Scanned from the MBP 2026-10-02 (ping sweep, mDNS, port probes); re-scan before trusting a DHCP address.

## Network

- ISP: Viettel (fiber). LAN `192.168.1.0/24`, gateway `192.168.1.1`, DNS = Viettel's (handed out by the router).
- Router: **ZTE F6601P** (Viettel ONT + router + Wi-Fi, internet login by PPPoE on the router), `192.168.1.1`, admin UI `https://192.168.1.1` (login in Vaultwarden). 3 of 4 LAN ports in use.
- Mesh nodes: 2 × **ZTE H3601P**, `192.168.1.3` and `192.168.1.5` (admin UI on each).
- DHCP pool: **`.2–.99`** (end changed from `.254` by Alex 2026-10-02), lease time 1 hour. `.100–.254` is never handed out.
- Wi-Fi name: "Dunder Mifflin". Router sits in a closed cabinet with the G8.
- Router menus: Local Network → LAN → DHCP; "DHCP Binding" (reservations) at the bottom; the same page lists handed-out addresses (incl. stale ones). **Never factory-reset**: it wipes the fiber login and internet stays down until Viettel reprovisions (support 18008119).
- Viettel blocks some sites at DNS level and hijacks port 53; only encrypted DNS gets around it. Direction was hosted encrypted DNS per device, not a home DNS server (power cuts happen overnight).
- Tailscale: handoff notes say in use (Mini, remote access with Jump Desktop); **not installed on the MBP** (checked 2026-10-02). No port forwards known.

## Devices

| IP | Device | MAC | Address type | Notes |
|---|---|---|---|---|
| .1 | ZTE F6601P router | 68:9e:29:a2:a1:d6 | fixed | gateway, DHCP, DNS relay |
| .3 | ZTE H3601P mesh node | 80:2d:1a:0c:16:70 | DHCP? | |
| .5 | ZTE H3601P mesh node | 80:2d:1a:0c:13:74 | DHCP? | |
| .4 | Chromecast | 90:ca:fa:b1:7c:6e | DHCP | the "unidentified" device in the handoff notes |
| .7 | Chromecast | 90:ca:fa:ad:e9:ee | DHCP | |
| .10 | `rml-225f38`: "Rainbow Music Led" LED strip controller (ESP chip, web UI on :80) | c8:2b:96:22:5f:38 | DHCP | identified from its web page title |
| **.100** | **`g8`: HP EliteDesk 805 G8 Mini (Proxmox)** | 84:69:93:4f:fe:41 | **typed into the box** | wired to router; was `pve1` at `.21` until 2026-10-02 |
| .39 | Hannah's iPad | private MAC | DHCP | |
| **.90** | **Mac Mini (`alexs-Mac-mini.local`)** | a6:54:90:62:c6:fe (private → Wi-Fi?) | DHCP | media host |
| .91 | MacBook Pro (`Alexs-MacBook-Pro`) | private MAC | DHCP | Wi-Fi (`en0`) |
| .131 | `HNNHPHM-PC` (Windows, SMB open) | f0:57:a6:cf:9c:7f | DHCP | |
| .57, .124, .129/.130 | unidentified, private MACs, no open ports | | DHCP | phones/watches likely |

Private (randomized) MACs change if the device's Wi-Fi setting is "Rotating"; a router reservation only holds when it is "Fixed" or the device is wired.

## Reservations on the router (DHCP Binding; confirmed from the router page 2026-10-02)

| IP | Binding name | Device | MAC bound |
|---|---|---|---|
| .80 | `md5stickc` | M5StickC (ESP32, Kobo page-turner remote) | f0:24:f9:97:86:98 |
| .90 | `Mac Mini` | Mac Mini, Wi-Fi | a6:54:90:62:c6:fe (its Fixed private address; hardware `1c:f6:4c:48:61:cd`, ethernet `1c:f6:4c:38:57:c2`) |
| .91 | `MBP` | MacBook Pro, Wi-Fi | 0e:90:e1:ca:88:2a (private; hardware `f8:4d:89:5f:c9:81`) |
| .92 | `Kobo Alex` | Kobo | a4:3c:d7:3a:65:42 |
| .93 | `Kobo Ha` | Kobo | a4:3c:d7:56:bb:f9 |

If a Mac's private Wi-Fi address changes (setting switched to Rotating or Off, or the Mini moves to ethernet), its binding stops matching.

Earlier scheme: `.80–.89` boards and DIY, `.90–.99` consumer devices, everything else handed out automatically.

## Servers

### g8 (HP EliteDesk 805 G8 Mini)

Ryzen 7 5700G (8c/16t), 64GB DDR4, 1TB NVMe. Proxmox VE 9.0.3, installed by the shop (xeon.vn); as-delivered state: `work/task-2/discovery.md`. Buying trail: `work/task-1/decision.md`. Setup: TASK-2, `work/task-2/plan.md`.

| | |
|---|---|
| Address | `192.168.1.100/24`, gw `.1`, bridge `vmbr0` on `eno1`. Hostname `g8.lab.alexluong.com`. DNS `192.168.1.1`, `1.1.1.1` |
| Web UI | `https://g8.lab.alexluong.com:8006` (or `https://192.168.1.100:8006`), user `root`, realm Linux PAM (self-signed cert) |
| SSH | `ssh g8` (MBP `~/.ssh/config`: `root@192.168.1.100`, key `id_ed25519` from Keychain). Password login still on |
| Root password | Vaultwarden, item `g8 root (Proxmox)` (Alex to rename the item and its URL) |
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
| Also (handoff notes) | Audiobookshelf, Kavita, Calibre-Web (Kobo sync); TerraMaster DAS attached; on Wi-Fi; remote access via Jump Desktop and Tailscale |
| Unknown | exact specs, macOS version, T7 filesystem. Details go in `mac-mini.md` (written from a session on the Mini) |

### collielab VM (cloud, Vultr)

`sshmylab` → `alex@149.28.40.6`. Vaultwarden etc. See `collielab.md`.

## Access (from the MBP)

| Target | Web | SSH | Status |
|---|---|---|---|
| Router | `https://192.168.1.1` | n/a | works; login in Vaultwarden |
| g8 host | `https://192.168.1.100:8006` | `ssh g8` | both work |
| g8 VMs | n/a | `alex@<vm>` | none yet |
| Mac Mini | Jellyfin/Plex/qBittorrent ports above | off | Remote Login to enable |
| collielab VM | `vault.collie.studio` etc. | `sshmylab` | works |

Home-only today: everything on `192.168.1.x` is reachable only on home Wi-Fi. Tailscale (planned) makes g8, its VMs and the Mini reachable from anywhere.

## Naming, numbering, URLs (agreed 2026-10-02; names and addresses applied, URLs not yet)

**Names.** Physical machines: `g8` (HP 805 G8; renamed from `pve1` 2026-10-02), `mini` (Mac Mini), `mbp`. VMs by purpose: `hookdeck`, `enable`, `solex`, `cs`, `ixchel`, later `media`. The same name is the Proxmox VM name, hostname, Tailscale name and DNS label.

**Home range: stay on `192.168.1.x`** (Alex, 2026-10-02). A move to an uncommon range (e.g. `192.168.77.x`) is deferred; once devices use URLs it is a DNS change plus the fixed addresses, not a per-device chore.

| Range | Use |
|---|---|
| `.1` | router |
| `.2–.79` | handed out automatically by the router (phones, TVs, guests, mesh nodes) |
| `.80–.99` | **reserved on the router** (DHCP Binding; the machine asks, always gets the same answer): `.80` ESP32, `mini` `.90`, `mbp` `.91`, Kobos `.92–.93`; future Macs/Windows PCs `.94+` (grow down into the `.80s` if needed) |
| `.100–.254` | **ours, typed into the machine; the router never hands these out** (pool = `.2–.99`). No router change per machine or VM |
| `.100–.149` | `g8` block (50, Alex): host `.100`, its VMs and containers `.101–.149`. **Proxmox VM ID = last number**: `hookdeck` = VM 101 = `.101` |
| `.150–.199`, `.200–.249` | one block of 50 per further host: host first, its VMs after |

The split is by how the address gets fixed, not by kind of machine: Macs, PCs and Kobos ask the router, so they are fixed by a reservation, which must sit inside the pool; Proxmox and its VMs have the address typed in, which must sit outside the pool. Whether this router honours reservations outside the pool is unknown, hence the pool end at `.99`. The Mini is as much a server as the G8; it stays at `.90` for now (moving it is cheap once devices use URLs).

**How `.100+` is kept free** (no per-address reservation exists or is needed): the router can only hand out addresses inside its pool, so pool end `.99` is the guarantee. Checks: (1) the router's DHCP page shows end `.99` and its allocated-address list shows nothing above; (2) a sweep from the MBP an hour after the change (lease time 1h) finds only our machines at `.100+`; (3) the VM-creation script tests that an address gets no reply (`arping`) before using it.

Every VM has its own address (it is a separate machine on the network); the address is set by the VM-creation script, nothing to do on the router.

**More machines are coming** (Alex, 2026-10-02): Hannah's current PC becomes a shared one, Hannah gets a new PC, maybe more. Rule for every machine we manage: a name, a fixed address in its block, the MBP's key installed, and an alias in the MBP's `~/.ssh/config`, so everything is reachable from the MBP (`ssh <name>`). The MBP is the control point; Windows PCs can take SSH too (OpenSSH Server).

Templates use VM IDs 9000+.

**URLs.** Zone `lab.alexluong.com` (unused as of 2026-10-02; DNS in Cloudflare via collielab terraform; records DNS-only, so Cloudflare's one-level certificate limit doesn't apply).

- One-of-a-kind services, flat: `jellyfin.lab.alexluong.com`, `plex.lab…`, `qbt.lab…`, `g8.lab…` (Proxmox UI). URL survives a move between hosts.
- Per-workspace services under the workspace: `hookdeck.lab.alexluong.com` (main page, T3), `board.hookdeck.lab…`, `t3.enable.lab…`. A host can't share a name with a flat service.
- **Two name sets, same gateway (a container on g8 running Caddy):** `*.lab.alexluong.com` → the gateway's home address, works at home on every device with no Tailscale (verified: router and Viettel DNS return private addresses for public names). `*.ts.alexluong.com` → the gateway's Tailscale address, works anywhere with Tailscale on, whatever range the other network uses (proposed). Same service names under both: `jellyfin.lab…` / `jellyfin.ts…`. No subnet router needed. Without Tailscale away: nothing connects.
- Caddy gets Let's Encrypt wildcard certificates by DNS check (no open ports); one wildcard per level (`*.lab…`, `*.hookdeck.lab…`). Only the gateway holds the Cloudflare token (scoped to `alexluong.com`); VMs hold none.
- SSH: `ssh g8`, `ssh hookdeck`, `ssh mini` via `~/.ssh/config` aliases.

**Records that exist** (collielab `terraform/alexluong_com.tf`, DNS-only, applied 2026-10-02):

| Name | Address | Use today |
|---|---|---|
| `g8.lab.alexluong.com` | `192.168.1.100` | `https://g8.lab.alexluong.com:8006` (Proxmox, self-signed cert warning) |
| `mini.lab.alexluong.com` | `192.168.1.90` | `http://mini.lab.alexluong.com:8096` (Jellyfin), `:32400` (Plex), `:8080` (qBittorrent) |

One record per machine or VM is added as it is created. Ports and the certificate warning go away with the gateway (TASK-3, not started), when these names move to it. The names are publicly resolvable (private addresses, nothing reachable from outside).

**If the range changes later:** update the DNS records, the gateway's backend addresses and the fixed addresses on g8, the Mini and VMs; devices that use URLs (Kobo, TV apps) keep working. So point the Kobo (today `192.168.1.90`, typed in its config; service/port on the Mini not found by scan, Mini session to document) and the TV's Jellyfin/Plex apps at URLs once the gateway exists. Other costs: house offline a few minutes; router admin moves; mesh nodes might need re-pairing; a Viettel reset puts the range back. To avoid locking g8 out: give it both addresses first, switch the router, then drop the old one.

## SSH keys on the MBP (2026-10-02)

| Key | Passphrase | In agent | Used for |
|---|---|---|---|
| `github_alexluong` | yes (Keychain) | yes | GitHub, collielab VM (`sshmylab`) |
| `gitlab_alexluong` | yes | no | GitLab |
| `id_ed25519` | yes (Keychain) | yes, since 2026-10-02 | **home servers and VMs** (Alex's choice) |
| `id_ed_hookdeck` | no | no | Hookdeck jump boxes (`hd_jumpbox`, `hd_jumpbox_stg`) |
| `google_compute_engine` | no | no | gcloud |

Claude can only use keys loaded in the agent (no passphrase prompt). After a restart `id_ed25519` reloads only if `~/.ssh/config` names it with `UseKeychain yes` + `AddKeysToAgent yes`: add that with the `g8` host entry. `~/.ssh/config` has no entries for home machines yet; its first line includes `~/.colima/ssh_config`, which no longer exists (harmless).

## Open

- [ ] Router: DHCP pool range; apply the address plan; save router login to Vaultwarden
- [ ] Mac Mini: Remote Login + MBP key, specs, wired vs Wi-Fi → `mac-mini.md`
- [ ] Later: Tailscale account + install on MBP/phone, `ts` names
- [ ] Identify the unidentified devices (`.57`, `.124`, `.129/.130`)
- [ ] Re-scan after 2026-10-02 18:00: `.124` and `.131` (old leases) should have moved below `.100`
