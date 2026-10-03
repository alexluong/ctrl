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

2. **gw: Tailscale installed and joined** (Alex's OK; Alex did the login).
   - `curl -fsSL https://tailscale.com/install.sh | sh` (official installer: apt repository `/etc/apt/sources.list.d/tailscale.list`, keyring `/usr/share/keyrings/tailscale-archive-keyring.gpg`, package `tailscale` 1.102.4, service `tailscaled` enabled). It also pulled in `iptables` (nft backend).
   - `tailscale up --accept-dns=false --hostname=gw`. gw = **`100.126.136.120`**, owner `lhtanh98@`, no tags.
   - Checked after: `/etc/resolv.conf` unchanged (still `192.168.1.1`); default route unchanged; `tailscale ping` to the Mini answers directly over the home network (`192.168.1.90:41641`); Caddy active; `https://lab.alexluong.com` 200; forwarding still off.
   - Tailscale's firewall chains as installed: forwarded packets going out of `tailscale0` are accepted unless their sender is in `100.64.0.0/10`; masquerade exists only for packets that came in from `tailscale0` (the subnet-router direction). So home → tailnet needs our own masquerade rule, as design.md expected.
   - Open: key expiry is still on for gw (default 180 days); turn off before relying on it.
   - Undo (below, after change 4): see the end of this entry.

3. **gw: forwarding and masquerade, runtime only** (Alex's OK). Gone when gw restarts.
   - `sysctl -w net.ipv4.ip_forward=1`
   - `nft add table ip task9`; `nft 'add chain ip task9 post { type nat hook postrouting priority 100; }'`; `nft add rule ip task9 post ip saddr 192.168.1.0/24 oifname tailscale0 counter masquerade`
   - Undo: `ssh gw 'nft delete table ip task9; sysctl -w net.ipv4.ip_forward=0'`

4. **MBP: hand-added route, runtime only** (Alex ran it). Gone at reboot.
   - `sudo route add -net 100.64.0.0/10 192.168.1.110`
   - Undo: `sudo route delete -net 100.64.0.0/10`

**Proof, from the MBP with no Tailscale installed (all passed):**

| Test | Result |
|---|---|
| `ping 100.91.137.41` (Mini) | 0% loss, ~6–20 ms |
| traceroute | 2 hops: `192.168.1.110`, then the Mini |
| `ssh` to the Mini's `100.x`, host key checked as `mini.lab.alexluong.com` | logged in; Mini sees the client as `100.126.136.120` (gw) |
| `http://100.91.137.41:8096/health` (Jellyfin direct) | 200 |
| `https://lab.alexluong.com` forced to `100.126.136.120` | 200, certificate valid |
| `https://jellyfin.lab.alexluong.com/health` forced to `100.126.136.120` | 200 |

Not tested: T3 (hookdeck-ws is not on the tailnet yet).

   - Undo for change 2: `ssh gw 'tailscale logout; apt purge -y tailscale; rm /etc/apt/sources.list.d/tailscale.list /usr/share/keyrings/tailscale-archive-keyring.gpg'`, then remove `gw` in the admin console. (`iptables` stays unless purged too.)

## 2026-10-04

**Router page read (Alex, screenshots; nothing saved).** Local Network → Routing → IPv4 → Static Routing exists. Egress choices: `LAN`, `omci_ipv4_pppoe_1`, `omci_ipv4_dhcp_3`. Help text: gateway must be reachable through the chosen connection; `0.0.0.0/0.0.0.0` = default route. No static routes saved.

Router's routing table (2026-10-04):

| Network | Mask | Gateway | Interface |
|---|---|---|---|
| `0.0.0.0` | `0.0.0.0` | `125.235.249.147` | `omci_ipv4_pppoe_1` (internet) |
| `30.177.192.0` | `255.255.240.0` | — | `omci_ipv4_dhcp_3` (second Viettel connection, likely their management/IPTV) |
| `125.235.249.147` | `255.255.255.255` | — | `omci_ipv4_pppoe_1` |
| `192.168.1.0` | `255.255.255.0` | — | `LAN` |

Nothing in `100.64.0.0/10`: the route does not collide with anything Viettel uses on this router (check 4, evidence for).

**MBP test route removed (Alex).** Then tested before the router rule existed:
- From the MBP: all `100.x` traffic went into a full-tunnel VPN, not to the router. `utun8` (`10.198.12.38`, routes `0/1` and `128.0/1` → `10.198.0.1`, server `185.150.0.180` via `en0`; Private Internet Access; Cloudflare WARP's app is open but disconnected, checked with `warp-cli status`). The first proof worked only because the hand-added `/10` route was more specific than the VPN's `/1` routes. **Any device with a full VPN on sends `100.x` into the VPN, so the router rule does not help it** (needs the VPN off, a split-tunnel exception for `100.64.0.0/10`, or the Tailscale app).
- From g8 (home machine, no Tailscale, no VPN), used as the test client from here on: `100.x` → router → Viettel (`125.235.249.147`, `10.255.38.221`) → dropped. As expected with no rule: the router sends unknown addresses to the internet.

5. **MBP: PIA split tunnel, `100.64.0.0/10` bypasses the VPN** (Alex's OK).
   - `"/Applications/Private Internet Access.app/Contents/MacOS/piactl" -u applysettings '{"splitTunnelEnabled":true,"bypassSubnets":[{"mode":"exclude","subnet":"100.64.0.0/10"}]}'` (PIA 3.5.7). Before: `splitTunnelEnabled false`, `bypassSubnets []`, `allowLAN true`, killswitch auto, OpenVPN.
   - Read back: `splitTunnelEnabled true`, `bypassSubnets [{"mode":"exclude","subnet":"100.64.0.0/10"}]`, still Connected. MBP routing table now has `100.64/10 → 192.168.1.1 en0`: `100.x` goes to the router, not into the VPN.
   - Undo: `piactl -u applysettings '{"splitTunnelEnabled":false,"bypassSubnets":[]}'`
   - Router rule still not added (g8's traceroute still goes to Viettel).

Every setting this depends on, in one place: `docs/tailscale.md` § Every setting this depends on.

6. **Router: static route `tailscale`** (Alex added it in the router UI).
   - Local Network → Routing → IPv4 → Static Routing: Name `tailscale`, Egress `LAN`, Network `100.64.0.0`, Mask `255.192.0.0`, Gateway `192.168.1.110`.
   - Undo: trash icon on the entry, Apply.

**Proof through the router (all passed):**

| From | Path (traceroute) | ping | ssh | Jellyfin `100.x` | lab page on gw `100.x` |
|---|---|---|---|---|---|
| g8 (no Tailscale, no VPN) | `192.168.1.1` → `192.168.1.110` → Mini | 0% loss, ~4 ms | port open | 200 | 200 |
| MBP (no Tailscale, PIA on with the exception) | same | 0% loss, ~6 ms | logged in, seen as gw | 200 | 200 |

100MB over ssh from the Mini to the MBP, twice: through router + gw ~200 Mbit/s; direct (`192.168.1.90`) 226 / 272 Mbit/s. gw load ~0.1. Large packets fine.

**Phone test (Alex), check 5 part 1:** iPhone on home Wi-Fi, Tailscale app off: `http://100.91.137.41:8096` (Jellyfin on the Mini's Tailscale address) works. Still to try: away on cellular with the app on.
