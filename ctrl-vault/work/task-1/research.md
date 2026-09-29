# TASK-1: always-on dev box for hookdeck — research

Started 2026-09-30. Buying in Vietnam. Mac Mini (base M4) stays on arrstack + enable/solex.

## Workload (from ~/workspaces/hookdeck)

- core: ~24 containers under one compose project (Postgres 17, Redis, Dragonfly, ClickHouse, Bigtable emu, Kafka + ZK + schema-registry + connect, PubSub emu, caddy/coredns/envoy, optional k3s) + ~8 PM2 Node services on host. Warm boot ~2 min.
- outpost (Go): api/delivery/log + Redis, ClickHouse, RabbitMQ.
- Today: one stack of each at a time; parallelism = agents in worktrees doing builds/tests (25 worktrees; core worktree ~1.8G node_modules each).
- **Goal: 5–10+ stacks at once.** That makes RAM the main constraint.
- Pain today on MBP (M1 Pro 32GB, 460G) is disk: Docker regrows 40–50G in 2 weeks, go-build 15G in 4 days.
- Nothing needs macOS; all Linux images. Claude runs via API — no local LLM.

## Sizing

Depends on stack mode (**measure one core stack before buying**):

| Mode | Per stack | 10 stacks | Box |
|---|---|---|---|
| Fully isolated (own Postgres/Kafka/ClickHouse…) | ~6–10GB (estimate) | 60–100GB+ | 128GB, 16+ cores |
| Shared infra + per-worktree namespaces (core supports it) | ~2–3GB (PM2 services) + ~8GB shared once | ~30–40GB | 64GB, 10–16 cores |

Always: 2TB+ NVMe (second M.2 slot for Docker is nice), Linux headless, Tailscale.

## What matters / doesn't

- **RAM capacity + slots**: the deciding spec. 2 slots ≈ 64GB ceiling; 4 slots = 128–192GB.
- **CPU**: floor Intel 12th gen / Ryzen 7000 (≈ M1 Pro). Prefer 65W desktop parts over 35W "T" parts (sustained builds throttle). Newest gen buys ~10–20%, not worth a premium.
- **Top-tier (M4/M5-class) single-core**: +30–50% per core, but agent time is mostly model latency → maybe ~10% faster tasks (unmeasured guess).
- **GPU**: irrelevant (containers + builds are CPU; browser tests fine on iGPU).
- **Power**: 10W extra 24/7 ≈ $10–25/yr — tiebreaker only.
- **24/7 niceties**: BIOS "power on after AC loss", quiet cooling, remote console (vPro on business SKUs, or a JetKVM/PiKVM for DIY).

## Device types

| Type | Examples | RAM ceiling | Fits | Notes |
|---|---|---|---|---|
| Business tiny/SFF (prebuilt) | Lenovo ThinkCentre M70s/M90q/neo 50s, HP Elite Mini/SFF, Dell OptiPlex | 64GB (2 slots) | shared-infra mode | reliable, quiet, warranty, vPro on M-series i5/i7 vPro SKUs; proprietary boards/PSU, few upgrade paths. Local VN: M70s Gen 5 i5-14400 8GB/512GB 17.8M VND is best value of the listings seen (neo 30t = laptop chip, skip) |
| x86 mini PC, laptop chip | Beelink SER9, Minisforum (Ryzen AI 9 HX 370 / 8845HS), MS-A2 (9955HX 16C) | 64–96GB SO-DIMM | shared-infra mode | efficient, small; MS-A2 = 16C, 3 M.2, 10GbE, ~$1.9k w/ 96GB |
| x86 "Mac-mini-like" (Strix Halo) | Beelink GTR9 Pro, GMKtec EVO-X2, Framework Desktop (Ryzen AI Max+ 395) | 128GB soldered | isolated mode | 16C ≈ M4 Pro multicore, ~10W idle; buy 128GB up front; $2k–4.3k (volatile) |
| Business workstation tower | Lenovo ThinkStation P3 Tower, ThinkCentre M90t, HP Z2 Tower | 128GB (4 slots) | isolated mode | prebuilt reliability + RAM headroom; pricier than DIY |
| DIY tower | Ryzen 9 9900X/9950X or Core Ultra 7 265, B650/B860 board, 4 DIMM | 128–192GB | isolated mode | best price/perf, fully upgradable, quiet with big cooler; bigger, ~30–50W idle, no vPro (add KVM), per-part warranty |
| Mac | Mac mini M4 Pro/M5 Pro, Mac Studio | 64GB (mini) | shared-infra mode | best perf/W, silent; Docker in VM, RAM/SSD pricey, no upgrades. Only if macOS on the box is wanted. Prefer refurb M4 Pro over M5 Pro |

## Leaning

- ≤64GB (shared infra) → prebuilt: business SFF (M70s-class, add RAM + SSD) or efficient mini PC.
- 128GB+ (isolated stacks) → DIY tower (price/upgradability) or Strix Halo box (compact/efficient).

## Open questions

- Measure core stack RAM: isolated vs shared-infra mode, plus a normal multi-agent session.
- Mac Mini spec: base M4 = 16GB? Enable runs up to 5 stacks — likely too tight alongside arrstack.
- Secrets/logins on new box: gcloud/kube (workspace-scoped), Doppler, Railway need redoing.

Sources (2026-09): Macworld M5 Pro mini review + 2026 Mac Studio; Minisforum store / Newegg MS-A2; ComputingForGeeks Strix Halo prices; Lenovo PSREF (M70s Gen 5, neo 50s/50t Gen 6, M90q Gen 3–5); BuyRefurbished M90q Gen 6.
