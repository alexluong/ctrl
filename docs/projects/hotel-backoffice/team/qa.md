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

- 2026-09-23 — **Slice 0a review: Room flip (0a5aa90, staging fd7bb970).** `pnpm check` green, 34 tests. OK: row + event in one `db.batch` via `recordChange` ✓ (test "leaves no event behind when the row write fails") · event names = §12 ✓ · actor = user id, names resolved at read ✓ · no PII in payloads ✓ · no-op → zero events ✓ · projector registry emptied with reasoning, replay button kept ✓ · rules pure + tested ✓.
  - **B1 (blocking before slice 1 reuses the pattern):** `recordChange` retries on `ConcurrencyError` with the *same precomputed events* and a row read *before* the first attempt (`store.ts` recordChange loop; `rooms/commands.ts` `change()`). Two desks `takeOutOfOrder` the same room: A wins v5; B's append fails on v5, retry re-reads only `streamVersion`, appends a second `room.taken_out_of_order` at v6 and overwrites the row. Violates D-8 clarification (iv) "retry re-reads and redecides". Fix: make the retry re-run read → rules (pass a thunk, like `handleCommand`), and/or make the row write itself the guard: `UPDATE rooms … WHERE version = :seen` and treat 0 changed rows as conflict. Second is cheaper and gives tier (b) a real guard.
  - **B2 (blocking, silent atomicity loss):** `runAtomically` falls back to sequential `await` when any write is not batchable. That's exactly the "row landed, event didn't" case the design forbids, and it fails silently. Fail loud instead (throw `NotBatchable`), or type `writes` so only batchable statements are accepted.
  - N1 (non-blocking, before slice 1 reaches a browser): server fn `.validator` casts `input as {…}` with no runtime check. Booking/Stay payloads from the browser need schema validation (zod/valibot) at the boundary.
  - N2 (tracked): `TODO(D-8)` in `rules.takeOutOfOrder` — must version `availability:<hotel>` + "no checked-in stay tonight" once Stay exists. Closes in slice 1 or overbooking is reachable via OOO.
  - N3 (FYI Alex): housekeeping went 3 → 2 states (`clean|dirty`, per §11); "inspected" gone from staging.
- 2026-09-23 — baseline at origin/main 9f5d3b4: `pnpm check` green (19 tests). Dev's Room flip 0a5aa90 not yet pushed; review when it lands.
