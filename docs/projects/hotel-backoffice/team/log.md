# Team log
- 2026-09-25 — Alex: do five journeys demonstrate the full system? No (Setup, stay changes, cancellation path, back office uncovered). Queued R6–R9 with QA after the wave-1 re-film; mvp.md §2 lists nine.
- 2026-09-25 — Ruling (B1 detail, dev vs product): **minimum one night** — a checked-in stay keeps its arrival night; same-day in/out pays one night; early check-out drops only nights after arrival. Dev's implementation stands; product to amend §10 6a. QA journey docs live in qa/journeys/ (README + R1–R5, do-not-demo list) since 9f90b40; R3 re-film includes a room-level routing exception (301 laundry → group).
- 2026-09-25 — QA: R3 group + company, R4 ask the owner, R5 house rules filmed and passing (solex e2e f0c0502 + aede635); player now lazy-loads player/<n>.js. Draft (pre wave 1) published as a new multi-file artifact https://claude.ai/artifact/RrF94hDrGJ8QWPaecge4xN (old self-contained one retired). R1/R3 move the hotel day off camera so check-out is next morning (B1). 13 on-screen findings N46–N58 with dev (N46 ID dropped beside placeholder name, N47 reprice card lacks the asked price, N53 bill-line subtitle still Vietnamese). N57 ruled: approval ask/answer belong in the stay's merged history. Re-film all five once wave 1 is stable.
- 2026-09-25 — Product applied review rulings B1 (§10 6a/6c, §6 Stay, §11 CheckOut: reversal `folio.charge_voided {cause: earlyCheckOut}` in the same batch, folio-0 guard after it) and B14 (refund cap incl. forfeits) — ctrl a784430. Same-day in/out now pays no room night; recorded in mvp.md §3. QA told by product.
- 2026-09-25 — Code review (Alex's ask): two read-only reviewers on solex 9b30ff9. A quality B+ (architecture real; copy-paste ledger write, nested account-open commits, read models in adapters, role-name checks in UI, comment rot). B correctness: ledger/replay/idempotency/tenancy hold; four reproduced demo-path bugs (early check-out charges + holds today's night; reprice past night re-billed by the roll; check-out in credit strands the refund; move in-house rewrites slept nights) + 10 before-real-use holes. Architect rulings + routing in review/2026-09-25-analysis.md: wave 1 (B1–B4, B8) to dev now; wave 2 after; rest → mvp.md §4.
- 2026-09-25 — vi pass 3 landed (dev, solex 2f61ef9, staging eef708e5): all 92 keys, i18n:report clean, 517 green; one vi-rendering test re-aimed at the raw-key invariant. Vietnamese is complete; language is no longer a demo gate. Product fixed §10 rule 1 (cfb0a3f). Dev + product idle; QA filming R3–R5.
- 2026-09-25 — product: vi pass 3 (92 keys) sent to dev (ctrl 6ecc7f4); mvp.md checked: ChargeItem catalogue spec'd but never built → follow-up; People row added to §1; six follow-ups added to §4 (custom roles, guest merge/VIP, ghép đoàn, receivable due dates, ExpenseCategory, day-of-week rates); ux.md screen redraws dropped for D-30. Product to fix §10 rule 1 wording (cron is live in wrangler.jsonc).
- 2026-09-25 — dev reviewed mvp.md: accurate; two open rulings closed for the MVP — (1) overbooking override stays on the new-booking form only, other paths refuse (follow-up); (2) G32 "As agreed" does not clear a room's own routing setting (keep as built). vi note: `approvalKind.*` fragments need a vi wording decision. Repo clean at 8130240, 517 unit green, migrations 0018–0020 applied dev + remote.
- 2026-09-25 — Alex: goal is a **demo-able MVP, not production**; prune docs, track follow-ups. Architect wrote `mvp.md` (entry point: core, demo script R1–R5, known edge cases, follow-ups, open questions); README/progress point at it; progress "Flag for Alex" folded in. Dev/QA/product re-briefed: no new features; QA films R3–R5; product vi pass 3 (92 keys) if demo is vi.
- 2026-09-25 — (architect catch-up after compaction) dev landed the rest of v1 unrouted while architect/product were unreachable: G29 house rules (3e9b447, form shows only the two rules that are read), G32 group routing table (d2e4199), G33 Needs attention + badge (ae22949, derived never stored), G34 overbooking check + override (2978428), G35 capacity + SetOccupancy (e85263b), reprice = void + re-post (a6df655), 5.8 approvals in three landings (a0beb3c, 41f2d3b, 5603ad8, e1c113d — "no unbuilt row left in §11"), QA N33–N45 fixed, vi pass 2 applied (74f99e3), every refusal/event has a sentence (a129a06, 8130240). QA: suite fully green on 8130240 (desk 154 + receptionist 12), raw-key net over every text node, S5-72..85 cases, R1/R2 re-filmed, staging e00bc289. Architect accepts all of it as landed; rulings stand as dev applied them.
- 2026-09-25 — QA (e2e f4308ad, ctrl b6cf721): suite on 30dbec5 110/118, specs updated for the new screens; N29/N30/N31 closed; new N33 double-submit safety lost since the command-id fix 8716fc2, N34 report prints source id 'walk-in', N35 G22 half-ID refused as input.invalid, N36 group's bill has no Move; all with dev. D-30 suite-wide capture live: `JOURNEY_RRWEB=1 pnpm test:replay`, test.step + page visits as markers, player groups journeys/suite and lazy-loads replays. N32 hangs track machine load (load avg ~190: a VM + stray python shims from several sessions). QA → screen pass for G14/G15/G20/BookingSource/SetRoomType, then S5-4x..7x.
- 2026-09-25 — Product spec'd G34/G35 (847ff15), accepted: override = `override?: true` on the adding command, OverrideOverbooking retired unbuilt; BookingRules.overbooking refuse|warn|allow (default warn) + capability stay.overbook; refuse availability.overbooked; only added nights checked, supply-side never refuses; G35 adults ≤ RoomType.capacity, children not counted, stay.overCapacity, new SetOccupancy. Vi pass 2 (24 pairs) sent to dev. Forwarded to dev; order G29 → G32 → G33 → G34 → G35 → 5.8.
- 2026-09-25 — G28 company defaultRouting landed (f82ea14, 439 green): company card with eight three-state selects (not said = fall through), UpdateCompany's first caller, kept deposit excluded (posted by its own command, never routed), selects in ui/routing.tsx for G32. G29 ruling: (b) BookingRules row carries all five §11 fields, the form shows only what is read (autoDirtyOnCheckout, idEnforcement now; the two day thresholds arrive with G33). Gap found: no capacity enforcement, no overbooking check, no OverrideOverbooking despite §11. New items after G33: **G34 overbooking** (warn when freeByType goes negative at create / requests add / ChangeNights, explicit OverrideOverbooking{stayId}, reads `overbooking`), **G35 capacity** (guests vs room-type capacity, children under childAgeThreshold not counted). Product to spec both briefly; product session idle, vi pass 2 (24 keys) also waiting on it.
- 2026-09-25 — G16 MoveCharge + G22 guest/contact edit landed (solex 30dbec5, staging a2476da4, 437 green, migration 0018 stay_guests). Ruling confirmed: a room charge stays with the guest who slept the night (own folio ↔ group master only; folio.roomChargeStays otherwise); desk keeps the command; picker = in-house tonight + master. G22: edit form on person page, contacts linked, 'where they stayed' from stay_guests (ids only, survives erasure). vi pass 1 committed (18da91f). QA N29 (folio.* merge via events.ofStayAndBill), N30, N31 fixed, N32 client half fixed; N32 server half (getViewer GET never completes on vite dev) open, QA to test under wrangler dev; not a v1 blocker if vite-only. One-code ruling applied. 24 new keys → product pass 2. Dev → G28 defaultRouting.
- 2026-09-25 — Alex: 'just continue iterating with Dev & QA, no compaction needed'. Manual compaction protocol retired (200k clean stops, hourly context-watch cron). Sessions auto-compact; resume notes kept current per landing. Dev, QA told; product session not reachable at the moment (idle process), will get it on next contact.
- 2026-09-25 — Product vi pass 1: 65 key → vi pairs for c8b3528 sent to dev (recorded in product notes/vi-pass-1.md, b105aa1); folio.void 'Huỷ' → 'Huỷ khoản'. Dev to apply + commit; product idle at ~95k.
- 2026-09-25 — Alex compacted dev, QA, product; all three re-briefed. Dev: G16 → G22 → G28 defaultRouting → G29 → G32 → G33 (+ one-code ruling, QA (b)(c)); QA: suite on main, file two cases, suite-wide rrweb, screen pass; product: 65-key vi pass via dev, Void≠Cancel in vi. Alex's priority: all v1 functionality before his UX pass.
- 2026-09-25 — Alex opened a `replay-demo` session to evaluate the rrweb journeys setup as a possible product/OSS project. Architect sent the high-level handoff (what exists, costs, rough edges, ideas, comparables); QA asked to send the implementer's note. Not a SoLex deliverable; SoLex keeps using the setup per D-30.
- 2026-09-25 — SetRoomType landed (c8b3528, staging e8ec202d, 419 green): select on every Setup rooms row incl. type-unknown rooms (G8 debt closed), allowed with a guest in the room, versions availability:all, proven through freeByType. Ruling: one code for one fact — `setup.roomTypeInvalid` (product's, covers unknown + retired) replaces `room.typeUnknown` on defineRoom; fold into next landing. i18n 65 keys. Dev clean stop at 287k, resume note 850d112; next G16 → G22 → G28 defaultRouting → G29 → G32 → G33 + QA (b)(c).
- 2026-09-25 — QA confirms the define-room silent drop is gone on `8716fc2` (seed 3/3 without the retry, S5-41 define passed); architect closed it, no N number, stamp collision ruled out. Void on a closed bill: refused server-side, no defect.
- 2026-09-25 — QA clean stop at 201k (solex a204175, ctrl 65bbadd, resume note in QA profile log). Define-room drop confirmed gone on 8716fc2 (in-flight getQuote before defineRoom in the one trace; stamp ruled out); no N number. Void on closed bill refused server-side, no defect. For product: vi ask dialog has Void and Cancel both 'Huỷ'. QA resume: full suite on current main first (G31/G13/G3/G5–G7 will break old specs), then file stay-history-merge and Clean/Dirty cases, then suite-wide rrweb capture.
- 2026-09-25 — dev: **SetRoomType landed, G8's debt closed** (solex `c8b3528`, staging `e8ec202d`, 419 green). Select on every row of the Setup rooms table; allowed with a guest in the room (product's ruling — the nights already carry their price, a type after the sale is a label and tomorrow's bucket); versions `availability:all`, proved by a scenario watching the double go to 0 and the suite to 1 through `freeByType`; unknown and retired types are one refusal. **Wart flagged:** `setup.roomTypeInvalid` (product's spelling, SetRoomType) vs `room.typeUnknown` (defineRoom) — two codes for one fact, unruled. **Dev at a clean stop for compaction; resume note below.**
- 2026-09-25 — BookingSource accepted (both landings, walk-in default, 414 green, staging c35d5e23). Numbering corrected: this is G30 + product §3, not G28 (G28 = company defaultRouting, still in the order). Dev's shared command-id fix is the likely cause of QA's define-room silent drop; QA re-verifying. Dev → SetRoomType.
- 2026-09-25 — dev: **5.7 G28 — BookingSource, both landings + a silent-drop fix** (solex `8716fc2`, staging `c35d5e23`, 414 green, migration 0017 dev + remote). Landing 1: `BookingSource` as a tier-b Setup entity per product `50a07b7` — name + one of four fixed buckets (the client's WALK-IN · OTA · TA · CORP), slug id, retire refused by nothing (a booking keeps the id it was taken with), `seedDefaults` for the v1 ten, Setup screen section. **`CreateBooking` now writes `walk-in` when nobody said**, so revenue-by-source has no "not recorded" row going forward; the payload keeps `sourceId?` and the report keeps its null bucket for what came before. Landing 2: source select beside "Billed to" (picking a company flips an *untouched* default to `company`, never a set one), name on the bookings list column and the booking header. **Numbering:** architect has been calling this G28, but ux.md's G28 is the company `defaultRouting` control — this work is really G30 + product §3's New-booking row; flagged for a docs fix. **Also fixed (QA (a) candidate):** one `useCommand` serves a whole screen, and its retry slot was shared, so a second command started while another was in flight took the first's id and the server answered it as a repeat — nothing written, nothing refused, `ok` back, form clears. Now an id is reused only when its attempt went unanswered and nothing else is waiting; `retryId` extracted and unit-tested. Offered as a candidate, not a confirmed repro. Also rebased twice onto QA's e2e pushes — solex main is shared now.
- 2026-09-25 — D-30: rrweb journeys are the standing review format (Alex: 'definitely prioritize the rrweb journeys, build them out as we continue testing'). QA briefed: suite-wide capture behind env flag + one showcase journey per accepted landing.
- 2026-09-25 — R2 owner morning delivered (QA, solex d290e53, 54 s; 12 min of work): dashboard → revenue → Owed → company statement → bank-transfer payment with reference → tile 103 → stay → void laundry line with reason → history → room page. R1 re-recorded same run. Player republished with both (same artifact). QA findings routed: define-room on /setup silently drops ~2/7 runs (real defect, repro to dev, top priority); ruled stay history merges stay + folio streams; ruled housekeeping badge = Clean/Dirty only, no 'Vacant'; void-on-closed-bill under empirical check; seed actor = persona fine. QA next: G14/G15/G20 through screens, then S5-4x..7x.
- 2026-09-25 — R1 pair delivered (QA, solex 84bd446: `pnpm journeys`, port 7022, data/journeys.db; recordings/ gitignored): webm 53 s + rrweb JSON + self-contained player.html (journey picker, step markers, clickable step list seeks; rrweb 2.1.6 inlined, cdnjs lacks it). Flow: map → Ready → tile 302 panel → booking → check in → minibar → settle cash → check out → 302 dirty. Published for Alex: https://claude.ai/artifact/PnZfbQDz5dZdxxef5U8JFr. QA time log: real work ≈50 min, half adapting to the day's UI changes; the rest of the '1h' was queued messages. Open: seed flaked 1/5; Void buttons show on a closed bill (N29 candidate). QA → R2.
- 2026-09-25 — dev: **G20 follow-up, both rulings** (solex `f6c98a4`, staging `69527878`, 404 green). The tape chart's free-of-this-type row and the hotel-wide free row now come from `calendar.freeByType` — one read owns that number, so the chart and the group grid cannot disagree; `used` and occupancy % stay room-based (rooms slept in, the occupancy report's pair). Kind select moved above the lines it controls, and **switching back to individual now drops all but the first line** — a leftover group line would have quietly booked a walk-in three rooms.
- 2026-09-25 — G20 landed (ee8513b, staging 920da5f3, 404 green): booking form one line per room kind (mixed-type groups; CreateBooking already took an array); new read hotel.calendar.freeByType drawn as the group availability grid. Accepted: unassigned nights subtracted, OOO in neither number (same denominator as N27), free returned signed and drawn as a warning, line stays submittable (N25); assigned night counts under the room's actual type. Rulings: calendar G9 footer must use freeByType (one read owns the number); Kind select moves above the lines. i18n 48 keys. Dev → G28 BookingSource.
- 2026-09-25 — dev: **5.7 G20 — mixed types per group + the availability grid** (solex `ee8513b`, staging `920da5f3`, 404 green). The booking form is now one line per kind of room, so "ten doubles and two twins" is one group instead of two bookings — `CreateBooking` has taken an array since groups landed; the form could not say it. New read `hotel.calendar.freeByType(from, to)` → rooms left per type per night: **nights held without a room count**, which is the point (a group is sold as unassigned stays, so counting room numbers would show ten doubles free the moment ten were promised); OOO rooms in neither number (N27); free returned **signed**, because nothing refuses an oversold group and a −2 on a Friday is the only place the desk ever reads it. Grid drawn on the group path only, oversold cells in the warning colour, ask-vs-free said beside each line; all of it a hint, the line stays submittable (N25). 6 new scenarios. **Flagged to architect:** the calendar's own "free of this type" row (G9) still ignores unassigned nights, so it and this grid can disagree — recommend pointing it at the same read; and the Kind select sits *below* the lines it controls (pre-existing order). i18n report 48 en-only keys. Next: G28.
- 2026-09-25 — G15 landing 2 landed (c6f5d36, staging 5f182144, 398 green): /stays/$id night rows carry rate + Save (SetNightRate) and Give it back (ChangeNights remove); add-night card defaults to next night, blank rate = stay's rate; only while booked/checked in. Adapters shape-only; no non-empty refine (nothingToChange). Posted pill kept (fact, not rule). i18n 43 keys. G15 done; dev → G20 group availability grid.
- 2026-09-25 — dev: **5.7 G15 landing 2 — the nights table edits itself** (solex `c6f5d36`, staging `5f182144`, 398 green). `/stays/$id`: every night row carries its own rate field and a *Give it back* button; one card below adds a night at either end (date defaults to the night after the last; blank rate keeps what the stay pays). Server fns `changeNights` / `setNightRate` are adapters only (D-24) — the input schemas check shape, and the unbroken run, the empty stay and the already-posted night come back as codes the page translates. No control decides for itself: a guest can check in and a night can be posted while the page sits open, so buttons stay pressable (N25). `posted` is drawn as a pill — the fact the rule is about, not the rule. Forms only while the stay is booked or checked in. `pnpm i18n:report` now **43** en-only keys. Next: G20.
- 2026-09-25 — QA reachable again (messages were held until its step finished). Journeys suite on port 7022, own DB, seeding off camera. First R1 webm was on 3c2e48f / old map / vi; QA re-recording on main in en (tile panel, settle dialog, defineRoom), then rrweb JSON + player.html, then R2. ETA R1 pair ~1h. Nobody signs in on camera (dev bypass); R2 opens signed in as owner.
- 2026-09-24 — G15 landing 1 landed (a48c254, staging 589cca66, 398 green): ChangeNights refuses charged night / gap / empty stay, added nights under availability guard; SetNightRate. Ruling: an added night is priced at the stay's current rate, not the rate table (extension of the agreement made; typed rate optional, SetNightRate after) — accepted. Dev at 241k, clean stop, resume note 2a9eb11; landing 2 = stay-page forms next. i18n report 33 keys → product (session not running). D1 7403 flake again.
- 2026-09-24 — dev: **5.7 G15 landing 1 — ChangeNights + SetNightRate rules** (solex `a48c254`, staging `589cca66`, 398 green). Commands and scenarios only; the stay-page screens are landing 2. ChangeNights refuses a charged night (`stay.nightPosted`), a gap (`stay.nightsNotContiguous` — the fold reads nights as an interval), and emptying the stay (`stay.nightsRequired`); added nights go through the availability guard and are priced at what the stay already pays, not the rate table. SetNightRate is per night, refused once the night is posted, so calendar and folio cannot disagree. **Dev at a clean stop for compaction; resume note below.**
- 2026-09-24 — G14 landing 2 landed (d5686fd, staging d4c4c896, 390 green): party/notes/requests, 3 events per §3; requests add = unassigned stay (room via AssignRoom, availability rule stays in one place — dev's narrower call accepted), remove refused by stayCheckedIn, reason on remove only, group-only forms. Quiet nothingToChange notice on all six forms (077ab9d). i18n report 23 keys → product's first vi pass, via dev. Dev → G15.
- 2026-09-24 — dev: **5.7 G14 landing 2 — correcting a booking after it is taken** (solex `d5686fd`, staging `d4c4c896`, 390 green; quiet-notice ruling in `077ab9d`). Three commands, three events per §3: `booking.party_changed` (ids only, `companyId: null` said out loud when cleared, erased-contact check as in CreateBooking), `booking.notes_changed`, `booking.requests_changed` (add + remove in one batch — `stay.created` per room added, `stay.cancelled` per room taken off, availability touched only when the rooms given back had numbers; each stay appended under its folded version; removal refused by `booking.stayCheckedIn`). **Narrower than the ruling on purpose:** an added room holds no room number, so the CreateBooking availability predicate has nothing to bite on and was not duplicated — `AssignRoom` already decides freeness under the guard. Add/remove forms are group-only; remove requires a reason, add does not. `pnpm i18n:report` at 23 en-only keys for product. Next: G15 (ChangeNights, SetNightRate).
- 2026-09-24 — Dev re-briefed after compaction. Slice-4 debts landed (a920697, staging 23c4346e, 375 green): N21 history grouped by correlationId; N22 nothingToChange refused on guest/contact/roomType/rate + company/hotel profile (stretch accepted). Ruling: UI renders nothingToChange as a quiet neutral notice on all six, no disabled-button logic. i18n report now 7 en-only keys for product. Dev on G14 landing 2 with the ruled requests_changed guard (reuse CreateBooking availability predicate; remove refused only by stayCheckedIn).
- 2026-09-24 — Alex: un-park rrweb for a comparison. QA to deliver R1 twice: plain webm (exists, 17:24) + rrweb JSON with seekable player.html. Alex picks the format after. R2 follows.
- 2026-09-24 — Alex: mockups artifact ≠ the seekable replay he had in mind. Ruling: plain Playwright videos (R1/R2) first; rrweb replay (seekable, HTML-based) parked, resume later. QA told.
- 2026-09-24 — dev: **5.7 G14 landing 1** (solex 417c5cd, staging ca754483, 375 green): group CancelBooking with reason, all still-booked stays in one batch, guard `booking.stayCheckedIn` read under the stay streams' versions; master stays open; deposit → cancel → forfeit covered at domain level (N28 path; QA to run S5-37 through the screens). **Dev at clean stop, idle, resume note 42f6045 → Alex compacts.** Owed early in 5.7 (missed from slice 4 rulings): history grouped by correlationId; `nothingToChange` surfaced on guest/contact/roomType/rate updates. Next: G14 landing 2 (party/notes/requests; requests_changed guard shape to architect first). First en-only keys now in `pnpm i18n:report` for product's pass.
- 2026-09-24 — dev: **5.7 G14 landing 1 — group CancelBooking on screen** (solex `417c5cd`, staging `ca754483`, 375 green). Booking page cancels the whole booking with a reason; every still-booked stay goes in the same batch and the nights go back on sale. Guard moved up to the booking: `booking.stayCheckedIn` (not `stay.notCancellable` about one room of twelve), read inside the plan under the stay streams' versions. Master folio stays open through the cancel — a scenario now takes a company deposit, cancels the group and forfeits it, **which is the N28 path**. **Dev at a clean stop for compaction; resume note below.** Next: G14 landing 2 (notes/party edits), then G15.
- 2026-09-24 — product: **SoLex, ezFolio-shaped mockups, all 5 screens** (c0388bc): shell (desk + owner with Needs attention badge), room map + quick panel, booking editor + settle dialog, status lists + one new-booking form, tape chart + nights without a room; English, SoLex style, our features only, ≤5 callouts, maps-to per control, "not carried over" per page. Architect reviewed all six files; calls accepted (4 tabs Front desk · Housekeeping · Back office · Setup; screen 3 = stay page, group = same page + Rooms tab; rendered as owner). Republished to artifact L2ivkCzKDWwXoCFcmF6bKP for Alex.
- 2026-09-24 — dev: **5.6 polish complete** (solex bc64f12 + D-29 04822c6, staging 5250b6e6, 371 green): tail G10 (empty cell → prefilled booking), G12 (checked-out-held legend, N9 closed), G19 (master payment form asks kind → company deposits; unblocks N28), G21 (room page: tonight/next), G26 (expenses default month, December-boundary test). D-29 built: `vi` is Partial, missing key renders the English sentence, `pnpm i18n:report` (in `pnpm check`, report only). Every P row in ux.md §6 landed. Accepted → **5.7 command coverage**: G14 → G15 → G20 → G28 → SetRoomType → G16 → G22 → G29 → G30 → G32 → G33.
- 2026-09-24 — dev: **5.6 complete** — tail G10/G12/G19/G21/G26 (solex `bc64f12`) + **D-29 i18n** (`04822c6`, staging deployed, 371 green). G10 empty tape-chart square → booking prefilled (room + that night, hover/focus affordance); G12 checked-out-night-still-held gets its own colour (was OOO's grey — QA N9 closed); **G19 master payment form takes a deposit kind — unblocks N28** (nothing on a group bill could be forfeited before); G21 room page says who is in it tonight and the next arrival, above housekeeping; G26 spending opens on this month, range returned by the server so the fields match the list (`monthOf` tested on December). D-29: `vi` is `Partial<Messages>`, missing keys render the **English sentence** not a marker, `pnpm i18n:report` (Node type-stripping, no new dep) lists untranslated keys and runs inside `pnpm check` as a report never a failure; existing vi untouched for product's pass. **5.6 polish is done** — every P row in ux.md §6 landed. Next: 5.7 command coverage (G31/G32 done; G14, G15, G20 first, then G16, G22, G28, G29, G30, plus `SetRoomType`).
- 2026-09-24 — Alex on the ezFolio flow: shapes, nav and vibe, not a pixel copy (modal "material-y"); logic and feature set ours → D-27 amended; one UI, not two skins. Product redoes 1+2 as "SoLex, ezFolio-shaped" (plain SoLex style, English, our features only) and continues 3–5 without a further gate.
- 2026-09-24 — **D-29** (Alex): English for everything the team produces; Vietnamese only in `vi` message files, filled by product after each accepted slice from an untranslated-keys report (dev adds `en` fallback + report); mockups/recordings in English. Dev, product (redo ezFolio mockups 1+2 in English), QA (English captions) briefed.
- 2026-09-24 — dev: **5.6 G4 landed** (solex 7bc8697, staging 9439978b, 368 green): history rows read as a line — translated event name + payload's readable fields in a fixed order (text → named ids → enums → labelled numbers/dates), ids the page cannot name are dropped, no extra fetches; /system keeps raw payloads; qty/unit price dropped from charge lines. Accepted. Next tail G10, G12, G19, G21, G26.
- 2026-09-24 — dev: **5.6 G4 — the log in words** (solex `7bc8697`, staging `9439978b`, 368 green). Stay / booking / room / person / account history tables no longer print JSON: one line per event = the event's name + the payload fields a person can act on (`Đã thu tiền · Tiền mặt · Thanh toán · Thành tiền: 650.000 · VCB 91`). Ids are dropped unless the page can name them — each page passes a names map (rooms, guests, charge categories, companies); qty/unit price dropped as duplicates of the bill. `src/ui/history.tsx` is the one table, with `merged` for pages showing several streams (no version column, since versions are per stream). **System events page keeps the raw payload** — an operator wants the record. New key `event.said`. Next tail: G10, G12, G19, G21, G26.
- 2026-09-24 — dev: **5.6 G1/G2 landed** (solex 84b68d6, staging f4648954, 368 green): nav in three named groups Lễ tân · Kinh doanh · Hệ thống (visible, no hover menus; Hệ thống hidden for the desk), Sơ đồ phòng first, calendar renamed Tình hình phòng (ezFolio's word). No icon ribbon (polish after client sees staging). `nav.rooms` key gone → QA spec pointed at `nav.roomMap` by dev. Accepted; group labels iterate with the client (D-27). Next G4.
- 2026-09-24 — dev: **5.6 G1 + G2 — grouped nav** (solex `84b68d6`, staging `f4648954`, 368 green). Nav is three drawn groups (not hover menus): Lễ tân (Sơ đồ phòng · Tình hình phòng · Đặt phòng · Khách & liên hệ) · Kinh doanh (Công nợ · Chi phí · Báo cáo) · Hệ thống (Thiết lập · Tài khoản · System, hidden entirely from a receptionist). Room map first and named **Sơ đồ phòng**. G2: calendar is **Tình hình phòng** in nav and page title both (was Lịch phòng / Tình trạng phòng). `nav.rooms` key gone; QA's hotel-profile spec updated to `nav.roomMap`. Next: G4 (history sentences per event type), then G10, G12, G19, G21, G26.
- 2026-09-24 — dev: **5.6 G8 landed** (solex e362433, staging 7645aabe, migration 0016 dev + remote, 368 green). Backfill proven on a synthetic table (id wins, name case-insensitive, per hotel, no match → null); staging had zero rooms. Define-room now on Setup with a live-type select; rule refuses `room.typeUnknown` (retired between render and submit); RetireRoomType checks rooms by id with a label fallback that must stay until no `room_type_id` is null. Fixtures idempotent for room/roomType; QA `defineRoom` helper moved to /setup by dev. Accepted. Next G1/G2.
- 2026-09-24 — dev: **5.6 G8 — a room belongs to a room type** (solex `e362433`, staging `7645aabe`, migration 0016 applied dev + remote, 368 green). `rooms.room_type_id` added; backfill matches the Setup type by id, else by name case-insensitively, **within the hotel**, exact only — verified against a synthetic table (id match, name match, no-match→null, and one hotel's label does not pick up another hotel's type). Staging had zero rooms, so the backfill was a no-op there. `room_type` text stays as the definition-time name (the label a retired type still reads as). Define-a-room moved off the map to Setup with a select; unknown type is `room.typeUnknown`, a rule, not a filtered-away option. Retiring a type checks rooms by reference, falling back to the slugged label for rows with none. Calendar groups on the id. Rooms with a null id are flagged in Setup — they cannot be re-typed yet (no command; architect put `SetRoomType` in 5.7 with G14/G15 and asked product for `room.type_changed`). **QA: `defineRoom` helper now goes to /setup and selects the type — I updated `e2e/support/desk.ts`.** Next: G1/G2 nav, then G4, G10, G12, G19, G21, G26.
- 2026-09-24 — dev G8 migration plan approved: 0016 adds nullable `rooms.room_type_id`, backfills by exact id or case-insensitive name within the hotel, unmatched stay null and are flagged on Setup; `rooms.room_type` text kept as definition-time name; `room.defined` gains roomTypeId (additive). No command to change a defined room's type → **SetRoomType / room.type_changed to 5.7** with G14/G15 (product adding to §12); workaround = define again. Define-room moves to Setup with a live-type select; calendar/counts/tiles read the id.
- 2026-09-24 — dev: **5.6 G18 + G25 landed** (solex d26eefb, staging a41c8dea, 367 green). G18 = folio lines show the hotel's category name (id only as fallback for a retired category). G25 = receivable statement lines link to their bill; a group transfer's booking is derived from the master account id (`folio:master:<bookingId>`), no new column; payments link nowhere by design; settled companies behind a URL toggle. `linesOf` now selects `entries.stay_id`. Accepted. Architect's brief mislabelled history sentences as G18 — that is **G4**, stays in the 5.6 tail (G1/G2 → G4 → G10, G12, G19, G21, G26). Next G8 (migration plan first).
- 2026-09-24 — dev: **5.6 G18 + G25** (solex `d26eefb`, staging `a41c8dea`, 367 green — 2 new domain tests). G18: folio lines show the category's name (system ones included), id only as fallback. G25: statement lines link to the bill the debt came off — a stay's transfer carries `stayId` on the entry; a group's has none, so the booking is read back out of the other account the entry touched (`folio:master:<bookingId>`), derived not stored. A payment against the account gets no link (it came off no single bill). Settled companies behind a URL toggle. Store change: `linesOf` now selects `entries.stay_id`. Next: **G8** (architect pulled it forward — rooms get a room-type reference, backfill by label, unmatched flagged in Setup, define-room moves to Setup), then G1/G2.
- 2026-09-24 — dev: **5.6 G9 landed** (solex 9627c78, staging 6a850ffe, 365 green): calendar grouped by room type, "Trống loại này" per group per night, foot rows đã dùng · trống · công suất, window 7/14/30 in URL. Rulings: free-per-type stays at each group's foot (the row does not exist in ezFolio, so placement is ours; reading it beside the rooms it counts wins); OOO in neither used nor free (N27 denominator); no sellable rooms → "—". **G8 pulled forward**: rooms.room_type is free text, so per-type counts match a typed label, not the Setup room type a booking asks for → G8 (room-type select on define-room, moved to Setup, additive migration + backfill by label) runs right after G18/G25, before G1/G2. Next G18/G25.
- 2026-09-24 — dev: **5.6 G9 — tape chart rows + grouping** (solex `9627c78`, staging `6a850ffe`, 365 green). Calendar groups rooms under a room-type sub-header, each group ending in a **free-of-this-type per night** row (the quoting row), and the grid foot carries ezFolio's three: phòng đã dùng · phòng trống · công suất. OOO rooms are in neither count (same denominator as the occupancy report, N27); no sellable rooms reads "—", not 0%. Window 7/14/30 in the URL beside `from`. All derived from rooms+nights already loaded. **Open:** grouping is on `rooms.room_type`, which is still free text typed on the define-room form — so "free of this type" answers by label, not by the Setup type a booking asks for. Quoting only becomes exact once G8 gives rooms a room-type select (suggest G8 sooner than the tail). Next: G18/G25.
- 2026-09-24 — dev: **5.6 G13 landed** (solex b211550, staging 5dfad5fb, 365 green): Bookings = six status tabs over one table (predicate counts and fills; overlapping like ezFolio), grouped khách lẻ/đoàn, ezFolio column order, find box. Rulings accepted: a row is a stay (group = n rows under one heading); no actor columns (three stream reads per row, add per tab if asked); booking link only on group rows. Nguồn "—" until G28. **QA: rows link to /stays/<id>; getBookings removed.** Next G9.
- 2026-09-24 — dev: **5.6 G13 — status lists** (solex `b211550`, staging `5dfad5fb`, 365 green). Bookings page is now ezFolio's Lễ tân lists over one table: Tất cả · Khách sẽ đến · Đến trong ngày · Đang ở · Đi trong ngày · Đã huỷ, each a predicate used twice (count + rows, so they cannot disagree), overlapping as ezFolio's do. **A row is a stay, not a booking** — room, rate, arrival are what the desk looks up — grouped khách lẻ / khách đoàn, ezFolio column order (# · tên · phòng · loại · giá · số đêm · đến · đi · nguồn · công ty · ghi chú). One find box over name/phone/company. Nguồn blank until G28 writes `sourceId`. Two smaller calls: the booking link shows only on group rows (an individual's booking page is the row's own stay page), and no who-created/booked/checked-in columns — three actor lookups per row means reading each stay's event stream; suggest a later column if the client asks. `getBookings` adapter deleted (nothing left importing it). **QA: the list now links rows to /stays/<id>, not /bookings/<id>.** Next: G9.
- 2026-09-24 — dev: **5.6 G31 landed** (solex bdf0fa1, staging 1f0b37b9, 365 green): money strip Tổng · Đặt cọc · Đã trả · Còn lại on stay + master bills (Đã trả net of refunds so the row reads as arithmetic; Còn lại = ledger balance itself, not the sum, so a disagreement would show; voided lines out of Tổng); check-out opens the quickout-shaped settle dialog (TakePayment or TransferToReceivable → CheckOut; owing bill refused by name inside it; dialog remembers the money leg landed so a retry after a refused CheckOut never pays twice). Accepted, flag kept. **Infra flag for Alex:** staging deploy hit Cloudflare 7403 on the D1 migrate step twice now (second attempt passes unchanged) — flaky auth, Alex-owned. Next G13.
- 2026-09-24 — dev: **5.6 G31 — money strip + settle-at-checkout** (solex `bdf0fa1`, staging `1f0b37b9`, 365 green). Bill opens with Tổng · Đặt cọc · Đã trả · Còn lại on both the stay folio and the master one; Đã trả is net of refunds so the strip is arithmetic, Còn lại is the ledger balance itself (not the other three summed — a disagreement should show). Check out opens the quickout dialog (balance · method · amount · reference, **Công nợ → company** last) and runs TakePayment|TransferToReceivable then CheckOut in sequence, one answer from the desk. The dialog remembers a landed money leg, so a check-out refused after payment can be retried without charging twice. No rule copied to the screen: a bill that still owes is refused by name in the dialog. Next: G13.
- 2026-09-24 — dev: **5.6 G5–G7 room map landed** (solex 32202ab, staging 3f0afbcd, 365 green): type code over number + tonight's guest on tiles, 8 status buttons with live counts that also filter (one predicate counts and filters, so they cannot disagree; counts overlap as ezFolio's do, tile colour exclusive), Chi tiết panel on tile click. Map reads nights ∪ stays touching today (departures own no night tonight); still fully derived. G8 half (define-room folded away). Accepted. **Dev at clean stop, idle, resume note 887ebb9 → Alex compacts.** Next: G31 → G13 → G9 → G18/G25 → G1/G2.
- 2026-09-24 — dev: **5.6 G3 + G5–G7** (solex `32202ab`, staging `3f0afbcd`, 365 green). G3: no browser `prompt()`/`confirm()` left — one `<Ask>` native dialog, five sites. G5–G7: room map tiles carry type code + guest, eight status buttons with live counts filter it, tile click opens the Chi tiết panel (rate, dates, nights, guest, company, note, Còn lại, quick charge per Setup category, mark clean/dirty, links to stay + room). Counts and colours derived, never stored. **Dev at a clean stop for compaction; resume note below.** Next: G31 → G13 → G9 → G18/G25 → G1/G2.
- 2026-09-24 — dev: 5.6 G3 landed (44c6c1a, staging c78cec1c): every browser prompt/confirm replaced by one native-dialog `<Ask>`; empty reason still refused by the rule. Accepted. Next G5–G7 room map as one commit; architect pointed dev at product's `diagrams/ezfolio-flow/room-map.html` for the count definitions and Chi tiết fields so one implementation serves both flows.
- 2026-09-24 — dev: **5.5 print done** (solex e7f1dd1, staging d96ba0c4, 365 green). Architect accepted; ruled voided lines stay off the printout (paper = what is owed, reconciles with ledger). Dev → 5.6 polish, G3 first. QA: print cases after R1/R2.
- 2026-09-24 — dev: **5.5 complete — the bill on paper** (solex `e7f1dd1`, staging `d96ba0c4`, 365 green). `/print/stay/<id>` + `/print/booking/<id>`, own routes, ezFolio report house style (letterhead / centred title / printed-on-by / lines / totals / three signatures), `@media print`, no VAT, no event. Voided lines are left off the printout (they are not owed and the totals already exclude them); charges − payments + refunds = balance, so the sheet reconciles with the ledger. Next: 5.6 polish in familiarity order.
- 2026-09-24 — Alex: go on both — product draws the ezFolio look-alike desk flow (HTML mockups, `diagrams/ezfolio-flow/`, shell + Sơ đồ + Chi tiết modal first, then booking editor, status lists, Tình hình); QA records R1/R2 flow videos.
- 2026-09-24 — architect: Alex found ux.md §4 ASCII wireframes too dense. Drew Stay (4.7) as an annotated HTML mockup template (artifact FnYDkwHfpSed7wtQmzgL3L); product reviewed (go, 9 fixes applied). Alex: still dense; also floated an ezFolio-look-alike flow variant for a client demo (deferred; mockups before any build). **Decision (Alex): record short flow videos of the built app instead of drawing.** QA owns a Playwright "journeys" suite: video per flow, data seeded off-camera, caption bar per step, 20–60 s, local dev only, output `solex/e2e/recordings/` (gitignored), re-recordable after each slice. First two: R1 desk walk-in check-in→check-out, R2 owner morning. HTML template kept as a later option; ux.md unchanged. Product + QA compacted and re-briefed (72k/71k); dev still 327k.
- 2026-09-24 — solex-qa 5.4 run 111/112 (1 skipped); N27 closed; N28 (group forfeit unreachable) ruled = G19 (5.6) + G14 (5.7), group cancel semantics pinned.
- 2026-09-24 — context watch: dev 313k, product 220k → both at clean stops for compaction. Dev: 5.5 half landed (8bed803, staging 9df6b465, 365 green; HotelProfile address/phone; print views not started, decisions in resume note 0198c58). Product idle (d7823cb).
- 2026-09-24 — dev (while idle): `error.folio.categoryReserved` reworded per product's ruling to cover every reserved category, en + vi (solex `3c2e48f`, staging `50c76694`, 365 green). Wording only. Build from `3c2e48f`, not `8bed803`.
- 2026-09-24 — dev: **5.5 started, clean stop for compaction** (solex `8bed803`, staging `9df6b465`, 365 green, migration 0015 applied dev + remote). Landed: HotelProfile gains `address` + `phone` (the letterhead) with Setup fields — a printed bill starts with who is sending it and the profile had only a name. Not started: the print views themselves. Resume from `8bed803`; plan in the dev section below.
- 2026-09-24 — dev: 5.4 deposits + MarkNoShow + N27 (755e585, staging d8da2b08, 365 green). Architect accepted; 5.5 print scoped (own + master, HotelProfile header, print CSS, no VAT). QA on 5.4 cases.
- 2026-09-24 — dev: **5.4 deposits + N27** (solex `755e585`, staging `d8da2b08`, 365 green). MarkNoShow (own status, frees nights, folio stays open, refused before the hotel day turns over). ForfeitDeposit: owner-only `folio.forfeit`, reserved system category `depositForfeit`, capped at taken − refunded − kept, allowed only once the booking is over. A refund or forfeit that leaves a cancelled/no-show folio at zero closes it in the same batch — `write()` now targets one account's stream. N27 fixed: the range report fills every night in `[from, to)` and shows rooms-in-service per row. Note: I sorted imports in QA's `e2e/specs/reports.spec.ts` — `biome ci` was red on it, mechanical only.
- 2026-09-24 — solex-qa 5.3 run 105/106; N26 closed; N27 occupancy denominator → dev with 5.4.
- 2026-09-24 — product: approvals 5.8 spec (e1b86a4) — kinds void/reprice/refund/forfeit/writeOff, request from the same button, owner card, grant re-checks + runs in one batch, expiry reactions; 5.4 §11 corrections (0b0d0df). Architect accepted → **D-28**; dev slice order now …5.6 polish → 5.7 command coverage → 5.8 approvals.
- 2026-09-24 — dev 5.4 plan; architect ruled: forfeit owner-only, system category depositForfeit, ceiling, cancelled/no-show only, MarkNoShow in 5.4, close folio at zero same batch. Product fixes §11.
- 2026-09-24 — product: BookingSource pinned (50a07b7): tier b Setup entity with kind direct|ota|agent|company (ezFolio Nguồn buckets), seed list from the client's debtor OTAs, default walk-in, source ≠ payer. Accepted → dev 5.7 with G28. Alex asked about async patterns: none by design (one D1 batch per command; cron + lazy roll only; cursor consumer reserved for external side effects). Alex: hash out approvals with product, simple + actionable → architect proposal sent (kinds void/refund/writeOff/reprice, same button as request, owner card in Needs attention, expire at check-out, 3 landings, slice 5.8).
- 2026-09-24 — dev: 5.3 complete (cecd997, staging 424f6139, 349 green); effective-date rule in; N26 fixed. Architect accepted; booking source vocabulary → product, build in 5.7. Dev → 5.4 deposits. QA on reconciliation cases.
- 2026-09-24 — dev: **5.3 landing 2 — revenue + occupancy reports** (solex `cecd997`, staging `424f6139`, 349 green). Revenue reads the ledger's revenue accounts with architect's effective-date rule (a reversal takes the date of the entry it reverses; cash keeps its own day); `range()` is one helper and the dashboard is it over today. Cuts: by category, by booking source, by payment method. Occupancy by night and room type vs today's sellable rooms. Range in the URL; `report.rangeInvalid` is a rule. **N26 fixed** (zones ∪ {default, saved, UTC}, de-duped by canonical spelling). **Note for product/architect: nothing sets `bookings.sourceId` — no screen records a source — so the by-source report is one "not recorded" row until a control exists. Sibling of G28; suggest the same slice.**
- 2026-09-24 — product: home & inbox spec (76d2594): desk home = room map + status strip; owner home = dashboard + NeedsAttention projection (aged receivables >30d, OOO >7d, unassigned tomorrow, overstay with balance, pending approvals; thresholds in BookingRules; ids only) + nav badge; approval flow shape pinned in §8, parked; notifications = async consumer, deferred. ux.md 4.14 = Owner home, G33 (C, v1 after 5.3). Architect accepted: inbox in v1 (5.7), approvals stay parked.
- 2026-09-24 — Alex: notifications / manager approval / home page? Architect: none designed; approvals parked (§8). Tasked product to spec (not build) per-persona home pages, an owner "needs attention" inbox projection, a log-shaped approval flow (request → grant/decline → original command with approval id), push as a deferred async consumer (D-8 Hookdeck slot).
- 2026-09-24 — solex-qa 5.2 run 97/98; N24/N25 closed; N26 (zone list alias Asia/Saigon vs Ho_Chi_Minh) → dev. Dashboard/report cases next.
- 2026-09-24 — dev: dashboard rulings on staging b7926041; flagged void/ledger date gap. Architect ruled: ledger date = day it happened; revenue report uses effective date (reversed entry's day) via reversesEntryId; cash uses actual date. Dev on 5.3 landing 2; QA cases refined.
- 2026-09-24 — product: D-27 familiarity pass (9e69e0a): every screen "familiar to / departs"; nav grouping and tile quick panel are *more* ezFolio-like (Q1/Q2 confirmed); stay page stays one page (rule-forced) with a Tổng/Đặt cọc/Đã trả/Còn lại strip; new G31 settle-dialog-at-checkout (P, high), G32 group-level routing table (C); 5.6 ordered by familiarity. Architect accepted; G31/G32 become §3 rows (two commands in sequence, dialog never decides).
- 2026-09-24 — dev: 5.3 landing 1 dashboard (b789aa8, staging 76130ae7, 344 green). Architect accepted; void nets on charge's date, OOO out of denominator, refunds beside + net, reads map capability refusal only. G28 → 5.7. Landing 2 revenue/occupancy reports in rpt-* shape next.
- 2026-09-24 — dev: **5.3 landing 1 — dashboard** (solex `b789aa8`, staging `76130ae7`, 344 green). Occupancy (out-of-order rooms leave the denominator), arrivals expected/arrived, departures due/left, in-house, revenue sold today (voids excluded from the charge's own business date, wherever the void happened), money taken split deposits/settlements/refunds, seven nights forward. Owner-only; `auth.forbidden` mapped to data so a read's refusal is a card, not an error page. Reads in `store/reports.ts`, projections only. **Answer for product: `Company.defaultRouting` has no Setup control — never built, not a deliberate per-stay-only choice.** `folio/routing.ts` reads it as precedence step 2, landing 2 shipped only the per-stay override, and the `/setup` comment promising it "in 5.1" is stale. Small job (routing row per charge category on the company form); architect's call which slice.
- 2026-09-24 — Alex: staff not tech-savvy, keep the UX similar-ish to ezFolio; Vietnamese wording iterates with the client, not a gate → **D-27**. Product to re-check ux.md against ezFolio screens; 5.6 ordered by familiarity; VN wording flag closed.
- 2026-09-24 — product: ux.md review fixes applied (e2ff980): G29 = BookingRules only, G23/24 wip, C = 5.7 command coverage (G14/15/16/20/22/28/29/30), board self-check (467 elements, zero overlaps). Final; with Alex.
- 2026-09-24 — product: ux.md + solex-ux board first complete draft (9c132b6). Architect review: G29 stale (HotelProfile built), G23/24 in progress, §11-command F rows are v1 scope → new 5.7 command-coverage pass after 5.6; board needs a bounds check. README pointer + Alex flag added.
- 2026-09-24 — dev: 5.2 complete (5485e9e, staging 42ef30f3, 335 green): Setup profile section, tz picker, timestamps in hotel zone. Architect accepted; 5.3 reports scoped (dashboard today → revenue by category/source/method, occupancy over time; owner-only; projections + ledger only; totals reconcile with ledger). QA: 5.2 cases.
- 2026-09-24 — dev: **5.2 done** (solex `5485e9e`, staging `42ef30f3`, 335 green). Setup opens with the hotel itself (name / zone / roll hour); zone picker from `Intl.supportedValuesOf` with a fallback that always keeps the current answer; hour is a 0–23 select. Timestamps now render in the hotel's zone, not UTC — `getHotelZone` in the root loader, carried on `useI18n` beside the locale, `formatTimestamp(value, locale, timeZone)`. Calendar dates stay UTC (they are days, not instants). Next: 5.3 reports.
- 2026-09-24 — dev: N24 + N25 landed (d84c906, staging 84f3f03c, 335 green); ready-to-close display dropped for a static hint + refusal. Architect accepted. QA verifying. Dev → Setup profile section, tz picker, profile-zone rendering.
- 2026-09-24 — dev: N24 + N25 fixed (solex `d84c906`, staging `84f3f03c`, 335 green). Closed master folio reads `account.status` and offers no forms (new `master.closed` key — `folio.closed` says the guest checked out, wrong sentence for a group). Finish always pressable; page copy of the two rules gone, `getBooking.masterBalance` gone with it, `booking.readyToClose` → `booking.closeHint` (prose, not a check). S5-12a/b/c should go green. Back on 5.2: Setup section, tz picker, tz rendering.
- 2026-09-24 — Alex: wants a clear UX wireframe of the app by persona. Architect tasked product: `ux.md` (personas, journeys, IA, per-screen low-fi wireframes, gap list vs built app) + `diagrams/solex-ux.excalidraw` via generator script; grounded in built routes (read-only). Architect reviews before it goes to Alex.
- 2026-09-24 — dev: 5.2 half landed (b531242, staging 7cfb5ced, 335 green): hourly cron for night posting (own server entry; hourly not at roll hour because roll hour is per-hotel config; idempotent, lazy path stays), HotelProfile backend + businessDateFor + CommandContext.day. Left: Setup screen section, tz picker, rendering via profile tz; N24/N25 first. Dev idle at 200k for compaction; resume note c26b107. Architect accepts hourly-cron reasoning.
- 2026-09-24 — solex-qa landing 3 run 95/96, N23 closed; N24 (closed master keeps forms), N25 (Finish hidden, page copies rule) → architect: N25 not an exception, button pressable. Dev at 200k, pausing for compaction; N24/N25 in 5.2.
- 2026-09-24 — dev: 5.1 landing 3 CloseBooking (624b7dd, staging fd74a805, 322 green); master folio closes in the same batch. Architect accepted, N23 closed. QA running S5. Dev → 5.2 cron + HotelProfile.
- 2026-09-24 — architect: pre-compaction checkpoint. State: solex db0c0e0 / staging 68192888 / 309 scenarios / 92 e2e; dev idle awaiting compaction with landing 3 spec at its log 592d5d8; QA waiting on landing 3; product aligned through 7709bc1. Session-ops notes added to architect profile.
- 2026-09-24 — solex-qa: N23 rulings in cases (e4e3dc3): S5-12d individual auto-close, S5-16 master charges keep stay (green), S5-13/15 reworded; e2e flake fixed. Waiting on landing 3.
- 2026-09-24 — product: row 7a / §11 CloseBooking group-only / RetireCompany guard aligned (7709bc1).
- 2026-09-24 — solex-qa landing 2 run 91/92; N23 (individual bookings never close). Architect: individual auto-close on last terminal stay; group explicit CloseBooking; company.inUse reads stays/master not status; master charges keep stay_id (intended). Dev picks up post-compaction as landing 3.
- 2026-09-24 — dev: 5.1 landing 2 (group form, routing, master panel; staging 68192888, 309 green). Architect accepted; ruled CloseBooking = new explicit command with master + stays guards. Dev paused for compaction (276k) before landing 3.
- 2026-09-24 — solex-qa: 84/84 e2e on d607656 (6b6635d); 5.1a cases S5-1..5 green; N21 (history grouping) + N22 (silent unchanged saves) numbered, both 5.6; landing 2 cases S5-6..13 drafted. Next N23.
- 2026-09-24 — dev: 5.1 landing 1 group domain + N20 (staging 38ecc5ac, 301 green). Architect accepted. Landing 2 (group form, booking detail w/ master folio, per-stay routing) started; VN wording for own bill / master folio still Alex's — dev uses marked placeholders.
- 2026-09-24 — solex-qa: plain-language S4 cases for Alex (beed8a1); 78/78 green on 4cb9908; N20 rate diff. Architect: history tabs group by correlationId; unchanged saves say so everywhere (dev, non-blocking).
- 2026-09-24 — product: rule 8 + §6 say routing/master folio group-only (4a77be0). Cash handover / day close parked in §8 Later (e0b3853; Alex: manual today, needs client conversation; candidate CloseShift{cashCounted} vs ledger cash-in + variance event). Not v1.
- 2026-09-24 — architect ruling (dev Q, 5.1 landing 1): **routing is a group-only concept.** An individual booking has no master folio; `postCharge` resolves `own` unconditionally when `booking.kind = individual`; `room → master` (or `Company.defaultRouting`) is the seed for a *group* booking's per-stay routing. A single company traveller's bill still goes own folio → transfer-to-receivable at check-out. Product aligns §10 rule 8 wording.
- 2026-09-24 — dev: 5.1a Company done (d896f3c, staging eda576d9, 285 green); routing control deferred to 5.1 landing 2 (accepted). Starting 5.1 landing 1 domain (N stays, party.companyId, lazy master folio, routing at postCharge).
- 2026-09-24 — dev (post-compaction): N19 fixed 4cb9908, staging be0647d5, 285 green; store port `people.contact` now returns `{id, write, stream}` so the type carries the rule. On Company Setup screen. Port 7531 held by another session's dev server (QA's?) — dev didn't run e2e; QA reruns S4-21.
- 2026-09-24 — solex-qa stopped for compaction (solex aa34fd7, 78 e2e). N19: booking-created contacts have no `contact.created` → blocking, dev first on resume. Plain-language S4 block for Alex still to write (QA first on resume).
- 2026-09-24 — architect: dev idle at clean stop for compaction (5.1a Company server side a9fe985, staging 138c9393, 284 green; resume = Setup screen + transfer picks from list). Docker: orphan postgres container/volume/network removed; local dev = `mise run dev` (SQLite, no Docker). QA stopped for compaction. Flag for Alex's Vietnamese pass: wording for "own bill" vs "master folio".
- 2026-09-24 — product: 5.1 alignments (3af0a08): routing per ChargeCategoryId, Company tier (b) entity + §11 rows (retire refused `company.inUse` while an open receivable/booking references it — accepted, same as roomType), §10 row 7a CloseBooking refused while master > 0.
- 2026-09-24 — architect rulings for slice 5.1 (dev's assumptions): (1) **Company first** as 5.1a — tier (b) Setup entity (name, defaultRouting), because `companyId` on transfer-to-receivable is free text today and a typo splits a debt; transfer picks from the list. (2) **Bucket = ChargeCategoryId** — routing per charge category; product aligns §6. (3) **Master folio guarded at `booking.close`**, not stay check-out: stays check out on their own folio; booking cannot close while master balance > 0; master visible + settleable on booking detail. Default routing without Company: room → master, rest → own.
- 2026-09-24 — dev: slice 4 done (booking history, N18; staging d006aa47, 276 green). Architect: slice 5 order set — group booking + master folio routing → cron entry + HotelProfile → reports/dashboard → deposits → folio print → search, overbooking override.
- 2026-09-24 — dev: slice 4 landing 2 roles + histories (staging 41b8114c, 274 green); N17 fixed; guest-at-check-in had no event → fixed. Architect audited tier (b) writes: no other bare path. Alex: compacting dev; wants slice 4 test cases documented clearly → solex-qa.
- 2026-09-24 — product: §11 DisableUser deferred, user stream/payload/session notes aligned (0b76254).
- 2026-09-24 — dev: slice 4 landing 1 accounts (staging 5d3807df, 272 green); N16 closed. Architect accepted; ruled no account-level DisableUser in v1 (D-18 built note); product to mark §11 DisableUser deferred. Next: roles + history tabs.
- 2026-09-24 — solex-qa: D-24 (b) verified; S3-32 sweep green; N16 refund form pre-fills reason (rule unreachable) → dev, non-blocking; slice 4 cases S4-1..5 prepared. Checklist line extended: UI never answers a rule on the user's behalf.
- 2026-09-24 — dev: D-24 (b) applied (staging acf36ff1, 259 + 45 green); found refund had no reason rule (schema-only) → `folio.reasonRequired`. Architect accepted; checklist: screen decides what to send, never whether allowed. Slice 4 started.
- 2026-09-24 — solex-qa: slice 3 reds green, expense cases added, N14/N15 → dev. Architect D-24 (b): adapters validate shape only; rule refusals are codes; zod failures return `input.invalid`, never throw.
- 2026-09-24 — product: §6/§11 ExpenseCommand aligned to built shape (d5a0ef9). Slice 3 spec == code.
- 2026-09-24 — dev: expense categories now the client's list (staging 0094e999). Architect rulings: id `hkOvertime` (camel, like every other id) stands; ExpenseCommand keeps dev's **required `description`** + optional `reference` — an advance with no name on it is unauditable; product drops `payee?`/`note?`. Dev on slice 4.
- 2026-09-24 — product: ExpenseCategory v1 fixed in code aligned (b7e73f3): §5/§6 clause, ids groceries/incidental/hk_overtime/advance/other + system writeOff, dropped from §11 Define/Update/Retire.
- 2026-09-24 — dev: slice 3 done — expenses (35d6db9) + form sweep N10/N11/N12 (9fd031b), staging 98e73650, 255 unit + 27 e2e. Architect: fixed expense category list accepted for v1, ids to match product's client list; slice 4 next, cron stays pre-go-live.
- 2026-09-24 — solex-qa: landing 6 run green (receivables S3-15/19–23, bootstrap S2-9 automated, void double-click S3-25); known reds S3-14/S3-24/S2-16 await dev's form sweep. Staging smoke stays Alex's (needs a signed-in session; no agent types credentials).
- 2026-09-24 — dev: staging wiped (events, projections, tier b gone; auth + migrations kept), on dba5704/81fdef66. D-26 recorded by dev (48e931d). Architect: drop unused `spike_items` via a migration; QA warned first sign-in on empty staging becomes owner (bootstrap).
- 2026-09-24 — Alex: confirmed the staging wipe with dev in dev's session; dev follows architect's instructions going forward, Alex checks in when he can.
- 2026-09-24 — dev: D-12 (f) landed dba5704, staging 81fdef66, 243 green; found folio deciding ran outside the retry thunk (D-8 property false for money) — fixed. Architect accepted; checklist: decide inside `plan()`. Next: expenses → N10+N11 sweep → slice 4.
- 2026-09-24 — architect: finding numbers minted by solex-qa from now (N12 clash resolved: N12 guest search, N13 mise .env override, QA's). QA e2e for N12 red (232a265), case S2-16.
- 2026-09-24 — product: §6 gains "PII never in a URL" (c28acae, tagged N11/N12); `ledger:` stream spelling confirmed applied (1034113). Spec and code aligned.
- 2026-09-24 — architect: N12 (`/guests?q=` puts a name in the URL) ruled same class as N11, non-blocking, fixed before go-live via server-fn search + client state; product adds "PII never in a URL" to §6.
- 2026-09-24 — architect: N11 (pre-hydration GET puts guest PII in the URL) ruled **blocking** under D-20; fix = `method="post"` on every form, before slice 4. solex-qa e2e live (ef6d242); N10 sweep red 15/15 → dev.
- 2026-09-24 — architect: reviewed slice 3 landing 6 receivables (dev 1ad54f4, 242 green). Ruled D-12 (f): commandId replay in `commit`, not per command. Non-blocking, before expenses. Screen walk → solex-qa.
- 2026-09-24 — Worktree swap: `../solex-qa` handed to the solex-qa session (name matches agent, Alex's ask); architect now reviews in `../solex-architect`. Alex: dev should keep asking architect questions, not wait for him.

Newest first. `YYYY-MM-DD — <agent>: what`.

- 2026-09-24 — architect: QA role split out — `solex-qa` profile + start prompt, `qa/README.md`, `qa/cases.md` (49 cases seeded from walkthroughs), `qa/runs.md`. Alex to open the session.
- 2026-09-23 — architect: slice 3 landing 5 (folio screen) walked green; N10 silent-required pattern → dev; ledger stream id `ledger:` ruled; Alex asked for the slice-3 staging pass.
- 2026-09-23 — product: UnpostedNights (derived) replaces NightRollStatus; receivable.opened dropped; account id `account:receivable:<companyId>` (5c03500).
- 2026-09-23 — architect: slice 3 landings 3+4 accepted (night roll derived + attempt-id; check-out guard). Cron deferred to pre-go-live. Order: money screens → Alex pass → receivable + expenses.
- 2026-09-23 — product: folio.opened dropped; lazy open w/ derived ids own `folio:<stayId>`, master `folio:master:<bookingId>` (72bf67f). Dev to confirm master shape.
- 2026-09-23 — architect: slice 3 landing 2 (folio vocabulary) accepted; lazy folio open → product to align; refund-cap flagged for Alex; one-batch-money checklist line.
- 2026-09-23 — product: ledger multi-append noted in §6/§12; v1 role bundles spelled out in §2, receptionist gains folio.move_line + expense.record (4724741).
- 2026-09-23 — architect: slice 3 landing 1 (Ledger core) accepted; stream-per-account w/ multi-append recorded in D-17; role split flagged for Alex.
- 2026-09-23 — product: D-25 folded into §10 row 1, §11 PostNightlyRoomCharges, §7 NightRollStatus projection (8b1aaf3).
- 2026-09-23 — architect: slice 2 closed (landing D accepted). **D-25** night posting = cron + lazy, idempotent. Dev → slice 3 money. Alex asked for staging pass on slices 1–2.
- 2026-09-23 — product: §12 gains staff.* (stream `<hotel>/staff:<userId>`), user.* = identity only; staff.lastOwner/alreadyStaff rules in §2 (453770b).
- 2026-09-23 — architect: slice 2C (staff/roles/capabilities) accepted; bootstrap rule flagged for Alex; script must emit staff.added.
- 2026-09-23 — architect: slice 2B (guests/contacts + erasure) reviewed, accepted; erase owner-gate tracked to land in C before D.
- 2026-09-23 — product: Contact events + `guests.erase` owner capability ruled (a14533f); logged under D-20.
- 2026-09-23 — product: §10 row 9 = refuse rate.notFound; guest.erased in §12; roomType retire refuses `roomType.inUse` (a56012b); dev told.
- 2026-09-23 — architect: slice 2A (RoomType + RateTable) reviewed; slug ids + half-open rates accepted; **no-rate night refuses, not 0** (overruled); 2 Qs → product.
- 2026-09-23 — dev: N8 (deploy now migrates D1 before the Worker flips — was a real gap) + N9 closed (5b93104). Architect: dev starts slice 2.
- 2026-09-23 — architect: slice 1 walkthrough green (f35bded). N8 migrate-on-dev, N9 checked-out style → dev. Alex asked for staging pass.
- 2026-09-23 — product: N7 ruled (§10 6c): check-in normalises nights to include today; dev told.
- 2026-09-23 — architect: D-24 refactor reviewed + accepted (92aa083, 100 green, 16 scenarios). B3/N5/mark_dirty verified closed. N7 (check-out before arrival) → product. Dev → slice-1 screens.
- 2026-09-23 — architect: D-24 amended — SQLite :memory: instead of hand-written MemoryStore (dev's argument), lint boundary on drizzle imports; Hotel shape reviewed w/ 3 notes. Dev landed B3+N5+mark_dirty (26d13b1) first.
- 2026-09-23 — architect: **D-24** (Alex) domain SDK `Hotel` + MemoryStore scenario suite; dev to refactor commands into it before slice-1 screens.
- 2026-09-23 — product: N5/N6 ruled in product.md ef88dca (§10 6a/6b, StayNightsChanged, availability.changed in §12, mark_dirty reaction confirmed); dev told.
- 2026-09-23 — architect: slice 1 server side reviewed (83 green). B3 blocking: check-in must version availability (race w/ OOO). N5 early checkout / mark_dirty reaction, N6 assign OOO room → product + dev. `availability.changed` accepted; D-20 addendum (replay never touches PII tables).
- 2026-09-23 — product: §11a frozen (92cefea) + told dev; 5 forward-compatible widenings (booking kind union, requests.qty, stay nights.posted + guestIds, room.marked_dirty stayId?); all stream ids hotel-first in §6/§11a/§12.
- 2026-09-23 — architect: slice 1 machinery reviewed (upcast split, appendAcross); `<hotel>/availability:all` blessed; product to freeze §11a.
- 2026-09-23 — product: §6 aligned to D-12 amendment (actor text, tz) + diagram (6f63e4d). Standby for slice 1.
- 2026-09-23 — architect: slice 0 closed (ca19a48). D-12 amended: actor text column, upcaster fail-loud on fold path, commandId semantics, tz hardcoded TODO(D-7), hand-written migration. Dev → slice 1.
- 2026-09-23 — architect: N4 verified (rule refusals render; "disable only for no-op" rule in QA checklist).
- 2026-09-23 — architect: slice 0a B1/B2 fixes verified + local browser walkthrough green; N4 silent rule rejections → dev. Dev-user bypass accepted.
- 2026-09-23 — architect: slice 0a (Room flip) reviewed — 2 blocking (retry redecide; silent non-atomic fallback), 3 notes → dev. `team/qa.md`.
- 2026-09-23 — architect: review/QA loop added to protocol (Alex's ask); `team/qa.md` checklist; QA worktree `solex-qa` at origin/main, 19 tests green.
- 2026-09-23 — architect: Alex green light for rough end-to-end; slice plan 0–5 in dev profile rev 6; product on gap duty.
- 2026-09-23 — architect: Alex greenlit Room flip + staging log wipe ("i'll defer to you; staging is indeed throwaway data"). Relayed to dev.
- 2026-09-23 — dev: D-23 built (redaction.ts, PII cols in). Wipe of staging log waits on Alex's explicit yes, not architect's. Room flip waits on Alex greenlight.
- 2026-09-23 — architect: D-12 clarification — commandId UNIQUE for idempotency; money commands must be idempotent.
- 2026-09-23 — product: PII columns listed in §6 for D-23 denylist (1e7dfb5); role per (hotel,user) pair.
- 2026-09-23 — architect: dev landed D-11 auth (Better Auth, Alex-directed). Accepted: `system_operator` ≠ owner; User + staff = tier b w/ library-owned table; staging log wipe at Room flip (flagged); **D-23** redact by column name.
- 2026-09-23 — architect: D-8 clarification (reads never fold; one intent = one command = one batch; reactions inline once, projectors replayed). Product tagged §11 tiers (b9c1c28), OOO read confirmed.
- 2026-09-23 — architect: **D-22** (Alex) two tiers: ES for Booking/Stay/Ledger, CRUD+events for reference data. Room flips to tier (b). Dev + product pinged.
- 2026-09-23 — architect: **D-21** Alex delegates routine decisions to architect. D-11 (app-owned auth v1) + D-20 (PII outside log) accepted. Dev unblocked for Booking.
- 2026-09-23 — architect: D-20 (PII outside log) queued for Alex; D-11 revised lean = app-owned username/password v1, OIDC later (fits product's auth answers).
- 2026-09-23 — architect: product v1 merged; D-12…D-19 accepted (Alex's calls). D-10 (my payload-versioning) folded into D-12; D-11 auth stays Proposed. §10 Qs + tz Q closed. Product → standby/spec owner. Dev next: envelope columns, then Booking/Stay from §11. (Note: 3bf8996 was product's renumbering commit, landed under my message.)
- 2026-09-23 — architect: dev's ES skeleton merged (Alex-directed). D-8 accepted de facto; D-10 (payload versioning) + D-11 (auth) proposed; dev rev 4 = those two before Booking.
- 2026-09-23 — architect: D-9 (multi-tenant by design, one tenant) flipped to Accepted — Alex's call in product session. Dev FYI: hotelId on every stream/table.
- 2026-09-23 — product: D-8 availability-stream covers invariants iff every supply/demand command versions it in-batch; dropping DO from §6. Alex session live.
- 2026-09-23 — architect: dev spike merged. D-3 amended (TanStack Start, CF build target only). **D-8 proposed** (D1 log + projections, optimistic concurrency, no DO, Hookdeck deferred) — conflicts with product §6 DO; product pinged. Progress/README updated.
- 2026-09-23 — architect: explore's lifecycle/money answers merged into README. Exploration complete bar 5 Alex-walkthrough items. Product resumes after Alex confirms.
- 2026-09-23 — product: v0.1 (2e5789c) — Setup context (HotelProfile, Floor/RoomType/Room, RateTable, ChargeItem, ChargeBehaviour, Company, BookingRules). Waiting on Alex §10.
- 2026-09-23 — architect: D-6 recorded (Setup scope, 3 personas, admin login dropped). Product objective +0c.
- 2026-09-23 — explore: Alex closed the admin-login question. Setup/configuration becomes **its own scope with a third persona** (setup/admin: rooms + prices, item catalogues + prices, tax & service behaviour, booking rules) — WS3 designs it rather than reverse-engineering ezFolio's blocked masters.

- 2026-09-23 — architect: product v0 merged into README; 5 more policy points → questions.md (8 total); aggregates forwarded to dev for storage sanity-check.
- 2026-09-23 — architect: merged explore's 4 findings + Alex-settled items into README; 3 decisions queued in questions.md; product pinged (folio routing + charge shape affect aggregates).
- 2026-09-23 — explore: flow board delivered as `board/solex-flow.excalidraw` (gitignored; generator + spec committed under `tools/excalidraw/`). 9 sections, 22 screens, incl. **charges** and **admin config** which the FigJam board never got — Figma's Starter plan caps the MCP at 20 calls/month, so that board is frozen. Alex settled: hourly stays unused (daily only); early/late fees are catalogue items, not rate multipliers; room map + tape chart are the two hub screens for every role.
- 2026-09-20 — architect: WS2 reviewed + merged into README. Explore → standby. 6 new questions (day boundary is the one needing a decision). `.profile/` gitignored explicitly.
- 2026-09-20 — architect: D-5 recorded. Product objective updated for second pass on existing-system.md; group bookings flagged as the hard aggregate.
- 2026-09-19 — architect: D-4 recorded (PMS exists, data-ownership rebuild, core subset). Product objective updated. All 3 agents caught up.
- 2026-09-19 — explore: Alex: `:99` = the PMS the client uses now. Rebuild motive = data ownership; target = core subset + enhancements, not a feature-by-feature copy. WS2 = map it first, via a slow walkthrough with Alex.
- 2026-09-20 — explore: Alex: **rebuild starts fresh, migration deferred** — ezFolio's Excel export is broken (data-URL truncation) but that's not a blocker; data import handled later. Full UI map + group-booking flow now in `existing-system.md`.
- 2026-09-20 — explore: existing system = **ezCloud ezFolio** (Windows on-prem, Oracle, LAN-locked). ~20 screens mapped in `existing-system.md` w/ screenshots (gitignored). Key: no rate plans (rates typed per booking), channel manager present but unused (OTA channel typed into guest name), housekeeping module unused, night audit off, 58 rooms / ~96% occupancy today. Constraints from Alex: **no card data ever**, two personas (manager, receptionist), group/company bookings are core, key cards out of scope. Excel export path deferred.
- 2026-09-23 — dev: console now follows the language picker too (was half VN / half EN — Alex caught it). Session notes + code map in stack.md, ready for a context compact. Open for me: D-10 on Alex's word, Booking waits on product v1 + D-11.
- 2026-09-23 — dev: i18n in (VN default + EN, server-resolved locale). Note for product: domain rule failures now return codes, not English sentences — keep that shape for new aggregates, it's what makes the UI translatable. VN wording needs a native pass.
- 2026-09-23 — dev: ES skeleton built and deployed (Alex asked for it directly, ahead of the standby in my profile). Event store w/ optimistic concurrency + same-batch projections + replay, Room as first aggregate, system console for browsing the log and every table, D-9 tenancy keyed in from the start. 7 unit tests, browser-verified on D1. `stack.md` updated. Console token in ctrl/secrets.
- 2026-09-23 — dev: WS1 spike done. https://solex-stg.collie.studio live (TanStack Start + D1, $0). Repo `alexluong/solex` pushed. `stack.md` has the stack, the dev loop, latency, and the storage-shape take architect asked for. Two gotchas recorded: free TLS is one subdomain label deep, and staging is public with no auth.
- 2026-09-19 — architect: D-3 accepted (TS Workers, no Go). Dev profile objective rev 2. Containers/paid Q moot.
- 2026-09-19 — dev: caught up; blockers: wrangler login expired, Containers needs paid.
- 2026-09-19 — architect: project dir split, requirements translated, agents + team/ created. WS1/WS3 may start; WS2 waits on Alex for `:99` + workbook.

## 2026-09-23 · WS2 — lifecycle & money (architect's 10 Qs)
Answered `solex-architect`'s ten questions in `existing-system.md` §"Lifecycle & money — architect
Qs, 2026-09-23". Read-only throughout; the booking editor's money model came out of its own
`get_*` / `list_*` / `load_*` AJAX endpoints, which the guard already allows.

Settled: settlement is the `quickout` dialog (method/currency/card/bank per room-stay, methods
cash/card/transfer/FOC/**debt**); `Đóng` is the night audit closing a day's revenue, not folio
settlement; receivables are per-folio in `giveback_debit`, partial settlement supported, **no due
date**; **room charge posts per night with an `is_post` flag** so the in-house folio grows nightly
while the daily revenue report is occupancy × rate; **departure date is exclusive** so turnover days
aren't conflicts and `allow_over_room` is real overbooking; deposits are forfeited by hand as
service line 38; cancel is blocked once checked-in or once charges exist; no-show is a bare flag;
a master folio is just a folio holding several room-stays' lines, assembled with `Chuyển dịch vụ`.

Still open (need Alex's walkthrough, not probes): room-status transitions, how group rooms get
assigned, whether the OTA receivable is net of commission.

Board: fixed the TWO/THREE personas contradiction, added three money findings, rebuilt.

## 2026-09-23 · WS1 — authentication shipped (Better Auth), console token retired
Alex picked **Better Auth 1.7.5**, self-hosted, **username + password**. Built and deployed the
same session; `solex-stg.collie.studio` now signs in. Architect accepted under D-21, product's
D-18/D-20 answers arrived mid-build and changed one thing in flight (username sign-in for *all*
roles, email optional, no email dependency anywhere).

Shape: identity (`user`/`session`/`account`/`verification`) is **not** event-sourced — a password
hash must never reach an append-only log. Staff roles *will* be, once the staff aggregate lands,
because who-granted-whom-what is what an audit trail is for. `/system` gates on a
`system_operator` flag rather than a hotel role: system admin, not admin personas.

**`events.actor` is real now** — `user:<id>`, resolved to a display name at read time so history
stays true when a name changes. Events written before today still say `"reception"` and were left
alone. That was the point of the column.

Retired: the shared console token (`SYSTEM_CONSOLE_TOKEN` deleted from the Worker) and
`SYSTEM_CONSOLE_FALLBACK`, which made the console open locally and locked when deployed — a
dev/prod difference on an access-control path.

**Found and fixed a bug I introduced**: the console's table browser was printing live session
tokens and password hashes, which would have let an operator become another user. Redaction is by
column name so future tables are covered by default; `queries.test.ts` guards it. It is also the
strongest argument yet for dropping the generic table browser in favour of Drizzle Studio.

Worth knowing: Better Auth's scrypt costs ~80ms CPU, which **exceeds the Workers free tier's 10ms
limit entirely**. We are on paid, so it works. Checked before recommending, not after.

15 tests green (was 7). Notes: `agents/solex-dev/notes/2026-09-23-2130-auth.md`; design rationale
in `stack.md` §Authentication. Next per D-22: Room → CRUD tier, then D-12 envelope, then Booking.

## 2026-09-23 · WS1 — slice 0 complete, slice 1 server side done (no screens yet)
Long build session, four sessions in parallel. `main` 26d13b1, staging e84e238a, **86 tests green**
(7 that morning).

Shipped: **Better Auth** (username+password, no email dependency, console token retired,
`events.actor` now a real user id) · **D-23 redaction** (one denylist, fail-closed, credentials +
product's PII columns) · **Room → tier (b)** per D-22 · **D-12 envelope** (ULID, schemaVersion,
businessDate, correlationId, commandId with unique index — a double-clicked command returns the
original events) · **cross-stream atomic writes + the `availability:all` guard** · **Booking and
Stay aggregates** · **the six occupancy commands** · **early check-out shortens the stay**.

**The finding worth carrying forward.** Three separate blocking bugs, all one shape: *if a
command's guard reads a table another command writes, both sides must serialise on the same guard,
not just the writer.* takeOutOfOrder not versioning availability; checkIn reading the rooms row
without versioning (architect's B3, found after I'd "closed" the first); a retry replaying a
decision made against moved state. Each looked correct in isolation, none was visible to a unit
test. Now a checklist line in `team/qa.md`.

Architect QA'd from a detached read-only worktree throughout and found two blocking bugs I would
not have found alone. Product answered five blocking questions in minutes and froze §11a mid-build.

**Still not done:** screens. A receptionist cannot do any of this in a browser, which is the bar
for "rough end to end" — slice 1 is open. Staging's event log is still unwiped (Alex's call,
relayed twice via architect; I held it because deleting data is not something a relayed green
light covers). It is now optional either way — the migration was hand-written to work on a
populated database.

Notes: `agents/solex-dev/notes/2026-09-23-2200-slice-0-and-1.md`. Design rationale in `stack.md`
§Two tiers and §Authentication.

---

### 2026-09-23 · dev (WS1) · D-24: the application layer became one `Hotel` object

Alex accepted architect's D-24 and told me to follow architect's lead on it. Landed before any
slice-1 screen, on architect's reasoning that screens written against `commands.ts` are the thing
that multiplies. `solex` 92aa083 — 100 tests green, 16 of them scenarios; board and room detail
walked in the browser.

`hotel.stays.checkIn({stayId, guests})` is the application layer now. A server function parses,
authenticates, calls the method, maps a rule failure to a code, and holds no domain logic. The
fold/decide code moved without changing.

**One amendment to D-24, which architect accepted and wrote in.** The spec called for a
hand-written `MemoryStore` emulating `UNIQUE(stream, version)`. I argued against it: the commands
do not only append events, they ask `roomFree`, read the rooms row, walk the stays under a
booking — so a fake needs its own implementation of the exact query whose bugs cost us this slice.
One that is subtly right where SQL is wrong makes the suite pass while production breaks, which is
the most expensive kind of green. The test store is the real `SqliteStore` on an in-memory
database with the deployed migrations, so the UNIQUE indexes the race tests lean on are the real
ones. The leakage that two implementations would have caught is caught instead by a biome rule:
drizzle imports only under `src/server/store`.

**Three things beyond the brief**, all flagged to architect. Three write paths became one
(`handleCommand` and `recordChange` were `handleAcross` with fewer options, each getting the retry
right independently). `occupancy.test.ts` deleted — its `book()` helper reimplemented
createBooking, which is the parallel arrangement D-24 exists to kill; its coverage moved to
scenarios and to `store/guard.test.ts`, where B3 is still pinned by name. Room commands got zod
schemas; N1 had only ever reached booking.

**A scenario found something, for product.** Checking out *before* the arrival date removes every
night and leaves a stay with no nights. `checkOut` only requires status checkedIn and nothing
stops a check-in before arrival, so the sequence is reachable — my first draft of the "last day"
scenario hit it by accident. Not touching it without a ruling: is early check-in a rule, a
warning, or fine, and should check-out before the first night be a cancellation rather than a
zero-night stay?

**Still not done:** screens — now to be written against `Hotel` from day one. Staging's event log
still unwiped, still Alex's own call.

---

## dev — slice-1 screens, and N7 landed (2026-09-23)

**N7 first, because product ruled while I was starting the screens.** Check-in now moves the stay
onto today: an early walk-in gains the nights between today and the booked arrival, a late arrival
loses the unposted ones before today, and posted nights are never touched. Nights being gained are
nights being sold, so they go through the same freeness question `assignRoom` asks, under the
availability guard. This closes the hole a scenario found last session — a checked-in stay now
always holds at least tonight, so check-out can no longer empty it. The fold learned to shorten
from the front as well as the back, and the stay projection moves `arrive` with its nights.

One fixture changed meaning and had to be made honest: `given.booking` used to arrive *tomorrow*
under the fixed clock, so every scenario that checked in was silently an early check-in. It now
arrives today, and a scenario about arriving early or late has to say so.

**The screens, written against `Hotel` from the first line** (solex `f35bded`):

- `/calendar` — every room down the side, a fortnight across the top, one query for the window.
  Nights held without a room get their own list underneath: they are sold, and no square on the
  grid would otherwise show them.
- `/bookings` — takes a booking and says **how many nights** it is next to the dates, as they are
  typed. Product's ask. The count comes from the same `nightCount` the domain holds the nights
  with, so the screen cannot disagree with what gets written.
- `/stays/$id` — assign, check in (with the guests, by name, stored as ids), check out, cancel,
  plus the nights held and the full history. Which buttons exist follows the status; what is
  *allowed* is still the domain's answer, rendered as a translated code. A disabled button cannot
  explain itself, and "the room is out of order" is something the desk needs to read.

**N6 closed**: assigning an out-of-order room is still allowed — the desk sometimes knows
something the system does not — but the stay page now says so instead of allowing it silently.

**Verified in a browser, not just in tests**: booking taken → three nights held on 305 → checked
in → checked out → 305 left dirty on the board → a second guest's early walk-in into 305 refused
with *"Phòng đã có khách trong những đêm này."* That last one is the N7 guard firing through the
whole path — adapter, Hotel, store, guard, code, translation.

**Still open:** the Vietnamese on the new screens is mine and wants Alex's native pass. Staging's
event log is still unwiped and still Alex's own call.

---

## dev — slice 2 (Setup minimum) landed in four (2026-09-23)

Four landings, each pinged and reviewed: **A** room types + rate table, **B** guests + contacts with
erasure, **C** staff/roles/capabilities, **D** the screens. solex `1245a45`, `86e6668`, `cef9f36`,
`71402c8`, `f5591d1`, `b65acd2`. 173 tests.

**A — room types and rates.** Room type ids are a slug of the name (`Phòng đôi` → `phong-doi`,
`Double` → `double`) so the free strings slice 1 already wrote are adopted rather than orphaned; a
rename never moves the id. Rates are half-open `[from, to)` and may not overlap, which SQLite
cannot express — so it is a rule decided against a query taken inside the plan, same pattern as
`roomFree`. Bookings price per night from the range each night falls in.

**The one I got wrong and architect overruled.** I had an unpriced night book at 0 and be
"flagged". Nothing rendered the flag, and slice 3 would have charged that zero, where it would have
looked exactly like a cheap room. It now refuses with `rate.notFound`. A *typed* zero is still a
real price (FOC) — that is the whole difference. Product aligned §10 row 9.

**B — people.** Product ruled contacts stay their own record (not folded into Guest): two thirds of
this hotel's business is companies, and the secretary who books never sleeps in the room. Both are
tier (b) with one extra rule running through every line: **no personal data reaches an event.**
Payloads carry an id; an edit carries the *names* of the changed fields. A scenario stringifies a
whole guest stream and asserts the name, phone and ID number appear nowhere in it. Erasure
overwrites the row and leaves a tombstone; asking twice is quiet; editing an erased person is
refused; a rebuild cannot resurrect them, because their name was never in the log.

D-23 paid for itself here — four new PII columns were redacted by the console the day the migration
ran, with no second list to update.

**C — roles.** `hotel_staff` per (hotel, user), read per request so a role revoked at 9am does not
work at 5pm. **The capability check lives in the domain**, not the adapter: `ctx.must("setup.edit")`
as the first line of each command. At the edge it would be a check the next server function forgets
and one no scenario can reach. Bundles are written out per role rather than "owner = everything",
so a new capability nobody can use is an obvious bug instead of one the owner silently acquired.
Last active owner cannot be demoted or deactivated — it is the one lockout available.

**The first-owner problem**, flagged for Alex: adding staff needs an owner, so an empty hotel could
never get one. While a hotel has *no staff rows at all*, a system operator is treated as its owner,
with a console warning; the moment anybody is added it stops for good. Rejected alternatives: a
migration backfill guessing the hotel id (staging may set `SOLEX_HOTEL_ID`, so I would have been
writing owner rows into the wrong tenant) and a seeded known password. Architect accepted it as
narrow and recorded it in D-11. The bootstrap window on the dev database is now **closed** — Alex's
owner row was added through the Setup screen itself.

**D — screens.** `/setup` and `/guests`. The booking form takes its room types from Setup and
previews the rate table live, so an unpriced night is visible *before* the guest is quoted a price
rather than arriving as a refusal afterwards.

**Still open:** Vietnamese across all of slice 2 is mine and wants Alex's pass. Staging's event log
is still unwiped and still his call. No screen creates *accounts* yet — `create-user.mjs` does, and
it now appends `staff.added` beside the membership row (architect: no tier-b write without its
event, scripts included, or the first owner is the one person with no history).

---

## dev — slice 3 (money) through landing 5 (2026-09-23→24)

Five landings, each pinged and accepted: **1** ledger core `61819a7`, **2** folios `c9bab9f` +
atomicity fix `077088d`, **3** night roll `b3c7597`, **4** check-out guard `c36f36f`, **5** the
folio screen `624ac57`. 232 tests, check 0, build clean, all pushed.

**1 — the ledger (D-17).** Accounts, and immutable entries whose lines sum to zero. Tier (a), and
the first place where that is not a preference: money has to be able to say what it said yesterday.
One stream per account with the entry appended to every account it touches — so each stream is that
account's statement and the version guard is per account. Balances are summed, never stored.
Architect accepted the multi-append shape; product wrote it into §7/§12.

**2 — folios.** Every command writes `folio.*` (what was sold) and `ledger.entry_posted` (what
moved) in one batch. `room` is reserved for the night roll in the *domain*, with an explicit
`system` flag rather than sniffing the actor string. Refunds are capped at payments received, not
at the balance — a folio can be in credit for several reasons and refunding against that is how a
till goes missing.

**The flaw I shipped and caught ten minutes later:** voiding did the ledger reversal in one commit
and marked the charge void in another. Between them, money back but the line still live — a bill
that adds up to something other than the sum of what it shows. Now one batch, pinned by a test
asserting both events share a correlation id. Architect made it a checklist line: *a money command
is one batch and a test asserts shared correlationId*.

**3 — the night roll (D-25).** One idempotent command, three callers: cron, the first request of
each business date, and check-in. Two guarantees it lands once — a deterministic command id per
(stay, night, **attempt**) hitting the UNIQUE index, and a read of what is already charged.

**The attempt counter is not decoration.** Without it the id never changes, so a night whose charge
was *voided* could never be posted again: the re-post was swallowed as a duplicate of the charge
just taken off, and the room would have gone free for the rest of the stay. A test found it within
a minute of the id being introduced.

The lazy roll is **derived, not watermarked** — it asks which nights of in-house stays have no live
room charge. A stored `lastRolledDate` is a second truth that a crash between posting and updating
leaves permanently wrong with nothing to notice. Self-heals after an outage of any length; a
three-day-outage test covers it. It runs as `system:night_roll` through a separate `systemHotel()`,
so history does not claim the receptionist who opened a page at 07:00 posted the 02:00 charge.

**4 — nobody leaves with the bill unpaid.** Check-out needs the folio settled or transferred to a
company receivable. The balance is read *inside the plan under the folio stream's version*, and
that stream is in the batch — a charge landing between read and write loses the race and the
command re-runs. The availability guard's shape, with money. A credit balance passes: the hotel
owing the guest is not a reason to keep them at the desk. Every scenario that ends with somebody
leaving now pays first, through a `given.settled` fixture — which is what the desk does.

**5 — the bill on the stay page.** Charges, payments, running balance; voided lines struck through
but still there; void and refund offered to owners only. Walked in the browser: check-in posted
650,000, two beers at 40,000 went on, check-out refused at 730,000, payment settled it, check-out
closed the folio.

**The bug that screen found, which had been live since slice 2.** `<input type="number" min={1}
step={1000}>` makes 650,000 an *invalid* value — the valid ones are 1, 1001, 2001 — and the browser
refuses the submit **silently**. Prefilling the payment box with the balance produced a button that
did nothing: no error, no request. `useCommand`'s own comment says a screen that silently does
nothing is indistinguishable from a broken one, and I had shipped exactly that in three forms
(payment, booking rate, Setup rate) without noticing. All money fields are `step={1}` now.

### Open, in the order architect set

1. **Receivable side** — `transferToReceivable` is built and tested (it is what lets a company
   booking check out); still to do: `receivable.record_payment`, `write_off` (owner), and a
   receivables screen.
2. **Expenses** — `expense.record` (receptionist, petty cash) / `expense.void` (owner).
3. **Cron entry** — deferred to pre-go-live by architect and recorded in D-25. `main` is
   `@tanstack/react-start/server-entry`, so a `scheduled` handler needs a custom entry wrapping the
   framework's. Lazy alone is correct because it catches up; the cost is a stale dashboard on a
   night with no requests, not lost revenue.

### Waiting on Alex

- **Vietnamese across slices 1–3 is mine** and wants his pass. The folio screen has the most of it:
  *Còn nợ*, *Đã thanh toán*, *Ghi nhận thanh toán*, the void-reason prompt, the check-out refusal.
- **Staging's event log** is still unwiped and still his call.
- **Whether a receptionist should refund at all** — currently owner-only, alongside voiding.
- The **folio screen itself** is his review checkpoint; architect asked for it clickable early for
  exactly that.

### Open question for product

Account id shape. Their spec writes `<hotel>/account:receivable:<companyId>`; mine is
`<hotel>/ledger:receivable:<companyId>` — the stream *kind* word differs, the rest matches, and
mine follows §12's `ledger:*` stream list. Folio, cash and revenue accounts already use it. Nothing
is deployed and only the dev database has ledger events, so it is a constant edit if they prefer
`account:` — needs deciding **before the receivable side lands**.

### State of the dev database (not staging)

The first-owner bootstrap window is **closed**: Alex has a real `hotel_staff` owner row, added
through the Setup screen. Charge categories are seeded. Room types `double`/`phong-doi` and rates
exist, rooms 201 (out of order), 305, 402. Staging has none of this — no money events at all.

## solex-dev — slice 3 finished: receivables, expenses, and the sweep (2026-09-24)

Commits `10c57ed` → head. Staging `solex-stg.collie.studio`, latest version `0094e999`. 255 unit
scenarios green, solex-qa's 27 browser tests green, `pnpm check` 0, build clean.

### 6 — what companies owe (`10c57ed`)

A debt that outlived the stay. Grain is the **company, not the folio** (D-16): a company with four
stays pays one transfer against one balance, which is how they actually pay and what "what does ABC
owe us" has to mean. A receivable is a ledger account like a folio, so the commands are the same
shape — a vocabulary event in hotel words and a balanced entry in one batch.

- A payment is **capped at the outstanding amount**. More is not a payment, it is a deposit from a
  company that has none, and it would leave a receivable in credit that nothing downstream reads.
- `receivable.settled` is emitted **explicitly** rather than left for a reader to infer from a
  balance reaching zero. A projection that has to guess what an event meant will eventually guess
  wrong.
- A write-off **requires a reason** and lands in `expense:writeOff` — the debt becomes money lost,
  which is what it was the moment it stopped being collectable. Owner only.
- The list drops settled companies; the account and its statement stay. A page of zeroes is a page
  nobody reads.
- **Found while building the screen**: `transferToReceivable` had no UI anywhere, so nothing in the
  app could create a receivable at all. Added the transfer control to the folio panel.

### The double-click hole, and where the fix belongs (D-12 (f), `dba5704`)

The receivable payment scenario caught it: the second click on a payment that *settled* a debt was
refused as "payment against a settled receivable". The command id already stopped a double click
writing twice — but only at the **unique index**, and the rules refuse before the write ever gets
there. Same hole in `folio.void` (alreadyVoided) and the refund cap.

I first fixed it locally in `receivables.ts` with a `replayOf` short-circuit. Architect ruled it
right in kind, wrong in place: **`commit` does the lookup before the first `plan()`** and returns
the original events; commands derive their answers from the events commit returns rather than from
ids minted before it, so a second click gets the first click's payment id instead of one belonging
to nothing.

The ruling had a consequence it did not state, and this is the part worth remembering: folio and
receivable commands were **reading, deciding and minting ids outside the plan thunk**, so nothing
would ever have reached the new guard. All of that moved inside `plan()`. Side effect: a retry after
a collision now genuinely re-reads and re-decides for money commands, which is the property
`prepare` always claimed and quietly did not have. Architect made it a checklist rule — *every read
and rule runs inside `plan()`, nothing minted before it*.

Both double-click scenarios were checked by disabling the lookup: they fail without it, so they
test the guard and not the rules.

### 7 — money out (`35d6db9`, categories corrected after review)

`expense.record` is the desk's and `expense.void` is the owner's: the receptionist pays the man who
brings the gas cylinder, and deciding a payment never happened is not the desk's call. A drawer that
stops matching the day's takings surfaces at midnight with nobody left to ask.

- Categories are a **fixed list in the domain**, not Setup data. I first guessed seven generic ones;
  architect sent me to the discovery notes, where the client's own list was sitting: đi chợ,
  chi phí phát sinh, tăng ca buồng phòng, tạm ứng, khác (requirements §4.7, product §6). `writeOff`
  is reserved from hand-posting, or an owner could file an ordinary purchase as a bad debt.
- `description` is **required** where product §6 has an optional `note`: "Tạm ứng · 2,000,000" with
  nobody's name on it is the row an owner cannot audit later. Architect accepted and product is
  aligning; no `payee` column, the name goes in the description.
- Voiding reverses in one batch carrying **today's** date — a correction that back-dates itself
  changes a closed day's total. The row stays, struck through, with its reason.
- Totals are summed **from the ledger**, where the reversal already cancelled a voided expense, so
  nothing has to remember to filter. A debt written off on the receivables screen shows up in the
  same totals under *Công nợ đã xoá*, which is the point of both being expenses.
- Migration `0011` drops `spike_items` — as a migration, not a hand-run statement, so every database
  stays the same shape and the log says when it went (architect's call).

### The form sweep — three leaks and one silence (`9fd031b`)

solex-qa's browser suite found all of it. Twenty forms, one pass:

- **N10, a blocked submit must say why.** `required`, `min` and `step` make the browser refuse with
  a bubble that vanishes on the next click and may never be drawn at all. An empty `required`
  select (no room types yet, categories not seeded) and `step={1000}` against 650,000 produce a
  button that silently does nothing. Every form is now `noValidate` and validates in the handler,
  in field order.
- **N11, submitting before hydration leaked PII.** A form with no method does a GET when the browser
  handles it alone — every field into the query string and from there into Cloudflare's access log.
  A guest's name and phone on /bookings; a **password** on /sign-in. Every form is `method="post"`.
  It still cannot do anything useful that early; it just stops leaking while it fails.
- **N12, `/guests?q=<name>`** was the same leak by another route. The search posts now and its
  results live in component state. Architect had scheduled this for slice 5; I did it in the same
  pass because I was already in that file.
- `src/ui/form.tsx` holds the shared piece (`useFormNotice`, `firstProblem`, `isMoney`, `filled`)
  so twenty forms say things one way and the reasoning lives in one comment.

### Staging is throwaway until production exists (D-26)

I had been holding the staging wipe for Alex on the grounds that a peer session cannot authorise a
destructive data op. He asked why architect's word wasn't enough, and the answer is now D-26:
**until production stands up, staging holds nothing worth protecting** and architect may call a
wipe, reseed or redeploy. Production data and deploys, secrets, permission/config changes and
rewriting shared history stay Alex's. He offered a separate throwaway `solex-dev` environment; I
declined it — staging already is that, and a third wrangler config, D1 binding and deploy path buys
nothing while D-26 holds.

Wipe done: events, all projections and tier (b) rows; auth tables and `d1_migrations` kept. Staging
comes back **signed in as owner**, because the first-owner bootstrap reopens while a hotel has no
`hotel_staff` rows — worth knowing before anybody walks it.

### Working with solex-qa

They own `e2e/**` and push to the same repo, so a `pull --rebase` before pushing is now routine.
Their suite wants `PORT_BASE+1` (7531); a stale vite dev server from 2026-09-23 squats on it here,
so I run with `E2E_PORT=7621` rather than killing a process I did not start. Their `test.fail`
marker on the empty-hotel setup spec now passes, which aborts the whole run until they remove it —
I ran the suite by disabling it locally and restored their file untouched. Theirs to delete.

### Waiting on Alex

- **Vietnamese across slices 1–3 is still mine and wants his pass.** Now also the receivables and
  expenses screens — *Công nợ*, *Chi phí*, *Ghi nhận thanh toán*, *Xoá nợ*, and every N10 message
  written in the sweep.
- **Whether a receptionist should refund at all** — still owner-only, alongside voiding.
- The **folio screen** remains his review checkpoint; the money loop is now complete around it
  (charge → pay → transfer → chase → write off → expense).

### Closed since the last entry

- Ledger stream id stays `<hotel>/ledger:<kind>:<id>`; product aligned to it.
- Staging wipe: done, and no longer needs asking (D-26).
- Expense category list: the client's own, not mine.

### State of the databases

**Dev** (local file): Alex is a real `hotel_staff` owner, bootstrap window closed. Charge categories
seeded; room types `double`/`phong-doi`, rooms 201 (OOO), 305, 402; several stays through the full
money loop; company `ABC` settled (500,000 transferred, 200,000 paid, 300,000 written off); one
expense recorded under the retired id `supplies`, which now shows its raw id — the fallback
working, and not something to edit away, because the log is the truth.

**Staging**: wiped, migrated to `0011`, first-owner bootstrap open again. No money events.

### Next

Slice 4: `CreateUser` / `UpdateUser` / `DisableUser` (no accounts screen exists — `scripts/create-user.mjs`
is still the only way to make one), roles, history tabs. The **cron entry stays pre-go-live**: `main`
is `@tanstack/react-start/server-entry` and a `scheduled` handler needs a custom entry around it;
the lazy roll loses nothing but dashboard freshness on a request-less night (D-25).

## solex-dev — slice 4: accounts, roles, histories (2026-09-24)

Three landings. Staging is at `d006aa47`; `main` at `b364ccd`; 276 scenarios green.

### What shipped

**Accounts (`/accounts`, `/accounts/$id`).** Identity, and it is deliberately not the same thing as
a position here: `hotel.users.*` creates the ability to sign in, `hotel.staff.*` grants the access.
An account with no membership is somebody who can sign in and do nothing, which is a real state and
one the owner can now see. Passwords cross the adapter boundary and go no further — hasher and row,
never the log, never a response. I read the raw `events` table to confirm it.

**Roles moved off Setup onto `/accounts`.** Two screens writing the same rows is how a role gets
changed in one place and read from another. Setup now says so and links across.

**A role change ends live sessions in the same batch** — architect's checklist line. `setRole` and
`deactivate` both carry `also: [accounts.endSessions(userId)]`.

**History tabs**, now on every entity: person (`/guests/$id`), account (`/accounts/$id`, which shows
the `user:` and `staff:` streams as one list), and booking (`/bookings/$id`, the booking's stream
plus its stay's — the booking's own is short, and a page that stopped at "taken" would look broken).
The bookings list became `bookings.index.tsx` so the detail route is a sibling, not a child of a
layout; that is the trap `/accounts` hit first.

### Two bugs the history pages found

**A guest created at check-in had a row and no `guest.created` event.** Their history was empty and
an erasure would have been a tombstone with nothing before it — which is the record the Decree 13
story rests on. `upsertGuests` now returns an event per guest and check-in spreads those streams
into its batch. Architect audited every other insert/update in `src/server` afterwards and found no
second instance; the checklist gained *every tier (b) row has a creating event*.

**N17 (QA, blocking): a hyphenated username could be created and never signed in to.** Better Auth's
username plugin re-validates at sign-in against `/^[a-zA-Z0-9_.]+$/`, narrower than ours, and our
deliberately vague "wrong username or password" — which exists so nobody can enumerate staff — hid
the real error. One exported `isUsername` now feeds both ends. Checklist: *where a library
re-validates, it gets our rule, not its default.*

### N18 — a save that changes nothing writes nothing

QA's, blocking, fixed in the same landing as the booking tab. Pressing Save on `/accounts/$id`
without touching anything wrote `user.updated {fields:["name","contactEmail"]}`. The rule counted a
field as changed because the form *sent* it — and a correction form sends every box it draws,
because it must: a screen may not decide on the user's behalf what counts as a change (N16). So the
rules now hold the row and compare. A field changed when its value differs; an empty box over an
empty column is not a change; a save that moves nothing refuses with `user.nothingToChange` and
appends nothing. Guests and contacts already worked this way (`changedFields`) — accounts were the
newest code and the odd one out, which is the shape to watch for on the next aggregate that grows an
update command.

### Waiting on Alex

Unchanged from the slice-3 entry, plus the **accounts and booking screens' Vietnamese**. Still open:
whether a receptionist should be able to refund at all.

### Next

Cron entry, still pre-go-live (D-25). Otherwise slice 4 is done.

## solex-dev — 5.1a Company landed, server side (2026-09-24)

`a9fe985`, staging `138c9393`, 284 scenarios green. Written mid-slice so the state survives a
compaction; the next session picks up from "What is next" below.

### Why Company came first

Architect's call, and the right one: `companyId` on a transfer-to-receivable was free text. "ABC"
and "Cty ABC" are one company to the desk and two ledger accounts to us — one real debt showing as
two, neither settleable in full. Group bookings would have multiplied that, since the master folio
is billed to a company by definition.

### What is built

- **`companies` table** (migration `0012`), tier (b): slugged id, name, taxCode, phone, note,
  `defaultRouting` as JSON, `retiredAt`. Unreadable JSON reads back as `{}` rather than throwing —
  a company with no stated routing bills everything to the guest, which is the safe direction.
- **`companyRules`** in `setup/domain.ts` — define / update / retire. Update compares field by field
  and writes nothing when nothing moved (the N18 line, applied on the way in this time rather than
  after QA found it).
- **`hotel.companies.*`** in `hotel/setup.ts`, and `hotel.events.ofCompany`.
- **`company.inUse`** — retire refused while an open receivable *or* a live booking points at the
  company. Both asked inside the plan. `bookings.company_id` is projected from
  `booking.created.party.companyId` (migration `0013`) so that half of the rule is real now rather
  than arriving later with the group screens; nothing writes a company onto a booking yet.
- **Adapters** — `defineCompany` / `updateCompany` / `retireCompany` / `getCompanies`, and
  `getSetup` now returns companies.

### What is next, in order

1. **The Setup screen section** for companies, and **replacing the free-text company box** on the
   folio transfer form and the receivables screen with a picker over the list. Until that lands the
   entity exists and nothing uses it.
2. **5.1 landing 1 (domain)** — group booking creates N stays from `requests[]`; `booking.party`
   gains `companyId`; master folio opens lazily on `folio:master:<bookingId>` (`masterFolioIdFor`
   already exists in `hotel/folios.ts`); routing resolved at `postCharge`, which today hardcodes
   `folioIdFor(stayId)`. `booking.groupNotSupported` in `booking/domain.ts` is the rule holding
   groups back — that check is the thing to delete.
3. **5.1 landing 2 (screens)** — group form, booking detail showing the master folio with
   pay/transfer/void, per-stay routing controls.
4. **5.1 landing 3** — the cascades: `booking.close` guarded on master balance, check-out unchanged.

### Architect's rulings on 5.1, so they are not re-litigated

- Routing is keyed by **ChargeCategoryId** (§6 aligned in product `3af0a08`).
- Default without a company: **room → master, everything else → own**, settable per stay per category.
- **Check-out keeps the own-folio guard.** The master is guarded at `booking.close`, not at
  check-out — a group stay can route everything to the master and walk out with a zero own folio,
  which is correct and is why the master needs a screen before `booking.closed` means anything.

### Slice 5 order (architect, for after 5.1)

5.2 cron entry + HotelProfile (D-7 zone + roll hour, replaces the hardcoded `Asia/Ho_Chi_Minh`) →
5.3 dashboard + reports → 5.4 deposits → 5.5 folio print → 5.6 search, overbooking override, rest
of §11. Cron moved up because the money loop is done and wants weeks of soak, not days.

## solex-dev — N19: a contact typed on the booking form is born with an event (2026-09-24)

`4cb9908`, staging `be0647d5`. 285 scenarios green, build clean.

QA's S4-21 reads the whole database and asks whether every tier (b) row has a creating event.
Contacts *picked from the list* had one — the people CRUD path goes through `contactRules.create`.
Contacts *typed into the booking form* did not: `upsertContact` in `store/people.ts` returned a row
write and nothing else, so the contact was born mute. Same gap as guests-at-check-in, fixed the same
way — `upsertContact` now returns a `StreamAppend` beside the `Write`, exactly as `upsertGuests`
already did, and `bookings.create` lands it in the same batch. Payload stays empty: the id is in the
stream id, the name is in the row where it can be erased (D-20).

Worth naming as a pattern rather than a third one-off: **both halves of a tier (b) row's birth have
to be returned by the same function**, because a caller that has to remember to append the event is
a caller that will forget. `upsertGuests` got this right and `upsertContact` was written next to it
and didn't. The store port's `people.contact` signature is now the thing that enforces it — it
returns `{ id, write, stream }`, so a batch that drops the stream doesn't typecheck.

Scenario: `"gives a contact minted by the booking form the same birth event"` in
`hotel/people.test.ts`. Verified red before the fix (`expected [] to deeply equal ['contact.created']`).

Not run here: QA's e2e. Port 7531 was already taken by another session's dev server, and killing it
isn't mine to do. S4-21 should go green on a rebuilt e2e db — it rebuilds every run, so rows the
older code left behind won't linger.

**Next**, unchanged from the entry above: the Company Setup screen, then the transfer form's
free-text company box becomes a picker over the list.

## solex-dev — 5.1a finished: companies are pickable (2026-09-24)

`d896f3c`, staging `eda576d9`. 285 green, build clean.

Last commit defined the entity and nothing could use it. Now:

- **Setup has a Companies section** — define (name, tax code, phone, note), list, retire. Retired
  rows stay visible and greyed, like room types and rates.
- **The folio's transfer form picks from the list.** That was the point of Company: "ABC" and
  "Cty ABC" were one company to the desk and two ledger accounts to us.
- **Receivables names the company** instead of printing its slug, reading the list with
  `{ all: true }` — a debt outlives the decision to stop booking somebody — and falling back to the
  id for a debt older than the list.

Two silences, two answers (N10): an empty picker says `folio.noCompanies`, a picker nobody chose
from says `folio.companyRequired` (reworded from "Say which company" to "Choose which company", and
VN "Nhập" → "Chọn", now that it is a select). The select has **no default**: which company owes this
is not the screen's to answer (N16), and the first name alphabetically is a wrong debt waiting.

Verified in the browser end to end, not just in unit tests: define a company → charge a stay →
transfer → the receivables page shows **the name** and the amount → retiring that company is refused
with `company.inUse` in readable Vietnamese. That last one is the guard from the previous commit
firing for real, on the receivable half. The booking half still can't fire — nothing writes
`bookings.company_id` until groups land, which is expected and why the column went in early.

**Deliberately not built: the routing control.** `Company.defaultRouting` decides own bill vs master
folio, and neither the master folio nor Alex's words for it exist until 5.1. A box writing a field
nothing reads, under a label still being translated, is not a head start. It arrives with landing 2,
where the per-stay routing controls are.

I touched **QA's e2e support file**: `companyOwesOneNight` now defines the company then
`selectOption`s it instead of `fill`ing free text, and S3-23's "transfer with no company" defines one
first so it still tests the silence it was written for rather than the new empty-list one. Mechanical
adaptations to a control I changed — QA owns them and should overrule me freely.

**Next: 5.1 landing 1 (domain)** — group booking creates N stays from `requests[]`, `booking.party`
gains `companyId`, master folio opens lazily on `folio:master:<bookingId>`, routing resolved at
`postCharge`. `booking.groupNotSupported` in `booking/domain.ts` is the check to delete.

## solex-dev — 5.1 landing 1: groups in the domain, plus N20 (2026-09-24)

`98f0989` (groups) and `d607656` (N20), staging `38ecc5ac`. 301 green, build clean.

### Groups

`booking.groupNotSupported` is deleted. A booking carries `requests[]` and mints one stay per room:
"ten doubles and two twins" is two requests and twelve stays. The array is the shape even for one
room, so the wire does not change with the number of rooms. `booking.party` gains `companyId`;
`kind` is read off the booking, not inferred from the stay count — a group of one is still a group.

**Routing lives in its own pure module** (`src/server/folio/routing.ts`) with its own scenarios,
because what costs money is *precedence*, not arithmetic: stay override → company agreement →
fallback of room-to-master. `postCharge` resolves it inside the plan like every other fact (D-12 (f)).
The master folio's id is the booking's and it opens on the first charge routed to it — never as a
side effect of taking the booking (architect's stream shape: `<hotel>/ledger:folio:master:<bookingId>`).

**Architect's ruling, recorded so it is not re-litigated:** routing is a **group-only** concept.
`postCharge` resolves `own` unconditionally for an individual booking; a lone company traveller keeps
the old path (own folio → transfer-to-receivable at check-out), even when their company has a routing
table. I asked rather than guessed, because the literal reading of "else room → master" would have
sent every individual's night charge to a master folio and left the check-out guard always seeing
zero — gutting slice 3 rather than extending it. There is a scenario pinning exactly that case.

`routeCharge` takes a `stayRouting` nothing supplies yet. That is the seam landing 2 plugs into, and
it is a parameter rather than a half-written rule.

Verified in the browser that individual bookings still create exactly one stay through the screen.

### N20 (QA)

`rateRules.update` was handed only `retiredAt`, so it was structurally unable to compare and always
emitted `setup.rate.updated`. Now takes the row and diffs. Same cause as N18 twice over: **a command
that reports what changed must be given the row.**

QA also verified N19 (78/78 green on a fresh e2e db, S4-21 finds no orphans).

### Standing, not done

Architect's item (2) from QA's slice-4 close-out: every update command should *refuse* with
`nothingToChange` and the screen say so, as accounts does — guest/contact/roomType/rate currently go
silent. Scheduled 5.6. It converts N20's `same ? [] :` into a `check`, so it should land as one
decision across four screens with its strings, not as a drive-by. Item (3), grouping history tabs by
correlationId, also 5.6.

**Next: 5.1 landing 2 (screens)** — group booking form, booking detail showing the master folio with
pay/transfer/void, per-stay routing controls. The routing controls need Alex's words for "own bill"
vs "master folio" before they are worth translating.

## solex-dev — 5.1 landing 2: group screens and the master folio (2026-09-24)

`f6b68cc` (group form + routing controls) and `98f5009` (master folio panel). Staging `68192888`.
309 green, build clean.

### The booking form takes a group

Whether it bills as a group is **said outright, not guessed from the room count**: a company block
of one room is still a group and wants a master folio; a family taking three rooms on holiday is
not. Choosing "a group" swaps the room picker for a room *count* and sends the desk to the booking
afterwards rather than to a stay, because there is no single stay to go to. The company picker is
offered on both kinds — an individual on company business still has one.

### Per-stay routing

New `stay.routing_set` / `stay.routing_cleared`, folded onto the stay, read by `postCharge`. **Two
events, not one with a nullable target**: clearing an override means "back to whatever the company
agreed", which is a different answer from overriding to the guest, and the control offers all three.

The control only exists on a group, and `stay.notRoutable` is what makes that safe rather than
cosmetic. This is N16 read the other way: the screen may not answer a rule for the user, and may not
offer a choice the rules will refuse either.

### The master folio

Folio commands now take `{ stayId } | { bookingId }` — a union, not two optional fields, because
optional fields can express "both" and "neither". The entry a master folio writes carries **no
stayId**: a group's bill has twelve stays under it and naming one is a lie the reports repeat.

**The panel deliberately has no way to post a charge.** Lines arrive by routing, from the room they
belong to, which is what keeps "who drank the minibar" answerable. A box posting straight to the
master would be a way to bill a company for something no room admits to. Pay, transfer, void only.

### Verified through the real stack, not just scenarios

Group of 3 booked against a company → 3 stays → minibar override set to `master` on one stay →
charge posted there lands on the **group's** bill → transferred to the company → the receivables page
shows **120.000 on one account**, being that transfer plus an earlier stay-level one. One company,
one debt, whichever bill it came from. That is the thing Company was built for, working.

### Wording

"Own bill" / "master folio" and the `routing.*` and `master.*` keys are the developer's placeholder
in both languages, marked in `messages.ts`. Nothing depends on the words — Alex's pass is a string
swap.

### Next

**5.1 landing 3**: `booking.close` guarded on the master balance; check-out unchanged (architect's
ruling — a group stay can walk out with a zero own folio, which is correct). Then 5.2 cron +
HotelProfile.

QA has S5-6…S5-13 waiting for these screens; told them the affordance names.

## solex-dev — paused for compaction; landing 3 spec (2026-09-24)

Everything green and pushed at `db0c0e0` (solex), staging `68192888`. 309 scenarios, build clean.
Nothing half-written.

**Resume here — 5.1 landing 3, CloseBooking.** Architect's ruling, verbatim enough to build from:

- A **new explicit command** `booking.close`, on the desk capability. `booking.closed` already exists
  in `foldBooking` and nothing has ever emitted it — this is what emits it.
- Refused unless **every stay is checked out or cancelled** (`booking.staysOpen`) **and the master
  balance is ≤ 0** (`booking.masterNotSettled`).
- Both read **inside the plan, under the master stream's version**, the same way the check-out guard
  reads the folio balance — otherwise a charge landing mid-command closes a booking that owes money.
- **Not automatic on the last check-out.** The money guard stays a visible act somebody performs.
- Booking detail shows "ready to close" and the button.

Check-out is unchanged (earlier ruling): a group stay walks out with a zero own folio, which is
correct, and is why the master needed its own screen first.

Two i18n keys will be needed for the refusals plus the button and the ready state; the
`routing.*` / `master.*` / `booking.kind*` placeholders are still awaiting Alex's wording pass and
should not be touched by this landing.

After landing 3: **5.2 cron entry + HotelProfile** (D-7 zone + roll hour, replacing the hardcoded
`Asia/Ho_Chi_Minh`), then 5.3 dashboard/reports → 5.4 deposits → 5.5 folio print → 5.6 search,
overbooking override, plus architect's two deferred items (N22 `nothingToChange` everywhere, N21
history grouped by correlationId).

Still waiting on Alex, not blocking: the Vietnamese pass (now including the group and routing
screens, which are live with my placeholder wording).

**Correction (architect):** "whether a receptionist may refund" was never open — it is settled in
`product.md:45`, where `folio.void/refund`, `receivable.write_off` and `expense.void` are in the
owner bundle (D-17 role split). The code has always matched it. I had been carrying it in this log
as an open question for Alex; it is not one, and should not be raised again unless he reopens it.

## solex-dev — N23 recorded (QA, on db0c0e0); still paused

Verified QA's report in the code before logging it. It is real, and it is mine.

`projectBooking` only ever writes `status: "booked"` or `"cancelled"` — there is **no `booking.closed`
case in the projection at all**, because nothing has ever emitted that event. `bookingsOfCompany`
(`store/projections.ts:409`) counts `status = 'booked'` as open. So any company that has ever been
booked can never be retired: `company.inUse` refuses forever, individual or group, paid or not.

**This corrects something I wrote two entries up.** When I projected `bookings.company_id` early I
said it made `company.inUse` "whole rather than half", and that the booking half was correctly
always-false until groups landed. That was wrong in the direction that matters: it is always
**true** once a company has a booking. I built a guard whose second half could not be satisfied,
because the state it waits for has no way to be reached. Projecting the column early was still
right; claiming the rule was therefore complete was not — a guard is not complete when nothing can
clear it.

**Landing 3 must include the projection**, not just the command: a `booking.closed` case in
`projectBooking` setting `status = "closed"`. Without it CloseBooking would emit an event the
company guard cannot see, and N23 would survive a landing that looks like its fix.

Open question with architect (QA raised it, not mine to answer): whether CloseBooking covers
**individual** bookings too, or whether an individual's booking should close on check-out. Landing 3
as specced is group-shaped — "every stay checked out or cancelled, master balance ≤ 0" reads fine
for one stay and a master folio that was never opened (balance 0), so one command may cover both.
Waiting on the ruling before building either way.

No code change yet; still paused for compaction. Nothing pending in either repo.

### Addendum (architect) — landing 3 spec revised by N23. **Build from this, not from 004a199.**

- **(a) Individual bookings close automatically**: `booking.closed` is emitted **in the batch of the
  last stay's `checked_out` / `cancelled`** — same commit, a reaction and not a click. No guard: there
  is no master folio, and the own-folio guard has already fired at check-out.
- **(b) Group bookings close only via the explicit CloseBooking**, with `booking.staysOpen` and
  `booking.masterNotSettled` as specced in 004a199.
- **(c) `company.inUse` must read live stays, or master balance > 0 — not `booking.status`.** This
  **supersedes** `bookingsOfCompany` as written (`store/projections.ts:409`, currently
  `status = 'booked'`). The guard should ask what is actually outstanding, not what a status column
  happens to say.

So landing 3 is three things, not one: the automatic close on the last stay, the explicit
CloseBooking for groups, and rewriting the company guard's query.

**The projection case is still needed** — `projectBooking` has no `booking.closed` branch, so without
one the row would keep saying `booked` after the event says otherwise. It is no longer what
`company.inUse` depends on (that is (c) now), but a status column that contradicts its own log is its
own bug, and the booking list reads it.

Also confirmed by architect, and it is correct as built: **charges routed to a master folio keep
their `stay_id`** — the charge really did come from a room, and that is what makes "who drank the
minibar" answerable. Only master *payments and transfers* have none, because those belong to the
booking. No change needed; noting it so nobody "fixes" it later.

Two i18n keys for the refusals are still mine, to be written with the landing.

**Landing 3 scope, settled (architect).** Five things, no more:

1. Individual bookings emit `booking.closed` in the batch of the last stay's `checked_out` /
   `cancelled` — a reaction, no guard.
2. Explicit `CloseBooking` for groups, `booking.staysOpen` + `booking.masterNotSettled`, both read
   inside the plan under the master stream's version.
3. `company.inUse` reads live stays or master balance > 0, replacing the `booking.status` query.
4. A `booking.closed` case in `projectBooking` — confirmed keep: a row contradicting its own log is a
   bug regardless of who reads it.
5. Two i18n keys for the refusals.

Booking detail shows "ready to close" and the button (group only). Check-out stays unchanged.

## 5.1 landing 3 — a booking that ends (solex `624b7dd`)

Built. All five items, nothing else. 322 scenarios green, build clean, deployed to staging
(`fd74a805`).

**Individual bookings** close themselves in the same batch as the last stay's `checked_out` or
`cancelled`. `decide.closeWithLastStay` is the pure half; `closesWithThisStay` in `stays.ts` reads
the booking stream and the sibling stay rows inside the plan and returns the append. Both check-out
and stay-cancel call it. One scenario asserts the reaction shares the check-out's `correlationId`,
which is the grouping N21 will read.

**Groups** close only via `hotel.bookings.close`, a new `booking.close` capability in both bundles
(desk work per §5). Refuses `booking.staysOpen` and `booking.masterNotSettled`, both answered inside
the plan.

**One thing I added that was not in the five, and why.** `appendAcross` drops any stream that
contributes no events, so including the master stream purely for its version would have been a guard
with no teeth — the balance read would not have been protected at all. So the close **also appends
`folio.closed` + `ledger.account_closed` to the master folio**, exactly as check-out closes a stay's
folio at zero. That makes the version real and is the same rule the stay side already follows: a bill
nobody can post to again. Flagging it rather than burying it; say if you want it out.

**N23 fixed.** `bookingsOfCompany` is gone. Two queries replace it: `liveStaysOfCompany` (stays
joined to bookings, status in booked/checkedIn) and `masterBookingsOfCompany` (its non-cancelled
groups, whose master balances `retire` then asks the ledger for one by one). Three scenarios pin it —
retire succeeds after an individual company guest checks out and pays, refuses while somebody is in
a room, refuses while a group's master still owes.

`projectBooking` gained the `booking.closed` case. `bookingStatus.closed` was needed to render it.

**One existing scenario changed**, and it is the behaviour being replaced, not a test bent to fit:
`scenarios.test.ts` "books a room, checks in, and checks out" asserted the booking stayed `booked`
after check-out. It now asserts `closed`.

**Five new i18n keys, not two**: the two refusals, plus `bookingStatus.closed`,
`eventType.booking.closed` and the panel's three strings (`booking.closeTitle`,
`booking.readyToClose`, `booking.close`) — a button and a status need words to be rendered at all.
All of them sit inside the "WORDING NOT FINAL (Alex's pass)" block with the rest of the group
vocabulary.

**N16 reading on the button**: the page does not offer it while either condition fails, and says
which one is in the way using the refusal's own string. The codes still exist for the race — a
routed charge can land between the page loading and the click.

## 5.2 — half built, clean stop for compaction

Build from **solex `b531242`**, staging `7cfb5ced`. 335 scenarios green, build clean, both repos
pushed. Two commits:

**`54a13b6` — the cron half of D-25. Done.** A server entry of our own
(`src/server-entry.ts`), because TanStack Start's default one exports `fetch` and nothing else, so
`scheduled` had nowhere to live. `tanstackStart({ server: { entry } })` points the build at it and
wrangler's `main` follows. Cron is **hourly**, not once at the cutover: the roll hour is per-hotel
config and a cron expression is not, so the handler asks the same idempotent question every hour and
usually finds nothing. The lazy first-request roll stays. Live on staging — `schedule: 0 * * * *`.

**`b531242` — HotelProfile, backend only.** `hotel_profile` (migration 0014), a singleton tier (b)
row: name, timeZone, rollHour. `hotelProfileRules` validate the zone against what `Intl` can actually
format, the hour against being an hour, and report which fields moved (N18/N20). `businessDateFor`
now takes a `HotelDay`; an instant before the roll hour belongs to the day before, stepped on the
calendar not on a millisecond count. `HotelDeps.day` is required, read from the profile by the
composition root with `DEFAULT_HOTEL_DAY` as a visible fallback. `systemHotel()` is now async.

Threading it cost **one field on `CommandContext`** (`businessDate?`). The log layer has no hotel to
ask, so the domain says which day the command falls in, once, where every command already passes.
Absent = the old default, which is what every event written before today carries.

### What is left of 5.2

1. **The Setup screen section** for the profile — form, i18n keys (en + vi), `saveProfile` is already
   wired in `src/server/api/setup.ts` and `getSetup` already returns `profile` + `defaultDay`.
2. A timezone picker. I dropped a `knownTimeZones()` helper from `getSetup` rather than invent one at
   the stop; `Intl.supportedValuesOf("timeZone")` is the obvious source.
3. Nothing reads the profile for **rendering** yet — `formatTimestamp` still uses the browser's zone.
   Architect's brief said "tz for rendering", so that is a real remaining item.

### Do these first, before the screen

Both are architect rulings on landing 3, arrived after it shipped. Neither is done.

- **N24**: a closed master folio still shows its pay/transfer forms; `src/ui/master-folio.tsx` should
  hide them and show `folio.closed`, the way `src/ui/folio.tsx` already does off
  `folio.account?.status === "closed"`. `getMasterFolio` already returns `account`.
- **N25**: `CloseBooking` in `src/routes/bookings.$id.tsx` must **always render the Finish button**
  while the booking is open, and let `booking.staysOpen` / `booking.masterNotSettled` come back
  through `CommandError`. **This reverses what I built and I was wrong**: I read N16 as "do not offer
  a choice the rules will refuse" and copied the open-stay filter and the balance check into the
  screen. Architect: N16 is about the screen *answering* a rule for the user, not about hiding a
  refused action, and a client-side copy of a rule is drift. A server-side "ready to close" *display*
  is still fine; the button must not depend on it. QA's S5-12a/b press Finish and expect the two
  refusals — red until this is fixed.

QA's landing 3 run: 95/96 on `624b7dd`, **N23 closed**.

## solex-dev — N24 and N25 (solex `d84c906`, staging `84f3f03c`)

335 green, build clean, both repos pushed. QA's 94/96 on `b531242` had exactly these two red.

**N24.** `MasterFolioPanel` now derives `closed` from `folio.account?.status === "closed"` — the
statement already carried the account, so nothing new is read and nothing is worked out. Closed: no
payment form, no transfer form, one line saying so.

Not `folio.closed`: that key reads "the guest has checked out", which is the stay's sentence, not a
group's. New `master.closed` en + vi, inside the placeholder block like the rest of `master.*`.

**N25.** The Finish button renders whenever the group is open. What went with it:

- the `openStays` / `masterBalance` props and the `blocked` ternary — the copy of the rule;
- `masterBalance` on `getBooking`, which existed only to feed that copy;
- `booking.readyToClose`, replaced by `booking.closeHint` — the two conditions as prose, so the desk
  still knows what Finish wants without the page deciding whether it has it.

The refusal now arrives the way every other refusal does: press, `booking.staysOpen` or
`booking.masterNotSettled`, `CommandError`. Which is also the only version that is right when a
charge lands between the page loading and the click.

**Next:** the Setup screen's profile section, the timezone picker, then `formatTimestamp` off the
profile's zone instead of the browser's.

## solex-dev — 5.2 complete (solex `5485e9e`, staging `42ef30f3`)

**The Setup section.** First on the page, above the things the hotel is made of, because those are
read in this hotel's terms. Name, zone, the hour the day starts. Nothing is checked before it is
sent: an empty name and an impossible hour are rules with codes, and asking them here would be the
same rule written twice (N25). New keys `setup.hotel*`, `setup.timeZone`, `setup.rollHour*`,
`setup.saveHotel`, plus `error.setup.timeZoneInvalid` / `error.setup.rollHourInvalid`, en + vi.

**The picker.** `knownTimeZones()` in `src/server/api/setup.ts` asks `Intl.supportedValuesOf`, the
same question `isTimeZone` asks: a zone this runtime cannot format is a business date the hotel
cannot compute. A runtime without it falls back to the zone in use plus the default, so the current
answer is never the one missing from the list. The hour is a select of 0–23 — shape, not judgement.

**Rendering in the hotel's zone.** `formatTimestamp` took `(value, locale)` and pinned UTC; it now
takes the zone. It arrives once, in the root loader (`getHotelZone`, which reads the profile row
directly rather than building the hotel — the root loader runs before every page and a lazy night
roll is not what a page load is for), and rides on `useI18n` beside the locale. Seven call sites.
Two people in two countries looking at one history now see one clock, and it is the hotel's.

Calendar dates are untouched and still UTC: a `YYYY-MM-DD` is a day, not an instant, and reading it
in a zone renders the day before.

`router.invalidate()` after a command already refetches the root loader, so saving a new zone
re-renders every timestamp on the page without a reload.

**Next:** 5.3 dashboard / reports.

## solex-dev — 5.3 landing 1: the dashboard (solex `b789aa8`, staging `76130ae7`)

344 green. Owner only, `reports.view`, business dates from the profile throughout.

**What it shows.** Occupancy (sold / sellable tonight), arrivals split into arrived and still
expected, departures split into gone and still in, in-house, what was sold today, what was actually
taken (deposits and settlements), what was given back, and seven nights forward with what is already
sold against today's sellable rooms.

**Three rulings I made and would like checked.**

1. A void is excluded from the business date the *charge* carries, wherever the void happened.
   Counting it against today would make a closed day's revenue move after the fact, which is the
   thing a business date exists to prevent (D-7).
2. A room out of order leaves the occupancy denominator. Occupancy measured against rooms nobody can
   let reads as a bad night every time something breaks.
3. Refunds are shown beside money taken, not netted out of it. "Took 700k, gave back 100k" is a
   truer day than "took 600k", and the schema already treats a refund as its own kind rather than a
   negative payment.

**The capability on a read.** `reports.view` throws in the domain like every other capability. A
command turns that into `{ok:false, code}`; a loader that throws is an error page, which is the wrong
answer for "this page is not yours". So the adapter maps that one refusal to data and the page shows
Setup's owners-only card. Everything else still throws.

**Reads.** `src/server/store/reports.ts` — `chargeTotal`, `paymentTotals`, `nightsSold`. All sums
over a half-open `[from, to)` business-date range, all against projections, never the log (D-22 (a)).
`nightsSold` counts `stay_nights`, the same table the calendar grid draws, so the dashboard and the
grid cannot disagree about who is in tonight.

**No ezFolio counterpart** for this page (D-27) — the reference shots are the range reports, whose
shape (date range, "summarise by", table, totals row) landing 2 will follow.

**Next:** landing 2 — revenue by category / source / method, occupancy over time, both over a
business-date range.

## solex-dev — 5.3 landing 2: the range reports (solex `cecd997`, staging `424f6139`)

349 green. Owner only, business dates throughout, `[from, to)` half-open everywhere.

**Revenue is now the ledger's**, on architect's ruling (c). An entry's *effective* date is its own,
unless it reverses another, in which case it is the reversed entry's — so a void nets against the day
the charge was earned, while the ledger keeps saying the reversal happened when it happened. Cash
reads `businessDate` as-is, which is what puts a refund on the day the money left the drawer.
`range()` is the single helper; the dashboard's "sold today" is `range()` over today, so the two
cannot drift.

Two scenarios pin the rule: a charge on the 23rd voided on the 25th leaves the 23rd smaller and the
25th untouched; a refund on the 25th of a payment taken on the 23rd leaves the 23rd's cash alone.

**Three cuts**: by charge category (a revenue account carries its category, so it is a group-by, not
a walk through charges), by booking source, and how the money arrived — the last one labelled as a
different question, because it is.

**Occupancy** by night and by room type, against the rooms the hotel can let *today*. Nothing records
how many rooms were out of order last Tuesday, so that is the only denominator available and the page
says which it is.

**The range lives in the URL.** An owner asking the office "what did we do last month" should be able
to send the question, not just the answer.

**One adapter rule worth knowing**: `read()` is for a page that asks nothing — the only thing that
can go wrong is being the wrong person. A read the reader typed input for goes through `command()`
instead, so `report.rangeInvalid` arrives as a code the page can say rather than an error page.

**Gap found, not filled**: nothing sets `bookings.sourceId`. The column exists, the report groups by
it, and no screen records one — so by-source is a single "not recorded" row today. Same shape as G28.

**Next**: 5.4 deposits, unless architect reorders.

## solex-dev — 5.4: deposits, no-shows, and the bill closing behind them (solex `755e585`, staging `d8da2b08`)

365 green. Built to architect's six rulings; the plan message listed what §11 left open and every
answer came back before I wrote any of it.

**MarkNoShow** is its own status rather than a cancellation with a note — the hotel held a room all
night and nobody slept in it, which is a different fact about the guest and a different line in a
report. It frees the nights, touches availability, can end a booking, and deliberately leaves the
folio open: the deposit still has to be given back or kept, and that decision comes after this one.
Refused until the hotel's day has turned over, because an empty room at six in the evening is a guest
running late.

**ForfeitDeposit** is a charge, not a payment. The money moved when the deposit was taken; what
changes is that the hotel earned it. Owner-only under the new `folio.forfeit`, posted against a
reserved `depositForfeit` revenue category — reserved for the same reason `room` is, so its line in
the revenue report means exactly one thing and cannot also contain whatever somebody typed.

The ceiling is deposits taken − refunded − already kept. Refunds are not tagged as refunding a
deposit rather than a settlement, so every refund counts against it: the cautious direction, which
can only refuse a forfeit that might have been allowed, never allow one that keeps money the hotel no
longer holds. Written down in the read's own comment.

**Close-at-zero.** A cancelled stay never checks out, so nothing else would ever close its folio.
`write()` learned an optional `closes` for one account's stream — "this folio is closed" does not
belong on the cash drawer's stream or on revenue's.

**N27** (QA): the range occupancy report averaged over the nights that sold rather than the nights in
the range, so a one-room hotel that sold two of four nights read 100%. The domain now fills every
night in `[from, to)`, and the table shows rooms-in-service per row so the percentage is checkable.

**Next:** 5.5 folio print.

## solex-dev — 5.5 resume note (build from solex `3c2e48f`, staging `50c76694`)

365 green, working tree clean, both repos pushed, migration 0015 applied to dev and to staging's D1.

### Built

`HotelProfile.address` and `.phone`, optional and defaulting to empty, on the Setup form and in the
changed-field-names list. No rules on either: a hotel can run for months before anybody prints a
bill, and blocking Setup on a field only the printout reads is the wrong trade. Architect's 5.5 brief
said "hotel name/address from HotelProfile" — the address did not exist, so this is it.

### Next: the print views

Architect's scope: own folio and master folio; hotel name/address/phone, guest or company,
stay/room/dates, lines by night, payments including deposits, refunds, balance; Vietnamese labels;
browser print CSS, no PDF service; print button on the stay page and the master panel; read-only, no
event; no VAT / red-invoice fields (later).

Decisions already taken, to save re-deriving them:

- **Routes**: `print.stay.$id.tsx` and `print.booking.$id.tsx` → `/print/stay/<id>`. Not
  `stays.$id.print.tsx`, which would turn `stays.$id.tsx` into a layout and force renaming the two
  biggest route files for nothing.
- **Shape (D-27)**: there is no folio printout in `screens/`, so follow the house style of the report
  printouts (`rpt-fd-revenue.png`): hotel block top-left, title centred, printed-on / printed-by
  top-right, the lines table, a totals row, and the three signature blocks
  (Người lập biểu / Trưởng bộ phận / Giám đốc).
- **Reads**: `hotel.folios.statement()` already returns folioId, balance, charges, payments and
  account. The print loader needs that plus `hotel.profile.get()`, the stay (room, dates) or the
  booking (company), and guest names. Worth one adapter each rather than reusing `getStay`, which
  drags history, rooms and routing the printout does not want.
- **Print CSS**: a `@media print` block in `src/styles.css` hiding `.topbar` and anything marked
  `.no-print`, plus a `.sheet` wrapper. `src/styles.css` has no print rules today.

### Known conservative rule, logged at architect's request

The forfeit ceiling counts **every** refund against the deposit, because a refund does not record
what it is refunding. It can refuse a forfeit that might have been allowed; it can never allow one
that keeps money the hotel no longer holds. Accepted as the cautious reading; revisit only if a
refund ever carries its target. Progress flag for Alex is architect's.

### Open, not mine to decide

- `bookings.sourceId` has no writer (by-source report is one "not recorded" row) — 5.7 with G28.
- `Company.defaultRouting` has no Setup control — G28, 5.7.

## solex-dev — 5.5 landing 2: the printed bill (2026-09-24)

`e7f1dd1`, staging `d96ba0c4`, 365 green. Two routes, one sheet component, one
`@media print` block.

**Routes.** `print.stay.$id.tsx` and `print.booking.$id.tsx`, not
`stays.$id.print.tsx` — the latter turns the two biggest route files into
layouts so a document can inherit furniture it then has to hide.

**Reads.** A new `src/server/api/print.ts` with two narrow adapters rather than
a reuse of `getStay`, which drags history, every room and the routing table
across the wire for a page that draws none of it. Each returns the letterhead
(`hotel.profile.get()`), a printed-at stamp taken on the server so the markup
hydrates to what was rendered, the addressee, and `folios.statement()`.
Read-only by construction: printing is not something that happened to the
hotel, so there is no event and nothing to refuse beyond being signed in.

**The one judgement worth recording: a voided line is left off the printout.**
On screen it stays, struck through, because the folio is a record of what
happened. On paper it is a line the guest does not owe, and the totals already
exclude it — printing it invites an argument about a number that is not in the
sum. Charges (un-voided) − payments + refunds = the balance, so the sheet
reconciles with the ledger, which is the property the reports are held to.

**Shape (D-27).** No folio printout exists in `screens/`, so this follows the
house style of the report printouts: hotel block top-left, title centred,
printed-on / printed-by top-right, lines table, totals hanging off the right,
three signature blocks (Người lập biểu / Trưởng bộ phận / Giám đốc). No VAT and
no red-invoice fields — that is a conversation with the client's accountant.

**Verified visually**, not only by tsc: a throwaway vitest that rendered the
sheet with `react-dom/server` and Playwright shots in both `screen` and `print`
media. Two fixes came out of it — the muted grey the screen uses for table
headings prints as a smudge, and the description column needed the slack.
The scaffolding is deleted; re-do it the same way if the sheet changes.

**Nothing to unit-test here.** No new rule, no new state: the adapters compose
existing reads and the sheet is markup. The coverage that matters is QA's — a
bill with a deposit, a refund and a voided line, and the group sheet.

## solex-dev — 5.6 resume note (build from solex `32202ab`, staging `3f0afbcd`)

365 green, build clean, working tree clean, both repos pushed. No migrations in
this stretch.

### Landed in 5.6 so far

- **G3** (`44c6c1a`) — `src/ui/ask.tsx`, a native `<dialog>`, replaces five
  `prompt()`/`confirm()` calls: void a folio line, void an expense, reset a
  password, erase a guest, erase a contact. Mounted only while the question is
  open, so `onClose` can only mean no. It judges nothing (N14/N25 intact).
- **G5–G7** (`32202ab`) — the room map. `getRoomMap()` and `getRoomPanel(id)`
  in `src/server/api/rooms.ts`; `src/ui/room-panel.tsx`; `src/routes/index.tsx`
  rewritten. The eight filters are one `FILTERS` record of predicates used
  twice (count + filter) so they cannot disagree; they overlap deliberately
  (leaving today counts as in house too), which is ezFolio's arithmetic and
  product's mockup. Tile state is exclusive, most urgent first.
- Also 5.5 before it: `e7f1dd1`, the printed bill.

### Next, in architect's order

G31 (check-out settle dialog + money strip) → G13 (search / list filters) →
G9 (tape-chart per-type rows, grouping, 7/14/30) → G18 (folio shows category
names, not ids) → G25 (receivables rows link to their stay/booking; settled
companies behind a toggle) → G1/G2 (nav grouping, `/` = "Sơ đồ phòng", one
name for the calendar). Tail after those: G4, G8, G10, G12, G19, G21, G26.

### Worth knowing before picking it up

- **Verifying UI without a dev server.** No port of mine is free and no agent
  signs in, so both landings were eyeballed by rendering a static harness
  (`src/styles.css` inlined into an HTML file) and shooting it with Playwright
  from `e2e/` (the workspace that has it installed). Two real fixes came out of
  it. Scaffolding is deleted each time; re-do it the same way.
- **G8 is half done**: the define-a-room form is folded into a `<details>` on
  the map. Moving it to Setup with a room-type select is still open.
- `pnpm deploy` failed once with a Cloudflare 7403 on the D1 migrate step and
  worked on an immediate retry. Nothing changed in between.

## solex-dev — 5.8 complete (build from solex `8130240`, staging `e00bc289`, 517 green)

Kept current at the landing. Both repos pushed, tree clean, build clean,
biome at the 4-warning baseline. **Migration 0019** (`booking_rules`) applied
dev + remote; 0018 (`stay_guests`) before it. Nothing pending.

**Landed since the `30dbec5` note:**
- **G28** (`f82ea14`) — `Company.defaultRouting` has decided which bill every
  group charge lands on since 5.1 and had no control, so hotels got the
  fallback whatever they had agreed. Companies are a card each now: eight
  categories is eight selects and a four-column row has nowhere to put them.
  **Three answers per category**, not two — "not said" is the common one and
  means fall through, and picking it back is how an agreement is withdrawn.
  Their other fields became editable in the same form (the update command
  replaces the row, so it has to be sent them anyway) — `UpdateCompany`'s
  first caller. No select for `depositForfeit`: that charge is posted onto the
  bill its command names and never consults routing. Selects live in
  `ui/routing.tsx`, which **G32 reuses one level down**. `.row` inside a card
  lays out like `form.row` now.
- **vi pass 2** (`74f99e3`) — product's 24 pairs for G16 and G22, verbatim.
- **G29** (`3e9b447`) — `BookingRules` did not exist at
  all. Row carries all five of product's settings; **the form shows the two
  that something reads** (architect's ruling (b): a control that changes
  nothing is a lie told where the owner cannot check it). Wired:
  `autoDirtyOnCheckout` (§10 rule 6 is a dial now) and `idEnforcement`
  ("required" refuses a check-in where nobody handed a document over — one
  between them, not one each, `stay.idRequired`). `bookingRules.get()` never
  answers null, so the defaults live in one place instead of `?? 6` at every
  read site. Both read inside the plan (D-12 (f)). `overbooking` is
  refuse | warn | allow after product's G34 spec.
- **QA N33** (`46a699e`) — **a regression I caused in 8716fc2.** Refusing to
  reuse a command id while anything was in flight is exactly the state a
  double-submit is in, so the second submit got a fresh id and met a rule that
  had already happened ("already settled") — or, for `PostCharge`, which has
  no such rule, would have posted the charge twice. Both that and the original
  silent drop are the same missing fact, *which* command this is, and only the
  caller knows it. `run` takes a **key** now and the slots are per key; where a
  screen has one per row the key names the row. Key is required, so the
  compiler found all 56 call sites.
- **QA N34 / N35 / N36** (`b4e501e`) — revenue "by source" names the channel
  (hotel's name, then the standard list, then the id); the ID-number adapter
  check is gone so `guest.idDocIncomplete` can be said instead of
  "input.invalid"; the group's master bill has a Move picker at last, offering
  the booking's own rooms, which is what made "master → stay" reachable.
- **N29/N30/N31 verified by QA** on the screens; G16's S5-44 passes.

**N32 is parked as environmental.** QA found the machine at load ~190 with
five `pyenv exec python3 -c …` shims spinning at 60–70%, reading a stdin that
never closes. One leftover was mine — the old `http.server 7913` scratchpad
server — and is killed. The others belong to other sessions (ebutler-qa,
replay-lab, /tmp) and I left them alone. Under that load QA's rerun hung 5 of
10; the suite already runs `--workers=1`, and staging walks have never shown
it. The client half of the fix (`run` no longer awaits `router.invalidate`)
stands on its own merits.

**Landed after that note was written:**
- **QA N37** (`7279fc1`) — **G29 shipped a switch that bricked check-in.**
  With "an ID is required" on, the stay page sent `guests: [{ name }]` and had
  no field for a document anywhere, so every check-in was refused with no way
  to comply, and setting the ID on the guest's page first does not help
  (check-in mints new guest rows). Each guest row at check-in now carries a
  type and a number, optional per person — the rule asks for one between them.
  Half a document is refused on the page, since check-in has no domain rule of
  its own to answer with. Tested that the number reaches the guest's row.
- **G32** (`d2e4199`) — the group's routing table on the booking page. Rows ×
  categories, each cell the effective target. Header select sets a column via
  new `bookings.setGroupRouting`, one commit across every stay stream.
  Product's rule holds: **a room somebody set differently keeps what it was
  set to**, marked in the cell, changed on its own page. `target: null`
  clears the column, overrides included — the way out of a column of
  exceptions. The column select never shows a state: the column can be three
  things at once.

- **G33** (`ae22949`) — Needs attention on the owner home + a count badge on
  the Reports nav link. **Derived, never stored, never dismissed**: computed
  from the projections on every read, so a row leaves because the fact stopped
  being true. Two readings to know: a company's debt is aged from its oldest
  unpaid line with payments knocking off the oldest first (dating it from
  `account.openedAt` would leave a monthly payer permanently overdue), and a
  room's OOO date comes off its stream rather than a new column. Needed a new
  query — `staysCheckedIn` — because an overstay is outside `staysOnDate`'s
  range by definition. `receivableAgeDays` and `oooDays` joined the G29 form
  in the same commit, which is when something finally read them.

- **G34** (`2978428`) — the overbooking check.
  Every command that adds demand checks the nights it adds, per type, against
  the rooms in service: create, add rooms to a group, ChangeNights add, early
  check-in. Refusal `availability.overbooked` **carrying numbers** — `short`
  and `date` — which needed `RuleError` to be able to carry a detail payload
  and `CommandResult` / `useCommand` / `CommandError` to pass it through.
  Four things it is careful about: only the nights added; supply-side commands
  never refuse; a room double-held stays `stay.roomTaken` (so the per-room
  check runs first, in both `create` and `changeNights`); never silent — the
  override is a flag and even `allow` requires it. New capability
  `stay.overbook`, owner default. "Take it anyway" is on the new-booking form
  only; the nights form and check-in take the flag but do not offer it.
  **Two fixture findings**: `given.booking` in a hotel with no rooms was
  selling a room that did not exist, and `groups.test.ts` was booking twelve
  of them. `given.rooms(h, n)` exists now and those hotels have rooms.
- **QA N38** (`d37bae1`) — **G32's sweep was wrong.** Writing each stay's own
  routing entry made every swept room look deliberately set, so a second sweep
  moved nothing and only "As agreed" could undo it. The group's decision lives
  on the *booking* now (`booking.routing_set` / `routing_cleared`), and a stay
  reads it unless told otherwise. Product's rule became the lookup order —
  stay → booking → company → default — instead of something the sweep had to
  implement. Behaviour change from what I first told QA: "As agreed" no longer
  clears a room's own setting.
- **QA N39** (same) — departure day is not an overstay.

- **G35** (`e85263b`) — `RoomType.capacity` had been in Setup since slice 2
  and **nothing read it**: four adults could be booked into a double and
  checked into it. `adults ≤ capacity` at create, add-rooms, the new
  `SetOccupancy`, and check-in — check-in against the **room's** type, since
  that is the moment four people are standing in a double. Children never
  counted (definition, not a discount). No override, per product. Refusal
  carries `{roomTypeId, capacity, adults}` using G34's detail payload.

**5.7 is complete.** Every C row in ux.md §6 is built.

**5.8 landing 1a — `RepriceCharge`** (`a6df655`). The only discount there is:
void + repost at the agreed price, one batch, both lines on the bill, and
**revenue moves with it** — which is the point of not having a discount
field. `repricedFrom` ties the two lines. Refuses the price it already has;
reason required. Owner only on `folio.void` until landing 3 turns it into
Xin duyệt for the desk. `Ask` can carry a number beside its reason now.

**5.8 landing 1 — the `Approval` aggregate** (`a0beb3c`, migration 0020).
Five kinds; **the grant and the act are one batch** (the folio's and the
receivables' write helpers take the approval's append and stamp `approvalId`
onto what they write); the act is **re-decided at grant time**, and if it
refuses now nothing is written and the request stays open; one open request
per subject; requesting needs no capability of its own (whoever cannot run
the command is who needs it) while deciding is the new owner-only
`approval.decide`; an open request expires **in the same batch as the
check-out that ended it**. 13 scenarios.

**QA N40 / N41 / N42** (`e17d85b`) — the overbooking select joined House
rules (now five dials, all read by something); a refusal's `date` detail is
formatted like every other date; and the overbooking override's history line
was present-but-unreadable (its payload is a type id and a list of dates, and
the history prints an id only when the page can name it and dropped date
lists entirely) — the stay page names room types now and a night list reads
as its first night plus a count. **Told QA my N42 diagnosis may be wrong** and
asked them to say so if the line is still absent.

**5.8 landing 2** (`41f2d3b`) — `approval.pending` is the first row of Needs
attention, as a **card** with both answers on it: this is the one row on that
page that is a question, and a person is at the desk waiting. Approve runs the
act; Refuse asks why and the reason lands on the line.

**5.8 landing 3** (`5603ad8`, finished in `e1c113d`) — Void and Reprice read
**"Ask the owner"** for a receptionist, same place, same reason field; the
line then carries *waiting for the owner* / *the owner said no — reason*, and
both buttons go while a request is open. Refund and the receivables write-off
followed: refund stays in the payment form's kind select rather than
disappearing (a control that vanishes teaches nobody anything and the desk
rings the owner instead of leaving a record), and the write-off form lost its
"owners only" note because it is no longer true.

**Every row in product.md §11 is built.** There is no unbuilt command left in
the catalogue.

**QA N42 is closed.** The rendering fix in `e17d85b` was the whole of it; QA's
"still nothing" was a spec clicking a stay link on the stale bookings list
after "Take it anyway" navigates, so they were reading another booking's stay.
The chase left behind `src/ui/history.test.tsx`, **the first rendering test in
this suite** (`renderToStaticMarkup`, no DOM, so it fits a server-only suite).
Worth knowing for e2e: after an override the URL moves to the group page
before it renders.

**Every event has a name too** (`8130240`). QA's e2e net — a spec fails if a
bare key shows on screen — prompted the question of what the codes test does
*not* cover: keys built at render time. (Their net watched `role=alert` only
at that point, so it would not have caught these either; QA corrected the
record themselves, and it scans every text node from their next run on.) The
biggest such key is the history's `eventType.<type>`, and eight events had no
name. Six were that afternoon's approvals; **`stay.routing_set`
and `routing_cleared` had been printing their own type in a stay's history
since routing was built**, because nobody had opened a stay's history after
changing its routing. Guarded the same way, reading the literals at the point
of emission (D-12: there is no enum, and a type is never renamed).

**Every refusal has a sentence now** (`a129a06`). N45 was one missing
message; auditing the rest found **seven more**, all written the same
afternoon — the five approval refusals and G32's two. A code with no entry
renders as itself ("error.approval.alreadyOpen") at whoever pressed the
button, which reads as the system breaking rather than as an answer. The fix
is the **test**: `src/i18n/codes.test.ts` reads the `…RuleCode` unions out of
the source, because the codes *are* the source and a registry beside them
would be a second copy to forget.

**QA N44 / N45** (`2f54f6d`) — the owner's approval card said a raw user id,
the kind of act and the desk's reason, and nothing about *what*: no line, no
room, no guest, and no amount, because a void carries none of its own (the
money is the line's). It now reads as the decision, with the room linking to
the stay; who asked is resolved to a name in the adapter the way the history
does it. New read `guestsOfStay` — G22's link the other way round. N45:
`folio.nothingToChange` had no sentence and printed its key.

**QA N43** (`1b6850f`) — both buttons on a bill line read "Ask the owner" for
a receptionist, side by side, one opening the reprice dialog and one the void
dialog. Landing 3's idea is that the control does not move and does not change
meaning, and I took the meaning out of the label. Now "Ask to reprice" /
"Ask to take off".

**The 92 en-only keys are written down** at
`agents/solex-dev/notes/2026-09-25-vi-pass-3-handover.md`, grouped by where
they came from, with the two that are sentence fragments flagged — so the
handover does not live only in a message product never received.

**QA's full suite is green on `8130240`** — desk 154/154, receptionist 13/13,
print (S5-80/81) and room map (S5-82..84) included, and their page-wide
raw-key net found nothing, so the eight event names hold. **No open N.**

**G34's load-bearing property is proved from the screens** (S5-85): under
`warn` a receptionist cannot oversell whether or not Take-anyway is drawn;
under `allow` they can, and `stay.overbooking_overridden` is written on every
stay that went over. QA found **no way to oversell silently**. That is the one
thing the override design rests on — the flag is required even under `allow`
precisely so the log never goes quiet about who chose — and it is now checked
from the outside rather than only by the domain tests.

**Both dev and QA are idle** pending architect (next slice; the two rulings)
or product (the 92 keys).

**Next: nothing is queued.** ux.md §6 has no outstanding row and §11 has no
unbuilt command. The open items are QA's N42 (diagnosis still open, see above)
and the 5.8 pieces product.md itself defers — notifications, and the approval
card's "what" naming the line rather than the kind. **Architect and product
have been unreachable for the whole of 5.8**; both need briefing on what
landed, and product has **92** en-only keys waiting (written down, see above). (product.md §11 Approvals, ux.md G34-the-5.8-row
— note ux.md reuses the number "G34" for it, which is *not* the overbooking
G34 just built). One rule: an owner-only money act the desk cannot do becomes
a request from the same button. Desk's void / reprice / refund / write-off
render as **Xin duyệt** with the same reason field → `RequestApproval`; the
line carries *đang chờ duyệt* / *từ chối: reason*; the owner home's
`approval.pending` row opens one card → `GrantApproval` (which runs the act
in the same batch) / `DeclineApproval`. New capability `approval.decide`
(owner). **Architect has not briefed this slice** — it is the next thing in
their stated order, but a slice boundary is normally theirs to open.
~~**G33**~~ (owner home + Needs attention; this is where `receivableAgeDays` and
`oooDays` join the G29 form) → **G34** overbooking → **G35** capacity → 5.8.
G34/G35 are spec'd in product.md (ctrl `847ff15`) and accepted by architect:
override is an `override?: true` flag on the adding command, `OverrideOverbooking`
retired unbuilt, gate on `BookingRules.overbooking` + new capability
`stay.overbook`, refuse `availability.overbooked {roomTypeId, date, short}`,
only nights the command adds are checked, supply-side commands never refuse.
G35: `adults ≤ RoomType.capacity`, children never counted, refuse
`stay.overCapacity`, new `SetOccupancy {stayId, adults, children}`.

**Open:**
- `pnpm i18n:report` at **39** en-only keys: G28, G29, G32, G33 and G34.
  **Product has been unreachable every time I have tried**, so none of these
  have been handed over. Send the whole set when they come back.
- `bookings.sourceId` on rows written before G30 stays null; no backfill.
- **solex `main` is shared** — QA pushes e2e there. Rebased onto `f4308ad`
  this stretch; always fetch + rebase.
- **Architect and product are both unreachable** as of the G33 landing
  (`ListAgents` shows neither). Undelivered: the G29/G32 report to architect
  (including two calls of mine that want a ruling — group-level "As agreed"
  clearing overrides too, and the routing cells being read-only with the
  exception made on the room's own page) and the 35-key list to product. QA
  has the G32/G33 walk and knows.

**Verification technique** (no dev server, no staging sign-in): inline
`src/styles.css` into a static HTML harness in the scratchpad, screenshot with
Playwright run from `solex/e2e` (a `file://` URL), read the PNG, **delete the
harness script from `e2e/` afterwards** — biome lints it and it will fail the
check if left. Used on the move dialog, the person page and the company card.

## solex-dev — 5.7 resume note, superseded (build from solex `30dbec5`, staging `a2476da4`)

Kept current at the landing. Both repos pushed, tree clean, `pnpm build`
clean, biome at the 4-warning baseline. **Migration 0018** (`stay_guests`)
applied dev + remote; nothing pending.

**Landed since the `69899bc` note:**
- **G22** (`fc17274`) — three things the people screens were missing.
  *Edit:* `UpdateGuest`/`UpdateContact` existed on the SDK since slice 1 with
  nothing calling them, so a wrong phone number could only be fixed by making
  a second person. Form on the person's page; no form for an erased person
  (the command refuses either way — this avoids inviting somebody to fill the
  blanks back in). *Contact detail link:* from the people list and from the
  booking header, which is the one that matters. *Where they have stayed:* new
  projection `stay_guests` (0018), **ids only**, from `stay.checked_in` — ids
  only is what lets the list survive erasure, because the room was occupied on
  those nights whatever the guest asked for afterwards. A booking nobody
  turned up for is not on it. One shape question answered on the page (N10):
  an ID number with no type would go over the wire as an empty enum and come
  back "input.invalid".
- **QA N31** (same commit) — the `Ask` dialog answered twice when both clicks
  landed in one tick, because the dialog closes on the caller's *next* render;
  the second answer reached a command that had already run, and the desk read
  "already voided" for pressing a button once, hard. One answer per asking,
  held in a ref.
- **QA N32, the client half** (`30dbec5`) — `run()` awaited
  `router.invalidate()` inside the try, so the button was tied to the refetch
  rather than to the command: one loader request that never settled left
  `busy` true forever, every button disabled, form uncleared, for a command
  that had already written the row. The refresh is now fired and caught, not
  awaited.

**N32's other half is open and is not mine yet.** QA sees a `getViewer` GET
never complete on the dev server (status -1), 4–6 of ~60 e2e tests, not on
`755e585`. That also stalls the root `beforeLoad`, which is why navigations
never land (S5-35, S5-14) — nothing in `run()` can fix that. Nothing obvious
in the server path: `getViewer` → Better Auth session → one libsql client,
and the store uses `db.batch` (atomic, short) with **no long transaction** to
deadlock on. Next probe for whoever picks it up: does it reproduce against
the built worker (`wrangler dev`) or only vite dev, and does it survive
`--workers=1`.

**Next, in architect's order:** **G28 = company `defaultRouting`** → G29
BookingRules → G32 group routing table → G33 owner home + Needs attention →
5.8.

**Open:**
- `pnpm i18n:report` at **24** en-only keys: G16's nine plus G22's
  `people.details`, `people.detailsHint`, `people.save`, `people.email`,
  `people.notes`, `people.idDocType`, `people.idDocNumber`,
  `people.idTypeMissing`, `idDoc.cccd|passport|other|none`, `people.stays`,
  `people.staysHint`, `people.noStays`.
- `bookings.sourceId` on rows written before G30 stays null; no backfill.
- **solex `main` is shared** — QA pushes e2e there; always fetch + rebase.


**Verification technique** (no dev server, no staging sign-in): inline
`src/styles.css` into a static HTML harness in the scratchpad, screenshot with
Playwright run from `solex/e2e` (a `file://` URL), read the PNG, delete the
harness. Used on the move dialog and the person page this stretch.

## solex-dev — 5.7 resume note, superseded (build from solex `69899bc`, staging `00d1097a`)

Kept current at every landing, per Alex's process change (no manual
compaction cycles; auto-compaction happens on its own, and this note is the
safety net). Both repos pushed, tree clean, `pnpm build` clean, biome at the
4-warning baseline, **no migration pending** — 0017 (`booking_sources`) was
the last one and it is applied dev + remote.

**Landed since the `c8b3528` note:**
- **vi pass 1** (`18da91f`) — product's 65 key→vi pairs applied verbatim, plus
  QA's fix: `folio.void` was "Huỷ", the same word as `ask.cancel` on the
  dialog it opens, now "Huỷ khoản". I diffed their key list against
  `i18n:report` before inserting (exact match) and checked placeholder parity
  across the whole dictionary. Report said complete at that commit.
- **G16 / MoveCharge** (`d4fe94f`) — a line moves to another bill. Product's
  shape (§11): both bills open, `folio.charge_moved`, reversal + new entry.
  It is a *move*: the line keeps its id, description, qty and posting date,
  because a void-and-repost would show a struck-through line on one bill and
  a fresh one on the other. The new entry is the original's lines with the
  source folio swapped for the target, so revenue comes off in the reversal
  and goes back in the repost and the day's takings do not move. **A room
  charge stays with the guest who slept the night** — moving one between a
  stay's own folio and its group's master is allowed (that is the routing
  case, revisited), onto another guest's bill is refused by name. Target
  picker = in-house tonight + this booking's master; the desk's own permission
  (`folio.move_line` was already in the receptionist bundle) because nothing
  leaves the hotel's books. Two incidental changes in the same commit: the
  folio adapter's `write()` takes a **list** of entries now (RepriceCharge in
  5.8 wants the same), and `Ask` gained a **list-of-answers** variant, since
  "which bill" is a pick and the dialog could only ask for typed text.
- **Architect's code ruling, folded in** (same commit) — `room.typeUnknown` is
  gone; `setup.roomTypeInvalid` covers both defining a room under a type
  nobody defined and re-typing one into it. One fact, one sentence.
- **QA N29 + N30** (`69899bc`) — N29: a stay's history merges its own stream
  with its bill's, `folio.*` only (each of those is written beside a `ledger.*`
  entry, and showing both prints every line twice). The merge is on the SDK as
  `events.ofStayAndBill` so it is tested without a browser. N30: the
  housekeeping badge reads **Clean**, not "Vacant clean" — which also fixed
  the button beside it reading "Mark vacant clean". I trimmed the Vietnamese
  to match ("Trống sạch" → "Sạch") and told product; that is a word removed
  from their own string, not new copy.

**Next, in architect's order:** **G22** (edit guest/contact details,
`UpdateGuest`/`UpdateContact`, contact detail link, guest's stays on their
page) → **G28 = company `defaultRouting`** → G29 BookingRules → G32 group
routing table → G33 owner home + Needs attention → 5.8.

**Open:**
- `pnpm i18n:report` at **9** en-only keys, all from G16: `folio.move`,
  `folio.moveTitle`, `folio.moveHint`, `folio.moveTo`, `folio.moveToRoom`,
  `folio.moveToMaster`, `eventType.folio.charge_moved`,
  `error.folio.billClosed`, `error.folio.roomChargeStays`. Product is running
  again and knows.
- `bookings.sourceId` on rows written before G30 stays null; no backfill. The
  revenue report's null bucket exists for exactly those.
- QA has not walked G14 landing 1/2, G15, G20, G30, G16 or the N29/N30 fixes
  through the screens. Point them at `69899bc` / staging `00d1097a`.
- **solex `main` is shared** — QA pushes e2e there; always `git fetch` +
  rebase before pushing.

**Verification technique** (no dev server, no staging sign-in): inline
`src/styles.css` into a static HTML harness in the scratchpad, screenshot with
Playwright run from `solex/e2e` (a `file://` URL — the scratchpad http server
is gone), read the PNG, delete the harness. Used on the move dialog this
stretch, and it confirmed the dialog and the two-button action cell. The one
real catch there came from reading the CSS rather than the picture:
`dialog.ask` sized `input` and not `select`, so the picker needed its own
width rule.

## solex-dev — 5.7 resume note, superseded (build from solex `c8b3528`, staging `e8ec202d`)

Written at architect's clean-stop for compaction. Both repos pushed, working
tree clean, `pnpm build` clean, biome at the 4-warning baseline. **Migration
0017** (`booking_sources`) applied dev + remote in this stretch; nothing
pending.

**Landed since the `a48c254` note:**
- **G15 landing 2** (`c6f5d36`) — the stay page's nights table edits itself:
  per-night rate field + Save, per-night "Give it back", one card below adds a
  night at either end. Adapters only; the unbroken run / empty stay / posted
  night come back as codes. `posted` drawn as a pill (the fact, not the rule).
- **G20** (`ee8513b`) + follow-up (`f6c98a4`) — booking form is one line per
  kind of room, so a mixed group is one booking; new read
  `hotel.calendar.freeByType(from, to)` (rooms left per type per night):
  **unassigned nights subtracted** (a group is sold as stays without rooms),
  OOO in neither number, **free returned signed** because nothing refuses an
  oversold group. Follow-up pointed the tape chart's free-of-this-type row and
  the hotel-wide free row at the same read; `used` and occupancy % stay
  room-based. Kind select moved above the lines, and switching back to
  individual drops all but the first line.
- **G30/BookingSource** (`79f0a60` + `5a86ebc`) — architect called it G28; the
  real ux.md G28 (company `defaultRouting`) is still outstanding. Tier-b Setup
  entity, four fixed buckets, slug id, retire refused by nothing,
  `seedDefaults` for the v1 ten, Setup section. **`CreateBooking` writes
  `walk-in` when nobody said.** Source select beside "Billed to" (flip fires
  only on an untouched default), name on the list column and booking header.
- **Command-id fix** (`8716fc2`) — one `useCommand` serves a whole screen and
  its retry slot was shared, so a second command started while another was in
  flight took the first's id and the server answered it as a repeat: nothing
  written, nothing refused, `ok` back. Now reused only when the attempt went
  unanswered and nothing else is waiting. `retryId` extracted + unit-tested.
  **Confirmed by QA on `8716fc2`** (seed 3/3 with the retry removed, S5-41
  define passed); architect closed it with no N number. Their pre-fix trace
  shows a `getQuote` from /bookings just before the /setup define — that call
  is a read and does not take the retry slot, so the trace is consistent with
  the diagnosis rather than proof of it. Recording that here in case it comes
  back.
- **SetRoomType** (`c8b3528`) — the G8 debt closed. Select on every row of the
  Setup rooms table; allowed with a guest in the room (product's ruling);
  versions availability, proved through `freeByType`; unknown and retired are
  one refusal, `setup.roomTypeInvalid`.

**Next, in architect's order:** G16 → G22 → **G28 = company `defaultRouting`**
→ G29 → G32 → G33, with QA's (b) stay-page history merged with its folio
stream and (c) housekeeping badge Clean/Dirty only, folded in when their N
numbers arrive.

**Open:**
- `pnpm i18n:report` at **65** en-only keys. Product session is not running, so
  no Vietnamese batch is coming; en-only stands (D-29).
- **Code wart flagged, unruled:** `setup.roomTypeInvalid` (SetRoomType) and
  `room.typeUnknown` (defineRoom) are two codes for one fact.
- `bookings.sourceId` on rows written before G30 stays null; no backfill. The
  revenue report's null bucket exists for exactly those.
- QA has not walked G14 landing 1/2, G15, G20 or G30 through the screens.
- **solex `main` is shared now** — QA pushes e2e there. I rebased local
  landings onto their pushes twice this stretch; always `git fetch` + rebase
  before pushing.
- Cloudflare 7403 on the D1 migrate step did not recur this stretch.

**Verification technique** (no dev server, no staging sign-in): inline
`src/styles.css` into a static HTML harness in the scratchpad, screenshot with
Playwright run from `solex/e2e` (use a `file://` URL — the scratchpad http
server is gone), read the PNG, delete the harness. Used this stretch on the
nights table and the group form; caught nothing new, which is itself worth
knowing.

## solex-dev — 5.7 resume note, superseded (build from solex `a48c254`, staging `589cca66`)

Written 2026-09-24 at architect's clean-stop for compaction. Everything below landed and is pushed on both repos.

**Landed this session (after the previous note at `417c5cd`):**
- **Slice-4 debts** (`a920697`) — N21: history tables group events by `correlationId`, one action one row (headline = first event, the rest quieter under it in `.also`, version column shows a range like `2–4`; grouped by id not adjacency so merged streams still fold). N22: `nothingToChange` refused rather than swallowed on guest, contact, room type, rate, **and** company + hotel profile (stretch, accepted). Five tests rewritten to assert the refusal *and* that nothing was written.
- **Quiet notice** (`077ab9d`) — architect's ruling: `CommandError` renders any `*.nothingToChange` code muted with `role="status"` instead of red; no disabled-button logic (N25). Covers all six forms at once.
- **G14 landing 2** (`d5686fd`) — `booking.party_changed` / `notes_changed` / `requests_changed`. Party carries ids only and says `companyId: null` out loud when cleared; erased-contact check as in CreateBooking. Requests is add + remove in one batch (`stay.created` per room added, `stay.cancelled` per room off, availability touched only when the freed rooms had numbers, each stay under its folded version); removal refused by `booking.stayCheckedIn`. **Added rooms hold no room number** — AssignRoom already decides freeness under the guard, so the predicate is not duplicated (architect accepted this as narrower than his ruling, on purpose). Add/remove forms are group-only; remove needs a reason, add does not.
- **G15 landing 1** (`a48c254`) — the rules above.

**Next:** G15 landing 2 — the stay page's screens for ChangeNights and SetNightRate (`/stays/$id` already lists the nights; the forms go beside that table). Then G20 → G28 → SetRoomType (product `349073e`) → G16 → G22 → G29 → G30 → G32 → G33.

**Open:**
- `pnpm i18n:report` is at **33 en-only keys**; architect is sending the batch to product, who messages key → Vietnamese pairs back for dev to apply mechanically (D-29).
- Rooms with a null `room_type_id` still cannot be re-typed until SetRoomType lands.
- `bookings.sourceId` still has no writer (G28).
- Cloudflare `code: 7403` on the D1 migrate step keeps failing the first `pnpm deploy` attempt and clearing on retry. Flagged to Alex via architect; not ours.
- QA has not walked G14 landing 1 or 2 through the screens yet (S5-37 and the party/notes/requests paths).

**Verification technique** (no dev server, no staging sign-in): inline `src/styles.css` into a static HTML harness in the scratchpad, screenshot it with Playwright run from `solex/e2e`, delete the harness. Caught the nav-group and tape-chart defects earlier; used again this session on the grouped history table and the booking-correction cards.

## solex-dev — 5.7 resume note, superseded (build from solex `417c5cd`, staging `ca754483`)

375 green, build clean, working tree clean, both repos pushed. Migration 0016
(rooms.room_type_id) applied to dev and remote in this stretch; nothing pending.

### Landed since the last resume note

- **5.6 complete — every P row in ux.md §6.** G31 settle dialog + money strip
  (`bdf0fa1`), G13 status lists (`b211550`), G9 tape-chart tallies + type
  grouping (`9627c78`), G18 + G25 (`d26eefb`), G8 rooms reference a room type
  (`e362433`, migration 0016), G1 + G2 grouped nav (`84b68d6`), G4 history in
  words (`7bc8697`), tail G10/G12/G19/G21/G26 (`bc64f12`).
- **D-29** (`04822c6`): `vi` is `Partial<Messages>`, a missing key renders the
  **English sentence** (never a marker), `pnpm i18n:report` lists what is
  waiting and runs inside `pnpm check` as a report, never a failure. Node's own
  type stripping, so no new dependency. Product sends key → Vietnamese pairs
  after each accepted slice; dev applies them mechanically, no wording calls.
- **5.7 G14 landing 1** (`417c5cd`): group CancelBooking on the booking page,
  `booking.stayCheckedIn` as a booking-level refusal, master folio left open
  so a cancelled group's deposit can be forfeited (N28's path, now covered by
  a scenario in `groups.test.ts`).

### Next, in architect's 5.7 order

G14 landing 2 (ChangeBookingParty / Notes / Requests — product §3 names the
events `booking.party_changed` / `notes_changed` / `requests_changed`; add and
remove stays is the `requests_changed` half and is the big one) → G15
(ChangeNights, SetNightRate, on the stay page) → G20 group availability grid →
G28 BookingSource (product `50a07b7`) → SetRoomType (product `349073e`:
`room.type_changed`, `setup.roomTypeInvalid`, allowed with a checked-in stay) →
G16 → G22 → G29 → G30 → G32 routing table on the booking page → G33 owner home
+ NeedsAttention.

### Open, carried forward

- **Two QA rulings from slice 4 were due "latest 5.6" and did not land**: (a)
  history tables should group events by `correlationId` so one click reads as
  one entry — G4 rewrote those tables without it; (b) every update command
  should answer `nothingToChange` and the screen should say so (accounts does;
  guest/contact/roomType/rate still go silent). Both are small and want doing
  early in 5.7 — raised with architect.
- Rooms with a null `room_type_id` are flagged in Setup but cannot be re-typed
  until SetRoomType lands.
- `bookings.sourceId` still has no writer (G28).
- Cloudflare `code: 7403` on the D1 migrate step failed the first `pnpm deploy`
  twice this session and cleared on an immediate retry both times. Flagged to
  Alex as infra.

### How UI gets verified here

No dev server and no staging sign-in: inline `src/styles.css` into a static
HTML harness in the scratchpad, screenshot it with Playwright run from
`solex/e2e` (`@playwright/test` does not resolve from `/tmp`), delete the
harness after. It caught real defects in every landing it was used on — the
tape chart's foot headings, the money strip, the nav groups.
