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
- **Known issue after the kernel change:** no hardware-clock device (`/dev/rtc0` missing, `hwclock` fails). Kernel 6.14 registered `rtc_cmos 00:02`; 7.0.14 does not on this BIOS (T26 02.02.00, 2021). Time is still right (read at boot, then kept by chrony over the network). Effect: the hardware clock is no longer written back. Details and a second, bigger finding (TSC marked unstable, kernel on the slow HPET timer): `kernel-7-clock-issues.md`.
- **G8 SSH keys only:** `/etc/ssh/sshd_config.d/10-keys-only.conf` (`PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `PermitRootLogin prohibit-password`). Verified: key login works, password login refused. Password still works on the console and web UI. Undo: delete the file, `systemctl reload ssh`.
- **Mac Mini Remote Login (Alex + the Mini's Claude session):** turned on, limited to `alex`; MBP `id_ed25519` public key added to `~/.ssh/authorized_keys`. Password login still allowed. Undo: System Settings → General → Sharing → Remote Login off.
- **MBP `~/.ssh/config`:** appended `Host mini` (`192.168.1.90`, `alex`, `id_ed25519`, `UseKeychain`/`AddKeysToAgent`). Backup: `~/.ssh/config.bak-20261002-mini`. Host key checked against the Mini's doc (`SHA256:W06CBmqK…`). `ssh mini` works.
- **ctrl repo:** PR #1 from the Mini's clone (45 unpushed media commits on the old layout + `mac-mini.md`) merged into `main` as `33f9f4d`. The Mini's clone is still on branch `docs/mac-mini` (a Claude session is running there); switch it to `main` when idle.
- **MBP `~/.ssh/config`: names instead of addresses (Alex):** `g8` → `g8.lab.alexluong.com`, `mini` → `mini.lab.alexluong.com`. `known_hosts` got entries for both names, copied only after each scanned key matched the one already trusted for the address. Backup: `~/.ssh/known_hosts.bak-20261002`.
- **MBP `Host vultr`** (`alex@149.28.40.6`, key `github_alexluong`): replaces the `sshmylab` shell alias, which now runs `ssh vultr` (`~/.zshrc`, backup `~/.zshrc.bak-20261002`). Still an address: the VM has no DNS-only record.
- **DNS (collielab terraform, Alex approved):** A record `vultr.alexluong.com` → the Vultr instance's address (`149.28.40.6`), DNS-only. collielab commit `6d9be07`. MBP `Host vultr` now uses the name; `known_hosts` entry added after matching the trusted keys. Undo: delete the resource, `terraform apply`.
- **Fleet SSH config moved into git (collielab `d8dc870`):** `ssh/config`, `ssh/known_hosts`, `ssh/authorized_keys`. MBP `~/.ssh/config`: the three `Host` blocks replaced by `Include ~/git/hub/alexluong/collielab/ssh/config`. Backup: `~/.ssh/config.bak-20261002-fleet`. Undo: restore the backup.
- **vultr `authorized_keys`:** MBP `id_ed25519` public key appended (was `github_alexluong` only). Backup on the VM: `~/.ssh/authorized_keys.bak-20261002`.
- **collielab `hosts/vultr/Caddyfile`:** copy of the VM's `/etc/caddy/Caddyfile` (read only, nothing changed on the VM).
- **G8 kernel pinned to 6.14.11-9-pve** (Alex's call): `proxmox-boot-tool kernel pin 6.14.11-9-pve` (writes `/etc/default/grub.d/proxmox-kernel-pin.cfg`), reboot 17:38. Verified: clocksource `tsc` (clock read 71 ns per call, was 1421 ns on HPET), `rtc_cmos 00:02: registered as rtc0`, `hwclock` works, all services active, no failed units. Kernel 7.0.14 stays installed, unused. Undo: `proxmox-boot-tool kernel unpin` + reboot. Follow-up: TASK-4.

### VM template and the hookdeck VM (afternoon, Alex away; scripts in collielab `51405c4`)

- **Decision (Alex): scripts live in `collielab`**, not a new repo: `hosts/g8/vm-template/{build,provision,seal}.sh`, `hosts/g8/new-vm.sh`, `hosts/workspace-vm/setup.sh`, `hosts/hookdeck/setup.sh`, `bin/new-vm`, runbook `hosts/g8/README.md`.
- **g8:** copied the fleet's public keys to `/root/fleet-authorized_keys`; downloaded the Debian 13 cloud image to `/var/lib/vz/template/cloud/` (checksum verified).
- **Template VM 9000 `debian13-base`:** built at the temporary address `192.168.1.149`, provisioned (Docker, gh, mise, Node 22, Claude Code, T3 binary 0.0.44, limits, passwordless sudo, linger), sealed into a template. Rebuilt once at the end so it includes packages added after the survey. Undo: `qm destroy 9000 --purge`.
- **VM 101 `hookdeck`:** `new-vm.sh 101 hookdeck 8 32768 250` → `192.168.1.101`, starts with the host. Undo: `qm stop 101 && qm destroy 101 --purge` (destroys its disk).
- **DNS (terraform, applied):** `hookdeck.lab.alexluong.com` → `192.168.1.101`. **SSH:** `Host hookdeck` block and the VM's host keys in `collielab/ssh/`.
- **In the VM:** base re-applied (`provision.sh`); `hosts/workspace-vm/setup.sh` (T3 Code server as a user service on `127.0.0.1:3773`); `hosts/hookdeck/setup.sh` (Doppler, the workspace's pinned mise tools, gopls, golangci-lint, Playwright libraries, IPv4-first for `*.localhost`, an SSH key for GitHub); `~/.claude/settings.json` + `CLAUDE.md` copied from the dotfiles repo; the stacks' public Docker images pre-pulled.
- **Snapshot `clean-setup`** of VM 101: tools installed, no login or secret.
- **Repeatability test:** `bin/new-vm 148 test-vm 2 2048 20` created a working VM (clone, keys, alias, DNS snippet, T3 service) in 39 seconds; destroyed afterwards and its repo entries reverted.
- Snags fixed on the way (all in the scripts now): `ls | tr` under `pipefail` aborted the script when `~/go/bin` was missing (mise puts Go tools in the Go install's own `bin`); `sudo npx` went through alex's mise shims and was refused (use node's real path); `*.localhost` answered `::1` first.
- Not done, by design: any login or secret on the VM. First-run list: `hookdeck-vm.md`.
- **Checks at the end:** template rebuilt from nothing with the three scripts, unattended (about 6 minutes); pre-pull finished (26 images, 21GB; VM disk 26GB used of 246GB); **whole-box reboot test**: g8 back on the pinned kernel, VM 101 started by itself, Docker and the T3 service active about 30 seconds after the host. Snapshot `clean-setup` retaken to include the images.
- **Mini SSH keys only (Alex ran `sudo bash /tmp/root-setup.sh`, from collielab `hosts/mini/root-setup.sh`):** `/etc/ssh/sshd_config.d/100-keys-only.conf`. Verified from the MBP: password login refused, key login works. Undo: delete the file.
- **Evening, with Alex:** `claude` and `gh auth login` done on the VM (VM's own key uploaded to GitHub; `alexluong`, `hookdeck`, `amp-labs` repos reachable). Then on the VM: git identity set, workspace cloned (branch `workspace`), `mise trust` + `mise install`, `bin/wt init` (8 repos). `doppler setup` in core waits for `doppler login`. Per-VM requirements now have a home: `docs/vms/` (index + template, `hookdeck.md`).
- **Gateway `gw` (TASK-3):** terraform `lab_gateway.tf` (A records `lab`, `gw.lab`, `*.lab`, `*.mini.lab`, `*.g8.lab`, `*.hookdeck.lab`, `*.calibre.lab`, `*.calibre.mini.lab` → `192.168.1.110`; account token `lab-gateway-acme`, DNS edit on the `alexluong.com` zone). g8: Debian 13 container template downloaded; container 110 created (`hosts/gw/create.sh`), Caddy installed (`setup.sh`), config pushed (`push.sh`). Undo: `pct stop 110 && pct destroy 110 --purge` on g8; delete `lab_gateway.tf` and `terraform apply` (removes the records and revokes the token); remove `Host gw` and its keys from `collielab/ssh/`.
- **Mini (Alex):** "Allow full disk access for remote users" switched on in Sharing → Remote Login. Verified: SSH lists `/Volumes/Blue4/arr` and `/Volumes/Red4/arr`. Undo: switch it off.
