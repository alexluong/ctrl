# TASK-2 discovery: the G8 as delivered (2026-10-02, read-only)

Read over SSH from the MBP (`root@192.168.1.21`, key `id_ed25519` loaded in the agent via Keychain).

## Verdict

Clean shop install, nothing suspicious. No reinstall needed. Outdated: 181 package updates, BIOS from 2021.

## System

- Proxmox VE **9.0.3** (not 9.2), Debian 13.0, kernel 6.14.8-2-pve. Hostname `pve1.connected.com.vn`.
- HP EliteDesk 805 G8 Desktop Mini. Ryzen 7 5700G, 16 threads, AMD-V on.
- RAM: 2 × 32GB Micron `16ATF4G64HZ-3G2E2`, 3200 MT/s. 62GiB visible (graphics takes the rest). Memtest passed 2026-09-30.
- BIOS: `T26 Ver. 02.02.00`, dated 2021-11-03 → update.
- CPU microcode `0xa500011`; `amd64-microcode 3.20250311.1` already installed.
- Wi-Fi card present (`wlp3s0`), unused.

## Disk

- WD PC SN810 1TB NVMe (`SDCPNRY-1T00`, firmware HPS2). SMART passed: 0% wear, 100% spare, 0 media errors, 406 power-on hours, 4.05TB written. 187 unsafe shutdowns of 290 power cycles (history from before; harmless).
- Layout (Proxmox default): root 96G ext4 (3.4G used), swap 8G, thin pool `data` 816G for VM disks (empty), 16G unallocated.
- Storages: `local` (dir, `/var/lib/vz`: ISOs, container templates, backups), `local-lvm` (thin pool: VM and container disks).

## Network

- `vmbr0` static `192.168.1.21/24`, gateway `192.168.1.1`, on `eno1`. No VLANs.
- DNS `8.8.8.8`, search domain `connected.com.vn` (shop's) → change.
- Proxmox firewall off. Listening: 22 (SSH), 8006 (web UI), 3128 (SPICE proxy), 111 (rpcbind), 25 on localhost only.

## What the shop left

- Users: only `root`. Proxmox users: only `root@pam`, email `xeon@connected.com.vn` → change. No API tokens.
- `authorized_keys`: Proxmox's own `root@pve1` key (standard) and Alex's. Nothing else.
- No root crontab; `/etc/cron.d` is stock. No extra systemd services. No extra apt repos.
- Repos: enterprise repos enabled (need a subscription, so updates fail) → switch to no-subscription.
- `nmap` installed by hand (not a Proxmox dependency). Harmless.
- SSH: root login and password login both on → keys only.
- No VMs, no containers.

## Clock

The hardware clock read 2010-01-01 at every boot until the box first went online (2026-09-30 19:18), so the shop never set it; logs before that are dated 2025-06-25 (systemd's floor date). It is correct now and written back to the hardware clock. Unknown whether the clock battery holds through a long unplug: check `hwclock` after the next time the box has been without power.

## To do from this (phase 3, host basics)

- No-subscription repos, full upgrade (181 packages), reboot.
- BIOS update.
- Hostname → `g8`, drop `connected.com.vn`; address → `.91`; DNS → router or 1.1.1.1; root@pam email → Alex's.
- SSH keys only.
