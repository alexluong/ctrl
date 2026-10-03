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

7. **gw: Tailscale side made permanent** (Alex's OK): `ssh gw 'bash -s' < collielab/hosts/gw/tailnet.sh`.
   - Writes `/etc/sysctl.d/90-gw-tailnet.conf` (forwarding), `/etc/gw-tailnet.nft` (table `ip gw_tailnet`, same masquerade rule) and `gw-tailnet.service` (loads it at boot); deletes the hand-made `task9` table; **disables** Debian's `nftables` service (its start and stop both flush every rule, Tailscale's included; it only loaded an allow-all file). Disabled, not stopped: stopping would have run the flush right away (caught in review before running).
   - Restart test: `pct reboot 110`; back in seconds with tun, forwarding, `gw_tailnet`, Tailscale (same `100.126.136.120`), Caddy; g8 and MBP paths work.
   - New `collielab/hosts/gw/check.sh` (read-only health check of the whole chain): all good. `hosts/gw/README.md` rewritten to cover both jobs, rebuild order and traps.
   - Undo: `ssh gw 'systemctl disable --now gw-tailnet; rm /etc/systemd/system/gw-tailnet.service /etc/gw-tailnet.nft /etc/sysctl.d/90-gw-tailnet.conf; sysctl -w net.ipv4.ip_forward=0; systemctl enable nftables'`

**Cleanup (2026-10-04):** removed `g8:/root/110.conf.before-task9` (the tun change is permanent and in `create.sh`). gw has no leftover files. Key expiry noted: Mini 2027-01-10, gw 2027-03-31 (to turn off). Phone away with the app: assumed to work, Alex to confirm.

8. **Tailscale access rules, by Terraform** (Alex's OK). `collielab/terraform/tailscale.tf`, provider `tailscale/tailscale` 0.29.2, OAuth client `terraform` (scope policy file; Alex created it, credentials in `collielab/terraform/.env`). Policy: tags `gw`/`media`/`vm`; your devices → all; `tag:gw` → `tag:vm`, `tag:media`; nothing from `tag:vm`; three tests. Live policy read back: 3 tags, 2 grants, 3 tests, no `ssh` section (the old Tailscale-SSH "check" rule, unused, is gone). gw path and `check.sh` still fine (gw and the Mini are untagged until Alex tags them, so they still count as his devices).
   - Before: `policy-before-2026-10-04.hujson` (one grant: Alex → all; ssh check rule).
   - Undo: paste that file in the admin console, or delete `tailscale.tf` and apply (`reset_acl_on_destroy` restores Tailscale's default).

9. **DNS switched to Tailscale addresses** (Alex: "switching all the dns"). First a throwaway record `ts-dnstest.lab` → `100.126.136.120` proved the home router's DNS passes `100.x` answers (from g8, gw, hookdeck-ws); removed in the same apply. Then `lab_gateway_ip` → `100.126.136.120` (lab, gw.lab, all `*.lab` wildcards: 8 records) and `mini.lab` → `100.91.137.41`. `hookdeck-ws.lab` and `g8.lab` unchanged (not on the tailnet).
   - Tested by name from the MBP (PIA on): lab 200, jellyfin 302, plex 401, audiobooks 200, pve.g8 200, dozzle.hookdeck-ws 200, all on `100.126.136.120`; `ssh gw`, `ssh mini` (seen as gw), `ssh hookdeck-ws`, `ssh g8` fine. From g8: same pages. Calibre-Web returns 500 on every path, including directly on the Mini (`192.168.1.90:8074`/`:8073`): an existing Calibre-Web problem, not this change.
   - Undo: `lab_gateway_ip = "192.168.1.110"`, `mini.lab` → `192.168.1.90`, `terraform apply`.

10. **Opt-in VM join written** (collielab): `bin/vm-tailnet <name>` (copies the vm-join key to the VM's `/run`, runs `hosts/workspace-vm/tailscale.sh`: install, `tailscale up --auth-key=file:… --advertise-tags=tag:vm --accept-dns=false`, key deleted; then rewrites the VM's DNS record to its `100.x`), `bin/new-vm … --tailscale` calls it. Tested: syntax, the DNS-record rewrite on a scratch copy, refusal without the key. Not run yet: needs the `vm-join` OAuth client. `bin/new-vm` also stopped suggesting `git add -A`.
   - gw `check.sh`: DNS through the router and gw's home address as fallback added; all good.

**Waiting on Alex:** tag gw `tag:gw` and the Mini `tag:media`; create OAuth client `vm-join` (scope auth keys write, tag `tag:vm`) → `ctrl/secrets/tailscale/vm-join.key` + Vaultwarden. Then `bin/vm-tailnet hookdeck-ws`.

11. **Tags, key expiry and vm-join, by Terraform** (the `terraform` OAuth client turned out to have scope `all`). `tailscale_device_tags` gw → `tag:gw`, Mini → `tag:media`; `tailscale_device_key` expiry off for both (tagging alone left `keyExpiryDisabled=false`); `tailscale_oauth_client.vm_join` (scope `auth_keys`, tags `tag:vm`; description must be letters/digits/spaces/hyphens: the first try with `(` `/` failed with a 400). Secret saved to `ctrl/secrets/tailscale/vm-join.key` (600). The Mini is found by its full name `alexs-mac-mini.tail2b958c.ts.net` (its hostname is "alex’s Mac mini"). After: `check.sh` all good, `ssh mini` by name fine, `terraform plan` clean.
   - Undo: remove the resources from `tailscale.tf` and apply (tags come off; expiry back on; the client is deleted).
