# Team log

Newest first. `YYYY-MM-DD — <agent>: what`.

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
