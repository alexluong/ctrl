# TASK-2 log: every change made to the G8, the router and the MBP

Newest last. One entry per change: what, why, how to undo. Read-only checks go in `discovery.md`; decisions in `plan.md` and `docs/home-systems.md`.

## 2026-09-30

- **BIOS (Alex, at the box):** After Power Loss = Power On (Advanced → Boot Options). SVM was already on.
- **Root password (Alex, at the box):** changed with `passwd` from the shop's.
- **Memtest86+:** pass 1, 0 errors.
- **Moved to the router**, wired. Reachable at `192.168.1.21` (shop's static config, unchanged).

## 2026-10-02

- **G8 `authorized_keys` (Alex):** added the MBP's `id_ed25519` public key with `ssh-copy-id`. Undo: delete that line from `/etc/pve/priv/authorized_keys`.
- **MBP agent (Alex):** `ssh-add --apple-use-keychain ~/.ssh/id_ed25519` (passphrase saved in Keychain) so Claude can use the key. Undo: `ssh-add -d ~/.ssh/id_ed25519`.
- **MBP `known_hosts`:** host key for `192.168.1.21` accepted on first connect.
- Discovery run (read-only): `discovery.md`.
- **Router (Alex):** Local Network → LAN → DHCP Server: DHCP End IP Address `192.168.1.254` → `192.168.1.99`. Pool is now `.2–.99`; the 5 DHCP Bindings untouched. Undo: set the end back to `.254`.
- **G8 address `.21` → `.100`:** checked `.100` unanswered, added it live (`ip addr add`), tested SSH and web UI on it, then `/etc/network/interfaces` `address 192.168.1.100/24` (kept `.21` as a second address through the reboot, removed after).
- **G8 name `pve1` → `g8`:** `/etc/hostname` = `g8`; `/etc/hosts` = `192.168.1.100 g8.lab.alexluong.com g8`; postfix `myhostname=g8.lab.alexluong.com`; reboot (back in ~2 min); removed `/etc/pve/nodes/pve1` (no guests) and its old stats; `pvecm updatecerts --force` (new certificate for `g8`, `192.168.1.100`).
- **G8 shop leftovers replaced:** `/etc/resolv.conf` = `search lab.alexluong.com`, `nameserver 192.168.1.1`, `nameserver 1.1.1.1` (was `connected.com.vn`, `8.8.8.8`); `root@pam` email → Alex's (was `xeon@connected.com.vn`).
- Originals of every changed file: `/root/pre-rename-backup-20261002/` on the box (incl. the old node dir). Undo = copy back + reboot.
- **MBP `~/.ssh/config`:** appended `Host g8` (`192.168.1.100`, `root`, `id_ed25519`, `UseKeychain`/`AddKeysToAgent` so the key reloads after a restart). Backup: `~/.ssh/config.bak-20261002`. Removed the `192.168.1.21` entry from `known_hosts`.
- Verified after: `ssh g8` works, web UI 200 on `.100`, `.21` no longer answers, all Proxmox services active, no failed units, both storages active. Still above `.99` on old leases: `.124`, `.131`.
- **DNS (collielab terraform, Alex approved):** added A records `g8.lab.alexluong.com` → `192.168.1.100` and `mini.lab.alexluong.com` → `192.168.1.90`, DNS-only. collielab commit `fe385c3`. Undo: delete the two resources in `terraform/alexluong_com.tf`, `terraform apply`.
- **G8 update source:** enterprise repos disabled (`Enabled: false` in `pve-enterprise.sources` and `ceph.sources`), added `/etc/apt/sources.list.d/proxmox.sources` (`pve-no-subscription`, trixie). Originals in the backup dir under `apt/`.
- **G8 upgrade:** `apt-get dist-upgrade` (270 upgraded, 24 new, `libzfs6linux` replaced), finished 17:13 with exit 0. Proxmox 9.0.3 → **9.2.21**; kernel 7.0.14-20-pve installed (running 6.14.8-2 until the reboot). Log on the box: `/root/upgrade-20261002.log`. **Reboot pending.**
- **G8 reboot onto kernel 7.0.14-20-pve** (17:16): back in ~1 min, all services active, no failed units, microcode now `0xa500012`.
- **Known issue after the kernel change:** no hardware-clock device (`/dev/rtc0` missing, `hwclock` fails). Kernel 6.14 registered `rtc_cmos 00:02`; 7.0.14 does not on this BIOS (T26 02.02.00, 2021). Time is still right (read at boot, then kept by chrony over the network). Effect: the hardware clock is no longer written back. Recheck after the BIOS update; fallback is booting the 6.14.11 kernel still installed (`proxmox-boot-tool kernel pin`).
- **G8 SSH keys only:** `/etc/ssh/sshd_config.d/10-keys-only.conf` (`PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `PermitRootLogin prohibit-password`). Verified: key login works, password login refused. Password still works on the console and web UI. Undo: delete the file, `systemctl reload ssh`.
