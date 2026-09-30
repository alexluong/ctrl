# TASK-1 decision: HP EliteDesk 805 G8 Mini (2026-09-30)

Decided in a separate session; summary pasted by Alex. Research trail: [research.md](research.md).

## Pick

Used HP EliteDesk 805 G8 Mini **95W dual-cooler edition** from **xeon.vn** (61 Mai Xuân Thưởng, P3, Q6, HCMC · Zalo 0982538753 · 12-mo warranty per part) — **19.8M VND**.

- AMD Ryzen 7 5700G, 8C/16T Zen 3, 65W full power (not a T part)
- 64GB DDR4-3200 SODIMM (2×32GB, used) — 2 slots, **64GB ceiling**, no ECC
- 1TB NVMe (mixed brand); 2× M.2 (PCIe 3.0 on this CPU)
- Realtek 1GbE (optional 2.5GbE Flex IO)
- ~10–20W idle, ~80–90W full load, avg ~20–30W (~15–20 kWh/mo); ~1L
- Runner-up: HP 805 G6 Mini (Ryzen 5 4650GE, 64GB DDR4) 16.9M — ~3M cheaper, ~1.6–1.8× slower multi-core.

**Why:** agents wait on the Claude API most of each loop → a ~1.5× faster CPU finishes tasks only ~10–20% sooner. RAM decides how many envs run at once, so 64GB per VND beat speed. DDR4 dodges 2026 DDR5 prices.

Rejected: AI boxes (no local LLM), custom 9950X/DDR5 (~50–60M), old Xeon/EPYC (loud/hot/idle power), repurposed gaming PC (conflicts with gaming, no iGPU), P3 Ultra (~30–35M, barebone OOS), Precision 3260 (~30M+, best step-up), OptiPlex 7010 Plus Micro i7-13700T 64GB (31.1M, T-chip), ASUS NUC 15 Pro+ (~40M w/ RAM), GMKtec K4 (OOS, 32GB).

## Proxmox plan

Proxmox VE 9.2, no-subscription repo. One VM per project; only active projects powered on.

| Tier | Use | vCPU | RAM | Disk | Type |
|---|---|---|---|---|---|
| Heavy | app + ClickHouse + Kafka/Redpanda | 8 | 16–24GB | 60–100GB | VM |
| Medium | app processes, maybe a DB | 2–4 | 4–8GB | 40–60GB | VM/LXC |
| Light | audits, lint, unit tests | 1–2 | 2–4GB | 20–30GB | LXC |
| Host | Proxmox | – | ~4GB | – | – |

- RAM is the hard limit (running VMs hold memory). vCPUs overcommit across VMs; ≤16 per VM.
- Lean dev infra: Kafka KRaft 512MB–1GB heap or Redpanda; ClickHouse with lowered max_server_memory_usage (2–4GB).
- Fallback if RAM tight: one shared infra VM (topic prefix / DB per env).
- VM CPU type "host"; dev VMs get higher CPU units than infra; no pinning.
- Storage: LVM-thin on the 1TB (not ZFS; if ZFS cap ARC ~4GB). Second NVMe later for Kafka/ClickHouse data.
- Cloud-init VM template with toolchain; snapshot before risky agent runs; clone-and-delete for tests needing their own cluster.

## Shop order (sent to xeon.vn)

1. Update BIOS · 2. Enable SVM, IOMMU, After Power Loss = Power On · 3. Proxmox VE 9.2 on 1TB, ext4/LVM-thin · 4. `iface vmbr0 inet dhcp` in /etc/network/interfaces (installer saves shop IP as static) · 5. temp root password · 6. confirm 64GB seen, 2nd M.2 empty with screw.

## At home

- [ ] Change root password
- [ ] memtest86+ a few hours (used RAM)
- [ ] Find IP in router → https://<ip>:8006
- [ ] No-subscription repo, updates
- [ ] DHCP reservation on router
- [ ] Tailscale (no open ports)
- [ ] Backup jobs to another drive/machine
- [ ] Small UPS (overnight outages)
- [ ] Place with airflow; dust every few months; smartctl SSD health
- [ ] Note power-adapter wattage (brick = common 24/7 failure)

## Upgrade path

Watch Proxmox RAM/CPU graphs a few weeks.
- RAM full → second 805 G8 (another 64GB), two standalone hosts (a 2-node cluster needs a QDevice tie-breaker).
- CPU pegged, RAM free → Dell Precision 3260 i7-12700 (~30M+) or P3 Ultra.
- Both fine → keep. Used business minis resell easily in HCMC.

## First VMs (Alex, 2026-09-30)

Disk per VM = virtual disk size set at creation; on LVM-thin it's a cap, not reserved. Easy to grow later, hard to shrink → start modest.

| VM | Type | vCPU | RAM | Disk | Notes |
|---|---|---|---|---|---|
| hookdeck workspace | VM | 8–12 | 24–32GB | 250–300GB | Docker, mise, shared-infra mode for many stacks |
| arrstack (off Mac Mini) | VM (or LXC+Docker) | 2 | 4–6GB | 32GB | configs only; media/downloads stay on the Samsung T7 (`/Volumes/T7/arr` today) via USB passthrough. T7 filesystem must be Linux-readable (APFS isn't) — check before moving. Who plays the media (Plex/Infuse/…) decides whether T7 needs an SMB share |
| AI assistant (ClickUp interface) | LXC or VM | 2 | 2–4GB | 20–30GB | always-on, light |
| Proxmox host | – | – | ~4GB | installer default (~100GB root) | rest of 1TB = LVM-thin pool |

RAM ≈ 34–46GB of 64 → room for one more mid-size VM.
