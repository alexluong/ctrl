# solex-dev

**Role:** WS1 now (repo + Cloudflare Workers/TS spike), then the implementing engineer for SoLex. Pragmatic: prove things by deploying, not by reading docs.

**Owns:** `~/git/hub/alexluong/solex` repo (create it), `stack.md`.

**Constraints (from Alex):** TypeScript on plain Cloudflare Workers (D-3, 2026-09-19 — Go dropped). No VM. Free tier where possible; ask before paid. Ship > purity.

## Current objective (2026-09-25, rev 7 — demo-able MVP; feature freeze)

Alex via architect: the goal is a **demo-able MVP, not production**. Entry point is `../../mvp.md`. Every v1 function in `product.md` §11 is built and QA-green.

**From here: no new features.** Only (a) fixes QA files while filming showcase journeys R3–R5, (b) anything demo-blocking, (c) vi pass 3 (the 92 keys) if product sends it — apply + commit.

**Resume state:** solex `f77cad4`, staging `70dd7c8c`, 560 unit tests, green, `pnpm build` clean, biome at the 4-warning + 1-info baseline, both repos clean and pushed, migrations 0018–0020 applied dev + remote. QA suite 154/154 desk + 13/13 receptionist, no open finding.

**Known half-done** (architect 2026-09-25: both are §4 follow-ups, no work now):
- "Take it anyway" (overbooking override) is offered on the **new-booking form only**. `checkIn`, `changeNights` and `changeBookingRequests` all accept `override` but no screen sends it, so those paths refuse even under `warn`. Ruled: stays this way for the MVP.
- G32 routing-table cells are read-only; a room's own exception is set on the room's page. Ruled: "As agreed" keeps as built — it clears the column, not a room's own setting.

<details><summary>rev 6 (build the rough end-to-end, slice by slice — discharged 2026-09-25)</summary>

Alex: "green light, let's implement a rough version of the overall design." Auth already live. Each slice = commands + projections + one screen + unit tests on `decide` + deployed to staging + projections rebuildable via `/system`. Rough = one receptionist can do the flow in a browser; no polish/i18n/mobile.

| # | Slice | Commands (product.md §11) | Screen |
|---|---|---|---|
| 0 | Foundation (in flight) | Room flip → CRUD+events, staging wipe (Alex ok'd), D-12 envelope + `schema_version`/upcaster hook, `command_id` UNIQUE (idempotency) | `/system` |
| 1 | **Occupancy loop** | `booking.create` (walk-in, one room type, nights, contactId) → `stay.create` → `stay.assign_room` → `stay.check_in` → `stay.check_out` (no balance check yet) + `room.mark_dirty` reaction + `stay.cancel`. Every supply/demand command versions `availability:<hotel>` (D-8). | Front Desk room grid (dates × rooms), booking list, one stay page |
| 2 | Setup minimum (tier b) | RoomType, RateType, Guest/Contact CRUD + events; `hotel_staff` so `requireUser()` returns hotelId+role | plain Setup forms |
| 3 | **Money — next (2026-09-23)** | `folio.post_charge`, `payment.record`, night posting on business-date roll (D-7), transfer to company receivable, checkout blocked with balance (§10); Ledger = truth, folio = projection (D-16/17) | folio tab on stay, payment form |
| 4 | Roles + audit | owner-only guards on money commands; history tab (events per stream) on room/stay/folio | history tab |
| 5 | Long tail | **order (architect 2026-09-24):** 5.1a Company (Setup, tier b: name, defaultRouting; receivable transfer picks from list) → 5.1 group booking + master folio routing (§10/§11; Bucket = ChargeCategoryId; master guarded at booking.close) → 5.2 Cloudflare cron entry for the night roll (D-25) + HotelProfile (D-7 zone, roll hour) → 5.3 dashboard + revenue/occupancy/receivables reports (owner, `reports.view`) → 5.4 deposits + MarkNoShow → 5.5 folio print → 5.6 polish (ux.md §6 P rows, familiarity order, D-27) → 5.7 command coverage (ux.md C rows: G14/15/16/20/22/28/29/30/31/32/33 incl. BookingSource, Needs-attention inbox) → 5.8 approvals (product.md §11 Approvals, 3 landings; D-28) | as needed |

Alex reviews staging after slice 1 and slice 3. Product owns the spec: a gap goes into `product.md` first, then code. Ask architect only for breaking calls; ping architect with a one-liner per slice landed.

</details>

<details><summary>rev 5 (build Booking/Stay, superseded same day)</summary>

All blockers cleared (D-11, D-20, D-21, D-22 accepted; product v1 = spec). Order: **(1) D-22** flip Room from ES aggregate to CRUD table + `room.*` events appended in the same batch (tier b: table is truth, no fold, no version guard beyond the row); keep the log path. **(2) D-12** envelope columns + `schema_version` + upcaster hook `(type, from) → payload` at load. **(3) Booking → Stay** from `product.md` §11, every supply/demand command versions `availability:<hotel>` in-batch (D-8). **(4) D-11** app-owned username/password behind `requireUser()`; must land before staging holds real data. Product owns the spec — a gap goes into `product.md` first, then code. Ask architect only for breaking calls.


</details>

<details><summary>rev 4 (ES skeleton live, superseded same day)</summary>

Skeleton done (D-8 shape, D-9 in, Room aggregate, `/system` console). Before **Booking** (the real test — cross-aggregate availability): add `schema_version` on `events` + upcaster hook (D-10, proposed); auth waits on Alex's IdP pick (D-11). Booking itself waits on product v1 (§6 vocabulary + the availability-stream versioning rule in D-8). Take direction from Alex in-session over this profile; tell architect what changed.

</details>

<details><summary>rev 3 (standby, superseded same day)</summary>

Standby. Spike delivered (`stack.md`, staging live). Next work waits on: Alex accepting D-8 (storage), product v1 (schema/events). When both land: ES skeleton in `solex` — `events` table + one aggregate end-to-end (booking) with synchronous projections. Until then: nothing in `solex` beyond housekeeping; answer product/architect questions.

</details>

<details><summary>rev 2 (2026-09-19, done)</summary>


Spike, not scaffolding. Prove the simplest Workers/TS path end-to-end:

1. Bootstrap `solex` via `/new-project solex` (private repo). Needs `wrangler login` from Alex first.
2. Hello-world Worker (TS) deployed. Pick a minimal framework or none (Hono is the usual answer; justify).
3. **D1**: one table, one query, migration via wrangler. Note DO/KV only if D1 is clearly wrong for an event log (append-heavy, per-aggregate ordering) — flag, don't build.
4. Full-stack shape: how UI gets served (Workers static assets / Pages) — one page that hits the API. Framework choice deferred to product + collie-ui; just prove the plumbing.
5. `fix` / `check` per `docs/workflow.md` quality bar; local dev loop (`wrangler dev`) vs deploy.

Deliver in `stack.md`: deployed URL, dev loop, D1 fit for an event store (honest take), cost (should be $0), recommended app shape. Message architect when done or blocked.

Do **not** yet: domain code, ES infra, Hookdeck. Those wait on product + architect.

</details>

**Added 2026-09-23 — storage sanity-check (desk exercise, no code):** read `product.md` §5–6. Product proposes a single-writer Durable Object per hotel for the Reservations context (availability = cross-aggregate invariant), D1 for projections/read models. Write your take in `stack.md`: DO-as-event-store feasibility (storage API, size limits, replay), D1 vs DO for the event log, how projections get fed (DO alarms? queues?), and whether Hookdeck has a role. Keep it to a page.

## Later (not now)

- Event store implementation once architect decides Hookdeck-as-log vs bus+archive.
- Frontend: TS → React likely; coordinate w/ `collie-ui` (see README cross-ref).

## Log
- 2026-09-26 — **Code review wave 2 complete** (B5 B6 B7 B9 B10 B12 B13 B14 B15-partial A3 + N52 slug + QA N66): solex `f77cad4`, staging `70dd7c8c`, 560 unit green, biome baseline, migration 0021 (`approvals.method`) applied dev + remote. Two findings of dev's own that the review's fixes uncovered: booking/stay ids were minted **outside** `plan()` (D-12 f), latent until B7 gave two group creates something to collide on — a retry reused the losing attempt's stream ids and could never succeed; and `approvalDecide.request`'s doc comment claimed the underlying command's rules ran at request time when they did not (now they do). Deviations: B13's rule is "is there an active owner" not "is this the first row"; the second state turns out unreachable because the last-owner guard refuses first, pinned in one test so both are read together. **Deferred, product-spec'd, architect schedules:** the `{key, params}` stored-memo schema + `HotelProfile.locale` (mvp.md §4).
- 2026-09-25 — N65 (from collie-lab's demo of N64, reproduced by QA): erased rows outlived the erase because a search's results are component state and `router.invalidate()` does not touch them — the erase re-asks the box's question now. And the two lists disagreed: `listContacts` never had the erased filter `listGuests` has, so a guest vanished while the same person's contact stayed as a blank "(erased)" row. Contacts now match, with the same `includeErased` audit path. Second erase on a tombstone is a no-op, now tested.
- 2026-09-25 — N64 interim built (product ruled it the v1 answer, ctrl 1b4c8af): after an erase the People page names the same person in the other list and offers that second erase. Phone first, exact name only when there is no phone, never automatic. Receipt print stays out — in scope, after the demo, architect schedules.
- 2026-09-25 — QA N63 fixed (a closed bill says why it closed). N64 (erasing a guest leaves the same person's contact) left with product: `contacts.erase` already exists and the contacts list already offers it, so it is not a missing capability — the two records are linked only by a typed name, which is why "one button erases the person" is an identity decision and not a loop. Cheap interim offered, not built: after erasing a guest, say a contact of the same name still exists and link to it.
- 2026-09-25 — product ruled both open questions (ctrl 661d15c): §10 6a reading stands, no code change; stored memos become `{key, params}` rendered at read time, with `HotelProfile.locale` for the printed bill. **Not started — architect picks the wave.** Mechanism already exists (the early-check-out reversal uses it); the print path is the hard half, and the company-name-at-render fix for N52's slug is independent and tiny.
- 2026-09-25 — code review wave 1 (B1 B2 B3 B4 B8) landed, plus QA N46–N62 and N57. B1 grew: the reversal broke transfer-to-receivable at check-out (company invoiced for a night nobody slept; guest's folio in credit; check-out refused), fixed with one server-side `dueOnCheckOut` both the settle dialog and the transfer use. Product amended B1 twice — same-day in/out pays **one** night (ctrl 79631fd), which is where it landed. Deviation from the review, deliberate: B4 has no posted-night guard (the roll posts tonight before anyone moves anyone, so it would make an in-house move impossible).
- 2026-09-25 — Alex saw Vietnamese labels in English forms (recordings). Cause: seeded charge categories carry `name` + `nameEn`; eight screens render them and only the expenses page picked by locale. Fixed with one `localName()` rule + `names.test.ts` guard (solex `285648d`). Hotel-typed names (room types, sources, companies) correctly stay as typed.
- 2026-09-25 — vi pass 3 from product applied (solex `2f61ef9`); Tiếng Việt is complete. What remains is a native-speaker wording pass with the client, not translation.
- 2026-09-25 — architect: everything landed unrouted accepted as-is (ctrl 5fbd9e7). Alex's new direction: demo-able MVP, feature freeze; `mvp.md` is the entry point. Reported the three half-done items above for §3/§4.
- 2026-09-23 — architect: slice 3 order after landing 4: money screens (folio tab, post charge, take payment, check-out with balance) → Alex staging pass → receivable side (record payment, write off) + expenses → cron entry before go-live.
- 2026-09-23 — architect: slices 1–2 accepted (173 tests). Slice 3 go: Ledger (D-17) + folio projection + post_charge/payment + night posting per D-25 + checkout balance guard + transfer to receivable. Hotel methods + scenarios first; money commands idempotent by commandId; owner-only guards via ctx.must. CreateUser/UpdateUser/DisableUser → slice 4.
- 2026-09-23 — architect: rev 6, slice plan 0–5; Alex green light for rough end-to-end.
- 2026-09-23 — architect: auth landed ahead of order (fine). Answers: User/staff tier b, library owns row; system_operator ok; wipe staging log at Room flip; D-23 redaction.
- 2026-09-23 — architect: rev 5. D-22 (two tiers) accepted by Alex; Room → CRUD+events first, then envelope, Booking/Stay, auth.

- 2026-09-19 — session created.
- 2026-09-19 — objective rev 2: Go dropped (D-3), TS Workers + D1 spike.
- 2026-09-23 — + storage sanity-check vs product's aggregates (desk exercise).
- 2026-09-23 — spike shipped (9f54e73); storage take → D-8 proposed. Objective rev 3: standby.
- 2026-09-23 — Alex asked in-session for ES skeleton; built + deployed (Room, console, replay). Rev 4: D-10/D-11 before Booking.
