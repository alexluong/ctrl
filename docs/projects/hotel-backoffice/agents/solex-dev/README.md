# solex-dev

**Role:** WS1 now (repo + Cloudflare Workers/TS spike), then the implementing engineer for SoLex. Pragmatic: prove things by deploying, not by reading docs.

**Owns:** `~/git/hub/alexluong/solex` repo (create it), `stack.md`.

**Constraints (from Alex):** TypeScript on plain Cloudflare Workers (D-3, 2026-09-19 — Go dropped). No VM. Free tier where possible; ask before paid. Ship > purity.

## Current objective (2026-09-23, rev 6 — build the rough end-to-end, slice by slice)

Alex: "green light, let's implement a rough version of the overall design." Auth already live. Each slice = commands + projections + one screen + unit tests on `decide` + deployed to staging + projections rebuildable via `/system`. Rough = one receptionist can do the flow in a browser; no polish/i18n/mobile.

| # | Slice | Commands (product.md §11) | Screen |
|---|---|---|---|
| 0 | Foundation (in flight) | Room flip → CRUD+events, staging wipe (Alex ok'd), D-12 envelope + `schema_version`/upcaster hook, `command_id` UNIQUE (idempotency) | `/system` |
| 1 | **Occupancy loop** | `booking.create` (walk-in, one room type, nights, contactId) → `stay.create` → `stay.assign_room` → `stay.check_in` → `stay.check_out` (no balance check yet) + `room.mark_dirty` reaction + `stay.cancel`. Every supply/demand command versions `availability:<hotel>` (D-8). | Front Desk room grid (dates × rooms), booking list, one stay page |
| 2 | Setup minimum (tier b) | RoomType, RateType, Guest/Contact CRUD + events; `hotel_staff` so `requireUser()` returns hotelId+role | plain Setup forms |
| 3 | **Money — next (2026-09-23)** | `folio.post_charge`, `payment.record`, night posting on business-date roll (D-7), transfer to company receivable, checkout blocked with balance (§10); Ledger = truth, folio = projection (D-16/17) | folio tab on stay, payment form |
| 4 | Roles + audit | owner-only guards on money commands; history tab (events per stream) on room/stay/folio | history tab |
| 5 | Long tail | **order (architect 2026-09-24):** 5.1 group booking + master folio routing (§10/§11) → 5.2 Cloudflare cron entry for the night roll (D-25) + HotelProfile (D-7 zone, roll hour) → 5.3 dashboard + revenue/occupancy/receivables reports (owner, `reports.view`) → 5.4 deposits → 5.5 folio print → 5.6 search, overbooking override, rest of §11 | as needed |

Alex reviews staging after slice 1 and slice 3. Product owns the spec: a gap goes into `product.md` first, then code. Ask architect only for breaking calls; ping architect with a one-liner per slice landed.

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
