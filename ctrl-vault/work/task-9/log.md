# TASK-9 log: changes and undo

Design: `design.md`. Newest at the bottom. Each change has its undo.

## 2026-10-03

**Decisions (Alex)**
- Tailnet: keep `lhtanh98@gmail.com` (`tail2b958c.ts.net`). The Mini stays logged in at `100.91.137.41`.
- `iphone-15-pro` is Alex's current phone: keep. `67ee56ee4fc5` and `poc-client` can be removed (Alex, in the admin console; not blocking).
- Hannah's devices: on this tailnet later, media only. Out of scope for the proof.

**Found (read-only)**
- `gw` (container 110, unprivileged, `nesting=1`): no `/dev/net/tun`, `net.ipv4.ip_forward = 0`, empty nftables ruleset (all accept), Tailscale not installed.
- `g8`: `/dev/net/tun` exists (10,200), Proxmox 9.2.21.
- `hookdeck-ws`: `/dev/net/tun` exists, Tailscale not installed.
- MBP: Tailscale not installed.
- Userspace mode on `gw` does not fit option 2: with no `tailscale0` interface the kernel has nothing to forward home traffic into. The tun device is needed.

**Tailnet cleanup (Alex):** `67ee56ee4fc5` and `poc-client` removed; two machines left (`alexs-mac-mini`, `iphone-15-pro`).

**Changes**

1. **gw: tun device passed into container 110** (Alex's OK).
   - On g8: `pct set 110 --dev0 /dev/net/tun`. Adds `dev0: /dev/net/tun` to `/etc/pve/lxc/110.conf`. Config before the change: `g8:/root/110.conf.before-task9`.
   - **No restart was needed**: the device appeared in the running container at once (Proxmox 9.2.21). Checked: a dummy tun interface could be created and deleted inside gw; Caddy stayed active; `https://lab.alexluong.com` returned 200.
   - Not yet seen: the device coming back after a container restart (expected, it is in the config).
   - `collielab/hosts/gw/create.sh` got the same `--dev0` line so a rebuild matches.
   - Undo: `ssh g8 'pct set 110 --delete dev0'` (after removing Tailscale from gw).
