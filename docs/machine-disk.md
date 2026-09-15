# Machine Disk Baseline

**MacBook Pro only** (460G volume). The Mac Mini is a separate machine with its
own storage — none of this applies there. Devices: `docs/machine.md`.

Purpose: when the disk fills up again, compare a fresh snapshot against the last
one to see *which bucket moved* instead of re-deriving the whole picture from
scratch. Run `bin/disk-audit.sh` (~8 min, mostly `du` over node_modules).

## Buckets

Six buckets, defined in `bin/disk-audit.sh`. Grouped by how they behave: two
that regrow on their own and are worth pruning (`docker`, `repos`), one of
tooling state that mostly refills (`system`), two that only change by decision
(`apps`, `personal`), and the unclassified remainder (`other`).

| Bucket | Kind | What's in it |
|---|---|---|
| `docker` | prunable | `~/Library/Containers/com.docker.docker` (the `Docker.raw` VM disk) |
| `repos` | prunable | `~/git`, `~/code` — dominated by `node_modules` |
| `system` | tooling | pnpm store, `~/Library/Caches`, `~/.cache`, `~/.npm`, `~/go` module cache, Claude `vm_bundles`, mise/bun/asdf/pyenv/cargo, AI tool state |
| `apps` | stable | `/Applications`, `/opt/homebrew` |
| `personal` | stable | Messages, Pictures, Documents, Downloads, Music, iCloud local, Spark mail |
| `other` | — | Everything else: rest of `~/Library` (Application Support, Metadata, Containers besides Docker), `/Library`, OS. Steam and other App Support data land here. |

**What's in `system`, and what's worth clearing.** It's all tooling state, but
prunability varies a lot. Roughly a third is worth clearing; the rest refills or
isn't cache at all:

- `~/go` (11G) — Go has no prune-unreferenced for the module cache, unlike
  `pnpm store prune`. It's all-or-nothing, and a rebuild re-downloads what your
  live projects need.
- Claude `vm_bundles` (9.1G) — the Claude *desktop app's* Linux sandbox VM
  (`rootfs.img` + a compressed warm-start image). Binary, not accumulated;
  deleting only helps permanently if you don't use that feature.
- mise / bun / asdf / pyenv / cargo (7.4G) — installed language runtimes. Not
  cache at all. "Pruning" them means uninstalling versions you use.

Genuinely prunable within `system`: the pnpm store (`pnpm store prune`),
`~/Library/Caches` (~4.7G, and macOS evicts this itself under pressure), and
`~/.cache` (~1.1G). That's the part to reach for.

This started as two buckets (`caches` vs `system`) split on prunability. Folded
back into one on 2026-08-03 — the distinction is real but too fine-grained to
carry structurally, and `caches` was only ~15G. It lives in this table instead.

If you change a bucket's paths, past snapshots stop being comparable — note the
change below when you do.

## Budgets

**Baseline + headroom, not invented targets.** Each budget is roughly the
measured 2026-08-03 baseline plus ~25%. Over budget therefore means *this grew
past its normal range, go look* — not *this is wasteful*. That distinction
matters: a first pass at this set targets like "caches should be 35G" and then
had to justify deleting things that would immediately come back.

| Bucket | Baseline | Budget | Note |
|---|---|---|---|
| `docker` | 70.9G | **120G** | Deliberately generous, not baseline-derived. Primary dev runtime, and the baseline was measured right after a full prune, so it understates the working peak. |
| `repos` | 70.6G | **100G** | Headroom for a few fresh worktree installs. |
| `system` | 44.0G | **70G** | Raised 50 → 70 on 2026-09-16: over budget three audits running (58.1 / 57.8 / 66.2) and still ~59G after a genuine prune. Go caches, pnpm store, and `~/Library/Caches` all grow with normal dev. Growth past 70 means a new runtime or tool VM — worth knowing about, rarely worth pruning. |
| `apps` | 71.3G | **80G** | Moves only when something is installed. |
| `personal` | 30.6G | **40G** | Moves only by decision. |
| `other` | 58.2G | **70G** | Unclassified remainder; drifts with OS churn. |
| **sum** | 345.5G | **460G** | Equals the whole disk — see below. |

Also `FREE_FLOOR=50` — **free space below 50G is the real act-now signal**,
independent of buckets.

**Units, because this is easy to get wrong:** everything here is GiB, what `df`
reports. The disk shows as 460 GiB in `df` and 494 GB in `diskutil` (physical
500.3 GB) — that's decimal vs binary, the *same* space, not extra headroom.
Also `used + free` (345.6 + 89.3 = 434.9) doesn't reach 460: APFS reserves ~25 GiB
for metadata, so allocatable is ~435 GiB.

**Budgets are independent tripwires, not a partition.** They sum to 460G — the
entire disk — so they cannot all sit at ceiling at once, and `docker` + `repos`
alone (220G) grant more growth than the disk can actually give while keeping 50G
free. That's fine and intended: each budget answers "has *this* grown past its
normal range?", and `FREE_FLOOR` answers "is the disk actually in trouble?"

Budgets live in `bin/disk-audit.sh` as `BUDGET_*`. Revise them here and there
together, and note the change in History.

### How to prune each bucket

**`system`** (44.0G) — mostly leave alone. Worth clearing, in order: pnpm store
(`pnpm store prune`), `~/Library/Caches` (ms-playwright 2.1G is safe; CloudKit is
system-managed, leave it), `~/.cache` (puppeteer, amp-repos). pnpm's store only
releases what no `node_modules` still hardlinks, so prune `repos` *first*, then
the store.

The rest refills — only reach for it when genuinely desperate, and know what
you're buying:

| Item | Size | If cleared |
|---|---|---|
| `~/go/pkg/mod` | 11G | `go clean -modcache`. Re-downloads only what live projects reference — the rest is old versions from projects you've moved past. One slow, network-bound build. |
| Claude `vm_bundles` | 9.1G | Permanent only if you don't use the Claude desktop sandbox; otherwise it returns at the same size. |
| mise / bun / asdf / pyenv / cargo | 7.4G | Uninstalling runtimes. Not a cleanup. |

`~/Library/Caches/go-build` is a *separate* Go cache from the module cache
(`go clean -cache` vs `-modcache`). It was 3.4G at the start of 2026-08-02 and
macOS evicted it on its own during the disk-full event — which is exactly what
`~/Library/Caches` is for, and a reason not to bother pruning it by hand.

**`docker`** — `docker builder prune -a` first (build cache is usually the
regrowth), then `docker image prune -a --filter until=720h`, then
`docker volume prune` (no `--all`, so named dev-DB volumes survive). Never
`--volumes` on a system prune.

**`repos`** — delete `node_modules` untouched 90+ days:
`find ~/git ~/code -type d -name node_modules -prune -mtime +90`.
Then `pnpm store prune`.

### `repos` baseline — the big five

`repos` is one bucket but almost all of it is five trees. Measure these
individually before drilling anywhere else — if the bucket moved and these
didn't, the growth is somewhere unexpected and worth a real look.

```sh
du -sh ~/git/hub/*/*/ | sort -rh | head -8
```

| Tree | 2026-08-25 | 2026-09-16 | Expect | What it is |
|---|---|---|---|---|
| `alexluong/hookdeck` | 9.3G (14 wt) | 36G (37 dirs) | `~4G + ~1.8G/core worktree` | separate tree from `hookdeck-workspace`; `core-wt-*` worktrees are ~1.8G each and **not** hardlinked (du -c of three = sum) |
| `ebutler-qa/workspace` | 19G (11 wt) | 16G (13 wt) | `6.5G + ~1.2G/worktree` | worktrees, each with its own `node_modules` |
| `alexluong/hookdeck-workspace` | 15G (6 wt) | 15G (6 wt) | 10–18G | `core-workspace` alone is 7.4G |
| `alexluong/hookdeck-workspace.git` | 5.1G | 5.1G | ~5G | bare mirror backing the worktrees |
| `ebutler-qa/workspace.git` | 6.0G | 1.9G | ~2–6G | bare mirror backing the worktrees; shrank on its own (gc/re-clone) |
| everything else | ~30G | ~30G | ~30G | ~60 repos, none over 5.1G (`ebutler-qa/odoo`) |

`alexluong/hookdeck` became the biggest tree on 2026-09-16: 18 `core-wt-*`
worktrees, 13 of them with a full ~1.8G `node_modules`, all touched within the
prior two weeks. Same per-worktree duplication as `ebutler-qa/workspace`. When
this tree is over ~20G, the cheap win is `node_modules` in worktrees whose
branch has merged — check `git branch --merged` in `core/` first.

**Size the two workspace trees by worktree count, not by the absolute number
above.** They are actively managed and swing hard: during this audit
`ebutler-qa/workspace` went 39G/29 worktrees → 19G/11 worktrees in about forty
minutes, because worktrees were being deleted while the audit ran. A single
`du` of these trees has a shelf life of hours. `main` is the fixed ~6.3G base;
every additional worktree is ~1.2–2.0G on top.

Reading the numbers:

- **The two `.git` mirrors are fixed cost.** They only grow with history. If one
  jumps, someone fetched a large branch or a binary landed upstream — not a
  cleanup target.
- **Worktree count is the real driver.** Several sit at exactly 2.0G — the same
  dependency set installed over and over. Adding five branches costs ~7G with no
  new code. When this tree grows, check `ls -d */ | wc -l` first and divide;
  only conclude that dependencies got heavier if per-worktree cost actually
  moved.
- **Stale worktrees are the cheap win.** Deleting `node_modules` from ones you
  aren't actively on reclaims 1–2G each and costs one `install` to undo. See the
  90-day `find` in the prune playbook.
- **In `ebutler-qa/workspace` the duplication is real, not a `du` artifact.**
  Worth stating because the opposite is the usual assumption. pnpm normally
  hardlinks from `~/Library/pnpm/store`, in which case `du` bills the same bytes
  to every worktree and deleting one frees almost nothing. Measured here it does
  not: three worktrees are 2035 + 2035 + 2034 MB separately and 6042 MB under
  `du -c` (which counts a hardlink once) — only 62 MB shared. So each worktree
  really is its own ~2G copy and deleting one really does return ~2G. The store
  is at the default path with no `.npmrc` overriding `node-linker`, so *why*
  they aren't linked is unresolved — some of these sub-repos are on bun rather
  than pnpm, which is the first thing to check.
- **Elsewhere, assume the double-count until measured.** For pnpm trees that
  *are* linked properly, deleting `node_modules` frees less than its reported
  size until you also `pnpm store prune` — and prune the repos *first*, or the
  store still considers those packages referenced. `du -c` across two sibling
  worktrees tells you which case you're in, in about a minute.

## Optimization backlog

Neither of these is a cleanup — they're structural changes that would lower the
floor. Worth a dedicated session.

- **`repos` — reduce duplication.** 59.7G of `node_modules`, most of it across
  worktrees sharing the same dependency set. `ebutler-qa/workspace` (29
  worktrees) is the whole problem: 10 sit at exactly 2.0G each, and they are
  genuinely separate copies — `du -c` across three of them shows only 62 MB
  shared. The sub-repos do have `pnpm-lock.yaml` files and the store is at its
  default path, so the store linking is failing or being bypassed rather than
  absent; several sibling dirs (`dev`, `e2e`, `scripts`) are on `bun.lock`
  instead. `alexluong/hookdeck` runs 14 worktrees in 9.3G total, which is what
  this should look like. Finding out why the linking doesn't hold here is the
  single biggest structural win available — worth ~20G.
- **`docker` — reduce image footprint.** 34.8G of images, 20.4G of volumes, with
  ~13.6G of volumes unused. Worth auditing which named volumes are still live dev
  DBs vs abandoned, and whether the large `server-*` images (~5G each) share base
  layers or are rebuilt from scratch each time.

## Snapshots

All values in GiB (see units note above).

| Date | Used | Free | docker | repos | system | apps | personal | other |
|---|---|---|---|---|---|---|---|---|
| 2026-08-02 | 349.3 | 83.6 | 70.9 | 78.2 | 45.8 | 71.3 | 30.6 | 52.5 |
| 2026-08-03 | 345.7 | 89.2 | 70.9 | 70.6 | 44.0 | 71.3 | 30.6 | 58.3 |
| 2026-08-03 | 345.6 | 89.3 | 70.9 | 70.6 | 44.1 | 71.3 | 30.6 | 58.1 |
| 2026-08-17 | 421.8 | 15.1 | 128.7 | 70.9 | 58.1 | 71.9 | 28.7 | 63.6 |
| 2026-08-25 | 416.0 | 3.4 | 116.4 | 104.4 | 57.8 | 72.3 | 28.9 | 36.2 |
| 2026-08-25 | 376.6 | 42.8 | 77.9 | 90.3 | 57.8 | 72.3 | 28.9 | 49.4 |
| 2026-09-16 | 425.4 | 8.4 | 116.3 | 104.0 | 66.2 | 72.8 | 29.5 | 36.6 |
| 2026-09-16 | 364.3 | 69.6 | 61.2 | 88.1 | 58.7 | 70.7 | 29.5 | 56.1 |

The brief `caches`/`system` split on 2026-08-03 was folded back before any
snapshot depended on it, so every row above is directly comparable.

Baseline taken right after a large cleanup (see below), so it's a *clean* floor,
not a typical day. As of the 2026-08-03 re-split: prunable 156.3G,
baseline+stable 131.1G, **every bucket within budget**, 89.3G free.

`other` rose 52.5 → 58.3G across those two snapshots with nothing deliberately
added to it — it's the unclassified remainder, so it absorbs normal OS churn
(Application Support, Metadata, system caches). Treat movement there as noise
unless it's large.

## What normal looks like

Known-large items, so they don't get re-investigated every time:

- **League of Legends — 38G.** Two thirds of `apps`. Biggest single item on the
  disk. Stable; only moves if uninstalled.
- **Messages — 14G** (12G attachments), **Spark mail — 9G**. Both stable, both
  re-downloadable but slow.
- **`Docker.raw` is sparse**: ~256G apparent, ~71G actual. Always trust `du`, not
  `ls -lh`. Docker Desktop 29 TRIMs properly — space freed inside the VM does
  come back to the host.
- **pnpm store 11G + `~/go` 11G** grow monotonically and never self-prune.
- **Claude `vm_bundles` 9.1G** regenerates.

## Where regressions come from

Confirmed on 2026-08-02: Docker build cache went **0 → 17.2G in about an hour**
of normal dev after being pruned. That is the recurring offender.

1. **Docker** — build cache and images regrow per branch/rebuild. Check first.
2. **`node_modules` per worktree** — `ebutler-qa/workspace` has 11 worktrees,
   `hookdeck-workspace` has 5. Each `npm i` is another 1-2G.
3. **Package stores** — pnpm/go caches only grow.

## Cleanup safety

- **Safe** — Docker build cache, anonymous Docker volumes, unused images >30d,
  `node_modules` untouched 90+ days, package-manager caches. All regenerate.
- **Ask first** — named Docker volumes (dev databases: `hookdeck_postgres_data`,
  `hookdeck_clickhouse_data`, `enable-ebchat_mongo_data`, `outpost_postgres`…),
  Messages attachments, Spark mail.
- **Never without checking** — any repo directory. Check `git stash list`,
  unpushed commits, and untracked files first. On 2026-08-02 a "delete this whole
  dir" nearly destroyed 160 stashes across the hookdeck repos (123 in `outpost`
  alone). Stashes exist only in local `.git`.

Deleting `node_modules` in pnpm repos frees less than `du` suggests — files are
hardlinks into the store. Follow with `pnpm store prune` to actually collect it.

Moving files into iCloud Drive frees nothing on its own (same volume) — space
only returns once iCloud uploads and macOS evicts the local copies.

## History

- **2026-09-16** — Free space hit **8.4G**. Three weeks since the last audit.
  Docker was the mover again (+38.4G to 116.3, just under budget): 64G of
  images older than 30 days, 22.8G build cache. `repos` +13.7 to 104.0 (over
  budget), all of it `alexluong/hookdeck` going 9.3 → 36G on 18 `core-wt-*`
  worktrees — every one active in the last two weeks, so left alone. `system`
  +8.4 to 66.2: `~/Library/Caches` 4.7 → 16G (go-build 4.4, Homebrew 3.3,
  ms-playwright 3.1, Google 3.0), pnpm store 11 → 14, go mod 11 → 13.
  Safe-tier cleanup only: Docker build cache (22.8G) + images >30d (41.7G) +
  anonymous volumes (2MB, 92 empties), 73 `node_modules` dirs untouched 90+
  days (16.3G by `du`), `brew cleanup --prune=all` (3.5G), `pnpm store prune`
  (3.3G). **8.4 → 69.6G free.** Not touched, needs a by-name decision: 143
  named Docker volumes, 36.7G, all inactive — biggest are `server_gocache` 5.3G,
  `df-build-vol` 3.1G, `outpost_go_build_cache` + `outpost_go_mod_cache` +
  `server_gomodcache` ~7G, and ~15 `enable-*_node_modules` + 16
  `enable-*_mongo_data` at ~0.2–0.5G each. Raised `system` budget 50 → 70
  (over three audits running, ~59 post-prune — the budget was wrong).
  Two rows below: pre- and post-clean.

- **2026-08-25** — Free space hit **3.4G**. Docker was over again (116.4G, +45.5
  from baseline, having been pruned down from 128.7 on 08-17) and `repos` jumped
  33.8G in the eight days since the last audit — flat at 70.9 on 08-17, 104.4
  today. Pruned Docker build cache (28.2G) and images older than 30 days
  (19.2G): 116.4 → 78.5G on host, free 3.4 → 42G. Left `docker volume prune`
  alone — 32.2G shows reclaimable but 180 of 187 volumes are merely inactive,
  and some are dev DBs; needs a by-name pass first. Images still hold 29.4G
  reclaimable inside the 30-day window. Added the `repos` big-five baseline
  after finding the bucket has no per-tree expectations to diff against, and
  corrected the standing assumption that worktree `node_modules` are hardlink
  duplicates — measured, they aren't.

  Two rows below for this date: the second is post-prune. `repos` also drops
  104.4 → 90.3 between them, which was **not** my doing — `ebutler-qa/workspace`
  went 39G/29 worktrees → 19G/11 during the audit as worktrees were deleted
  from another session. Lesson recorded in the big-five section: size the
  workspace trees per worktree, because a single `du` of them goes stale within
  hours.

- **2026-08-17** — Free space hit 15.1G (floor is 50G), first re-audit since
  baseline. Docker was the mover, +57.8G to 128.7G (over budget) after two weeks
  of heavy outpost + enable/ebchat dev — build cache alone 50.9G, confirming it
  as the recurring offender. `system` also over (58.1 vs 50G budget) from
  go-build/pnpm/go-mod growth; left alone per the table. Cleanup: build cache
  prune (50.8G) + anonymous volume prune (2.9G) = 53.6G freed, **15 → 58G free**.
  Alex chose to keep all unused images (49.2G reclaimable, incl. 3-yr-old
  confluent stack) — actively on outpost, didn't want rebuild churn. Named
  volumes untouched. Docker bucket post-clean: ~85G.
- **2026-08-03 (final)** — Folded `caches` back into `system` (one tooling
  bucket) and gave every bucket a round-number budget, including the previously
  unbudgeted `apps` / `personal` / `other`: 120 / 100 / 50 / 80 / 40 / 70. Sum is
  460G, the whole disk — deliberately, since they're tripwires rather than an
  allocation. Also pinned down units: `df`'s 460 GiB and `diskutil`'s 494 GB are
  the same space, and APFS reserves ~25 GiB so allocatable is ~435 GiB. Every
  bucket within budget at 89.3G free.
- **2026-08-03 (earlier)** — Split `system` out of `caches` and re-derived budgets
  from measured baseline + ~25% headroom instead of invented targets. The old
  `caches` budget (35G) was pushing toward deleting `~/go/pkg/mod` and Claude
  `vm_bundles` — 20G that refills the moment you use Go or the desktop sandbox.
  That's churn, not cleanup. Added `FREE_FLOOR=50` as the real act-now signal,
  and made explicit that budgets are independent tripwires rather than a
  partition of the disk. Every bucket now within budget with nothing deleted.
- **2026-08-03** — `repos` pass, 78.2 → 70.6G (now under budget). Cleared
  `node_modules` from dirs kept for reference (`ebutler-qa/workspace-old` 2.9G →
  379M, `hookdeck-workspace-old` 965M → 717M, `enable-backend` 5.1 → 4.3G), and
  deleted `ebutler-qa/frontend` (4.1G) and `enable-frontend` (2.8G) — both
  superseded by `ebutler-qa/workspace`. `enable-frontend` carried 13 stashes and
  one unpushed `wip` commit, discarded knowingly. Note: one `node_modules` had a
  `user:alexluong deny delete` ACL and needed `chmod -N` before `rmdir`.
- **2026-08-02** — Disk hit 100% full (124Mi free). Freed ~83G: Docker prune
  (build cache 22.3G, anonymous volumes 7.5G, images >30d 41.6G), colima VM +
  uninstall (~5G, arrstack runs on a different device), npm caches (5.9G),
  minikube + platformio (4.2G), `git/hub/hookdeck` node_modules + two dead repos
  (6.3G). Baseline established.
