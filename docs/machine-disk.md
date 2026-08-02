# Machine Disk Baseline

Disk usage baseline for the Mac (460G volume). Machine layout: `docs/machine.md`.

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

## Snapshots

All values in GB.

| Date | Used | Free | docker | repos | caches | apps | personal | other |
|---|---|---|---|---|---|---|---|---|
| 2026-08-02 | 349.3 | 83.6 | 70.9 | 78.2 | 45.8 | 71.3 | 30.6 | 52.5 |

Baseline taken right after a large cleanup (see below), so it's a *clean* floor,
not a typical day. Volatile 194.9G / stable 101.9G.

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
