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
| `docker` | volatile | `~/Library/Containers/com.docker.docker` (the `Docker.raw` VM disk) |
| `repos` | volatile | `~/git`, `~/code` — dominated by `node_modules` |
| `caches` | volatile | pnpm store, `~/go`, mise/bun/asdf/pyenv/cargo, `~/Library/Caches`, `~/.cache`, Claude `vm_bundles`, AI tool state |
| `apps` | stable | `/Applications`, `/opt/homebrew` |
| `personal` | stable | Messages, Pictures, Documents, Downloads, Music, iCloud local, Spark mail |
| `other` | — | Everything else: rest of `~/Library` (Application Support, Metadata, Containers besides Docker), `/Library`, OS. Steam and other App Support data land here. |

If you change a bucket's paths, past snapshots stop being comparable — note the
change below when you do.

## Budgets

What we've **chosen to allocate**, not what happens to fit. Over budget means
prune — regardless of how much free space is left. The point is to act on a
number we picked rather than waiting for the disk to hit 100% again.

| Bucket | Budget | Rationale |
|---|---|---|
| `docker` | **120G** | Docker is the primary dev runtime here and gets room to work — starving it just means re-pulling and rebuilding constantly. Multi-service stacks (hookdeck core, enable, outpost) plus dev-DB volumes are genuinely large. Over budget means prune cache/dead images, not "use Docker less". |
| `repos` | **80G** | ~40G of actual source across `~/git` + `~/code`, plus roughly one full set of `node_modules`. Over means stale worktree installs. |
| `caches` | **35G** | Floor is ~12G (see below); 35G allows ~23G of accumulated cache before it's worth a pass. Fully reclaimable, so the cheapest bucket to enforce. |
| **volatile total** | **235G** | Leaves ~70G free at budget, against ~153G of stable + system. |

Stable buckets (`apps`, `personal`) are deliberately unbudgeted — there's no
routine pruning to do, and changes there are decisions (uninstall a game, delete
messages), not maintenance.

Budgets live in `bin/disk-audit.sh` as `BUDGET_*` and the script prints a verdict
per bucket. Revise them here and there together, and note the change in History.

### How to prune each bucket

**`caches`** — not at its floor. Measured 2026-08-02 at 46.1G, decomposing as:

| Item | Size | Prunable? |
|---|---|---|
| `~/go/pkg` (module cache) | 11G | yes — `go clean -modcache` |
| `~/Library/pnpm` (store) | 11G | partly — `pnpm store prune` drops unreferenced only |
| Claude `vm_bundles` | 9.1G | yes — regenerates |
| `~/Library/Caches` | 4.7G | partly — ms-playwright 2.1G yes; CloudKit 2.2G is system-managed, leave it |
| mise / bun / asdf / pyenv / cargo | 7.4G | **no — floor.** Installed runtimes, not cache. Pruning means uninstalling versions. |
| `.local/share` claude + opencode | 1.6G | no — tool state |
| `~/.cache` (puppeteer, amp-repos) | 1.1G | yes |

So ~23G is genuinely reclaimable and the floor is ~12G. Order of value:
`go clean -modcache` (11G) → `vm_bundles` (9.1G) → playwright + `~/.cache` (3G)
→ `pnpm store prune` (varies). Note pnpm's store only releases what no
`node_modules` still hardlinks, so prune repos *first*, then the store.

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

| Date | Used | Free | docker | repos | caches | apps | personal | other |
|---|---|---|---|---|---|---|---|---|
| 2026-08-02 | 349.3 | 83.6 | 70.9 | 78.2 | 45.8 | 71.3 | 30.6 | 52.5 |

Baseline taken right after a large cleanup (see below), so it's a *clean* floor,
not a typical day. Volatile 194.9G / stable 101.9G — within the 235G budget,
with `caches` the only bucket over (46.1G vs 35G).

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

- **2026-08-02** — Disk hit 100% full (124Mi free). Freed ~83G: Docker prune
  (build cache 22.3G, anonymous volumes 7.5G, images >30d 41.6G), colima VM +
  uninstall (~5G, arrstack runs on a different device), npm caches (5.9G),
  minikube + platformio (4.2G), `git/hub/hookdeck` node_modules + two dead repos
  (6.3G). Baseline established.
