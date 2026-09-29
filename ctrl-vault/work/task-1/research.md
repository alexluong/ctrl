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

- **Decided 2026-09-30 (Alex): 64GB ceiling is enough; start at 16–32GB.** → 2-slot box that supports 64GB is fine; buy RAM as 1×32GB (not 2×16) so the upgrade is +1×32. 16GB too tight (one core stack ~6–10GB est + builds). DIY/128GB options parked.

- ≤64GB (shared infra) → prebuilt: business SFF (M70s-class, add RAM + SSD) or efficient mini PC.
- 128GB+ (isolated stacks) → DIY tower (price/upgradability) or Strix Halo box (compact/efficient).

## Open questions

- Measure core stack RAM: isolated vs shared-infra mode, plus a normal multi-agent session.
- Mac Mini spec: base M4 = 16GB? Enable runs up to 5 stacks — likely too tight alongside arrstack.
- Secrets/logins on new box: gcloud/kube (workspace-scoped), Doppler, Railway need redoing.

Sources (2026-09): Macworld M5 Pro mini review + 2026 Mac Studio; Minisforum store / Newegg MS-A2; ComputingForGeeks Strix Halo prices; Lenovo PSREF (M70s Gen 5, neo 50s/50t Gen 6, M90q Gen 3–5); BuyRefurbished M90q Gen 6.

## Buying plan (2026-09-30)

Alex isn't handy and doesn't want to spend time → buy a prebuilt from a big chain and have the shop do upgrades + testing. No DIY.

- Box: Lenovo ThinkCentre M70s Gen 5 NoOS (12U3000LVA, i5-14400, 8GB/512GB), 17.8M VND.
- Shop swaps RAM → 1×32GB DDR5 (or 1×16GB if pricey), adds 1TB NVMe, tests. Ubuntu Server 24.04 if they'll do it, else Claude walks Alex through a USB install.
- VN RAM is very expensive (Sep 2026): GearVN 2×16GB DDR5 kits 13.9–15M VND. Estimate total ~26–30M VND; get quotes.
- Shops: Phong Vũ, GearVN (HN + HCM), HACOM, An Phát (HN). All do free assembly/testing.
- Used/"from someone": only via a refurb shop with warranty, not Chợ Tốt/FB.
- After purchase: Tailscale, BIOS power-on-after-AC-loss, Docker, mise, clone hookdeck workspace, redo gcloud/kube/Doppler/Railway logins.

## Stock check 2026-09-30 (Phong Vũ, An Phát, Hacom, GearVN)

- 14th-gen M70s/neo Gen 5 at An Phát all "Đặt hàng" (no showroom stock) incl. 12U3000LVA. Gen 6 (Core Ultra 200) units are what's in stock. All 16GB units ship 1×16GB (slot free); no 32GB configs.
- **Pick:** Hacom neo 50t 12UB0008VA — i7-14700 (20C/28T), 16GB, 512GB, NoOS, 23.999.000, còn hàng. hacom.vn/pc-lenovo-thinkcentre-neo-50t-12ub0008va-gen-4-i7-14700-16gb-ram-512gb-ssd-wl-bt-k-m-no-os
  - + 1×16GB DDR5-5600 JEDEC (Kingmax 6.090.000 / Lexar 6.290.000, Hacom còn hàng) → 32GB dual-channel.
  - + 1TB NVMe (Kioxia Exceria Plus G3 3.890.000 / Kingston NV3 4.590.000, Hacom còn hàng) for Docker — confirm 2nd M.2 slot.
  - ≈ 34M VND total. Hacom install not free by default (100k off in-store upgrades >1M).
  - Raptor Lake i7: make sure BIOS has Intel 0x12B+ microcode (instability fix).
- Runner-up: neo 50t Gen 6 13BB0006VA — Core Ultra 5 225 (10C), 1×16GB, 512GB, NoOS; Hacom 21.599.000 / An Phát 22.199.000 (stock in HN + HCM).
- RAM (Sep 2026): 1×16 ~6.1M, 1×32 ~13.7M, 2×16 ~13.9M, 2×32 ~20.5–26M. ThinkCentres ignore XMP → buy JEDEC 5600 sticks.
- Dual vs single channel: dual (2×16) now; 64GB later = swap to 2×32.
- Free install: Phong Vũ yes (parts bought with PC); others unverified/paid.

## Shop follow-up 2026-09-30

Alex prefers GearVN (bought there before); dislikes Phong Vũ-type chains.

- GearVN: no Lenovo/Dell/HP business desktops. Own builds only. "PC GVN Homework i7 14700" 17.990.000 (https://gearvn.com/products/pc-gvn-homework-intel-i7): parts table = Gigabyte H610M-H V3 **DDR4**, 8GB SSTC DDR4, 256GB SSTC Gen3 SSD, CoolerMaster PN600, EDRA mATX case; highlights say 16GB/512GB/RTX 3050 — inconsistent, stock_total 1. Budget parts; use only as a base for a custom quote. Sales 1900.5301, Zalo https://zalo.me/450955578960321912.
- Hacom 12UB0008VA confirmed: 23.999.000 (promo 20.999.000), 1 unit at Kho HUB (43 Louis 8, Hoàng Mai, HN), 2 RAM slots / 64GB, **1× M.2 only** + 3.5"/2.5" bays, 12-mo warranty, hotline 1900.1903.
- Phong Vũ has ThinkCentres: neo 50t Gen 6 13BB000AVN (U5 225, 16GB, 512GB, Win11) 24.990.000 in stock.
- Candidate from Alex (Shopee, seller An Khang): neo 50s Gen 6 13DM003NVA — Core Ultra 7 265, 1×16GB DDR5, 512GB, NoOS, 12-mo — 31.190.000, 10 in stock. Same SKU at Hacom 29.999.000 (hacom.vn/pc-lenovo-thinkcentre-neo-50s-gen-6-pcle0323). PSREF: 2 DDR5 UDIMM (64GB), **2× M.2 2280 PCIe 4.0** + 1× 3.5" bay, 1GbE. Better than the neo 50t i7-14700 pick (2 M.2, newer/cooler CPU, no Raptor Lake instability).

## Other shops for 13DM003NVA (2026-09-30, verified on product pages)

- Hanoi, established: An Khang website 28.790.000 (sẵn hàng; their Shopee is 31.19M) https://www.ankhang.vn/may-tinh-de-ban-lenovo-thinkcentre-neo-50s-gen-6-13dm003nva.html · Phúc Anh 28.990.000 (có hàng, 1900 2164) https://www.phucanh.vn/pc-lenovo-thinkcentre-neo-50s-g6-13dm003nva.html · Laptop World 28.890.000.
- HCMC: Hugotech 23.690.000 (lowest believable; smaller shop — call first) https://hugotech.vn/pc-lenovo-thinkcentre-neo-50s-gen-6-13dm003nva/
- Suspicious-cheap: hancomputer.vn 20.54M (NVA), compro.com.vn 15.99M (MVA).
- Alternatives: M70s Gen 6 12YK001VVA (U7 265/16/512) ~24.95–25.4M (Mạnh Phát HCMC đặt hàng; nhanhavui HCMC; Bảo An HN unverified). M70t Gen 6 12YH002PVA 25.49M Hugotech. 12YH002QVA is 8GB.
- Seller lists via websosanh.vn/compare-api/get-compare-normal-merchant?rootProductId=<id>.

## FB deals (Alex browsing, 2026-09-30)

Alex doesn't weigh warranty (dislikes dealing with it) → used deals judged on price/perf + condition checks only.

- Dell Pro Micro QCM1250, Core Ultra 5 235T (14C/14T, 35W), 16GB DDR5 SO-DIMM (1 slot free), 256GB NVMe (1 M.2 free), 90W adapter, "lightly used" — 15.5M. Verdict: OK if service tag checks out; T-chip ≈ well below U7 265 sustained. Ask: service tag (Dell warranty lookup), BIOS unlocked/no admin password, SMART hours.
- FB no-name mini PCs: i5-7400T/7500T 16/256 2M (too old, 4C/4T — skip); i7-10750H 4.2M; i7-11800H 4.5M; i9-11900H 5M (8C/16T laptop chips, DDR4, ≈ M1 Pro multicore). Cheap because old platform + likely used/no-name. Possible as a cheap trial box; ask brand/model, slots, warranty, noise.
- HP Z2 Mini G9, i5-13500 (14C/20T, 65W desktop), 16GB DDR5 SO-DIMM, 256GB, adapter — 16M. Seller (FB): https://www.facebook.com/groups/610350386210787/user/1032893592/ Workstation mini: 2 SO-DIMM (up to 64–96GB, ECC capable), 2× M.2 Gen4. Best FB deal so far (vs Dell Pro Micro 235T at 15.5M). Same checks (serial → HP warranty, BIOS lock, SSD hours).
- HP EliteDesk 800 G8 Mini (Japan off-lease), i7-11700T (8C/16T, 35W), 16GB DDR4, 256GB — 10M. Pass: below CPU floor, T-chip, HP warranty long expired; Z2 Mini G9 at 16M is far stronger, no-name 11900H at 5M similar speed for half.
- Dell Precision T5610 (2013), 2× Xeon E5-2695 v2 (24C/48T), 32GB DDR3 ECC, 256GB — ~5M each, HCMC (Zalo 0989219822). Pass: ~half M1 Pro single-thread (tsc/jest/pnpm), no AVX2, ~100W+ idle, big + loud. Only upside: cheap DDR3 → lots of RAM.
