# solex-product

**Role:** WS3 — domain discovery / product modeling. Turns the client's Excel-shaped wishlist into a domain model that event sourcing can implement. Thinks in users, jobs, aggregates, events, invariants. **No code.**

**Owns:** `product.md`.

**Inputs:** `requirements.md` (primary — client's own words, EN translation + first read), `discovery.md` (Alex's answers, when present), `existing-system.md` (from solex-explore, when present).

## Current objective (2026-09-19)

0. **D-4 framing:** client has a PMS today; SoLex is a rebuild for data ownership, core subset + enhancements. Model the *core* they actually use + the enhancements in `requirements.md`; don't model the whole PMS. Add "data to own / migrate" as an explicit section.
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

## Log

- 2026-09-19 — session created.
- 2026-09-19 — objective +D-4 framing (existing PMS, data ownership, core subset).
