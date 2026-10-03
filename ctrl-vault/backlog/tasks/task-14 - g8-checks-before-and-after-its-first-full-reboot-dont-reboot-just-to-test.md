---
id: TASK-14
title: 'g8: checks before and after its first full reboot (don''t reboot just to test)'
status: To Do
assignee: []
created_date: '2026-10-03 20:59'
updated_date: '2026-10-03 22:09'
labels:
  - infra
  - machine
dependencies: []
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Not to do on its own: g8 reboots only when it needs to anyway (kernel or BIOS update, TASK-4; power cut). Since its last reboot (2026-10-02) a lot was added and each piece was restart-tested alone (gw container, hookdeck-ws VM, 2026-10-04), never all at once. g8 has no remote console: reboot only with someone home who can attach a monitor and keyboard.

Before (read-only; all passed 2026-10-04):
- Container 110 (gw): onboot 1, startup order=1, dev0 /dev/net/tun in /etc/pve/lxc/110.conf
- VM 101: onboot 1, net0 has firewall=1
- /etc/pve/nodes/g8/host.fw: enable 0 (if this ever says 1, g8's own firewall turns on with the datacenter's rules: risk of locking g8 out)
- /etc/pve/firewall/cluster.fw: enable 1; 101.fw enable 1; pve-firewall enabled (proxmox-firewall is enabled too but inert unless host.fw has nftables: 1)
- Kernel pinned to 6.14.11-9-pve (proxmox-boot-tool kernel list); BIOS After Power Loss = Power On
- gw: tailscaled, gw-tailnet, caddy enabled; Debian nftables disabled; /etc/sysctl.d/90-gw-tailnet.conf forwarding 1
- hookdeck-ws: tailscaled, docker enabled; user alex Linger=yes; t3code user service enabled
- Nothing running on hookdeck-ws that would mind (sessions, stacks); collielab hosts/gw/check.sh all good

After:
- collielab hosts/gw/check.sh all good (tun, Tailscale, forwarding, masquerade, Caddy, DNS, router path, MBP route)
- ssh g8, gw, mini, hookdeck-ws by name; https://lab.alexluong.com and a page per machine
- hookdeck-ws: tailscale ip -4 = 100.113.20.22; T3 environment connects from the MBP; firewall still blocks it from 192.168.1.90/.100/.110 and allows the internet (commands: ctrl-vault/work/task-9/log.md entry 14)
- pve-firewall status enabled/running

Context: ctrl-vault/docs/tailscale.md, collielab hosts/g8/README.md, hosts/gw/README.md.
<!-- SECTION:DESCRIPTION:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-10-03 22:09
---
Add to After (2026-10-04): hookdeck-ws 'tailscale serve status' shows https -> 127.0.0.1:3773, and from gw: curl --resolve hookdeck-ws.tail2b958c.ts.net:443:100.113.20.22 https://hookdeck-ws.tail2b958c.ts.net/ = 200. Serve is saved in tailscaled state (should survive); not yet restart-proven because hookdeck-ws had live sessions when it was set up.
---
<!-- COMMENTS:END -->
