# Fleet: how the MBP manages the other machines

**Status (2026-10-02): §1 SSH, §3 repo and §4 gateway built (collielab `d8dc870`, `3e27e1f`). Still proposals: §2 a general `fleet` script (the gateway has its own `push.sh`), §5 the Mini's `media/` repo, §6 a dedicated domain.** Alex's ask: a "ctrl system" where the MBP is the control point for `g8`, `mini`, `vultr` and the VMs to come: SSH, running and deploying things on them, where config lives, clean URLs through a gateway.
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

Built 2026-10-02: `collielab/ssh/config` (blocks for `g8`, `mini`, `vultr`), `ssh/known_hosts`, `ssh/authorized_keys`; the MBP's `~/.ssh/config` includes it (backup `~/.ssh/config.bak-20261002-fleet`). Verified: all three connect using only the repo's host keys. `vultr` now takes `id_ed25519` too.

How it works:

- **The fleet's SSH config lives in git**, in the infra repo (§3): `ssh/config` (one `Host` block per machine) and `ssh/known_hosts` (their host keys). `~/.ssh/config` gets one line, `Include <repo>/ssh/config`; the blocks set `UserKnownHostsFile` to the repo file. A new control machine (or an agent on a VM that is allowed to reach others) gets every alias and never sees a "trust this host?" prompt. No secrets in either file.
- **Adding a machine = one commit:** DNS record (terraform), `Host` block, host key line. The VM-creation script does all three.
- **Names only.** `<machine>.lab.alexluong.com` at home, `vultr.alexluong.com` in the cloud. Fallback by address when DNS is down stays documented in `home-systems.md`.
- **Keys:** one key per control machine (MBP: `id_ed25519`); `ssh/authorized_keys` in the repo is the list every managed machine gets. One key covers the fleet.
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
| `collielab` (planned name `collielab/infra`) | **decided (Alex, 2026-10-02): ctrl is docs and notes, the actual work lives in collielab or other repos.** All machine config: `terraform/` (DNS, Vultr), `hosts/<machine>/` (per-machine files and scripts), `ssh/`, `bin/fleet`, VM template and creation scripts. Already holds terraform and `vultr`'s services, and the `lab.alexluong.com` records |
| `ctrl` | the map and the history: `home-systems.md`, this doc, change logs, board, decisions. Also `media/` (the Mini's stack) for now |
| `dotfiles` | setting up a Mac for Alex (apps, shell). Adds the `Include` line for the fleet SSH config |

`collielab` layout (`ssh/`, `hosts/{g8,gw,mini,vultr}/` and a README exist; `hosts/vultr/Caddyfile` is a read-only copy for now; `bin/fleet` and the `services/` move not done):

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

**Built 2026-10-02** as designed below: container 110 `gw` on g8 (`192.168.1.110`, 1 core, 512MB, starts with the host), Caddy 2.11 with the Cloudflare DNS module, three wildcard certificates issued, every route tested from the MBP. URLs: `home-systems.md`. Runbook: `collielab/hosts/gw/README.md`. Token `lab-gateway-acme` (DNS edit on the `alexluong.com` zone only) made with terraform; copy in `ctrl/secrets/gw/caddy.env`.

Goal: `https://jellyfin.mini.lab.alexluong.com` instead of `http://mini.lab.alexluong.com:8096`, real certificate, no port.

**Naming rule (one rule for everything):**

- `<machine>.lab.alexluong.com` = the machine itself (SSH, its real address).
- `<service>.<machine>.lab.alexluong.com` = a service on it, through the gateway: `jellyfin.mini.lab…`, `qbt.mini.lab…`, `books.mini.lab…`, `pve.g8.lab…`, `board.hookdeck.lab…`, `t3.hookdeck.lab…`.
- Optional short alias for the few services typed into devices that would be painful to re-point when the service moves machines: `jellyfin.lab…`, `books.lab…` (Kobos, TV apps). The media stack is planned to move to g8 one day; the alias survives that, the long name does not.

This replaces the earlier "flat for one-of-a-kind, nested for workspaces" split in `home-systems.md` with one rule, and settles TASK-3's open question.

**Shape: one central gateway, not one per machine.**

- A small Debian 13 container on g8 (`gw`), Caddy with the Cloudflare DNS module, config = `hosts/gw/Caddyfile` in git, pushed with `fleet push gw`.
- DNS: wildcard records `*.mini.lab`, `*.g8.lab`, `*.<vm>.lab` (and the aliases) → the gateway's address; the bare machine names keep pointing at the machines.
- Certificates: Let's Encrypt wildcard per machine level, proven through DNS, so nothing is opened to the internet. Only `gw` holds a Cloudflare token: a new one limited to DNS edit on the `alexluong.com` zone, created with terraform (`cloudflare_account_token`; the terraform token can create tokens, see `collielab.md` § Tokens). The terraform token itself never goes on a machine: it covers the whole account.
- Caddy forwards to `192.168.1.90:8096` etc. over the home network.

Why central: one routing file, one certificate holder, one token (a Cloudflare token can't be limited to `lab.` names, only to the whole `alexluong.com` zone, so fewer holders is better); adding a URL is one line + one push; the Tailscale name set later needs only the gateway on Tailscale. Cost: if g8 is down, the Mini's URLs stop working (the ports still do). g8 powers itself back on after a power cut; the Mini does not.

Per-machine gateways (Caddy on each machine) would keep each machine independent, but mean a token and a Caddy install per machine, including on macOS inside Colima. Not worth it at this size.

`vultr` is separate: it already runs Caddy for the public names (`vault.collie.studio`, …) behind Cloudflare. Same treatment (Caddyfile in git, pushed), no change in shape.

**Per-service settings to expect:** Proxmox UI needs HTTPS to the backend with its self-signed cert accepted; qBittorrent checks the Host header (allow the new name); Jellyfin and Plex want the gateway listed as a known proxy / custom URL.

## 5. The Mini: managed from the MBP, and where `media/` goes (proposal)

Checked over SSH 2026-10-02:

| Works | Does not |
|---|---|
| Docker (`docker --context colima-arr …`), Colima, git, tmux, Tailscale CLI | **reading `/Volumes/Blue4`, `/Volumes/Red4`** ("Operation not permitted": macOS privacy; fix = System Settings → General → Sharing → Remote Login → (i) → "Allow full disk access for remote users", Alex, one click) |
| | the login Keychain (locked for SSH sessions) |
| | anything needing sudo or a click on the screen |

So with the full-disk-access switch on, media work can be driven from the MBP: long jobs run in `tmux` on the Mini and survive the MBP sleeping. Sessions started on the Mini stay as the fallback for the right-hand column.

`media/` is two different things: config and scripts (compose, `up.sh`, `catalog.py`; change rarely) and **data the scripts write on the Mini** (`catalog.json`, `downloads.json`: 21 commits each, the busiest files). The data is why the Mini has to commit, and a second clone of a repo the MBP also writes is how PR #1 happened.

Proposal: **no workspace for the Mini** (it is a machine, not a project; board, notes and the `media-ops` skill stay in ctrl). `media/` becomes its **own repo with one working clone, on the Mini**; the MBP session edits and commits there over SSH. One writer, so no second timeline. ctrl's clone leaves the Mini. Machine-level files (launch agents) go in `collielab/hosts/mini/`.

### What the Mini is for (Alex asked 2026-10-02: use it for more than media)

Measured 2026-10-02: 16GB RAM, of which the media VM holds 8.4GB (qBittorrent alone 5.6GB) and 4.7GB is already compressed, so **~4-6GB is spare**. Internal disk 61GB free; `~/.colima` is 63GB and includes a stopped 50GB `hookdeck` profile from before g8 (plus 2GB of hookdeck clones). On Wi-Fi. **FileVault is on, no auto-login, auto-restart off**: after a power cut it stays off, and after power-on nothing starts (containers, likely SSH too; untested) until someone unlocks it at the screen.

So the split:

| | g8 | Mini |
|---|---|---|
| Good at | Linux/Docker, lots of RAM (64GB), wired, comes back by itself | things only a Mac does; fast cores; 8TB of drives attached |
| Role | **the server**: workspace VMs, gateway, every new Linux workload | **the Mac in the fleet + the storage box** |

New general workloads go to g8, not the Mini: it has the RAM and restarts unattended. The Mini gets:

1. Media stack and the drives (today).
2. **Backups of g8's VMs** onto Blue4 (817GB free); already in the g8 plan, wants the Mini wired.
3. **Mac-only jobs:** Xcode builds for `fitjournal` (SwiftUI; needs ~40GB disk, so clear the old `hookdeck` Colima profile first), anything needing a real logged-in browser or macOS apps (e.g. fetching bank/PM statements for bookkeeping: idea, not planned).
4. **Watchdog from outside g8:** a small check that g8, the gateway and vultr answer, notifying Alex. Must not live on the thing it watches.

Getting real spare capacity on the Mini means moving the media services to a VM on g8 (they are Linux containers and gain nothing from macOS). Blocked: the drives are APFS and nearly full, so it needs a third drive to shuffle ~6TB through. Later, if ever.

Making it dependable (Alex, at the Mini, once): full disk access for remote users; SSH keys only; ethernet if the cable can reach; decide auto-restart + FileVault (hands-off recovery needs auto-restart on and either FileVault off with auto-login, or accepting an unlock at the screen after each power cut). Then from the MBP: Colima + `up.sh core` as a launch agent, cap qBittorrent's memory, fix `gluetun` / `seedboxapi`.

## 6. A dedicated domain for the lab (proposal; Alex asked 2026-10-02, open to buying one)

Today everything hangs under `lab.alexluong.com`. Proposal: buy **`collielab.net`** (free on 2026-10-02; `.com` and `.org` are taken by others; name matches the repo) and move the lab onto it.

| Today | With `collielab.net` |
|---|---|
| `jellyfin.lab.alexluong.com` | `jellyfin.collielab.net` |
| `jellyfin.mini.lab.alexluong.com` | `jellyfin.mini.collielab.net` |
| `mini.lab.alexluong.com` (SSH) | `mini.collielab.net` |
| `vultr.alexluong.com` | `vultr.collielab.net` |
| later, away from home | `jellyfin.ts.collielab.net` |

Same three rules (machine, service on a machine, short alias), one level shorter. Public sites stay where they are (`alexluong.com`, `collie.studio`).

Why it is worth ~$12 a year:

- **The gateway's token can then only touch `collielab.net`.** Today it can edit all DNS of `alexluong.com` (the personal site), because Cloudflare tokens are per zone, not per subdomain.
- Home services stop sharing a site with `alexluong.com` in the browser (cookies set for `.alexluong.com` are visible to every `*.lab.alexluong.com` app and the other way round).
- Private addresses and machine names leave the domain that carries Alex's name.
- Shorter to type into a TV or a Kobo.

Avoid `.dev` / `.app`: browsers force HTTPS on them, which breaks the plain `:port` fallback addresses.

Cost of moving now: small, nothing but the MBP uses the names yet (new zone in terraform, new records and token, search-and-replace in `ssh/config`, `ssh/known_hosts`, the Caddyfile, `new-vm`; machine hostnames on g8 and the VMs). It gets more expensive once Kobos, TVs and bookmarks use the URLs, so decide before pointing devices at them. Buying needs Alex (Cloudflare Registrar, in the dashboard).

## Order

1. `collielab`: `ssh/` + `Include`, `hosts/` skeleton, `bin/fleet` (diff/push/run). Bring `vultr`'s Caddyfile into `hosts/vultr/` (read-only copy first, then push becomes the way to change it).
2. Gateway (TASK-3): container on g8, Cloudflare token (terraform), wildcard records, routes for the Mini's services and the Proxmox UI. Then point the Kobos and TV apps at URLs.
3. VM template + `hookdeck` VM (TASK-2 steps 4-5), created by a script that also adds DNS, SSH block, host key and gateway routes.
4. Mini: Colima autostart as a user launch agent, SSH keys only (Alex), clone onto `main`.
5. Tailscale + `*.ts` names. Backups (g8 → Mini drive).

## Decisions needed (Alex)

1. ~~Infra repo~~ decided: `collielab`, a directory per machine.
2. ~~Gateway~~ built (Alex: "do whatever you think is best"): central on g8, `<service>.<machine>.lab` names + short aliases.
3. Mini: `media/` → own repo, single clone on the Mini, driven from the MBP over SSH (recommended, §5) vs a ctrl clone on the Mini limited to `media/`.
4. Gateway container number/address in g8's block (`hookdeck` is promised 101): proposal `gw` = container 110 = `.110`, infra containers 110-119.
