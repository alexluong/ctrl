# solex-product

**Role:** WS3 — domain discovery / product modeling. Turns the client's Excel-shaped wishlist into a domain model that event sourcing can implement. Thinks in users, jobs, aggregates, events, invariants. **No code.**

**Owns:** `product.md`.

**Inputs:** `requirements.md` (primary — client's own words, EN translation + first read), `discovery.md` (Alex's answers, when present), `existing-system.md` (from solex-explore, when present).

## Session agenda w/ Alex (set 2026-09-23 by architect)

Exploration is complete (README → Existing system, incl. lifecycle & money). Alex will work through, in order: **1 schema · 2 roles/personas · 3 actions/interfaces · 4 rules/policy/logic (§10 + hotel day, see `team/questions.md`) · 5 events shape**. Drive each as a section of `product.md` v1; get Alex's decision per item and record it in `team/decisions.md` as Proposed → I accept. Hotel day / business date replaces the old "day boundary" question — read Alex's note in `discovery.md`.

## Current objective (2026-09-23, rev 3 — v1 delivered)

Standby, spec owner. `product.md` v1 is the spec (D-12…D-19). Answer dev's questions as Booking/Stay get built; keep §11/§12 canonical — a dev-discovered gap goes into `product.md` first, then code. Don't redesign without Alex. Rev 2 items below are done.

<details><summary>rev 2 (done)</summary>


0. **D-4 framing:** client has a PMS today; SoLex is a rebuild for data ownership, core subset + enhancements. Model the *core* they actually use + the enhancements in `requirements.md`; don't model the whole PMS. Per D-5 (2026-09-20): **no migration** — model the domain fresh; "data to own" = going forward only.
0b. **`existing-system.md` has landed** (ezFolio map, group-booking flow, candidate core, hard constraints). Second pass is now: reconcile your aggregate sketch with explore's candidate core. Non-negotiables from explore: no card data ever; personas = manager + receptionist; **group/company bookings are core** (company + per-room-type qty/pax/rate, rooms assigned later → waiting list — model this, it's the hard aggregate); key cards out of scope.
0c. **D-6 (2026-09-23):** third persona **setup/admin** + a Setup bounded context. Design from explore's checklist (rooms/types w/ prices · minibar/laundry/extra-service catalogues w/ prices · tax %/service % / net-gross per charge type · booking rules: day boundary, overbooking, child age, auto-assign · hotel identity). Your `Catalogue`/`HotelPolicy` aggregates probably become this context. Not a copy of ezFolio masters.
1. Read `requirements.md` closely. Interview Alex on README open questions + gaps flagged in requirements §5 (OTA commission rates, seasonal rates, VAT/red invoice, channel-manager vs manual).
2. Deliver in `product.md`:
   - Users + roles (owner / reception / housekeeping — confirm)
   - Jobs-to-be-done per role
   - Bounded contexts
   - Aggregates (Booking, Room, Rate, Guest, Folio/Payment, Receivable, Expense …) w/ **events** (named — this becomes the ES vocabulary) and **invariants** (no double-booking, date-range overlap, tz = hotel-local)
   - The "Need" cascade from requirements §1 mapped to event → projections
   - Core vs later scope; what "semi-professional" means operationally
3. Mark every place the model depends on existing-system findings. Second pass when solex-explore reports.

Message architect with proposed aggregate list early (before polishing) so dev's spike can sanity-check storage shape.

</details>

## Log

- 2026-09-19 — session created.
- 2026-09-19 — objective +D-4 framing (existing PMS, data ownership, core subset).
- 2026-09-23 — D-6: Setup context + setup/admin persona.
- 2026-09-20 — D-5 (no migration); existing-system.md landed → second pass; group bookings core.
- 2026-09-23 — v1 delivered after Alex session (D-9, D-12…D-19). Rev 3: standby, spec owner.
- 2026-09-24 — resume: product.md at 0b0d0df+ (D-20…D-28 applied; BookingSource, Home & inbox, approvals 5.8 = D-28, 5.4 forfeit/no-show); `ux.md` + `diagrams/gen-solex-ux.py` final for Alex → client (D-27 familiarity pass done). Standby for dev/qa/architect questions on 5.5 print → 5.6 polish → 5.7 coverage → 5.8 approvals; answer in product.md first, then tell peers, tell qa on §10 changes. Open on Alex: domain-canvas status tags go/no-go; cash handover needs client. Latest notes entry covers method + state.
- 2026-09-24 (later) — ezFolio-shaped flow mockups done: `diagrams/ezfolio-flow/` (gen.py + solex.css → 5 screens, c0388bc), Alex direction "shapes/nav/vibe ours-style", published by architect. SetRoomType added (349073e). D-29: English everywhere; vi pass = after each accepted slice send dev key → vi pairs from `pnpm i18n:report` (solex stays read-only). Stay-template HTML for ux.md §4 screens pending Alex approval (architect draft). Standby.
- 2026-09-25: vi pass 1 sent to dev — 65 keys (c8b3528) + folio.void → "Huỷ khoản"; pairs in notes/vi-pass-1.md. Standby for Alex on mockups.
- 2026-09-25: G34 overbooking + G35 capacity specced in product.md (override flag, stay.overbook cap, SetOccupancy, OverrideOverbooking retired); vi pass 2 (24 keys @30dbec5) sent to dev. Pass 1 landed solex 18da91f. Compaction suspended — keep this line current.
- 2026-09-25: vi pass 3 (92 keys @8130240) sent to dev; mvp.md check sent to architect (ChargeItem unbuilt vs 'all §11 built', rule-1 cron text stale, People/erase missing from §1, deferred items missing from §4). v1 complete; phase = demo prep. Pending: Stay-template screens if Alex approves.
