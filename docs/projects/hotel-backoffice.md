# Project: SoLex — Hotel Back Office

Semi-professional (not full professional). Booking/reservation management back-office app for the SoLex hotel.

Naming: product/hotel name is **SoLex** (keep that casing in prose/UI). Folders, repos, package names use local casing conventions (`solex`, `solex-backoffice`, etc.).

## Core idea

- Back-office tool: manage bookings for a hotel
- Scope beyond that TBD — Alex to elaborate on scope + how to proceed (pending as of 2026-09-19)

## Direction (2026-09-19, early thinking — not decided)

- **Event sourcing** architecture — bookings/reservations as an event log, state derived from projections
- **Simple full-stack app**, probably deployed on **Cloudflare** (Workers/Pages + D1/R2/Durable Objects TBD)
- _Maybe_ **Hookdeck** for events/queue (Alex has Hookdeck repos locally — see `docs/machine.md`)
- **Constraints (2026-09-19):** wants Go, wants to ship, does **not** want to run/deploy on a VM. Cloudflare = "simple, no hosting to worry about." Supersedes the collielab-VM assumption in `docs/stack.md` for this project.
- Go-on-Cloudflare options to evaluate (not decided):
  - **Cloudflare Containers** — plain Go binary in a container, fronted by a Worker; closest to "just Go," no VM. Storage via Hyperdrive→Postgres (Neon/Supabase) or D1 through the Worker.
  - **Workers via Go→WASM** (`syumai/workers`, TinyGo) — Workers-native (D1/KV/DO bindings) but rough edges, limited stdlib, cold starts.
  - **TS Worker + Go elsewhere** — fallback if Go-on-CF fights back; keeps Go for domain/ES core.
- Secrets: env/gitignored is fine for now — existing-system creds are temporary.

## Notes

- Best fit for the **"Go at larger scope/scale" learning goal** — real domain modeling (reservations, room inventory, rates, calendars), real users, real data integrity concerns. (Revisit if Cloudflare/TS wins.)
- "Semi-professional" — clarify what that means for reliability/support expectations
- Cross-refs: `docs/stack.md` (guest capability tokens, tenancy/roles, Keto-if-ever), `docs/projects/collie-ui/` (hotel app = DS portability test; needs `Table`; React vs Go/templ open)
- Existing hotel system: URLs + login in `secrets/hotel-backoffice.md` (gitignored, machine-local; canonical in Vaultwarden). Unlabeled — confirm what it is (current PMS?).

## Open questions (discovery needed)

- Which hotel / whose? Relationship, and who are the actual users (front desk? owner?)
- Size: rooms, bookings/day?
- Current process: paper? Excel? existing PMS (the system at the URLs above)?
- OTA channels (Booking.com, Agoda, Airbnb)? Channel-manager integration or manual entry?
- Just reservations, or also check-in/out, housekeeping, payments/invoicing, reporting?
- Timeline/urgency? Anyone waiting on this?
- Event sourcing: full ES (event store + projections + replay) or just an append-only audit log? Which aggregates (Booking, Room, Rate)?
- Cloudflare: which storage (D1 vs Durable Objects vs external Postgres)? Offline/LAN needs at the hotel?
- Hookdeck: what's the actual queue need — OTA webhooks in, async projections, notifications?

## Plan (agreed 2026-07-10)

This is the **Go-at-scale learning project**: backend-heavy, web back office, no mobile. Discovery (questions above) comes before any scoping — Alex to brain-dump, Claude structures it.

## Status

- 2026-07-10 — plan agreed, awaiting discovery brain-dump.
- 2026-09-19 — named SoLex; early direction: event sourcing, simple full-stack on Cloudflare, maybe Hookdeck. Constraint: Go, no VM. Scope elaboration pending. Creds moved out of git (temporary creds, env is fine).
