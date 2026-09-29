# TASK-1: always-on dev box for hookdeck — research (2026-09-30)

## Workload (from ~/workspaces/hookdeck)

- core: ~24 containers under one compose project (Postgres 17, Redis, Dragonfly, ClickHouse, Bigtable emu, Kafka + ZK + schema-registry + connect, PubSub emu, caddy/coredns/envoy, optional k3s) + ~8 PM2 Node services on host. Warm boot ~2 min.
- outpost (Go): api/delivery/log + Redis, ClickHouse, RabbitMQ.
- One stack of each at a time (fixed ports / shared infra); parallelism = agents in worktrees doing builds/tests (25 worktrees now; core worktree ~1.8G node_modules each).
- Pain today on MBP (M1 Pro 32GB, 460G) is disk, not RAM: Docker regrows 40–50G in 2 weeks, go-build 15G in 4 days. Docker Desktop capped at 16GB.
- Nothing needs macOS; all Linux images. Claude runs via API — no local LLM, so GPU/unified memory doesn't matter.

## Sizing

64GB RAM min (96GB comfortable), 2TB SSD, 12–16 fast cores, 10GbE nice-to-have. Tailscale into the mesh.

## Options (Sep 2026 prices, DRAM shortage inflated everything)

| Option | Spec | Price | Notes |
|---|---|---|---|
| Minisforum MS-A2 (Linux) | Ryzen 9 9955HX 16C/32T, 96GB DDR5, 2TB | ~$1,919 preconfig ($799 barebone) | native Docker, 3× M.2 + U.2, 2×10G SFP+; ~fan noise, ~25W idle |
| Mac mini M5 Pro | 18C, 64GB, 1TB | ~$2,899 | same env as MBP, silent, low power; Docker in VM; 1TB tight (external TB5 SSD) |
| Mac Studio M5 Max | 64GB+ | $2,499 base (36GB) + $400 for 64GB (needs 40-core GPU tier) | overkill unless also for local LLMs |
| Business mini/SFF, refurb (Lenovo M90q Tiny / HP Elite Mini 800) | e.g. M90q Gen 6, Core Ultra 7 265T, 64GB, 2TB | ~$1,139 refurb | home-server-grade: quiet, ~10W idle, 24/7-rated, vPro remote mgmt; Tiny = 2 SO-DIMM (64GB max), 2 M.2; SFF towers take 128GB |
| Strix Halo boxes (GTR9 Pro / EVO-X2 / Framework) | Ryzen AI Max+ 395, 128GB | $2k–$4.3k | pay for iGPU/LLM memory we don't need |

Leaning (2026-09-30, after "why beefy?"): refurb Lenovo/HP business mini at 64GB; MS-A2 if more cores/10GbE wanted. Either way: Linux (Ubuntu/Debian), headless, Tailscale. CPU floor: Intel 12th gen+ / Ryzen 7000+ (~M1 Pro level); older 8th–10th gen Tinies are slower than the MBP. Oldest M90q to consider: Gen 3 (12th gen, DDR5, 64GB max); prefer 65W non-T i7 (sustained builds). GPU irrelevant (no local LLM; containers + builds are CPU).

## Open questions

- No record found of the earlier HP/Lenovo discussion (vault, git, transcripts).
- macOS vs Linux: does Alex want T3 Code / Claude desktop running on the box, or remote-drive via ssh/Tailscale?
- Mac Mini spec: base M4 = 16GB? Enable runs up to 5 stacks (Mongo, 3 Redis, Postgres…) — likely too tight alongside arrstack.
- Secrets/logins on new box: gcloud/kube (workspace-scoped), Doppler, Railway need redoing.

Sources: Macworld M5 Pro mini review, Macworld 2026 Mac Studio, Minisforum store/Newegg MS-A2, ComputingForGeeks Strix Halo price comparison.
