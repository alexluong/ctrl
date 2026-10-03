# Workspace VM maintenance

Routine care of the VMs on g8: snapshots, what needs the VM idle, what a restart breaks. Building a VM: `playbook.md`. Host runbook: `collielab/hosts/g8/README.md`.

## Snapshots vs backups

| | Snapshot | Backup (TASK-13, not set up yet) |
|---|---|---|
| Where | g8's own SSD, same thin pool (`local-lvm`) as the VM disk | another machine |
| Protects against | a bad change inside the VM (upgrade, an agent wrecking the setup) | g8 or its SSD dying |
| Cost | holds the old copy of every block changed since; grows over time | disk elsewhere, transfer time |
| Speed | instant to take and to roll back (rollback discards everything after it) | minutes to hours to restore |

Rules for snapshots:

- Take one before a change that is hard to undo inside the VM (OS upgrade, big tool change, a TASK-8-style setup rewrite). Name `<what>-<yyyymmdd>`, with a description saying what state it holds.
- Keep at most 2 per VM: the newest known-good state, and the one before a change in progress. Delete the rest (`qm delsnapshot <id> <name>`).
- Prefer taking it while the VM is idle (no stacks, no sessions): the copy is consistent without relying on the guest-agent freeze.
- Commands on g8: `qm snapshot <id> <name> --description "…"`, `qm listsnapshot <id>`, `qm rollback <id> <name>`, `qm delsnapshot <id> <name>`.

The thin pool is overcommitted on paper (VM disk ceilings plus snapshots exceed its 816GB; LVM warns on every snapshot). Real use is what counts: `ssh g8 lvs pve/data` (Data% column; 9.5% on 2026-10-04). Watch it before adding VMs; TASK-7 monitoring should alert on it.

## Keeping VMs in step with the scripts

The template and running VMs drift apart when a script changes. After changing `collielab/hosts/g8/vm-template/provision.sh` or a `hosts/<vm>/setup.sh`, rerun it on each live VM it applies to (both are idempotent): `ssh <vm> 'sudo bash -s' < hosts/g8/vm-template/provision.sh`. The template only matters for the next VM; rebuild it then (`hosts/g8/README.md`).

## What needs the VM idle

Most work happens with the VM running. Save these for a quiet window (no T3 turns in flight, stacks stopped or disposable):

| Change | Why it needs downtime | How |
|---|---|---|
| CPU or RAM size, balloon, other `qm set` hardware options | applied only on a full stop/start (a reboot from inside the VM is not enough) | `qm set …`, then `qm shutdown <id>` + `qm start <id>` |
| Disk grow | none (live): `qm resize <id> scsi0 +50G` | any time |
| g8 kernel or Proxmox upgrade with reboot | every VM stops | `apt list --upgradable` on g8 first |
| BIOS update, kernel 7.0 retest | at the box | TASK-4 |
| Rollback to a snapshot | discards everything after it | `qm rollback` |

Not worth a window: guest `apt upgrade` (any time; reboot only for a new guest kernel), Docker cleanup (most "reclaimable" image space on hookdeck-ws is the pre-pulled stack images; pruning them only costs a re-download).

## What a VM restart breaks

- Every T3 session on the VM ends (threads resume from the app).
- Containers without a restart policy stay down: dev stacks started by a task (e.g. hookdeck's `task22-*`) need their start command again. Containers with `restart: unless-stopped` (Dozzle, Isaiah) come back.
- Hand-started tunnels (`ssh -N hd_jumpbox`) are gone.
- Comes back by itself: the VM (`onboot 1`), Docker, the T3 service (`systemctl --user is-active t3code`).

## Checks after a restart

```sh
ssh g8 'qm status <id>; pvesh get /nodes/g8/qemu/<id>/status/current --output-format json | jq "{mem, maxmem}"'
ssh <vm> 'systemctl --user is-active t3code; docker ps --format "{{.Names}} {{.Status}}"; free -g | sed -n 2p'
```

Proxmox memory shows real guest use only when the VM has a balloon device (`balloon` equal to `memory`, so RAM is never taken back). `new-vm.sh` sets it since 2026-10-04; hookdeck-ws got it the same day.

## Log

- 2026-10-04 hookdeck-ws: balloon on (Proxmox showed 100% memory), compose 5.6, snapshot `idle-20261004`. Template 9000 rebuilt (service PATH fix).
