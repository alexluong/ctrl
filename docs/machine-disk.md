# Machine Disk Baseline

**MacBook Pro only** (460G volume). The Mac Mini is a separate machine with its
own storage — none of this applies there. Devices: `docs/machine.md`.

Purpose: when the disk fills up again, compare a fresh snapshot against the last
one to see *which bucket moved* instead of re-deriving the whole picture from
scratch. Run `bin/disk-audit.sh` (~8 min, mostly `du` over node_modules).

## Buckets

Six buckets, defined in `bin/disk-audit.sh`. Split by whether they regrow on
their own — that split is the whole point, because regressions are almost always
volatile and cleanups should almost never touch stable.

| Bucket | Kind | What's in it |
|---|---|---|
| `docker` | prunable | `~/Library/Containers/com.docker.docker` (the `Docker.raw` VM disk) |
| `repos` | prunable | `~/git`, `~/code` — dominated by `node_modules` |
| `caches` | prunable | pnpm store, `~/Library/Caches`, `~/.cache`, `~/.npm` |
| `system` | baseline | `~/go` module cache, Claude `vm_bundles`, mise/bun/asdf/pyenv/cargo, AI tool state |
| `apps` | stable | `/Applications`, `/opt/homebrew` |
| `personal` | stable | Messages, Pictures, Documents, Downloads, Music, iCloud local, Spark mail |
| `other` | — | Everything else: rest of `~/Library` (Application Support, Metadata, Containers besides Docker), `/Library`, OS. Steam and other App Support data land here. |

**Why `system` is separate from `caches`.** Everything in `system` is technically
deletable, but it refills to the same size the moment you use the tool, so
clearing it is churn rather than cleanup:

- `~/go` (11G) — Go has no prune-unreferenced for the module cache, unlike
  `pnpm store prune`. It's all-or-nothing, and a rebuild re-downloads what your
  live projects need.
- Claude `vm_bundles` (9.1G) — the Claude *desktop app's* Linux sandbox VM
  (`rootfs.img` + a compressed warm-start image). Binary, not accumulated;
  deleting only helps permanently if you don't use that feature.
- mise / bun / asdf / pyenv / cargo (7.4G) — installed language runtimes. Not
  cache at all. "Pruning" them means uninstalling versions you use.

`caches` after the split is genuinely transient: things with a real prune command
we'd actually run.

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
| `repos` | 70.6G | **90G** | Headroom for a couple of fresh worktree installs. |
| `caches` | 14.7G | **22G** | Genuinely transient after the `system` split. |
| `system` | 29.2G | **36G** | Shouldn't move much. Growth here means a new runtime or tool VM, worth knowing about but not pruning. |

Also `FREE_FLOOR=50` — **free space below 50G is the real act-now signal**,
independent of buckets.

Budgets are **independent tripwires, not a partition of the disk.** They sum past
capacity on purpose, because the buckets don't all peak at once. Don't try to
make them add up to 460G.

`apps` and `personal` stay unbudgeted — changes there are decisions (uninstall a
game, delete messages), not maintenance.

Budgets live in `bin/disk-audit.sh` as `BUDGET_*`. Revise them here and there
together, and note the change in History.

### How to prune each bucket

**`caches`** (14.7G) — `pnpm store prune`, plus `~/Library/Caches` (ms-playwright
2.1G is safe; CloudKit is system-managed, leave it) and `~/.cache` (puppeteer,
amp-repos). pnpm's store only releases what no `node_modules` still hardlinks, so
prune `repos` *first*, then the store.

**`system`** (29.2G) — **don't, routinely.** It refills. Only reach for it when
genuinely desperate, and know what you're buying:

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

## Optimization backlog

Neither of these is a cleanup — they're structural changes that would lower the
floor. Worth a dedicated session.

- **`repos` — reduce duplication.** ~40G of `node_modules` across worktrees that
  largely share dependencies. Open questions: can `ebutler-qa/workspace` (11
  worktrees) and `hookdeck-workspace` (5) share a single pnpm store properly, or
  are some on npm/yarn and duplicating outright? Are `workspace-old` (2.9G) and
  `hookdeck-workspace-old` (965M) still needed? Is `ebutler-qa`'s loose
  `enable-backend` / `enable-frontend` / `frontend` (12G) superseded by the
  workspace? Standardising on pnpm across these repos is probably the single
  biggest structural win.
- **`docker` — reduce image footprint.** 34.8G of images, 20.4G of volumes, with
  ~13.6G of volumes unused. Worth auditing which named volumes are still live dev
  DBs vs abandoned, and whether the large `server-*` images (~5G each) share base
  layers or are rebuilt from scratch each time.

## Snapshots

All values in GB.

| Date | Used | Free | docker | repos | caches | system | apps | personal | other |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-02 | 349.3 | 83.6 | 70.9 | 78.2 | 45.8* | — | 71.3 | 30.6 | 52.5 |
| 2026-08-03 | 345.7 | 89.2 | 70.9 | 70.6 | 44.0* | — | 71.3 | 30.6 | 58.3 |
| 2026-08-03 | 345.6 | 89.3 | 70.9 | 70.6 | 14.7 | 29.2 | 71.3 | 30.6 | 58.2 |

\* Pre-split: these `caches` values still include what is now `system`, so they
aren't comparable to later rows. Compare against the third row onward.

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

- **2026-08-03 (later)** — Split `system` out of `caches` and re-derived budgets
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
