# TASK-6 handoff: remote services in `svc` (2026-10-02)

Started inside the TASK-2 session, stopped at Alex's request ("turn it into a dev task") before anything was merged. The menubar Alex uses is unchanged.

## What Alex asked for

An easy button on the MBP to turn the jumpbox tunnel on and off **inside `hookdeck-ws`**. The MBP must not affect the tunnel (sleep, leaving home); the definition lives on the MBP (ctrl `services.conf`). Alex has not yet confirmed the design below: explain it to him in plain terms first.

## Why

`prd pg` and the staging scripts look for the tunnel on the localhost of the machine the session runs on. Sessions on the VM therefore need the tunnel on the VM. The Mac rows `hookdeck-tunnel-prd/-stg` only serve sessions on the Mac.

## Done already (outside this branch)

- On the VM: `~/.ssh/id_ed_hookdeck`, `~/.ssh/config` with the `hd_jumpbox` and `hd_jumpbox_stg` blocks (copies of the MBP's; they drift if the MBP's forwards change), host fingerprints. Login to both jumpboxes tested with no forward opened. Recorded in `docs/vms/hookdeck-ws.md`. The same key also opens Alex's GitLab on the MBP.

## Design on the branch (`svc-remote`, worktree `local/svc-remote`, commit `485e5cd`)

- `services.conf`: a row whose dir is `<ssh host>:<dir>` runs on that host. New group `[hookdeck-ws]` with `tunnel-prd`, `tunnel-stg`.
- `bin/svc`: for such rows, start = `ssh <host> systemd-run --user --unit svc-<name> … mise exec -- bash -c "exec <cmd>"` (transient unit, `Restart=on-failure`, nothing installed on the VM; the VM has linger on, so the unit outlives the SSH session). Stop and state = `systemctl --user stop|is-active`. Logs = `journalctl --user -u svc-<name>`. One kept-open SSH connection per host (`ControlPersist`), 3s timeout, a host that fails is asked once per run.
- States: `running`, `stopped`, `failing` (restart loop), `offline` (host unreachable).
- `menubar/svc.10s.sh`: checkmark = running on the VM, click = toggle, `⚠️` = failing, greyed `(host offline)`.

## Tested from the worktree

Start, stop, toggle, restart, status with a `sleep` service; a command that exits at once (reported, unit removed); an unreachable host (reported). `svc ls` with the VM up: 0.2s (0.7s for the first call).

## Not done

1. **Staging tunnel fails on the VM while the outpost stack runs.** `hd_jumpbox_stg` forwards local port `26379`; the outpost stack's `outpost-redis-1` publishes the same port. `ExitOnForwardFailure=yes` then ends the tunnel. Options: change the port on one side (the forward lives in the VM's `~/.ssh/config`; what reads `26379` in the hookdeck workspace must follow), or drop that forward on the VM. The prod block has no clash with what was running.
2. **Prod tunnel on the VM not started** (only the login was tested).
3. **Menubar not tested in SwiftBar** with the new code (only `svc ls` output). SwiftBar starts scripts with a bare environment: check the SSH agent is reachable from it.
4. **Temporary rows** `test`, `bad`, `gone` in `services.conf` on the branch: remove before merging.
5. **Decisions for Alex:** prod tunnel closing itself after N hours (`-p RuntimeMaxSec=`; needs a place in `services.conf`, whose last column is the command and may contain `|`); keep or drop the Mac-side tunnel rows.
6. **Board on the VM** (`backlog browser` binds 127.0.0.1 only: needs a port forward or the gateway). Same mechanism, later.
7. **Docs:** `services.conf` header (done on the branch), AGENTS.md layout line for `bin/svc`, `docs/vms/playbook.md` (survey: what the workspace runs from the menubar), hookdeck `machines.md`, and the hookdeck workspace's "jumpbox tunnel is down (Alex: ssh hd_jumpbox)" hint.

## Found on the way (separate fix, collielab)

`hosts/g8/vm-template/provision.sh` line 126 writes `PATH=%h/.local/bin:…` to `~/.config/environment.d/10-path.conf`. `%h` is not expanded there, so systemd user services on the VMs get a PATH with literal `%h`. Use `${HOME}`. T3 is unaffected so far (its unit uses full paths); `svc` calls mise by full path for the same reason. Fix the script and the file on `hookdeck-ws`; takes effect at the next start of the user manager.
