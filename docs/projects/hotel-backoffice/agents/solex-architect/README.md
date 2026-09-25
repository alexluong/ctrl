# solex-architect

**Role:** cockpit. Holds the whole picture, makes/records decisions, keeps `README.md` coherent, merges cross-WS findings, writes session prompts + these profiles. Talks to Alex most. Does not implement.

**Owns:** `README.md`, `agents/`, `team/decisions.md`, `team/progress.md`, `team/qa.md`, `requirements.md`, `discovery.md`.

## Current objective (2026-09-23, rev 2 — build phase)

Alex: "work with Dev on this and make sure to help with review/QA as we go." Per slice (dev profile rev 6): review diff in `~/git/hub/alexluong/solex-architect` (read-only, detached; `solex-qa` worktree handed to the QA session 2026-09-24) against decisions + product.md using `team/qa.md` checklist, run `pnpm check`, walk the flow, findings → `team/qa.md` + message dev; blocking fixed before next slice. Keep decisions/progress/log current; accept routine decisions under D-21; ping Alex after slices 1 and 3 with what to click on staging. Never commit to `solex`.

<details><summary>rev 1 (2026-09-19, done)</summary>

## Current objective (2026-09-19)

- Get WS1–3 unblocked and non-colliding. Done: dir split, prompts, roster.
- Collect from Alex: discovery brain-dump → `discovery.md`; Hookdeck retention answer; what the `:99` system is.
- Merge: when `existing-system.md` lands, trigger solex-product's second pass. When `stack.md` spike lands, record stack decision.
- Next WS to define: event-store design (Hookdeck-as-log vs bus + archive).

</details>

## Inbox expectations

- From dev: spike result + recommendation; anything needing paid resources.
- From explore: "For other WSs" section ready; what the system is.
- From product: proposed aggregates/events; scope questions for Alex.

## Log

- 2026-09-23 — rev 2: review/QA role added; `team/qa.md` created; QA worktree set up.
- 2026-09-19 — session named; roster created.

## Session ops (Alex's standing asks, 2026-09-24)

- **Context (Alex 2026-09-25, temporarily suspends the 250k/200k rule until the first full iteration is done):** no manual compaction cycles for now. Sessions run continuously and auto-compact; every agent keeps a resume note current in its profile log at each landing/milestone as the safety net. Architect re-briefs in one message after any restart. Session ids: dev `local_94ba0f28-75c1-4021-b985-cff336fc9aeb`, qa `local_0640ecfd-d1c2-4094-9c55-9ba59e066319`, product `local_6a799d7c-a89c-4af6-a987-c0d7579a5b29`. The hourly context-watch cron is retired.
- **Questions go to architect, not Alex** (dev/QA/product); architect escalates only breaking calls. Alex checks in when he can.
- **Local dev = Node only**: `mise run setup` then `mise run dev` (SQLite `data/solex.db`); Docker stack torn down 2026-09-24 (orphan postgres from the spike removed; compose `up/down/logs` tasks remain unused).
- Architect worktree `~/git/hub/alexluong/solex-architect` (detached, read-only); QA owns `../solex-qa`.


## Resume note — 2026-09-25 late (architect, before compaction)

**Phase: demo-able MVP (Alex 2026-09-25), review package delivered, awaiting Alex's full-system review.** Entry point `mvp.md` (core, demo script R1–R9, edge cases incl. rulings, follow-ups, open questions). v1 functionality complete; nothing new gets built without Alex.

- **Review package**: player https://claude.ai/artifact/RrF94hDrGJ8QWPaecge4xN (nine journeys, Oanh owner / Dao receptionist, filmed on solex c4b0350; republish = `player.html` page + `player/0..8.js` as `files` from `solex-qa/e2e/recordings/`; scratchpad path `solex-journeys.html`). Docs `qa/journeys/` (README + R1–R9 with product's "In ezFolio today"). Old artifact PnZfbQDz5dZdxxef5U8JFr retired (can't republish: self-contained, 528KB read).
- **Code review 2026-09-25**: `review/2026-09-25-{quality,correctness,analysis}.md`, artifact https://claude.ai/artifact/EeDpiBCWeMbaFuE92jNrtF. Wave 1 (B1–B4, B8) landed. **Wave 2 with dev** (B5 read-side role gate, B6 operator guard, B7 version availability on group create/add, B9 transfer cap, B10 approval method, B12 cancel group w/ terminal stays, B13 first staff = owner, B14 refund cap incl. forfeits, B15 default roll 02:00 + openAccount no-op, A3 grant inside plan) — accept per landing, log, no restructuring. Rest in mvp.md §4.
- **Rulings today**: minimum one night on early check-out (same-day in/out pays one night); reprice keeps original businessDate; check-out in credit refused; move from today; void in-house room line refused → reprice; overbooking override on new-booking form only; "As agreed" doesn't clear room overrides; N57 approval ask/answer in stay history; per-language Setup display names = follow-up (Alex deferred to me).
- **Open with peers**: dev's N51 (stored memo language) / N52 (company slug) questions never reached me — ask again. Product idle (vi complete; §10 amended). QA idle after package; N-numbers next free ~N65.
- **Alex**: reviewing the nine journeys; feedback → findings for dev/product via me. Deferred the code-review handling to me.
- Peer ids: dev local_94ba0f28-75c1-4021-b985-cff336fc9aeb, product local_6a799d7c-a89c-4af6-a987-c0d7579a5b29, qa local_0640ecfd-d1c2-4094-9c55-9ba59e066319 (names often unreachable; ids work).

## Resume note — 2026-09-25 (architect, before compaction)

**State:** slice 5.7 command coverage nearly done. Landed and accepted today: slice-4 debts N21/N22 + quiet nothingToChange notice; G14 (cancel, party/notes/requests), G15 (nights, per-night rate), G20 (mixed-type groups + freeByType grid), BookingSource (= G30 + §3, not G28), SetRoomType (G8 debt closed, one-code ruling `setup.roomTypeInvalid`), G16 MoveCharge (room charge stays with the guest who slept the night), G22 guest/contact edit + stay_guests, G28 company defaultRouting. Latest: solex f82ea14, 439 green.
**Dev now:** G29 BookingRules, ruled (b): row carries all five §11 fields, form shows only what is read. Then G32 routing table → G33 owner home + NeedsAttention → G34 overbooking → G35 capacity (both spec'd by product, ctrl 847ff15, accepted) → 5.8 approvals (D-28). Alex's priority: all v1 functionality before his big UX review; estimate ~3 dev cycles.
**QA:** suite on new screens 110/118 (e2e f4308ad); N29–N31 closed; N33 (double-submit safety lost since 8716fc2), N34, N35, N36 with dev; N32 hangs = machine load. D-30 suite-wide rrweb live (`JOURNEY_RRWEB=1 pnpm test:replay`). Next: screen pass G14/G15/G20/BookingSource/SetRoomType, then S5-4x..7x. R1/R2 replays published: https://claude.ai/artifact/PnZfbQDz5dZdxxef5U8JFr.
**Product:** vi pass 1 committed (18da91f), pass 2 (24 keys) sent to dev; reach product via `SendMessage` to its session id when the name is unreachable (idle process). Mockups artifact L2ivkCzKDWwXoCFcmF6bKP unreviewed by Alex.
**Process:** manual compaction suspended for now (temporary); context-watch cron retired; every agent keeps its resume note current per landing. replay-demo session was handed the rrweb setup for product/OSS evaluation (docs/projects/replay.md, not SoLex's).
**Open for Alex:** machine load ~180 from stuck `pyenv exec python3` shims across sessions (`pkill -f "pyenv exec python3"`); CF 7403 migrate flake; no staging smoke pass since 5.6.

## Resume note — 2026-09-24 (architect at 230k, awaiting compaction)

State: solex main `bc64f12`+`04822c6` (5.6 complete, D-29 built), staging `5250b6e6`, 371 green. Dev in 5.7 (order G14 → G15 → G20 → G28 → SetRoomType → G16/G22/G29/G30 → G32 → G33), at 349k → clean-stop requested. Product (198k) redoing `diagrams/ezfolio-flow/` 1+2 as "SoLex, ezFolio-shaped" (D-27 amendment) then 3–5; I republish per screen to artifact L2ivkCzKDWwXoCFcmF6bKP. QA (108k, **unchanged for hours — check it is receiving messages**) owes R1/R2 flow videos + rrweb replays (`solex/e2e/recordings/`), then 5.5 print, 5.6 cases, S5-37/N28 once G14 lands. Decisions today: D-27 amendment, D-28, D-29 (vi strings: product → dev). Open with Alex: none blocking; flags in progress.md (CF 7403 on D1 migrate, ezFolio 1+2 review superseded by restyle). Cron 5733ce9e = hourly context watch at :41. Stay-template artifact FnYDkwHfpSed7wtQmzgL3L parked.
