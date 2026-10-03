# TASK-9 design: Tailscale for the lab (to explore, 2026-10-03)

From a discussion with Alex. **Nothing is built or installed.** The direction below is the one Alex likes ("i like that option"); it is to be proven, not decided. Plain explainer of how it works: `docs/tailscale.md`. Background: `docs/home-systems.md` (network, names), `docs/fleet.md` (machines, rules), `collielab/hosts/gw/` (the gateway).

## What Alex wants

- As seamless as possible "from t3 dev tool to internal hosted apps to the services like plex jellyfin": the same URL, the same `ssh hookdeck-ws`, the same T3 environment at home and away.
- "tailscale on each is fine but i dont want tailscale to connect": installing Tailscale on machines is fine; his Mac and phone should not have to be connected to it at home.
- Routes "that public router cannot intercept": lab addresses a foreign network does not answer for.
- Asked for: the iPhone on home Wi-Fi being "just part of the tailscale network" with no app.
- Standing rules: stay on `192.168.1.x` at home for now (`192.168.77.x` was discussed, deferred); never factory-reset the Viettel router; a VM holds no access to the host or other machines; no secrets in git.

## Direction to explore ("option 2"): one address set, the router sends 100.x to the gateway

```
                         INTERNET
                            │
                   ┌────────┴────────┐
                   │  Viettel router │  192.168.1.1
                   │  + ONE RULE:    │
                   │  100.x → .110   │
                   └────────┬────────┘
        home network 192.168.1.x (wifi + cable)
   ┌──────────┬─────────────┼──────────────┬──────────────┐
 iPhone      TV      ┌──────┴──────┐  ┌────┴─────┐   ┌────┴────┐
 MBP        Kobo     │  gateway    │  │hookdeck- │   │  Mini   │
 (no app             │  .110       │  │ws  .101  │   │  .90    │
  needed)            │  Tailscale  │  │Tailscale │   │Tailscale│
                     └──────┬──────┘  └────┬─────┘   └────┬────┘
                            └──── Tailscale network ──────┘
```

- Every lab machine (gateway, each workspace VM, the Mini) is on the tailnet with its own `100.x` address.
- All names point at Tailscale addresses: `hookdeck-ws.lab…` → the VM's; `*.hookdeck-ws.lab…`, `*.g8.lab…`, media names → the gateway's (Caddy). Public DNS records carrying `100.x` values (DNS-only, as today).
- The home router gets one static route: the tailnet's range → `192.168.1.110`. The gateway forwards home-network traffic into Tailscale (IP forwarding + masquerade out of `tailscale0`).

| Situation | Path | Result |
|---|---|---|
| At home, no app (phone, TV, Mac with Tailscale off) | device → router → gateway → Tailscale → machine | works, one extra hop |
| Tailscale app on (home or away) | device → machine, encrypted, direct | works |
| Away, app off | no route for `100.x` | fails (see § Trap) |

## What has to be true (check in this order)

1. **The gateway container can run Tailscale.** `gw` is LXC 110 on g8: needs `/dev/net/tun` passed in (container config on g8) or Tailscale's userspace mode. Touches `gw`: coordinate with the TASK-3 session.
2. **Forwarding works** (prove without the router): Tailscale on `gw` and on `hookdeck-ws`; on the MBP, Tailscale off, add the route by hand (`sudo route add -net <range> 192.168.1.110`, gone at reboot); test `ssh`, T3, a gateway web page. Tailscale's own firewall rules on `gw` may need a masquerade rule added for LAN → `tailscale0`; the documented setups are "subnet router" and "site-to-site", this is the reverse direction, so expect to adjust.
3. **The Viettel router (ZTE F6601P) accepts a static route** and sends matching traffic back into the home network. Unknown. Read its routing page first; the change itself is Alex's or on his say-so.
4. **Range of the route.** Tailnet addresses are spread over `100.64.0.0/10`. Viettel's visible hops do not use that range (traceroute 2026-10-03: `125.235.x`, `10.255.x`, `27.68.x`; not proof). Narrower is safer: Tailscale's "IP pool" setting can keep our nodes in one small block (to verify it exists on this plan), else one route per machine (a router change per VM, which Alex does not want).
5. **iPhone behaviour** with and without the app, on home Wi-Fi and on cellular.

### Results so far (2026-10-03; steps and undo in `log.md`)

- **Check 1: passed.** `pct set 110 --dev0 /dev/net/tun` gave the running container the device with no restart. Tailscale 1.102.4 runs in `gw` with the normal kernel interface; `gw` = `100.126.136.120`. Userspace mode would not have worked for this design (no interface to forward into).
- **Check 2: passed for ssh and web, target = the Mini** (already on the tailnet, so no test VM was needed). MBP without Tailscale + `route add -net 100.64.0.0/10 192.168.1.110`: ping, `ssh` to the Mini's `100.x` (pinned host key accepted; the Mini sees the connection as coming from `gw`'s `100.x`), Jellyfin on the Mini's `100.x`, and `https://lab.alexluong.com` / `https://jellyfin.lab…` on `gw`'s `100.x` with a valid certificate. On `gw` it took `net.ipv4.ip_forward=1` plus one masquerade rule of our own (`ip saddr 192.168.1.0/24 oifname tailscale0 masquerade`); Tailscale's own rules already accept the forwarded packets. Both are runtime only so far.
- **Check 3: passed (2026-10-04).** The ZTE has Local Network → Routing → Static Routing with egress `LAN`; entry `100.64.0.0` / `255.192.0.0` → `192.168.1.110`. From g8 and the MBP (no Tailscale): router → gw → Mini; ping, ssh, Jellyfin, lab page; 100MB over ssh ~200 Mbit/s. The one-sided path (reply skips the router) is not a problem on this router; no packet-size problem seen.
- **Check 4: the full `/10` is fine on this router** (its routing table has nothing in `100.64.0.0/10`). Narrower block not needed for now.
- **New: devices with a full VPN** send `100.x` into the VPN. The MBP's PIA got a split-tunnel exception for `100.64.0.0/10`. Every such device needs one (or the Tailscale app).
- **Check 5, at home: passed.** iPhone on home Wi-Fi, app off, opens Jellyfin on the Mini's `100.x`. Away with the app on: still to try.
- **Not yet:** T3 (needs Tailscale on `hookdeck-ws`), phone away with the app, making the `gw` settings permanent, key expiry off on servers.

## Weak points

- At home the gateway is the door for every device without the app. g8 off → names stop for them. Keep `mini.lab` → `192.168.1.90` as the emergency way in.
- The router rule can disappear after a provider firmware update or reset: devices with the app keep working, the rest fail until it is re-added. Record the rule in `home-systems.md`.
- Home devices arrive on the tailnet "as the gateway": access rules must let the gateway reach the VMs and the Mini and nothing else, and VMs must be reachable but unable to start connections to other machines.
- New connections depend on Tailscale's service; servers need key expiry off.
- Every device on home Wi-Fi still reaches lab pages (as today): Dozzle and Isaiah run with no login, actions and shell on. Put one login at the gateway in front of sensitive pages and close the VM's direct ports.

## Trap (Alex: "is there any concern that someone may trap us?")

Away with the app off, a hostile network can answer for any address, `100.x` included. By accident it is very unlikely with `100.x` (common with `192.168.1.x`); on purpose it stays possible. What catches it: SSH host keys pinned in `collielab/ssh/known_hosts` (an impostor is refused; logins are by key, never a password) and HTTPS certificates only the gateway holds. Unprotected: plain `http://` by port, and clicking through a certificate warning. With the app on, nothing on the path can intercept.

Hardening list (none done):
1. Only `https` gateway URLs in apps and bookmarks, never address-and-port.
2. HSTS on the gateway (not set in `hosts/gw/Caddyfile` today).
3. Login at the gateway for sensitive pages.
4. Tailscale access rules; other people's devices get media only.
5. `StrictHostKeyChecking yes` for the fleet hosts in `collielab/ssh/config` (default "ask" today).
6. Guest Wi-Fi separated, if the router can.
7. Two-factor on the account that owns the tailnet.

## Fallbacks (same Tailscale installs, so nothing is wasted)

- **Option 1, two addresses picked automatically:** names keep home addresses in public DNS; with the app connected, Tailscale's DNS answers our names with Tailscale addresses (needs a small DNS responder on the gateway) and an SSH `Match … exec` rule picks the Tailscale address. The apps' "VPN On Demand" (connect except on the home Wi-Fi; from memory, check the current app) makes the phone and Mac switch by themselves. Needs nothing from the router.
- **Forwarding node only (subnet router):** the gateway announces only our blocks (`192.168.1.100–.149`, `.90`) as narrow routes so they win over a café's `192.168.1.0/24`. Nothing on the VMs. Away with the app off, traffic goes to the foreign network.
- Rejected: a second name set `*.ts.alexluong.com` (the earlier proposal in `home-systems.md`): two URLs per service, and it does not cover SSH.
- Deferred: renumbering home to `192.168.77.x`.

## State today (checked 2026-10-03)

- Tailnet of account `lhtanh98@` (Alex to confirm it is the one to use): `alexs-mac-mini` `100.91.137.41` online (Tailscale 1.92.3); `iphone-15-pro` offline 70 days; `67ee56ee4fc5` (linux) and `poc-client` (macOS) offline 230+ days: candidates to remove.
- Tailscale is not installed on the MBP, g8, `gw` or `hookdeck-ws`.
- `bin/new-vm` would join new VMs automatically with a key kept in `ctrl/secrets/` (to design: tagged, reusable or one-off).

## Open for Alex

1. Which tailnet/account; who else is on it (Hannah's devices: media only?).
2. OK to add a static route on the router once the Mac-only proof works?
3. Media names: also through the gateway's Tailscale address (one address set for everything), with `mini.lab` as the fallback?
