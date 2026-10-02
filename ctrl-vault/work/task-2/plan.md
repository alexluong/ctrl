# TASK-2 plan: set up pve1 + hookdeck workspace VM

Milestone (Alex, 2026-10-02): get the G8 (`pve1`) set up with **one VM, the hookdeck workspace**. Other workspaces (enable, solex, cs, ixchel), arrstack and backups come after.
Claude runs on the MBP (ctrl session) and manages the box over SSH. Files here: `plan.md` (this), `discovery.md` (the box as delivered), `log.md` (every change made, with how to undo). Home map and addresses: `docs/home-systems.md`. Hardware and sizing numbers: `work/task-1/decision.md`.

## Rules

- Read-only discovery first; each change proposed before it runs.
- Ask before anything hard to undo (storage, network bridge, deleting VMs).
- Host stays minimal: nothing agent-related installed on it.
- VMs never get the host's SSH key or API access.
- No secrets in git. Root password and tokens live in Vaultwarden; copies Claude needs go in `ctrl/secrets/`.
- Everything done goes into scripts in a repo so it can be rebuilt.

## Manual steps (Alex) before Claude can start

1. ~~SSH key to the box~~ done 2026-10-02: `id_ed25519` installed with `ssh-copy-id`, loaded in the agent with `ssh-add --apple-use-keychain`.
2. **Root password in Vaultwarden**: item named for the box (`g8 root (Proxmox)`), user `root`, URL `https://192.168.1.21:8006`.
3. **Router** (`http://192.168.1.1`, ZTE F6601P): log in (sticker under the router; save the login to Vaultwarden), send a screenshot of the LAN/DHCP page. Screenshots received 2026-10-02 (pool `.2–.254`, 5 reservations). To do: DHCP End IP Address → `192.168.1.99`, Apply.

Later, inside the VM (Alex types these; Claude can't): `claude` login, `gh auth login`, hookdeck env/secrets.

## Order (agreed 2026-10-02: keep it simple, stay on `192.168.1.x`, Tailscale later)

0. **Discovery (read-only)**: done 2026-10-02, see `discovery.md` (clean, no reinstall). Proxmox version, storage layout, bridge config, repos, disk health (`smartctl`), BIOS version. **Audit what the shop left**: `authorized_keys`, users, cron, extra repos/packages. Anything odd → reinstall from the official ISO.
1. **Router**: read the DHCP page (pool range, existing reservations: `docs/home-systems.md`), then pool end `.254` → `.99` (one field) so `.100` and up is never handed out. Reserved devices (`.80–.99`) stay inside the pool and keep their addresses.
2. **Box address and name** (before any VM exists): rename `pve1` → `g8`, move `192.168.1.21` → `192.168.1.100`. Done with both addresses on the box for a moment so it is never unreachable. (`.91` was the first idea, but it is the MBP's reserved address.)
3. **Host basics**: no-subscription repo, updates, `amd64-microcode`, SSH password login off (keys only), BIOS update if outdated.
4. **VM template**: Debian 13 cloud image + cloud-init: user `alex`, MBP key, qemu-guest-agent, Docker, mise, git, GitHub CLI, Claude Code. VM ID 9000.
5. **hookdeck VM**: clone of the template. Start: 8 vCPU, 32GB RAM, 250GB disk, VM ID 110, `192.168.1.110`. Then hookdeck workspace + repos, one core stack up (~8.5GB idle), T3 Code server as a service. Stop for Alex to test from the MBP.
6. **Gateway + `lab` URLs**: small container on g8 with Caddy, `*.lab.alexluong.com` → its home address, Let's Encrypt by DNS check. Then point the Kobo and TV apps at URLs. Scheme: `docs/home-systems.md`.
7. **Later**: Tailscale + `*.ts.alexluong.com` names (access away from home), snapshots/backup target, more workspace VMs from the same scripts, arrstack move, runbook ("add a workspace", "restore a VM").

## Open questions

- Repo for the scripts. Proposal: new private repo in the `collielab` org (personal infra); inventory summarized in `docs/home-systems.md`.
- T3 server: how it authenticates; which address it listens on (behind the gateway).
- Stack approach inside the VM (full stacks vs shared infra); not every stack runs all the time.
- Backup target: Mac Mini share needs enough space (VM backups 100GB+).

## Prompt for the Mac Mini session

Paste into a Claude Code session running **on the Mac Mini**. Output lands in `docs/mac-mini.md`.

```
You're running on my Mac Mini (base M4) at home. Goal: let my MacBook Pro
(and the Claude session on it) manage this Mac over SSH, and document this
machine. Plan first; don't change anything until I confirm.

## 1. Discovery (read-only)
- Model, chip, RAM, internal disk size and free space, macOS version, hostname.
- Network: wired or Wi-Fi, IP, MAC, and whether Wi-Fi uses a private address
  (Fixed or Rotating). Expected today: 192.168.1.90, alexs-Mac-mini.local.
- How is the address fixed: typed into this Mac's network settings, or handed out
  by the router?
- Is Remote Login (SSH) on? Which user accounts exist?
- What runs here: Colima/Docker containers, Plex, Jellyfin, qBittorrent, the book
  server my Kobo syncs with (service, port, how the Kobo is pointed at it), anything
  on port 53, launch agents/login items, what starts after a reboot.
- External drives: the Samsung T7 (mount point, filesystem, size, free space) and
  any others.
- Sleep/energy settings (does it stay awake, restart after power failure).
- The arrstack: repo location (~/git/hub/alexluong/arr), compose services, ports,
  where config and media live, how it starts, VPN (gluetun) setup, which app
  plays the media. I want to move it to a Linux VM on a Proxmox box later, so
  note what would block that (APFS/exFAT on the T7, hardware transcoding, paths).

## 2. SSH access from the MacBook Pro
- Remote Login needs me: tell me the exact clicks (System Settings → General →
  Sharing → Remote Login) and to limit it to my user.
- Then add this public key to ~/.ssh/authorized_keys (create with correct
  permissions, don't duplicate):
  ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMjg8Brv2ipx0cshwJ1gBlXvoSrrAJjO2MbIEPXkPZgD alexluong@Alexs-MacBook-Pro.local
- Propose turning off password login for SSH (keys only) and show me the change
  before applying.
- Tell me the command to test from the MacBook Pro: ssh <user>@192.168.1.90

## 3. Write it up
- If ~/workspaces/ctrl exists here: git pull, write ctrl-vault/docs/mac-mini.md
  (specs, network, services and ports, drives, how things start, SSH access,
  arrstack details and migration blockers), commit and push. Touch no other file.
- If it doesn't exist: give me the same content as one markdown block to paste
  into the MacBook Pro session.

## Rules
- No secrets in the doc (VPN keys, passwords, tokens): name where they live only.
- Don't restart or reconfigure any running service.
- Ask before anything that needs sudo.
```
