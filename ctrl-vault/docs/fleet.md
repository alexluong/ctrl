# Fleet: how the MBP manages the other machines

The MBP is the control point for `g8`, `gw`, `mini`, `vultr` and the VMs. This doc is the current state, the rules, and what is open. Rewritten 2026-10-02 at the end of the session that built it; the design discussion it replaced is in git (`git log -- ctrl-vault/docs/fleet.md`).

Where the details are:

| Topic | Where |
|---|---|
| Addresses, devices, URLs, router | `home-systems.md` |
| Mac Mini | `mac-mini.md` |
| Cloud VM, terraform, tokens | `collielab.md` |
| Workspace VMs | `vms/README.md`, `vms/hookdeck-ws.md` |
| Every change made, with undo | `work/task-2/log.md` |
| Runbooks and all config | repo `collielab` (`~/git/hub/alexluong/collielab`): `README.md`, `hosts/g8/README.md`, `hosts/gw/README.md` |
| Board | TASK-2 (g8 + hookdeck-ws VM), TASK-3 (gateway), TASK-4 (BIOS, kernel) |

## Machines (2026-10-02)

| Name | What | Address | SSH | sudo for an agent | Agent on it |
|---|---|---|---|---|---|
| `mbp` | control point | `.91` | n/a | n/a | yes (ctrl sessions) |
| `g8` | HP 805 G8, Proxmox host, 64GB | `.100` | `ssh g8` (root) | is root | no, stays bare |
| `gw` | home gateway, container 110 on g8 | `.110` | `ssh gw` (root) | is root | no |
| `hookdeck-ws` | workspace VM 101 on g8 | `.101`, tailnet `100.113.20.22` | `ssh hookdeck-ws` | yes (passwordless) | yes |
| `mini` | Mac Mini M4 16GB, media + 2 × 4TB drives | `.90` (Wi-Fi) | `ssh mini` | no (password) | has Claude; see § The Mini |
| `vultr` | Debian 12 cloud VM, 1GB, public services | `vultr.alexluong.com` | `ssh vultr` | no (password) | no |

## Rules (decided)

**Repos.** ctrl is docs, notes, board and logs. The actual config and scripts live in `collielab`, one directory per machine under `hosts/` (Alex, 2026-10-02). `dotfiles` sets up a Mac.

**The MBP is the only writer.** Config is pushed to machines from the MBP; machines do not commit to `collielab`. Plain shell and compose, no Ansible (five machines of three kinds).

**SSH.** Blocks and host keys are in git: `collielab/ssh/config`, `ssh/known_hosts`, `ssh/authorized_keys`; `~/.ssh/config` on the MBP has one `Include` line. One key for the whole fleet (MBP `id_ed25519`). Keys only everywhere (g8, mini, VMs). A new machine = DNS record + `Host` block + host key, in one commit; `bin/new-vm` does all of it for VMs.

**Names, not addresses** (Alex). `<machine>.lab.alexluong.com` (Tailscale address where the machine is on the tailnet, so the name works at home and away: `tailscale.md`), `vultr.alexluong.com` for the cloud VM. Fallback by address when DNS is down: `home-systems.md`.

**URLs.**

- `<machine>.lab.alexluong.com` = the machine itself (SSH; Tailscale address if on the tailnet).
- `<service>.<machine>.lab.alexluong.com` = a service on it, through the gateway.
- `<service>.lab.alexluong.com` = short alias for what gets typed into devices; survives the service moving machines.
- Calibre-Web is `alex.calibre.lab…` / `hannah.calibre.lab…` (Alex's naming).
- The private qBittorrent stays off the gateway and the index page (Alex).
- Index page with every link: `https://lab.alexluong.com`.

**Domain stays `alexluong.com`** (Alex, 2026-10-02). A dedicated domain (`collielab.net`) was proposed and rejected; don't raise it again unless he does. Known cost: the gateway's Cloudflare token can edit all DNS of the `alexluong.com` zone, because Cloudflare tokens are per zone.

**Gateway: one central one** (`gw` on g8), not one per machine: one routing file, one certificate holder, one token. Cost accepted: if g8 is down the URLs stop; services still answer on `<machine>.lab.alexluong.com:<port>`.

**Agents.** None on infra machines (`g8`, `gw`, `vultr`); they are driven from the MBP over SSH. Workspace VMs exist to run agents. A VM never gets keys to the host or to other machines, and cannot open connections to them: Proxmox firewall on the home network (`hosts/g8/firewall.sh`), Tailscale policy on the tailnet (`terraform/tailscale.tf`). Exceptions are explicit rules.

**sudo.** Agents cannot type a password. On `mini` and `vultr`, design around it (Docker, user-level services); the few root steps are one-time scripts Alex runs (e.g. `collielab/hosts/mini/root-setup.sh`). No blanket passwordless sudo there.

**Secrets.** Never in a repo. Canonical in Vaultwarden, working copy in `ctrl/secrets/<machine>/` (gitignored), pushed to the machine by its push script. Today: `secrets/gw/caddy.env` (the gateway's token; recreate with `terraform output -raw lab_gateway_token`).

**Sessions share checkouts.** Several Claude sessions work in the same `ctrl` and `collielab` working copies at once. Pull first, `git add` specific paths (never `-A`), commit and push promptly.

## What is built

| Piece | State |
|---|---|
| SSH config in git | done; `g8`, `gw`, `mini`, `vultr`, `hookdeck-ws` all connect using only the repo's host keys |
| DNS | `terraform/alexluong_com.tf` (machines), `terraform/lab_gateway.tf` (wildcards → `gw`, the token); lab names on Tailscale addresses since 2026-10-04 |
| Tailscale | tailnet `lhtanh98@`: Mini, gw (and opt-in VMs: `bin/vm-tailnet`, `bin/new-vm --tailscale`); access rules in `terraform/tailscale.tf`; router static route `100.64.0.0/10` → gw. All of it: `tailscale.md` |
| g8 | Proxmox 9.2.21, kernel pinned to 6.14.11; template VM 9000; `bin/new-vm` |
| Gateway | container 110, Caddy + Cloudflare DNS module, Let's Encrypt wildcards; `hosts/gw/push.sh` validates then reloads; backend addresses in its `/etc/hosts` (`hosts/gw/machines`) so requests never wait on DNS; also the door into the tailnet for home devices (`hosts/gw/tailnet.sh`, TASK-9); health check `hosts/gw/check.sh` |
| Index page | `https://lab.alexluong.com` = `hosts/gw/site/index.html` (a new service needs a route **and** a card) |
| Mini | SSH keys only; full disk access for SSH on (drives readable over SSH, verified); media stack unchanged |
| vultr | DNS-only name for SSH; fleet key installed; `hosts/vultr/Caddyfile` is a **copy**, not deployed from git |

Common jobs: add a URL → `collielab/hosts/gw/README.md`. New VM → `collielab/hosts/g8/README.md`. New phone, laptop, control Mac, server or someone else's device → `tailscale.md` § Adding a device. Rebuild the gateway → same README, four commands.

## The Mini

**Role:** the Mac in the fleet plus the storage box; planned to become the cs workspace and ctrl's home (Direction below).

**Measured 2026-10-02:** 16GB RAM; the media VM holds 8.4GB (qBittorrent 5.6GB), so about 4-6GB spare. Internal disk 60GB free; about 80GB more comes back with TASK-5 (old `hookdeck` Colima profile 52GB, hookdeck repos 7GB, dev caches 19GB). Wi-Fi.

**Over SSH from the MBP:** Docker/Colima, git, tmux, and (since the full-disk-access switch) the drives all work. Not available: the login Keychain, sudo, anything needing a click. Long jobs go in `tmux` on the Mini so they survive the MBP sleeping.

**Power cuts: left as is** (Alex, 2026-10-02): auto-restart off, FileVault on, no auto-login. After a cut the Mini stays off; after power-on someone unlocks it at the screen and the containers need `media/scripts/vm-start.sh` + `up.sh core`.

**Cleanup: TASK-5** (scan, decisions, step list: `work/task-5/scan.md`). Alex approves each step before it runs. Hookdeck leftovers: delete, no need to save (go still pending). Apps: list kept, not acting yet. Jump Desktop: no watchdog; check/start over SSH (commands in the scan).

**What the Mini is for beyond media** (brainstorm with Alex, open, nothing decided; full list in `work/task-5/scan.md` § Ideas). Its strength is CPU (M4, ~1.5x g8 overall, ~2x per core, from memory) and being a Mac; its limit is memory (~6GB spare). General workloads and workspace VMs still go to g8 (47GB free).
- **Local CI** (Alex's idea, leading): GitHub Actions self-hosted runner, free; VMs push and the runner picks the job up, so no VM needs a key to the Mini. Linux jobs in a small separate Colima VM, Mac jobs (Xcode, `fitjournal`) natively. Private, personal repos only. Needs: pick a first repo.
- Media compute: Jellyfin as a native app (hardware transcoding), HEVC re-encode of the library to free drive space, Whisper subtitles.
- Storage: backup target for g8's VMs, Time Machine for the MBP (Blue4, 817GB free).
- Mac-only: a logged-in browser for automations (bank/property-manager downloads), local copy of iCloud.
- Books/audiobooks to g8: 22GB, frees only ~0.4GB RAM on the Mini; gain is separation; catch is the qBittorrent hardlink flow. Later, after backups.
- Earlier rejected: Mini as the CS/personal workspace (memory, isolation). Reversed 2026-10-04, see below.

**Direction (Alex, 2026-10-04; ideas, nothing set in stone, nothing acted on):**
- **g8:** hookdeck-ws, enable-ws, and small always-on agents (one VM per access level, e.g. a persistent agent for enable). Assigned VM memory is a ceiling, not a reservation (host used 5GB with hookdeck-ws at 32GB); resize with `qm set <id> --memory` + `qm reboot`.
- **Mini = cs workspace + ctrl**, so nothing runs on the MBP: the MBP becomes a terminal (T3/SSH/browser) and any cheaper laptop would do. Machine name stays `mini` (no `-ws`: it holds several things; workspaces are folders `~/workspaces/<name>`). One macOS user `alex` for now (same exposure as the MBP today); a separate `cs` user is optional hardening later (own Colima if so: sharing a Docker socket across users exposes `/Users/alex`).
- **Mobile dev:** Mac-native on the Mini (Xcode, simulator; Claude can check screenshots via `xcrun simctl io booted screenshot`); Android via a real phone over `adb connect` or `scrcpy`.
- **dots** (idea): a personal assistant on the Mini using Mail/Calendar/Messages/Reminders, able to hand work to workspaces without access to them (it files a request in a shared inbox, e.g. GitHub issues; a watcher in each workspace starts the session; approval gate for workspaces with production access). Depends on which email/calendar Alex uses (open).
- **Media, long term:** media VM is 8GB on the Mac but apps use ~1.7GB (rest is Linux file cache); shrinking it to 4GB frees ~4GB. Options weighed: (a) arr on g8 writing to the DAS on the Mini over NFS: works but torrent I/O and seeding cross the LAN and break when the Mini is down; (b) **preferred long term: DAS on g8** (arr, qBittorrent, seeding local; library shared read-only to the Mini; Plex/Jellyfin native on the Mini; Sonarr/Radarr trigger library refresh). Catch for (b): Blue4's format (APFS can't be written from Linux: reformat + copy several TB). For now media stays on the Mini as is.
- **Prerequisites that keep coming up:** Ethernet on the Mini (it has a port, `en0`, currently on Wi-Fi `en1`), backups (TASK-13), FileVault after a power cut.

**State of its ctrl clone:** `~/git/hub/alexluong/ctrl`, still on branch `docs/mac-mini` (merged as PR #1), with a Claude session running there on 2026-10-02. `media/` in ctrl is what it runs from.

## Open, in rough order

1. **What the Mini should run next**: brainstorm continues (§ The Mini). Cleanup is TASK-5. Pending with it:
   - `media/` as its own repo with a single clone on the Mini, edited from the MBP over SSH (proposal: its busiest files, `catalog.json` and `downloads.json`, are written on the Mini, and a second ctrl clone there is how PR #1 happened). Not decided.
   - Delete hookdeck leftovers (TASK-5; agreed, waiting for go).
   - Start Colima + the core stack at login (user launch agent, `collielab/hosts/mini/`).
   - `gluetun` unhealthy (DNS/TLS timeouts through the VPN); `seedboxapi` crash-looping (expired MAM session, needs a new session ID from Alex); qBittorrent memory.
   - Ethernet, if a cable can reach.
2. **Backups:** nothing is backed up; the `hookdeck-ws` VM holds real setup. **TASK-13** (where they go, how often, restore test; options: file + rclone to R2, Blue4 on the Mini, Proxmox Backup Server, files-only from inside the VM).
3. **Devices → URLs:** Kobos and TV apps still use `192.168.1.90`. Try one Kobo first: untested whether Kobo firmware trusts Let's Encrypt and whether Calibre-Web's Kobo sync works behind the gateway.
4. **hookdeck-ws routes** on the gateway (`*.hookdeck-ws.lab` has DNS but no site block; its T3 server listens on `127.0.0.1` only).
5. **vultr:** deploy its Caddyfile from git (needs one sudo step from Alex); move `services/` under `hosts/vultr/`.
6. **A general `fleet` script** (diff/push/run per machine). Not written; the gateway has its own `push.sh`. Write it when a second machine needs pushing.
7. **Tailscale** (TASK-9): built and working (`tailscale.md`). Alex: keep Vaultwarden copies of the Tailscale `terraform` OAuth client (in `collielab/terraform/.env`); vm-join and the gw token are regenerable from `terraform output`. g8's first full reboot: TASK-14 checklist. MBP setup outside git (ssh `Include` line, `.env`, `ctrl/secrets`, PIA exception): deferred TASK-15.
8. g8: BIOS update and kernel retest (TASK-4, Alex at the box; add-on: memory reporting for VM 101); small UPS.
9. **Monitoring:** none beyond the Proxmox UI (no temperatures, no alerts). **TASK-7**: a `mon` VM with Grafana; Alex wants metrics synced to R2 (Thanos or VictoriaMetrics, undecided).
