---
id: TASK-7
title: 'Monitoring VM on g8: Grafana for host, VMs, temperatures'
status: To Do
assignee: []
created_date: '2026-10-02 16:33'
labels:
  - infra
  - machine
dependencies: []
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Idea (Alex, 2026-10-02): an infra VM running Grafana that tracks g8 and every guest. Today there is no dashboard beyond the Proxmox UI (CPU/RAM/disk/net graphs per node and guest; no temperatures, no alerts). Sensors exist on g8 and read fine: k10temp (CPU), nvme, amdgpu under /sys/class/hwmon; smartctl is installed; lm-sensors is not. Readings 2026-10-02 23:40: CPU 65C, NVMe 49C, GPU 50C; NVMe 0% worn, 407 power-on hours.

Proposed shape (not agreed yet):
1. VM 'mon' from template 9000 via bin/new-vm (about 2 vCPU, 2-4GB, 20-30GB). Reuse collielab services/observability (Grafana + Prometheus + Loki compose, today on vultr scraping only cadvisor).
2. Host and guest numbers without touching the host: Proxmox API token (read-only, PVEAuditor) + prometheus-pve-exporter in the VM. Alternative: Datacenter > Metric Server (built-in push to InfluxDB/OpenTelemetry).
3. Temperatures, fan, SMART: need something on the host. prometheus-node-exporter (one apt package, hwmon + textfile collectors) breaks the rule 'host stays bare: no Docker, no agents' (collielab hosts/g8/README.md). Decision for Alex: allow this one exception.
4. Inside guests: node_exporter in the template (per-process and real memory numbers; also fixes the misleading 100% memory view, see TASK-4 add-on), cadvisor on VMs with Docker.
5. Mini and vultr as extra scrape targets later.
6. Route grafana.lab.alexluong.com on the gateway + a card on the index page.
7. Alerts (CPU temp, disk full, NVMe wear, VM down) to email or a phone push.

Open decisions:
- R2 sync: Prometheus cannot store to R2 directly (needs Thanos/Mimir, or VictoriaMetrics with vmbackup). Claude's view: skip it for metrics (history is disposable; dashboards and config live in git); spend R2 on VM backups instead (fleet.md open item 2: nothing is backed up).
- Monitoring that lives on g8 goes dark when g8 does. A check from outside (vultr or the Mini pinging g8/gw) covers that; fleet.md already lists a watchdog as a Mini candidate.
- Host exception in step 3.
<!-- SECTION:DESCRIPTION:END -->
