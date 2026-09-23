# Team log
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
