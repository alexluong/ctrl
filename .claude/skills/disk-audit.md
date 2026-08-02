---
name: disk-audit
description: Audit disk usage on the MacBook Pro when it's filling up — snapshot the six buckets, check them against budget, diff against the last baseline to find what grew, then clean up safely. Use when disk is low/full or to record a fresh baseline. MBP only, not the Mac Mini.
user_invocable: true
---

# Disk Audit

**MacBook Pro only.** The Mac Mini has its own storage and none of these buckets,
paths, or budgets apply to it — if the ask is about the Mini, stop and say so.

Find *what changed* rather than re-deriving the whole disk picture. Baseline,
budgets, bucket definitions, and safety rules: `docs/machine-disk.md`.

## Instructions

1. **Snapshot** — run `bin/disk-audit.sh` from the repo root. Takes ~8 minutes.
   If the disk is so full that tooling fails (sandboxed bash can't `mkdir`), free
   something trivial first — emptying `~/.Trash` is usually enough to unblock.

2. **Diff and check budget** — two separate questions, report both:
   - *Over budget?* Budgets are baseline + headroom, so over means "grew past
     its normal range, go look" — not "this is wasteful". The script also flags
     free space below `FREE_FLOOR` (50G), which is the real act-now signal.
   - *What moved?* Compare against the latest row in `docs/machine-disk.md`,
     biggest mover first. A bucket that didn't move needs no investigation; say
     so and move on.

   A bucket that is over budget **and** grew is the one to work on first.

3. **Explain the mover** — only drill into buckets that actually grew:
   - `docker` → `docker system df -v`. Build cache and images are the usual cause.
   - `repos` → stale `node_modules`:
     `find ~/git ~/code -type d -name node_modules -prune -mtime +90`
   - `caches` → pnpm store, `~/Library/Caches`, `~/.cache`.
   - `system` → growth means a new runtime or tool VM. Worth knowing about, but
     it is NOT a prune target — it refills. Don't propose clearing it to hit a
     number; see the table in `docs/machine-disk.md`.
   - `apps` / `personal` growing is unusual — an install or an app hoarding data.
     Investigate rather than assume.
   - `other` → `du -sh ~/Library/*` and `~/Library/Application Support/*`.

4. **Propose, then clean** — present findings grouped by the safety tiers in
   `docs/machine-disk.md` (safe / ask first / never without checking), with sizes,
   and get agreement before deleting. Then execute.

   Non-negotiable checks:
   - **Before deleting any repo directory**, run `git status --porcelain`,
     `git stash list`, and `git log --branches --not --remotes --oneline` for
     every repo under it. Stashes and unpushed commits exist only locally. Report
     what would be lost and confirm before proceeding. A directory that looks
     like "one old repo" is often a dozen.
   - **Never prune named Docker volumes** without naming them and asking — they
     hold dev databases. `docker volume prune` (no `--all`) spares them; keep it
     that way.
   - **Don't touch running containers** or repos with a live dev stack.

5. **Record** — append the new row (the script prints it) to the snapshot table
   in `docs/machine-disk.md`, and add a line to its History section describing
   what was freed and why. Commit.

6. **Revisit budgets** — if a bucket sits over budget after a genuine cleanup,
   the budget is wrong, not the machine. Propose a new number with a reason and
   update both `bin/disk-audit.sh` and the Budgets table together. Don't silently
   raise a budget to make a verdict pass.

## Notes

- Report real numbers from `df` before and after; don't estimate what was freed.
- Moving files into iCloud Drive does not free space — same volume.
- Deleting `node_modules` in pnpm repos frees less than `du` shows (hardlinks into
  the store); follow with `pnpm store prune`.
