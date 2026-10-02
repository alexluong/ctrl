# Home network context (handoff from earlier chats)

Pasted by Alex 2026-10-02; compiled from past Claude chats (Jan to Sep 2026), kept as written. The current, checked picture is `home-systems.md`: where the two differ, that file wins.

Treat anything marked "unverified" as something to check against the live router before relying on it.

## Hardware

- ISP: Viettel fiber, Ho Chi Minh City
- Router/ONT: Viettel F6601P (ZTE-based GPON ONT, acts as router, DHCP server and wifi AP)
- Sits in a closed cabinet alongside an HP G8 mini PC
- LAN subnet: 192.168.1.0/24
- Wifi SSID: "Dunder Mifflin"
- Admin UI: web login on the gateway (likely http://192.168.1.1, unverified). Credentials are not in these notes. Defaults did not work at first, Alex got in on his own.

## Router admin UI notes

- Top nav has "Local Network" and "Management & Diagnosis"
- DHCP bindings live under Local Network > LAN > DHCP, in a "DHCP Binding" section at the bottom of the page. Fill name, MAC, IP, hit Apply, then "Create New Item" for the next one.
- The same page shows the allocated address list with hostnames, MACs and IPs. It includes stale historical leases, so the same MAC can show up more than once.
- Factory reset wipes the PPPoE/fiber config and kills internet until Viettel reprovisions. Avoid. Viettel support: 18008119.

## IP scheme

- .80 to .89: boards and DIY devices
- .90 to .99: consumer devices
- Everything else: dynamic DHCP

Pre-binding dynamic leases were up in the .215 to .226 range, so the pool appears to overlap the .80 to .99 block. Bindings protect the reserved IPs, but the actual pool range was never checked (unverified).

## DHCP bindings

| Device | Interface | MAC | IP | Status |
|---|---|---|---|---|
| ESP32 (hostname esp32-978698) | wifi | f0:24:f9:97:86:98 | 192.168.1.80 | Planned, not confirmed created |
| Mac Mini M4 | wifi (en1) | 1c:f6:4c:48:61:cd | 192.168.1.90 | Created |
| MacBook Pro | wifi (en0) | f8:4d:89:5f:c9:81 | 192.168.1.91 | Created |
| Kobo 1 | wifi | a4:3c:d7:3a:65:42 | 192.168.1.92 | Created |
| Kobo 2 | wifi | a4:3c:d7:56:bb:f9 | 192.168.1.93 | Created |

Bindings only take effect when a device renews its lease. Toggle wifi, or on macOS: `sudo ipconfig set <iface> DHCP && ipconfig getifaddr <iface>`.

### Open issue: private wifi addresses on the Macs

macOS uses a per-network private MAC by default, and the router only sees that one. Two things from the same day conflict:

- The bindings above use hardware MACs. They only match if "Private Wi-Fi Address" is Off for the network on that Mac.
- Later that day Alex had a Mac set to "Fixed" private address, showing `a6:54:90:62:c6:fe`, and was told to bind that one. Not recorded which Mac that was or whether the binding was updated.
- Earlier the MacBook Pro was seen on the router as `0e:90:e1:ca:88:2a` at .215 (an older private address).

So for each Mac, check which MAC the router actually sees and make sure the binding uses it. Verify with `ipconfig getifaddr en0` (MBP) and `en1` (Mini).

### Other MACs for reference

- Mac Mini built-in ethernet (en0): 1c:f6:4c:38:57:c2. Not in use at the time, Mini was on wifi. If it moves to ethernet the binding needs this MAC.
- Unidentified device seen in the lease table: 90:ca:fa:b1:7c:6e at .4

## DNS

- Viettel blocks some sites (Reddit) at DNS level and hijacks port 53, so changing plain DNS servers on the router or devices does nothing.
- Encrypted DNS (DoH/DoT) gets around it. Check at 1.1.1.1/help.
- Decision direction: hosted encrypted DNS (NextDNS or AdGuard DNS) per device, not a self-hosted resolver. Reason: the home gets occasional overnight power outages and core internet should not depend on the Mac Mini being up. No record of which service was actually set up (unverified).
- Tailscale is in use, with MagicDNS handling local naming.

## Other hosts on the network

- Mac Mini M4: main home server. Plex, Jellyfin, *arr stack, qBittorrent behind VPN, Audiobookshelf, Kavita, Calibre-Web. TerraMaster DAS attached. Semi-headless, remote access via Jump Desktop and Tailscale.
- HP G8 mini PC: second semi-headless server, in the same cabinet as the ONT. Suggested but not decided: wire it straight to the ONT over ethernet, improve airflow, maybe add a small switch. No IP binding yet.
- ESP32: Kobo page-turner remote project (repo `kobo-md5stick-remote`), talks to the Kobos over LAN, which is why they have fixed IPs.

## Not known / worth checking first

- Actual DHCP pool start and end
- Whether the ESP32 binding at .80 exists
- Which MAC each Mac currently presents to the router
- Whether any port forwards, UPnP, or DMZ settings exist (never discussed)
- Whether the ONT is in router mode with PPPoE on it (assumed, never confirmed)
