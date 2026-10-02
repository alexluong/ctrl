# Fleet: how the MBP manages the other machines

**Status: proposal (2026-10-02), not decided.** Alex's ask: a "ctrl system" where the MBP is the control point for `g8`, `mini`, `vultr` and the VMs to come: SSH, running and deploying things on them, where config lives, clean URLs through a gateway.
Map of machines and addresses: `home-systems.md`. Cloud VM: `collielab.md`. Mini: `mac-mini.md`. g8 setup: `work/task-2/plan.md`. Gateway task: TASK-3.

## Machines (2026-10-02)

| Name | What | SSH user | sudo without password | Docker | Claude on it |
|---|---|---|---|---|---|
| `mbp` | control point | n/a | n/a | no | yes (ctrl session) |
| `g8` | Proxmox host | `root` | is root | no (stays minimal) | no |
| `mini` | Mac Mini, media | `alex` | no | Colima `arr` VM | yes (own ctrl clone) |
| `vultr` | Debian 12, 1GB RAM, public services | `alex` | no | yes (`docker-compose` v1) + Caddy under systemd | no |
| g8 VMs (`hookdeck`, …) | one per workspace | `alex` | set by the template | yes | yes (that is their purpose) |

## 1. SSH

Today: aliases `g8`, `mini`, `vultr` in the MBP's `~/.ssh/config`, by domain name; host keys in `~/.ssh/known_hosts`. Both exist only on the MBP.

Proposed:

- **The fleet's SSH config lives in git**, in the infra repo (§3): `ssh/config` (one `Host` block per machine) and `ssh/known_hosts` (their host keys). `~/.ssh/config` gets one line, `Include <repo>/ssh/config`; the blocks set `UserKnownHostsFile` to the repo file. A new control machine (or an agent on a VM that is allowed to reach others) gets every alias and never sees a "trust this host?" prompt. No secrets in either file.
- **Adding a machine = one commit:** DNS record (terraform), `Host` block, host key line. The VM-creation script does all three.
- **Names only.** `<machine>.lab.alexluong.com` at home, `vultr.alexluong.com` in the cloud. Fallback by address when DNS is down stays documented in `home-systems.md`.
- **Keys:** one key per control machine (MBP: `id_ed25519`); `ssh/authorized_keys` in the repo is the list every managed machine gets. `vultr` still takes `github_alexluong`; add `id_ed25519` there so one key covers the fleet.
- **sudo:** agents cannot type a password, so on `mini` and `vultr` anything needing root stops and waits for Alex. Design around it instead of opening sudo: services run in Docker or as user-level services (launchd agents on the Mini, `systemd --user` or the docker group on Linux); the few root steps (sshd config, Caddy install) are one-time, done by Alex, logged. If that gets tedious on one machine: a sudoers rule limited to named commands (`systemctl reload caddy`), never blanket.
- **Away from home:** Tailscale, later (already agreed). The same aliases get a second name set (`*.ts.alexluong.com`).

## 2. Running things on machines: three levels

| Level | What | Use for |
|---|---|---|
| a. Command over SSH | the MBP session runs `ssh <machine> '<cmd>'` | looking, one-off fixes, restarts. Works today |
| b. Config in git, pushed | each machine's files in the infra repo; a small script copies them over and applies | everything that should still be true after a rebuild: Caddyfiles, compose files, service units, host settings |
| c. Agent on the machine | Claude (or T3 server) running there | work that must outlive the MBP being awake, or needs the machine's own tools: dev in workspace VMs, media jobs on the Mini |

**b in detail (the missing piece).** `bin/fleet` in the infra repo:

- `fleet diff <machine>`: what differs between the repo and the machine (read-only).
- `fleet push <machine> [service]`: rsync `hosts/<machine>/…` to the machine, then run that directory's `apply.sh` (usually `docker compose up -d` or `systemctl reload`).
- `fleet run <machine> <script>`: run an idempotent setup script from the repo on the machine.

Push from the MBP rather than `git pull` on each machine: machines need no GitHub login and hold no repo history; the MBP is the only place that writes. Plain shell and compose, no Ansible: five machines of three different kinds, and Claude writes the idempotent scripts either way; Ansible would add an inventory language and a Python dependency on every target for little gain. Revisit if the fleet passes ~10 machines.

**Secrets** never go in the repo. Canonical in Vaultwarden, working copy in `ctrl/secrets/<machine>/`, pushed by `fleet push` as `.env` with mode 600. Each machine holds only its own.

**c in detail.**

- Infra machines (`g8` host, gateway, `vultr`): no agent. Driven from the MBP. Keeps them minimal and keeps Claude credentials off them (`vultr` has 1GB RAM anyway).
- Workspace VMs: Claude + T3 server installed by the template; Alex logs in once per VM (`claude`, `gh`). Reached from the MBP through the gateway URL or `ssh <vm>`.
- Mini: already has Claude and a ctrl clone for media work. Keep it, with one rule so the two clones don't diverge again (PR #1): **the Mini's session only touches `media/` and pushes to `main` when it finishes a piece of work; the MBP owns everything else.** Starting it from the MBP: `ssh -t mini 'cd ~/git/hub/alexluong/ctrl && claude'`, or a T3 server on the Mini.
- A VM never gets keys to the host or to other machines (existing rule).

## 3. Where config lives

| Repo | Holds |
|---|---|
| `collielab` (planned name `collielab/infra`) | **all machine config**: `terraform/` (DNS, Vultr), `hosts/<machine>/` (per-machine files and scripts), `ssh/`, `bin/fleet`, VM template and creation scripts. Already holds terraform and `vultr`'s services, and the `lab.alexluong.com` records |
| `ctrl` | the map and the history: `home-systems.md`, this doc, change logs, board, decisions. Also `media/` (the Mini's stack) for now |
| `dotfiles` | setting up a Mac for Alex (apps, shell). Adds the `Include` line for the fleet SSH config |

Proposed `collielab` layout:

```
terraform/
ssh/config, known_hosts, authorized_keys
hosts/
  g8/          host settings scripts, vm-template/, new-vm.sh
  gw/          Caddyfile, apply.sh            (the home gateway, §4)
  vultr/       Caddyfile, services/<name>/    (today's services/ moves here)
  mini/        launchd agents (Colima autostart), later the media stack
  hookdeck/    what is specific to that VM
bin/fleet
```

This answers the open question in `work/task-2/plan.md` ("repo for the scripts") with the existing repo instead of a new one. `media/` in ctrl is the odd one out (compose and scripts next to notes); moving it to `collielab/hosts/mini/media` is a later cleanup, not a blocker.

Already-known gaps this closes: `vultr`'s `/etc/caddy/Caddyfile` is in no repo (`collielab.md` § Open items); the Mini's containers don't start after a reboot.

## 4. Gateway and URLs

Goal: `https://jellyfin.mini.lab.alexluong.com` instead of `http://mini.lab.alexluong.com:8096`, real certificate, no port.

**Naming rule (one rule for everything):**

- `<machine>.lab.alexluong.com` = the machine itself (SSH, its real address).
- `<service>.<machine>.lab.alexluong.com` = a service on it, through the gateway: `jellyfin.mini.lab…`, `qbt.mini.lab…`, `books.mini.lab…`, `pve.g8.lab…`, `board.hookdeck.lab…`, `t3.hookdeck.lab…`.
- Optional short alias for the few services typed into devices that would be painful to re-point when the service moves machines: `jellyfin.lab…`, `books.lab…` (Kobos, TV apps). The media stack is planned to move to g8 one day; the alias survives that, the long name does not.

This replaces the earlier "flat for one-of-a-kind, nested for workspaces" split in `home-systems.md` with one rule, and settles TASK-3's open question.

**Shape: one central gateway, not one per machine.**

- A small Debian 13 container on g8 (`gw`), Caddy with the Cloudflare DNS module, config = `hosts/gw/Caddyfile` in git, pushed with `fleet push gw`.
- DNS: wildcard records `*.mini.lab`, `*.g8.lab`, `*.<vm>.lab` (and the aliases) → the gateway's address; the bare machine names keep pointing at the machines.
- Certificates: Let's Encrypt wildcard per machine level, proven through DNS, so nothing is opened to the internet. Only `gw` holds the Cloudflare token.
- Caddy forwards to `192.168.1.90:8096` etc. over the home network.

Why central: one routing file, one certificate holder, one token (a Cloudflare token can't be limited to `lab.` names, only to the whole `alexluong.com` zone, so fewer holders is better); adding a URL is one line + one push; the Tailscale name set later needs only the gateway on Tailscale. Cost: if g8 is down, the Mini's URLs stop working (the ports still do). g8 powers itself back on after a power cut; the Mini does not.

Per-machine gateways (Caddy on each machine) would keep each machine independent, but mean a token and a Caddy install per machine, including on macOS inside Colima. Not worth it at this size.

`vultr` is separate: it already runs Caddy for the public names (`vault.collie.studio`, …) behind Cloudflare. Same treatment (Caddyfile in git, pushed), no change in shape.

**Per-service settings to expect:** Proxmox UI needs HTTPS to the backend with its self-signed cert accepted; qBittorrent checks the Host header (allow the new name); Jellyfin and Plex want the gateway listed as a known proxy / custom URL.

## Order

1. `collielab`: `ssh/` + `Include`, `hosts/` skeleton, `bin/fleet` (diff/push/run). Bring `vultr`'s Caddyfile into `hosts/vultr/` (read-only copy first, then push becomes the way to change it).
2. Gateway (TASK-3): container on g8, Cloudflare token (Alex creates, DNS edit on `alexluong.com`), wildcard records, routes for the Mini's services and the Proxmox UI. Then point the Kobos and TV apps at URLs.
3. VM template + `hookdeck` VM (TASK-2 steps 4-5), created by a script that also adds DNS, SSH block, host key and gateway routes.
4. Mini: Colima autostart as a user launch agent, SSH keys only (Alex), clone onto `main`.
5. Tailscale + `*.ts` names. Backups (g8 → Mini drive).

## Decisions needed (Alex)

1. Infra repo = `collielab` (recommended) vs a new repo vs inside ctrl.
2. Gateway: central on g8 with `<service>.<machine>.lab` names + a few short aliases (recommended) vs per-machine.
3. Mini's agent: keeps its own ctrl clone, limited to `media/` (recommended) vs no agent there, everything driven from the MBP.
4. Gateway container number/address in g8's block (`hookdeck` is promised 101): proposal `gw` = container 110 = `.110`, infra containers 110-119.
