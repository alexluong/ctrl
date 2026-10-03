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

**Phone away from home:** the Tailscale app must be on; nothing else routes `100.x` there. iOS runs one VPN at a time (PIA on = Tailscale off). The iOS app's "VPN On Demand" can switch it on whenever you are not on home Wi-Fi (from memory; check the current app).
| `gw` | container 110 on g8; Caddy (web pages) **and** the door into the tailnet for home devices without the app | home `192.168.1.110`, tailnet `100.126.136.120` |
| Router rule (planned) | one static route on the Viettel router: "`100.64.0.0/10` → `192.168.1.110`" | — |

`100.64.0.0/10` = every address from `100.64.0.0` to `100.127.255.255`, the range Tailscale picks addresses from. Mask form: `255.192.0.0`.

## End state: names point at `100.x` addresses

`ssh hookdeck-ws` → `hookdeck-ws.lab.alexluong.com` → public DNS answers with hookdeck-ws's `100.x`. Web names (`*.lab…`) answer with gw's `100.x` (Caddy). The same answer at home and away; what changes is **who carries the packet** there. **Done 2026-10-04** for gw's names (`lab`, `gw.lab`, every `*.lab` wildcard → `100.126.136.120`) and `mini.lab` (→ `100.91.137.41`). `hookdeck-ws.lab` moves when hookdeck-ws joins; `g8.lab` stays `192.168.1.100` (g8 is not on the tailnet; its web UI `pve.g8.lab` goes through gw and works everywhere). Home addresses still work by address as the fallback.

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

**If a big transfer ever feels slow** (GBs between the MBP and a VM; not needed so far), three ways around gw, easiest first:

1. **Turn the Tailscale app on** on the MBP: it goes straight to the machine (direct over the home network at home), gw is skipped. Same names, nothing else to change.
2. **Use the home address directly**, at home only: `scp alex@192.168.1.101:file .` (hookdeck-ws), `192.168.1.90` (Mini). `192.168.1.x` never touches gw or Tailscale. Addresses: `home-systems.md`.
3. **Give gw more CPU**: `ssh g8 pct set 110 --cores 2` (live, no restart). Only if gw is the measured bottleneck (`ssh gw top` during the copy).

Measured 2026-10-04 for reference: ~200 Mbit/s through gw vs ~230–270 direct, to the Mini on Wi-Fi; gw almost idle, so Wi-Fi is the real limit today.

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

### 2. gw: Tailscale, forwarding and masquerade

**Permanent and automated since 2026-10-04**: `collielab/hosts/gw/tailnet.sh` (safe to re-run) sets it all up; it survives restarts (tested). gw's full map, rebuild steps and traps: `collielab/hosts/gw/README.md`. **Health check for the whole chain** (container, Tailscale, forwarding, masquerade, Caddy, router route, MBP route): `collielab/hosts/gw/check.sh` from the MBP, changes nothing.

| | |
|---|---|
| tun device | `dev0: /dev/net/tun` in container 110's config on g8 (`create.sh`) |
| Tailscale | joined as `gw`, `100.126.136.120`, `--accept-dns=false` |
| Forwarding | `/etc/sysctl.d/90-gw-tailnet.conf`: `net.ipv4.ip_forward = 1` |
| Masquerade | `/etc/gw-tailnet.nft`, table `ip gw_tailnet`: `ip saddr 192.168.1.0/24 oifname "tailscale0" masquerade`; loaded at boot by `gw-tailnet.service` |
| Debian's `nftables` service | disabled on purpose |

**Firewall rules on gw, and the one trap.** gw's firewall (nftables) holds Tailscale's own rules (`ts-input`, `ts-forward`, `ts-postrouting`: accept tailnet traffic, drop packets faking a `100.x` sender from the home network) and our masquerade, each in their own place. Debian's `nftables` service starts and stops with "flush ruleset", which erases all of them; it only ever loaded an allow-everything file, so it is disabled. Never re-enable or restart it. If rules get wiped anyway: `ssh gw systemctl restart tailscaled gw-tailnet`.

If the home range changes from `192.168.1.0/24`: re-run `tailnet.sh` with `HOME_NET=<range>`, and fix the router route (§ 1).

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
| `alexs-mac-mini` (`tag:media`) | `100.91.137.41` | Tailscale app | off (Terraform) |
| `gw` (`tag:gw`) | `100.126.136.120` | `tailscale up --accept-dns=false --hostname=gw` | off (Terraform) |
| `iphone-15-pro` | `100.122.122.29` | app (Alex's login) | normal |
| `hookdeck-ws` (`tag:vm`) | `100.113.20.22` | `collielab/bin/vm-tailnet hookdeck-ws` (2026-10-04) | off (tagged at join) |

**New workspace VM: opt-in.** `bin/new-vm … --tailscale` in collielab (or `bin/vm-tailnet <name>` for an existing VM) installs Tailscale in the VM, joins it as `tag:vm` with the `vm-join` key (`ctrl/secrets/tailscale/vm-join.key`; that OAuth client can only add `tag:vm` machines), and points `<name>.lab.alexluong.com` at its `100.x`. Then `terraform apply` and commit (printed by the script). No restart, the VM keeps its home address. Without the flag the VM is home-only, as before.

### 4b. Access rules (Tailscale policy)

Who may reach whom on the tailnet. **Owned by Terraform**: `collielab/terraform/tailscale.tf` (applied 2026-10-04); edits in the admin console get overwritten. Credentials: OAuth client `terraform` (scope: **all**, created by Alex; it can do anything on the tailnet, so it stays on the MBP only) in `collielab/terraform/.env` (`TF_VAR_tailscale_oauth_client_id/_secret`), copy in Vaultwarden. Policy before the change: `../work/task-9/policy-before-2026-10-04.hujson`.

In plain words:

1. **You can reach everything.** Devices logged in as you (MBP, phone).
2. **The house can reach the lab.** Home devices without the app arrive as gw, which may reach the VMs (`tag:vm`) and the Mini (`tag:media`), nothing else.
3. **VMs can't knock on anyone's door.** `tag:vm` may answer but not start a connection to anything on the tailnet.

Everything else is blocked. The policy has **tests** (Tailscale rejects a change that breaks the three rules). **Need more?** Add a narrow grant (one source, one destination, one port) in `tailscale.tf` with the reason, e.g. `{"src": ["tag:enable-ws"], "dst": ["tag:hookdeck-ws"], "ip": ["tcp:5432"]}` (each VM gets its own tag only when a rule needs it). Hannah's devices later: a media-only grant.

Labels: tagged machines belong to the tag, not to your login. gw → `tag:gw`, Mini → `tag:media`, set by Terraform (`tailscale_device_tags`), with key expiry off (`tailscale_device_key`: tagging an already-joined machine did not switch it off by itself). VMs get `tag:vm` when they join, which is enough for a new machine.

**The vm-join key** is an OAuth client Terraform created (`tailscale_oauth_client.vm_join`: scope auth keys, tag `tag:vm` only). Its secret: `terraform output -raw tailscale_vm_join_key > ~/workspaces/ctrl/secrets/tailscale/vm-join.key` (done 2026-10-04; the MBP has it). New machine: run that line again; nothing to create.

The policy covers `100.x` traffic only. On the home network (`192.168.1.x`) a VM can still reach other machines by address; closing that = Proxmox firewall per VM (`design.md` hardening #8).

A node that is removed and re-added gets a **new** `100.x`: update DNS and anything that has the address typed in.

### 5. DNS: names point at Tailscale addresses (done 2026-10-04)

| Name | Address | Where in collielab |
|---|---|---|
| `lab`, `gw.lab`, `*.lab`, `*.mini.lab`, `*.g8.lab`, `*.hookdeck-ws.lab`, `*.calibre.lab`, `*.calibre.mini.lab` | gw `100.126.136.120` | `terraform/lab_gateway.tf`, `local.lab_gateway_ip` (one value) |
| `mini.lab` | Mini `100.91.137.41` | `terraform/alexluong_com.tf` |
| `hookdeck-ws.lab` | hookdeck-ws `100.113.20.22` | same; written by `bin/vm-tailnet` |
| `g8.lab` | `192.168.1.100` (g8 not on the tailnet) | same |

Public DNS records, DNS-only. Checked: the home router's DNS passes `100.x` answers through (some routers filter them; this one does not). gw's Caddy still reaches its backends by home address (`/etc/hosts` on gw), so nothing behind the gateway changed.

**Fallback when something in the chain is down** (gw, router rule, Tailscale): the home addresses, `192.168.1.90` (Mini, `:8096` Jellyfin…), `192.168.1.110` (gw), `192.168.1.101` (hookdeck-ws), `192.168.1.100` (g8). `ssh alex@192.168.1.90`, `ssh root@192.168.1.110` work at home. Kobos and TV apps still use `192.168.1.90` directly, so they never depended on this.

**Back to home-only, everything at once:** set `lab_gateway_ip = "192.168.1.110"` and `mini.lab` → `192.168.1.90`, `terraform apply`.

**Who can lose these names:** any home device with a full VPN on and no `100.64.0.0/10` exception (§ 3), e.g. Hannah's PC or iPad if they run one. Fix there, or the Tailscale app.

### When something changes: checklist

| Change | Do |
|---|---|
| New or reset router | re-add § 1; test from g8 |
| gw or g8 restarted | nothing; comes back by itself. Confirm with `collielab/hosts/gw/check.sh` |
| gw rebuilt | rebuild steps in `collielab/hosts/gw/README.md`; it gets a new `100.x`: update DNS and `check.sh` |
| New VPN app on a device, or PIA reinstalled/reset | § 3 on that device |
| New lab machine or VM | VM: `bin/new-vm … --tailscale` or `bin/vm-tailnet <name>` (§ 4); other machines: join with a tag, DNS record → its `100.x` |
| A VM needs to reach another machine on the tailnet | narrow grant in `collielab/terraform/tailscale.tf` (§ 4b) |
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

- 2026-10-03: gw has the tun device and Tailscale (`100.126.136.120`).
- 2026-10-04: forwarding and masquerade made permanent (`collielab/hosts/gw/tailnet.sh`), restart-tested; `check.sh` all good.
- Proven from the MBP with no Tailscale and a hand-added route: ping, ssh, Jellyfin on the Mini's `100.x`; lab pages on gw's `100.x` with a valid certificate.
- 2026-10-04: PIA on the MBP lets `100.64.0.0/10` bypass the VPN. Router static route added (`100.64.0.0/255.192.0.0` → `192.168.1.110`, egress LAN). From g8 and the MBP, no Tailscale on either: traceroute router → gw → Mini; ping, ssh, Jellyfin, lab page all work; 100MB over ssh ~200 Mbit/s through gw vs ~230–270 direct (the Mini is on Wi-Fi). The router does not mind the reply skipping it, and large packets get through (no packet-size problem seen).
- 2026-10-04: iPhone on home Wi-Fi with the app off opens Jellyfin on the Mini's `100.x`. Away with the app on: assumed to work (plain Tailscale), Alex to confirm.
- 2026-10-04: access rules applied by Terraform (§ 4b). DNS switched: gw's names and `mini.lab` → `100.x` (§ 5); tested by name from the MBP and g8 (lab pages, Jellyfin, Plex, Audiobookshelf, Proxmox, Dozzle; `ssh gw`, `ssh mini`). `bin/vm-tailnet` and `bin/new-vm --tailscale` written (opt-in join).
- 2026-10-04: Terraform tagged gw and the Mini, turned their key expiry off, and created the vm-join client; its secret is in `ctrl/secrets/tailscale/vm-join.key`. `check.sh` all good after tagging.
- 2026-10-04: hookdeck-ws joined (`100.113.20.22`, `tag:vm`), name moved. From the MBP with no Tailscale: router → gw → VM, ssh, T3 through the ssh tunnel, its ports; Dozzle through gw. The VM cannot reach the Mini or gw over the tailnet. Docker unaffected.
- `bin/new-vm` also adds a new VM's `*.<vm>.lab` gateway record and gw's backend entry, so its web pages need only Caddyfile lines.
