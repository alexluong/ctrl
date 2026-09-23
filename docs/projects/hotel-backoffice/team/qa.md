# QA / review log

Architect reviews each slice dev lands. Worktree: `~/git/hub/alexluong/solex-qa` (detached, read-only; `git fetch && git checkout --detach origin/main`). Findings newest first. Blocking = violates decision/spec/data safety; fixed before the next slice.

## Checklist per slice

- [ ] Every supply/demand command versions `availability:<hotel>` in the same batch (D-8 list: assign/change room, dates change, check-in w/ assignment, OOO/return, room retire/type change, overbooking override)
- [ ] Event names `agg.past_verb`, envelope fields per D-12; `schema_version` set; types never renamed
- [ ] `command_id` UNIQUE + duplicate → original result (D-12 clarification); money commands idempotent
- [ ] Tier split honoured (D-22): Booking/Stay/Ledger fold; Room/Setup/Guest/User rows are truth + event appended in same batch
- [ ] No PII in event payloads — ids only (D-20); new sensitive columns on the D-23 denylist
- [ ] Projections written in the same `batch()`; `rebuildProjections` reproduces them (truncate → replay → diff)
- [ ] Reactions (§10) run once inline, not on replay
- [ ] `requireUser()` on every server fn; owner-only commands guarded (from slice 4)
- [ ] `decide` functions unit-tested incl. the reject paths; conflict retry tested
- [ ] `pnpm check` green; staging deploy loads; flow walkable in a browser
- [ ] product.md amended for any gap dev discovered (not just code)

## Findings

- 2026-09-23 — baseline at origin/main 9f5d3b4: `pnpm check` green (19 tests). Dev's Room flip 0a5aa90 not yet pushed; review when it lands.
