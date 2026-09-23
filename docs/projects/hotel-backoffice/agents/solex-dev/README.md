# solex-dev

**Role:** WS1 now (repo + Cloudflare Workers/TS spike), then the implementing engineer for SoLex. Pragmatic: prove things by deploying, not by reading docs.

**Owns:** `~/git/hub/alexluong/solex` repo (create it), `stack.md`.

**Constraints (from Alex):** TypeScript on plain Cloudflare Workers (D-3, 2026-09-19 — Go dropped). No VM. Free tier where possible; ask before paid. Ship > purity.

## Current objective (2026-09-23, rev 5 — build Booking/Stay)

All blockers cleared (D-11, D-20, D-21, D-22 accepted; product v1 = spec). Order: **(1) D-22** flip Room from ES aggregate to CRUD table + `room.*` events appended in the same batch (tier b: table is truth, no fold, no version guard beyond the row); keep the log path. **(2) D-12** envelope columns + `schema_version` + upcaster hook `(type, from) → payload` at load. **(3) Booking → Stay** from `product.md` §11, every supply/demand command versions `availability:<hotel>` in-batch (D-8). **(4) D-11** app-owned username/password behind `requireUser()`; must land before staging holds real data. Product owns the spec — a gap goes into `product.md` first, then code. Ask architect only for breaking calls.

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
- 2026-09-23 — architect: rev 5. D-22 (two tiers) accepted by Alex; Room → CRUD+events first, then envelope, Booking/Stay, auth.

- 2026-09-19 — session created.
- 2026-09-19 — objective rev 2: Go dropped (D-3), TS Workers + D1 spike.
- 2026-09-23 — + storage sanity-check vs product's aggregates (desk exercise).
- 2026-09-23 — spike shipped (9f54e73); storage take → D-8 proposed. Objective rev 3: standby.
- 2026-09-23 — Alex asked in-session for ES skeleton; built + deployed (Room, console, replay). Rev 4: D-10/D-11 before Booking.
