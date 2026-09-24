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

- **Context cap:** Alex keeps every session under **250k** tokens; he compacts. Architect watches via `get_usage` (session ids: dev `local_94ba0f28-75c1-4021-b985-cff336fc9aeb`, qa `local_0640ecfd-d1c2-4094-9c55-9ba59e066319`, product `local_6a799d7c-a89c-4af6-a987-c0d7579a5b29`) and tells Alex in one line when anyone crosses **200k**. Run as a session-only `CronCreate` hourly (off-minute), paused while the team is idle (each check costs ~3.5k of architect's own context) and re-armed when work resumes. Before a compaction: tell the agent to reach a clean stop, commit/push, write a resume note in its profile log, then confirm idle to Alex; re-brief it in one message after.
- **Questions go to architect, not Alex** (dev/QA/product); architect escalates only breaking calls. Alex checks in when he can.
- **Local dev = Node only**: `mise run setup` then `mise run dev` (SQLite `data/solex.db`); Docker stack torn down 2026-09-24 (orphan postgres from the spike removed; compose `up/down/logs` tasks remain unused).
- Architect worktree `~/git/hub/alexluong/solex-architect` (detached, read-only); QA owns `../solex-qa`.


## Resume note — 2026-09-24 (architect at 230k, awaiting compaction)

State: solex main `bc64f12`+`04822c6` (5.6 complete, D-29 built), staging `5250b6e6`, 371 green. Dev in 5.7 (order G14 → G15 → G20 → G28 → SetRoomType → G16/G22/G29/G30 → G32 → G33), at 349k → clean-stop requested. Product (198k) redoing `diagrams/ezfolio-flow/` 1+2 as "SoLex, ezFolio-shaped" (D-27 amendment) then 3–5; I republish per screen to artifact L2ivkCzKDWwXoCFcmF6bKP. QA (108k, **unchanged for hours — check it is receiving messages**) owes R1/R2 flow videos + rrweb replays (`solex/e2e/recordings/`), then 5.5 print, 5.6 cases, S5-37/N28 once G14 lands. Decisions today: D-27 amendment, D-28, D-29 (vi strings: product → dev). Open with Alex: none blocking; flags in progress.md (CF 7403 on D1 migrate, ezFolio 1+2 review superseded by restyle). Cron 5733ce9e = hourly context watch at :41. Stay-template artifact FnYDkwHfpSed7wtQmzgL3L parked.
