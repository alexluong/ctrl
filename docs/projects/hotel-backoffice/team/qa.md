# QA / review log

Architect reviews each slice dev lands. Worktree: `~/git/hub/alexluong/solex-qa` (detached, read-only; `git fetch && git checkout --detach origin/main`). Local walkthroughs: `SOLEX_DEV_USER=qa` in the worktree `.env` + a seeded `user` row (id `qa-local`, operator) → no sign-in form; `mise run dev` on port 7020. Findings newest first. Blocking = violates decision/spec/data safety; fixed before the next slice.

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
- [ ] **Disable a control only for a no-op, never for a rule.** If the domain can refuse it, the click goes through, the domain refuses, the reason renders (`useCommand` + `CommandError`, `src/ui/command.tsx`). Overbooking override must be clickable. Not unit-testable — click every refused path by hand.
- [ ] `pnpm check` green; staging deploy loads; flow walkable in a browser
- [ ] product.md amended for any gap dev discovered (not just code)

## Findings

- 2026-09-23 — N4 closed (d629752, staging e9c6d416). Real cause: the button was `disabled` while OOO, i.e. the UI enforced a domain rule by hiding the control, so nothing could explain itself. Now disabled only for no-ops; rule refusals render via `useCommand`/`CommandError` (`role="alert"`). Verified locally: click on OOO room → alert with reason, version unchanged, no event. Rule added to checklist.
- 2026-09-23 — **Slice 0a re-review + local walkthrough (origin/main d45adf7, staging 1e81a8d9).** B1 fixed: `recordChange` takes a `prepare` thunk re-run per attempt (regression test forces a real collision, asserts the 2nd decision's event lands). B2 fixed: `runAtomically` throws on a non-batchable write (test asserts nothing written). Dev declined my `UPDATE … WHERE version` suggestion with a correct argument: a zero-row UPDATE inside a batch still commits, so it would turn a lost update into log/table divergence; the stream's UNIQUE is the guard. Agreed. `SOLEX_DEV_USER` bypass: build-time linked runtime module, CF build returns undefined unconditionally, refuses `NODE_ENV=production`, needs an existing row, real session wins, header pill — accepted as distinct from the deleted runtime fallback. 36 green.
  - Walkthrough (local, dev-user bypass, seeded `user` row by SQL, no password): define 101 ✓ · mark dirty ×2 → exactly one `room.marked_dirty` (v2) ✓ · OOO "AC broken" → v3 ✓ · mark clean while OOO → rejected, no event ✓ · history tab shows 3 rows, actor "QA" ✓ · `/system/tables/user` → name/email `••• redacted` ✓ (session table empty under bypass; token redaction covered by unit test) · replay button → "3 events in 1 ms", `rooms` row untouched ✓ (tier b not truncated).
  - **N4 (non-blocking, pattern needed before slice 1):** rule rejection is silent in the UI — "mark clean" on an OOO room did nothing visible; the `{ok:false, code}` result isn't rendered. Slice 1 is full of rejections (room occupied, stay not assignable, overbooking warn+override) so the screen needs one shared way to show a rule code. Not blocking for rooms.
  - N1 (zod at the boundary) → agreed to land with slice 1, not sooner.
- 2026-09-23 — **Slice 0a review: Room flip (0a5aa90, staging fd7bb970).** `pnpm check` green, 34 tests. OK: row + event in one `db.batch` via `recordChange` ✓ (test "leaves no event behind when the row write fails") · event names = §12 ✓ · actor = user id, names resolved at read ✓ · no PII in payloads ✓ · no-op → zero events ✓ · projector registry emptied with reasoning, replay button kept ✓ · rules pure + tested ✓.
  - **B1 (blocking before slice 1 reuses the pattern):** `recordChange` retries on `ConcurrencyError` with the *same precomputed events* and a row read *before* the first attempt (`store.ts` recordChange loop; `rooms/commands.ts` `change()`). Two desks `takeOutOfOrder` the same room: A wins v5; B's append fails on v5, retry re-reads only `streamVersion`, appends a second `room.taken_out_of_order` at v6 and overwrites the row. Violates D-8 clarification (iv) "retry re-reads and redecides". Fix: make the retry re-run read → rules (pass a thunk, like `handleCommand`), and/or make the row write itself the guard: `UPDATE rooms … WHERE version = :seen` and treat 0 changed rows as conflict. Second is cheaper and gives tier (b) a real guard.
  - **B2 (blocking, silent atomicity loss):** `runAtomically` falls back to sequential `await` when any write is not batchable. That's exactly the "row landed, event didn't" case the design forbids, and it fails silently. Fail loud instead (throw `NotBatchable`), or type `writes` so only batchable statements are accepted.
  - N1 (non-blocking, before slice 1 reaches a browser): server fn `.validator` casts `input as {…}` with no runtime check. Booking/Stay payloads from the browser need schema validation (zod/valibot) at the boundary.
  - N2 (tracked): `TODO(D-8)` in `rules.takeOutOfOrder` — must version `availability:<hotel>` + "no checked-in stay tonight" once Stay exists. Closes in slice 1 or overbooking is reachable via OOO.
  - N3 (FYI Alex): housekeeping went 3 → 2 states (`clean|dirty`, per §11); "inspected" gone from staging.
- 2026-09-23 — baseline at origin/main 9f5d3b4: `pnpm check` green (19 tests). Dev's Room flip 0a5aa90 not yet pushed; review when it lands.
