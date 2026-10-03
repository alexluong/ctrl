# T3 Code against a remote machine

App quirks and filing upstream: `t3-code.md`.

How the T3 Code desktop app on the MBP drives agent sessions on another machine (workspace VMs on g8). Researched 2026-10-02 from the v0.0.44 source and docs plus the local install; set up on `hookdeck` the same day. Scripts: `collielab/hosts/g8/vm-template/provision.sh` (binary), `collielab/hosts/workspace-vm/setup.sh` (service).

## Facts

- MBP app: `/Applications/T3 Code (Alpha).app`, 0.0.44 (latest stable, 2026-09-29). It bundles its own server on `127.0.0.1:3773`; state in `~/.t3/userdata/`. No `t3` CLI on the Mac.
- The server is a self-contained binary: `curl -fsSL https://t3.codes/install.sh | sh` → `~/.t3/runtime/versions/<ver>/`, symlink `~/.local/bin/t3`. `T3CODE_VERSION` pins a version. No Node needed.
- Commands: `t3 serve` (headless), `t3 pair`, `t3 auth pairing|session …`, `t3 project add|remove|rename`, `t3 service install|status|restart|uninstall`, `t3 update`.
- Settings by env var: `T3CODE_HOST` (default `127.0.0.1`), `T3CODE_PORT` (default: first free from 3773), `T3CODE_HOME`, `T3CODE_NO_BROWSER`.
- One server serves many projects. Projects, threads and provider logins live on the remote machine.
- The server reads PATH at start from the user's login shell, so tools from mise are found; restart the service after changing PATH.
- Auth: no static token. A one-time pairing token is exchanged for a per-device session. A paired session is a shell as that user.

## Three ways the app reaches a remote server

1. **SSH (what we use):** Settings → Connections → Add environment → SSH → `user@host`. The app starts or reuses the server on the remote's loopback and forwards the port through SSH. Encrypted; nothing listens on the network. It reuses a running server only if that server is bound to loopback or `0.0.0.0`.
2. LAN pairing: `t3 pair` on the remote prints a URL (valid 5 minutes) to paste into Add environment. Plain HTTP on the network; would need `T3CODE_HOST=0.0.0.0`.
3. T3 Connect: cloud relay, needs an account. Not used (so no push notifications on the phone).
4. **Tailscale HTTPS (what the iOS app uses):** the iOS app has no SSH option. Each tailnet VM runs `tailscale serve`: `https://<vm>.tail2b958c.ts.net` → the T3 server on `127.0.0.1:3773`. Tailnet only, real certificate, the server stays on loopback. § iPhone below.

## Our setup on a workspace VM

- Binary in the template, pinned to the MBP app's version (`T3_VERSION` in `provision.sh`). **When the app updates, update the VMs** (`t3 update` in each, and bump the pin).
- Service per VM (not in the template: its identity and signing keys in `~/.t3/userdata` must differ per VM): `t3 service install` writes `~/.config/systemd/user/t3code.service`; our drop-in `t3code.service.d/override.conf` sets `T3CODE_HOST=127.0.0.1`, `T3CODE_PORT=3773`, `T3CODE_NO_BROWSER=1`. Linger is on, so it runs without a login. Logs: `~/.t3/userdata/logs/boot-service.log`.
- Loopback only, by choice: the SSH path needs nothing more, and plain HTTP would otherwise be readable on the home network. For a browser on another device later: the gateway (TASK-3) in front, or `t3 pair --tailscale`.
- Away from home: the SSH environment uses the VM's name, so it works away once the VM is on the tailnet (`bin/vm-tailnet <name>`, `tailscale.md`) and the Mac's Tailscale app is on. Nothing to change in T3.

## Connect from the MBP (by hand, in the app)

1. Settings → Connections → Add environment → SSH → `hookdeck-ws` (or `alex@hookdeck-ws.lab.alexluong.com`).
2. Settings → Providers → pick that environment → enable Claude (set "Binary path" to `/home/alex/.local/bin/claude` if it isn't found). Claude must be logged in on the VM first.
3. Add a project: from the app against that environment, or on the VM `t3 project add ~/workspaces/hookdeck --title hookdeck`.

Revoke access: `t3 auth session list|revoke` on the VM.

## iPhone (T3 Code iOS app) → a workspace VM

Automatic per VM since 2026-10-04 (decided: Tailscale HTTPS route, no T3 Connect):

| Piece | Where it is set | Survives restarts |
|---|---|---|
| HTTPS certificates on for the tailnet | `collielab/terraform/tailscale.tf` (`tailscale_tailnet_settings`, `https_enabled`) | tailnet setting |
| `tailscale serve --bg` https:443 → `127.0.0.1:3773`; dev user as Tailscale operator | `collielab/hosts/workspace-vm/tailscale.sh`, run by `bin/vm-tailnet <vm>` and `bin/new-vm … --tailscale` | yes: saved in tailscaled's state on the VM, restored at boot; the T3 server itself starts at boot (user service, linger) |
| The phone may reach a VM on :443 | policy grant 1 (your devices → everything) + a test (`lhtanh98@gmail.com` → `tag:vm:443`) | policy |
| Pairing the phone (once per phone and VM) | **by hand**: `bin/vm-t3-pair <vm> [label]` in collielab prints a one-time link + QR (10 min); on the phone with the Tailscale app on: T3 → Settings → Environments → add | the pairing stays until revoked (`t3 auth session list|revoke` on the VM) |

hookdeck-ws: `https://hookdeck-ws.tail2b958c.ts.net` (checked 2026-10-04: 200, valid certificate; the first request after enabling waits ~30 s while the certificate is issued). The MBP stays on SSH, unchanged. The phone needs the Tailscale app on (at home too: the name `*.ts.net` only resolves through Tailscale). Check on a VM: `tailscale serve status`. Mini: later.

Versions: VM and MBP on 0.0.44; 0.0.45 is out: update (`T3_VERSION` in the template, `t3 update` on the VM) if the App Store app complains.

## Not verified

- Whether the app honours `~/.ssh/config` aliases (`hookdeck`) or needs `user@host`.
- The drop-in env vars are traced through the source, not documented upstream. They work on `hookdeck`: `server-runtime.json` shows `127.0.0.1:3773`, `serviceManaged: true`.
- 0.0.45 nightlies were not read.

## Sources

- https://github.com/pingdotgg/t3code/blob/v0.0.44/docs/user/remote-access.md
- https://github.com/pingdotgg/t3code/blob/v0.0.44/docs/user/install.md
- https://github.com/pingdotgg/t3code/blob/v0.0.44/docs/user/background-service.md
- https://github.com/pingdotgg/t3code/blob/v0.0.44/docs/internals/environment-auth.md
- https://github.com/pingdotgg/t3code/blob/v0.0.44/apps/server/src/cli/config.ts
