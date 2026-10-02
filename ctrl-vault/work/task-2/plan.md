# TASK-2 plan: set up pve1 + hookdeck workspace VM

Milestone (Alex, 2026-10-02): get the G8 (`pve1`) set up with **one VM, the hookdeck workspace**. Other workspaces (enable, solex, cs, ixchel), arrstack and backups come after.
Claude runs on the MBP (ctrl session) and manages the box over SSH. Home map and addresses: `docs/home-systems.md`. Hardware and sizing numbers: `work/task-1/decision.md`.

## Rules

- Read-only discovery first; each change proposed before it runs.
- Ask before anything hard to undo (storage, network bridge, deleting VMs).
- Host stays minimal: nothing agent-related installed on it.
- VMs never get the host's SSH key or API access.
- No secrets in git. Root password and tokens live in Vaultwarden; copies Claude needs go in `ctrl/secrets/`.
- Everything done goes into scripts in a repo so it can be rebuilt.

## Manual steps (Alex) before Claude can start

1. **SSH key to pve1** (own terminal): `ssh-copy-id -i ~/.ssh/id_ed25519.pub root@192.168.1.21` → `yes` → root password.
2. **Root password in Vaultwarden**: item `pve1 root (Proxmox)`, user `root`, URL `https://192.168.1.21:8006`.
3. **Router** (`http://192.168.1.1`, ZTE F6601P): log in, read the DHCP pool range, then keep `.21` safe (see `docs/home-systems.md` § Address plan). Save the router login to Vaultwarden.
4. **Tailscale**: create the account (tailscale.com, sign in with Google/GitHub), install the app on the MBP and phone. Later, per machine, Alex opens a login link Claude prints.

Later, inside the VM (Alex types these; Claude can't): `claude` login, `gh auth login`, Tailscale login link, hookdeck env/secrets.

## Phases

0. **Discovery (read-only)**: Proxmox version, storage layout, bridge config, repos, disk health (`smartctl`), BIOS version. **Audit what the shop left**: `authorized_keys`, users, cron, extra repos/packages. Anything odd → reinstall from the official ISO.
1. **Host basics**: no-subscription repo, updates, `amd64-microcode`, Tailscale on the host, SSH password login off (keys only), BIOS update if outdated.
2. **VM template**: Debian 13 cloud image + cloud-init: user `alex`, MBP key, qemu-guest-agent, Docker, mise, git, GitHub CLI, Claude Code, Tailscale.
3. **hookdeck VM**: clone of the template. Start: 8 vCPU, 32GB RAM, 250GB disk, static `192.168.1.22`. Then hookdeck workspace + repos, one core stack up (~8.5GB idle), T3 Code server as a service on the VM's Tailscale address. Stop for Alex to test from the MBP and phone.
4. **After the milestone**: snapshots/backup target, more workspace VMs from the same scripts, arrstack move, runbook ("add a workspace", "restore a VM").

## Open questions

- Repo for the scripts. Proposal: new private repo in the `collielab` org (personal infra); inventory summarized in `docs/home-systems.md`.
- T3 server: must start after Tailscale is up; how it authenticates.
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
- Is Remote Login (SSH) on? Which user accounts exist?
- What runs here: Colima/Docker containers, Plex, Jellyfin, qBittorrent, anything
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
