# Playbook: a new Proxmox box

How to take a new machine from the delivery box to a host that `bin/new-vm` can create workspace VMs on. Written from g8 (HP EliteDesk 805 G8 Mini, 2026-09-30 to 2026-10-02); details of every step as done there: `../../work/task-2/log.md`, `discovery.md`. Buying: `../../work/task-1/decision.md`. After this, workspaces go on with `playbook.md`.

**Time:** about 3 hours, mostly waiting (memory test, upgrade). Alex is needed at the box for step 1 and at the router once.

## 1. At the box (Alex; monitor + USB keyboard)

1. Install Proxmox VE from the official ISO if the seller did not (g8 came with it; the shop's install was audited in step 3 instead).
2. BIOS: virtualization on (AMD: SVM); **After Power Loss = Power On** (HP: Advanced → Boot Options) so it returns by itself after a power cut. Easy way into the BIOS from Linux: `systemctl reboot --firmware-setup`.
3. Memory test: Memtest86+ from the boot menu, one full pass with 0 errors (1–2 hours for 64GB).
4. Set a root password (`passwd`); save it in Vaultwarden as `<host> root (Proxmox)`.
5. Give it its address (`/etc/network/interfaces`, bridge `vmbr0`) from the plan in `../home-systems.md`: each host gets a block of 50 (`g8` = `.100–.149`, next `.150–.199`): host first, its VMs after. Addresses from `.100` up are never handed out by the router (pool ends at `.99`), so nothing to do on the router for a second host.
6. Plug it into the router by cable. No monitor or keyboard needed after this.

## 2. Access from the MBP

```sh
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@<address>      # Alex, once, types the root password
```

The key must be loaded in the MBP's agent for Claude to use it (`ssh-add --apple-use-keychain ~/.ssh/id_ed25519`). Then in `collielab`: DNS record `<host>.lab.alexluong.com` (terraform), a `Host` block in `ssh/config`, host keys in `ssh/known_hosts`, a folder `hosts/<host>/`.

## 3. Discovery and audit (Claude, read-only)

Versions, CPU and memory as sold, disk health (`smartctl`), storage layout (`pvesm status`, `lvs`), network config, and **what the installer or seller left**: `authorized_keys`, users, Proxmox users and tokens, cron, apt sources, extra packages and services, listening ports. Anything odd → reinstall from the official ISO. Record as `discovery.md`.

## 4. Host basics (Claude; each change logged with its undo)

1. Name and address: `/etc/hostname`, `/etc/hosts` (`<address> <host>.lab.alexluong.com <host>`), postfix `myhostname`, `/etc/resolv.conf`; do it **before any VM exists** (afterwards: remove the old `/etc/pve/nodes/<old>` and run `pvecm updatecerts --force`). When moving an address remotely: add the new one alongside the old, test, make it permanent, reboot, then drop the old.
2. Update source: disable the enterprise repos (`Enabled: false` in `pve-enterprise.sources`, `ceph.sources`), add `pve-no-subscription`.
3. Upgrade under `nohup` on the box (`apt-get dist-upgrade`), reboot.
4. **After every new kernel, check the clock**: `cat /sys/devices/system/clocksource/clocksource0/current_clocksource` must say `tsc`, and `/dev/rtc0` must exist. On g8, kernel 7.0.14 fell back to the slow `hpet` timer (clock reads 20× slower) and lost the hardware clock; fixed by `proxmox-boot-tool kernel pin 6.14.11-9-pve` (`../../work/task-2/kernel-7-clock-issues.md`, TASK-4). A different machine may be fine on the default kernel: test, don't assume.
5. SSH keys only: `/etc/ssh/sshd_config.d/10-keys-only.conf` (`PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `PermitRootLogin prohibit-password`). The password still works on the console and web UI.
6. BIOS update when next at the box.

The host stays bare: no Docker, no agents, no project code.

## 5. VM template

```sh
cd ~/git/hub/alexluong/collielab
scp ssh/authorized_keys <host>:/root/fleet-authorized_keys
ssh <host> 'BUILD_IP=<last address of the host block> bash -s' < hosts/g8/vm-template/build.sh
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null alex@<build ip> 'sudo bash -s' < hosts/g8/vm-template/provision.sh
ssh <host> 'bash -s' < hosts/g8/vm-template/seal.sh
```

About 6 minutes. For a second host the scripts need two small changes first: `new-vm.sh` checks IDs against g8's block (`101–149`) and `bin/new-vm` calls `ssh g8`; make both take the host as a parameter.

## 6. Prove it

- Throwaway VM: `bin/new-vm <id> test-vm 2 2048 20`, check `ssh`, destroy it (`qm stop <id>; qm destroy <id> --purge`), revert the three files it touched.
- Whole-box reboot: VMs with `onboot` come back by themselves (g8: Docker and T3 in the VM up ~30 seconds after the host).

## Still open on g8 (applies to any host)

Backups of VMs to another machine (plan: the Mini's Blue4 drive), Tailscale for access away from home, the gateway for clean URLs (TASK-3), a UPS.
