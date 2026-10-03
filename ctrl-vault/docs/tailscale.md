# Tailscale and the gateway: how lab access works (explainer)

Written for Alex to come back to (2026-10-04). Plain explanation of the setup from TASK-9, with the real addresses. What has actually been built and tested: § Current state. Design, checks and fallbacks: `../work/task-9/design.md`. Every change with its undo: `../work/task-9/log.md`. Network map: `home-systems.md`.

## The goal

Same name, same address, everywhere: `ssh hookdeck-ws`, T3, `https://jellyfin.lab.alexluong.com` work at home (phone, TV, Mac, no app needed) and away (app on).

## The pieces

| Thing | What it is | Address |
|---|---|---|
| Tailscale | a private network ("tailnet") between our machines, encrypted, works across the internet | each node gets a `100.x` address |
| Tailnet | `lhtanh98@gmail.com`, suffix `tail2b958c.ts.net` | admin: https://login.tailscale.com/admin/machines |
| Node | a machine running Tailscale | Mini `100.91.137.41`, gw `100.126.136.120`, phone `100.122.122.29`; hookdeck-ws not yet |
| `gw` | container 110 on g8; Caddy (web pages) **and** the door into the tailnet for home devices without the app | home `192.168.1.110`, tailnet `100.126.136.120` |
| Router rule (planned) | one static route on the Viettel router: "`100.64.0.0/10` → `192.168.1.110`" | — |

`100.64.0.0/10` = every address from `100.64.0.0` to `100.127.255.255`, the range Tailscale picks addresses from. Mask form: `255.192.0.0`.

## End state: names point at `100.x` addresses

`ssh hookdeck-ws` → `hookdeck-ws.lab.alexluong.com` → public DNS answers with hookdeck-ws's `100.x`. Web names (`*.lab…`) answer with gw's `100.x` (Caddy). The same answer at home and away; what changes is **who carries the packet** there. (Today DNS still has the `192.168.1.x` addresses; names move only after the router rule works.)

## The three cases

**1. At home, Tailscale app off** (phone, TV, Kobo, a Mac without the app)

```
device ──► router ──► gw ══Tailscale══► hookdeck-ws
   ◄──────────────── gw ◄══════════════┘    (the reply skips the router)
```

1. The device's own routing table only knows "`192.168.1.x` = on my Wi-Fi, deliver directly" and "everything else = send to the router". `100.x` is "everything else", so it goes to the router.
2. Normally the router sends unknown addresses to the internet, where `100.x` dies. The one rule makes it hand them to gw instead.
3. gw passes the packet into Tailscale; Tailscale encrypts it and sends it to hookdeck-ws.
4. The reply goes back to gw, which sends it straight to the device.

**2. Tailscale app on** (at home or in a café)

```
device ══Tailscale, encrypted══► hookdeck-ws
```

The app adds its own routes for `100.x`, so the device encrypts and sends directly. gw is not involved (except for web pages, which live on gw). A café network sees only encrypted traffic.

**3. Away, app off**: the café router has no idea what `100.x` is; nothing connects. Possible trap (a hostile network answering for `100.x`) and what catches it: `design.md` § Trap.

## What gw does, exactly

Three pieces. None of them is a proxy; nothing in the apps needs a setting.

| Piece | What it is | Job |
|---|---|---|
| `tailscaled` | the Tailscale service | makes gw a node: `tailscale0` interface, keys, the encrypted tunnel to each node |
| `net.ipv4.ip_forward=1` | Linux kernel setting (not ssh, not Tailscale) | lets the kernel pass on packets addressed to someone else instead of dropping them = makes gw a router |
| masquerade rule (`nft`, Linux's firewall) | NAT, the same trick the Viettel router does for the whole house toward the internet | rewrites the sender `192.168.1.x` → gw's `100.x`, because tailnet nodes only accept packets from tailnet addresses |

Being a Tailscale node alone is not enough: a normal node only sends and receives its own traffic. The two kernel settings turn it into a router for other devices.

**Router vs proxy.** A proxy ends your connection and opens a new one (apps must be told to use it). A router passes packets through. So the ssh session runs end to end MBP ↔ hookdeck-ws: the host key and ssh encryption are hookdeck-ws's own, gw cannot read it. Only the sender address is rewritten. Any protocol works.

**Two jobs in one container, independent:** Caddy (a *reverse* proxy: ends HTTPS with its certificate, opens a new connection to Jellyfin etc.) and the router (kernel + `tailscaled`). Restarting one does not touch the other; both stop when gw or g8 is off.

## What `tailscaled` does

| Job | Meaning |
|---|---|
| Identity | logs in to Tailscale's coordination service, gets the `100.x`, keeps the list of nodes with their keys and real addresses (how it "sees the others") |
| Interface | creates `tailscale0`, adds routes (`100.x` → `tailscale0`, routing table 52) and firewall chains (`ts-input`, `ts-forward`) |
| Encryption | WireGuard: every packet encrypted for the receiving node |
| Finding a path | direct if possible, even through routers on both sides (hole punching); else through Tailscale's relays (DERP), still encrypted |
| Access rules | drops what the tailnet policy does not allow (today: allow all; to be tightened) |
| Key renewal | node keys expire (180 days) unless expiry is turned off; to do for servers |

The coordination service hands out keys and addresses only; traffic goes node to node (or through a relay that cannot decrypt it).

## A packet from gw to hookdeck-ws, two layers

Tailscale wraps the real packet inside an ordinary encrypted UDP packet that crosses the same home Wi-Fi and cables as always:

| Layer | From | To |
|---|---|---|
| inner (what ssh sees) | `100.126.136.120` (gw) | hookdeck-ws's `100.x` |
| outer (what the network carries) | `192.168.1.110:41641` | `192.168.1.101:41641`, encrypted |

Seen live: `tailscale ping` from gw to the Mini answered `via 192.168.1.90:41641`.

## Does it slow anything down?

Normal dev work: no. Only traffic between your device and the VM passes gw; the VM's own internet traffic (git, npm, Docker pulls, Claude API) goes straight out.

| Workload | Through gw? | Feel |
|---|---|---|
| ssh, T3, editor over ssh, dev server in the browser | yes | no difference (measured +1–3 ms) |
| git / npm / Docker / API calls on the VM | no | unchanged |
| Copying GBs between MBP and VM | yes | measured ~200 Mbit/s through gw vs ~230–270 direct (to the Mini on Wi-Fi), gw nearly idle |
| Jellyfin to a TV or phone without the app | yes | probably fine (4K ≈ 40–80 Mbit/s), not measured |

Things to know:

- **Packet size.** Tailscale's tunnel carries packets up to 1280 bytes, the home network 1500. Normally the sender is told and adjusts. If that fails it looks like: small things work, big pages or downloads hang. Fix: one rule on gw ("MSS clamping"). Not tested yet.
- **gw is a single door** for devices without the app: g8 or gw off → their `100.x` names stop. Fallback: `mini.lab.alexluong.com` (`192.168.1.90`) and the other `192.168.1.x` addresses.
- **Everyone at home looks like gw** to the lab machines, so access rules cannot tell your MBP from a guest's phone. Hence: gw may reach only what home devices should reach.
- **Your Mac with the app on skips gw** entirely, even at home. gw matters for the phone, TV, Kobo and guests.
- **A device with a full VPN on (the MBP runs Private Internet Access) sends `100.x` into the VPN**, never to the router, so the router rule does not help it. Turn the VPN off, add a split-tunnel exception for `100.64.0.0/10` in the VPN app, or use the Tailscale app. Check with `route -n get 100.91.137.41`: `utun…` with a `10.x` gateway = the VPN.

## Every setting this depends on (re-apply after a change)

Each piece below lives on a different box and can be lost independently. If `100.x` names stop working for some devices, walk this list. Status as of 2026-10-04; history in `../work/task-9/log.md`.

### 1. Router: static route (Viettel ZTE F6601P)

| | |
|---|---|
| Where | `https://192.168.1.1` (login in Vaultwarden) → Local Network → Routing → IPv4 → Static Routing → Create New Item |
| Name | `tailscale` |
| Egress | `LAN` (not `omci_ipv4_pppoe_1` = internet, not `omci_ipv4_dhcp_3` = Viettel's second connection) |
| Network Address | `100.64.0.0` |
| Subnet Mask | `255.192.0.0` (= `/10`, every Tailscale address) |
| Gateway | `192.168.1.110` (gw) |
| Undo | trash icon on the entry, Apply |
| Status | **added by Alex 2026-10-04, verified** (from g8 and the MBP: router → gw → Mini, ssh, Jellyfin, lab page; 100MB over ssh at ~200 Mbit/s) |

Lost by: a factory reset (never do it, see `home-systems.md`), possibly a Viettel firmware update or a router swap. Symptom: devices *without* the app lose `100.x`; devices with the app are fine. Check from g8 (a home machine with no Tailscale and no VPN): `ssh g8 traceroute -n -m 4 100.91.137.41` must show `192.168.1.1`, then `192.168.1.110`, then the Mini. Hops like `125.235.x` / `10.255.x` = the rule is gone and traffic goes to Viettel.

New router (any brand): the same four values. Look for "Static route(s)", interface/egress = LAN. If it has no such page: fallbacks in `../work/task-9/design.md`.

### 2. gw: forwarding and masquerade

| | |
|---|---|
| Forwarding | `net.ipv4.ip_forward=1` |
| Masquerade | nftables table `ip task9`, chain `post` (nat, postrouting), rule `ip saddr 192.168.1.0/24 oifname "tailscale0" masquerade` |
| Status | **runtime only: lost when gw or g8 restarts.** To be made permanent (a file in `collielab/hosts/gw/`) |
| Re-apply by hand | `ssh gw 'sysctl -w net.ipv4.ip_forward=1; nft add table ip task9; nft "add chain ip task9 post { type nat hook postrouting priority 100; }"; nft add rule ip task9 post ip saddr 192.168.1.0/24 oifname tailscale0 counter masquerade'` |
| Check | `ssh gw 'sysctl -n net.ipv4.ip_forward; nft list table ip task9'` |

Also on gw: the tun device (`dev0: /dev/net/tun` in container 110's config on g8; in `collielab/hosts/gw/create.sh`) and Tailscale itself (`tailscale up --accept-dns=false --hostname=gw`). A rebuild of gw needs both again plus the two settings above. If the home range ever changes from `192.168.1.0/24`, change it in the masquerade rule too.

### 3. Each device with a full VPN: exception for `100.64.0.0/10`

A VPN that takes all traffic also takes `100.x`, so the router rule never sees it. Each such device needs `100.64.0.0/10` excluded from the VPN.

**MBP, Private Internet Access** (done 2026-10-04, PIA 3.5.7):

| | |
|---|---|
| In the app | Settings → Split Tunnel: on; Add IP Address `100.64.0.0/10` → Bypass VPN |
| By command | `"/Applications/Private Internet Access.app/Contents/MacOS/piactl" -u applysettings '{"splitTunnelEnabled":true,"bypassSubnets":[{"mode":"exclude","subnet":"100.64.0.0/10"}]}'` |
| Read settings | `piactl -u dump daemon-settings` (fields `splitTunnelEnabled`, `bypassSubnets`, `allowLAN`) |
| Undo | `piactl -u applysettings '{"splitTunnelEnabled":false,"bypassSubnets":[]}'` |
| Check | `route -n get 100.91.137.41` → `interface: en0`, `gateway: 192.168.1.1` (router). `utun…` = still in the VPN |

`piactl` lives at `/Applications/Private Internet Access.app/Contents/MacOS/piactl`. Its normal `set` command does not cover split tunnel; `-u` (unstable) does, and PIA may change it between versions. If a PIA update or reset drops it, use the app's page.

`allowLAN` (on) is what keeps `192.168.1.x` outside PIA; it does not cover `100.x`.

Another VPN app (WARP, Mullvad, a work VPN, …): look for "split tunnel", "excluded routes" or "bypass" and add `100.64.0.0/10`. Cloudflare WARP on the MBP is installed but disconnected (2026-10-04); if it is turned on it needs the same exception (WARP: Settings → Split Tunnels, exclude mode). A phone with a VPN app: same idea, or just use the Tailscale app.

### 4. Tailscale on each lab machine

| Node | Address | Joined with | Key expiry |
|---|---|---|---|
| `alexs-mac-mini` | `100.91.137.41` | Tailscale app | default (to turn off) |
| `gw` | `100.126.136.120` | `tailscale up --accept-dns=false --hostname=gw` | default (to turn off) |
| `hookdeck-ws` | — | not yet | |

A node that is removed and re-added gets a **new** `100.x`: update DNS and anything that has the address typed in.

### 5. DNS (not done yet)

Names will point at `100.x` (collielab `terraform/`). Until then they still give `192.168.1.x`, and everything works as before.

### When something changes: checklist

| Change | Do |
|---|---|
| New or reset router | re-add § 1; test from g8 |
| gw or g8 restarted | § 2 (until it is permanent) |
| gw rebuilt | § 2 plus tun device and Tailscale join; check its `100.x` is the same, else update DNS |
| New VPN app on a device, or PIA reinstalled/reset | § 3 on that device |
| New lab machine or VM | join Tailscale; DNS record → its `100.x` |
| Home range changes | masquerade rule in § 2, router gateway address in § 1 |
| A device can't reach `100.x` at home | `route -n get <100.x>` on it (Mac): `utun…` = VPN (§ 3), `192.168.1.1` = router → then test from g8 (§ 1, § 2) |

## Checking things (commands)

| Question | Command |
|---|---|
| Who is on the tailnet | `ssh gw tailscale status` |
| Can gw reach a node, and how (direct or relay) | `ssh gw tailscale ping <100.x>` |
| Is forwarding on | `ssh gw sysctl net.ipv4.ip_forward` (1 = on) |
| The masquerade rule and its hit counter | `ssh gw nft list table ip task9` |
| Where the MBP sends a `100.x` packet | `route -n get 100.91.137.41` (gateway `192.168.1.110` = via gw; `utun…` = Tailscale app; `192.168.1.1` = router) |
| The path, hop by hop | `traceroute -n 100.91.137.41` |
| Hand-added route on the MBP (test only, gone at reboot) | add `sudo route add -net 100.64.0.0/10 192.168.1.110`, remove `sudo route delete -net 100.64.0.0/10` |

## Current state

See `../work/task-9/log.md` for the details and undo of each change.

- 2026-10-03: gw has the tun device and Tailscale (`100.126.136.120`). Forwarding and the masquerade rule are on but **runtime only** (gone if gw restarts).
- Proven from the MBP with no Tailscale and a hand-added route: ping, ssh, Jellyfin on the Mini's `100.x`; lab pages on gw's `100.x` with a valid certificate.
- 2026-10-04: PIA on the MBP lets `100.64.0.0/10` bypass the VPN. Router static route added (`100.64.0.0/255.192.0.0` → `192.168.1.110`, egress LAN). From g8 and the MBP, no Tailscale on either: traceroute router → gw → Mini; ping, ssh, Jellyfin, lab page all work; 100MB over ssh ~200 Mbit/s through gw vs ~230–270 direct (the Mini is on Wi-Fi). The router does not mind the reply skipping it, and large packets get through (no packet-size problem seen).
- Not yet: Tailscale on hookdeck-ws (T3 test), phone test, names moved to `100.x`, access rules, making gw's settings permanent, key expiry off.
