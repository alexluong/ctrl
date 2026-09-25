# solex-qa

**Role:** test owner. Turns every accepted rule (product.md §10/§11, decisions D-n) into a numbered test case, keeps the plan current per landing, runs it, files findings. Does not decide design (architect) or scope (product); does not fix (dev).

**Owns:** `../../qa/` (plan, cases, run log) and, in the `solex` repo, `e2e/**` only (Playwright). Reads everything else. Never commits outside those paths; never edits `src/`.

**Reports to:** dev for blocking bugs (message + `qa/runs.md` entry); architect for design smells, spec gaps, "this rule is untestable"; product for wording/behaviour questions (via architect unless trivial).

## Current objective (2026-09-24, rev 1)

1. Read `../../qa/README.md` (how the plan works) and `../../qa/cases.md` (seeded from architect's walkthroughs, slices 0–3). Read `../../team/qa.md` for the history of findings so far.
2. Set up your worktree: `~/git/hub/alexluong/solex-qa` is yours (detached from origin/main; architect moved to `../solex-architect` 2026-09-24), then `mise run setup`, seed a `user` row + `SOLEX_DEV_USER` (see `../../qa/README.md` "Local login").
3. First deliverable: `solex/e2e/` Playwright project running against `pnpm dev` on your worktree port, with specs for cases tagged `e2e` in `cases.md` for slice 1 and 3 (booking → check-in → charge → refused check-out → payment → check-out; overlapping booking refused; rule refusal renders as alert; silent-block regression: every form submits or shows why). Report which cases are now automated by updating the `automated by` column.
4. From then on: per dev landing (dev pings you and architect), add cases for the new rules, run, log in `qa/runs.md`, file findings. Blocking = violates an accepted decision/spec or data safety; dev fixes before the next landing.

## Checklist (from `../../team/qa.md`, keep in sync)

Availability versioned on every supply/demand command · one batch per money command (shared correlationId) · no PII in payloads · `command_id` idempotency on money · disable only for no-op, never for a rule · a blocked submit says why on the page · replay never touches tier (b)/PII tables · migrations additive, applied on a populated DB · `pnpm check` green.

## Inbox expectations

- From dev: "landed: <commits>, staging <version>" per landing.
- From architect: rulings that change expected behaviour (case updates), new decisions.
- From Alex: staging-pass notes to turn into cases.

## Log

- 2026-09-24 — architect: profile created; plan + cases seeded.
- 2026-09-24 — qa: worktree `solex-qa` taken over; e2e suite (solex ef6d242): S3-13, S1-1, S1-2, S0-5 green, S3-14 red (N10). Findings N11, N13 (mise env). Cases S2-12..15, S3-16..24 added.
- 2026-09-24 — qa: slices 3–4 e2e through b364ccd (solex aa34fd7), 78 specs. Findings N14–N19. **Pending on resume:** plain-language S4 block in `qa/cases.md` for Alex (architect's list: account create/update/reset/deactivate/role change, receptionist, no-position, guest history, erasure, correlationId per click, user.created PII, tier (b) creating events, library re-validation, untouched-save no-event across user/guest/contact/room type/rate); product §10 rows 7/7a/8 + §11 company retire (3af0a08) → slice 5 cases; tell dev N19.
- 2026-09-24 — qa: S4 plain-language block (beed8a1), 5.1a companies e2e (solex 423606d), d607656 84/84. N19, N20 closed; N21 (history grouping) and N22 (silent unchanged saves) wait for dev's 5.6 pass, so S4-3 and S4-23..26 stay pending. Waiting for 5.1 landing 2 screens → run S5-6..13. Next free N23.
- 2026-09-24 — qa: 5.1 landings 2–3 e2e (solex b03e8d4, 4c39a3c, e620c3f), 624b7dd 95/96. N23 closed; N24 open (closed group bill still shows its payment form). Next free N25.

- 2026-09-25 — qa: journeys suite (solex 84bd446, d290e53): `e2e/journeys.config.ts`, `pnpm journeys`, port PORT_BASE+2, `data/journeys.db`. The seed runs off camera, then each `*.journey.ts` is filmed in English with a caption bar, writing `e2e/recordings/<name>.webm` + `.rrweb.json` + `player.html` (gitignored; rrweb 2.1.6 inlined from jsDelivr). R1 (desk walk-in) and R2 (owner morning) delivered to architect. S5-41 added (a204175). **Resume:** (1) Run the full suite on main: it hasn't run since 755e585. The balance strip (G31) likely breaks `folioBalance` in `support/desk.ts`, plus there's the settle dialog, bookings list (G13), room map tiles (G5–G7) and dialogs replacing `prompt()` (G3). (2) File for dev as cases: the stay history merges the folio stream; the housekeeping badge reads Clean/Dirty only. Verify N21/N22 (dev 077ab9d) and close them. (3) G14/G15/G20 through the screens: S5-37/N28 are now reachable, plus S5-39/40, party/notes/requests, nights/rates, mixed-type group. (4) Print cases S5-4x; 5.6 map/panel cases S5-5x. (5) Suite-wide rrweb behind `JOURNEY_RRWEB=1`: `test.step` names become markers, one JSON per test. Do it first if it takes under 1 h. (6) One showcase journey per accepted landing. Next free N29.

- 2026-09-25 — qa: no manual compaction anymore (Alex via architect); the resume note is kept current at every milestone. N29 (stay history lacks folio lines) and N30 (badge mixes occupancy in) filed as S5-42/43 and sent to dev. **Resume:** (1) Full suite on c8b3528 running; fix the specs the new screens broke (strip, settle, G13, map, dialogs). Verify N21/N22 and close them. (2) Suite-wide rrweb behind an env flag, with `test.step` markers; the player lists all (D-30). (3) G14/G15/G20/BookingSource/SetRoomType through the screens; then the S5-4x..7x backlog. (4) One showcase journey per accepted landing. Next free N31.

- 2026-09-25 — qa: suite green apart from findings on 30dbec5 (e2e f4308ad); suite-wide rrweb done (`pnpm test:replay`, `support/test.ts`, player lists journeys + suite, lazy per-recording scripts); N29–N31 closed; N32 half fixed, the rest environmental (load avg ~190); N33–N36 filed with dev. **Resume:** (1) Retest when dev lands N33–N36; rerun S5-45/46a/47 on a quiet machine. (2) G14/G15/G20/BookingSource/SetRoomType through the screens: S5-37/N28, S5-39/40, party/notes/requests, nights/rates, mixed-type group grid; G28 agreement (f82ea14). (3) Print cases S5-4x; the map/panel backlog S5-5x..7x. (4) G34 overbooking / G35 capacity cases once dev lands them after G33 (product ctrl 847ff15, product.md §6). (5) One showcase journey per accepted landing. R2 is not re-filmed since the merged history. Next free N37.

- 2026-09-25 — qa: N33–N36 fixed by dev (b4e501e), retest pending. N37 filed (G29: ID required, but check-in has no ID field). Specs written, **not yet run** (load avg ~260; other sessions' stuck python shims): cancel-booking (S5-37/39/40 pass; S5-48..50 G14 landing 2), nights (S5-51..54, G15), setup-changes (S5-55 SetRoomType, S5-56 G28 agreement), house-rules (S5-57/58, G29), S3-34 (Add-to-bill double-submit). All in a local WIP commit in solex-qa, not pushed. **Resume:** once load < 40 (`sysctl vm.loadavg`): run the full suite, fix the specs, push `test(e2e)`, add case rows (S5-48..58, S3-34), close N33–N36. Then G20 mixed-type grid, print S5-4x, the map/panel backlog, then G34/G35 after G33. Next free N38.

- 2026-09-25 — qa: suite green bar findings on e1c113d (e2e pushed); N33–N42 closed; N43 filed (identical "Ask the owner" buttons). Architect and product have been unreachable through 5.8; dev is working from QA's findings. **Resume:** (1) Walk 5.8 approval on screen with a throwaway receptionist account in a second context: ask to void/reprice/refund/write off; the owner's card (dev asks whether it is thin without naming the line and whose bill); approve = one batch (charge_voided and approval.granted share a correlation id; the line carries approvalId); re-decided at grant (void by hand, then Approve → folio.alreadyVoided, request stays open); one open request per line; the request expires at check-out in the same batch; refuse puts its reason on the line. RepriceCharge as owner: revenue moves; the same price is refused; a reason is required. Receptionist under overbooking `allow`. (2) Print S5-4x; the map/panel backlog. (3) Re-film journeys R1/R2 on the current screens. Next free N44.

- 2026-09-25 — qa: 5.8 walked (e2e pushed). N43 closed; N44 (thin approval card, raw user id) and N45 (raw key on a same-price reprice) filed. Dev is idle and led by QA. **Resume:** retest N44/N45; re-film journeys R1/R2 on the current screens (map panel, settle dialog, merged history); print S5-4x; the map/panel backlog; a receptionist under overbooking `allow` (second pass). Next free N46.

- 2026-09-25 — qa: full suite green on 8130240 (desk 154, receptionist 12; e2e 28b2ee5). Raw-key net over every text node. Print and room-map backlog done. No open N. **Resume:** walk whatever dev lands next; a receptionist under overbooking `allow` (second pass); the 92 English-only keys wait on product (dev's handover `agents/solex-dev/notes/2026-09-25-vi-pass-3-handover.md`). If defineRoomType fails in a full run again, its error now names the refusal (seen twice at 5 red, never reproduced alone). Next free N46.

---

**Session prompt (Alex pastes to start the session, named `solex-qa`):**

> You are `solex-qa` for the SoLex project. Read `docs/projects/hotel-backoffice/agents/solex-qa/README.md` in the ctrl repo first, then `docs/projects/hotel-backoffice/qa/README.md`, `qa/cases.md`, `team/qa.md`, `README.md`, `team/log.md`. Follow the roster protocol in `agents/README.md` (one owner per file, commit prefix `docs(hotel-backoffice/qa)`, message peers by session name: `solex-dev`, `solex-architect`, `solex-product`). Start with objective step 2 and 3. Be concise.

- 2026-09-25 — qa: MVP demo journeys (architect, mvp.md §2): R3 group+company, R4 ask the owner, R5 house rules filmed, 6/6 pass (e2e f0c0502, aede635); recordings `solex-qa/e2e/recordings/` (player.html + player/0..4.js, lazy). `dayStartsAt()` shifts the hotel day off camera so R1/R3 check out on departure day (B1). N46–N58 filed with dev; N57 to product (session unreachable, via architect). **Resume:** (1) On dev's "wave 1 stable" ping: pull, full `pnpm test` (B1 same-day check-outs, B3 credit refusal may redden specs → tell dev, don't work around), then `pnpm journeys` re-film all five, check frames, tell architect to republish. (2) Retest N46–N58 as dev lands them; drop R5's name-typing workaround once N46 is fixed. (3) Tighten the raw-key net to catch keys embedded in longer text (N48 slipped past). (4) Case for B3 receptionist path (settle in credit → Ask the owner). Next free N59.
