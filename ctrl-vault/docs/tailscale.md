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
| Copying GBs between MBP and VM | yes | might be capped by gw's single core; Wi-Fi may be the limit anyway |
| Jellyfin to a TV or phone without the app | yes | probably fine (4K ≈ 40–80 Mbit/s), not measured |

Things to know:

- **Packet size.** Tailscale's tunnel carries packets up to 1280 bytes, the home network 1500. Normally the sender is told and adjusts. If that fails it looks like: small things work, big pages or downloads hang. Fix: one rule on gw ("MSS clamping"). Not tested yet.
- **gw is a single door** for devices without the app: g8 or gw off → their `100.x` names stop. Fallback: `mini.lab.alexluong.com` (`192.168.1.90`) and the other `192.168.1.x` addresses.
- **Everyone at home looks like gw** to the lab machines, so access rules cannot tell your MBP from a guest's phone. Hence: gw may reach only what home devices should reach.
- **Your Mac with the app on skips gw** entirely, even at home. gw matters for the phone, TV, Kobo and guests.

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
- Not yet: Tailscale on hookdeck-ws (T3 test), the router rule, names moved to `100.x`, access rules, making gw's settings permanent, key expiry off, packet-size and speed tests.
