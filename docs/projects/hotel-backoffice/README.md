# Project: SoLex — Hotel Back Office

Semi-professional (not full professional). Booking/reservation management back-office app for the SoLex hotel.

Naming: product/hotel name is **SoLex** (keep that casing in prose/UI). Folders, repos, package names use local casing conventions (`solex`, `solex-backoffice`, etc.).

**Doc map** — this project's notes are a directory (see `docs/workflow.md`). Each parallel workstream owns one file; commit only your own.

| file | holds | owner |
|---|---|---|
| `README.md` | what/why, direction, decisions, open questions, status, session prompts | cockpit session |
| `stack.md` | WS1: repo + Go-on-Cloudflare spike, stack decision, deploy shape | WS1 |
| `existing-system.md` | WS2: what the current `:99` system is, feature inventory, entities, what staff use | WS2 |
| `product.md` | WS3: domain discovery — bounded contexts, aggregates, events, user roles, scope | WS3 |
| `discovery.md` | Alex's brain-dump answers to open questions (input to WS2/WS3) | Alex→Claude |
| `agents/<name>/` | per-agent: `README.md` profile (role, owned files, current objective, log) + `notes.md` personal scratch — **read yours at session start** | that agent (profile objective: architect) |
| `team/` | shared: `decisions.md`, `questions.md`, `log.md` — any agent appends, dated + signed | all |
| `requirements.md` | client's initial requirements (2026-09-19), EN translation + structure + first read | cockpit |
| `client/` | raw client inputs, untouched, dated filenames (`2026-09-19-requirements-raw.md`) | frozen — never edit |

Secrets (existing-system URL/login): `ctrl/secrets/hotel-backoffice.md` (gitignored, MBP only).

## Core idea

- Back-office tool: manage bookings for a hotel
- Scope beyond that TBD — Alex to elaborate on scope + how to proceed (pending as of 2026-09-19)

## Direction (2026-09-19, early thinking — not decided)

- **Event sourcing** architecture — bookings/reservations as an event log, state derived from projections
- **Simple full-stack app**, probably deployed on **Cloudflare** (Workers/Pages + D1/R2/Durable Objects TBD)
- **Hookdeck** as the event system / source-of-truth-ish (Alex's intent, 2026-09-19; Hookdeck repos local — see `docs/machine.md`)
  - Open concern: ES needs a permanent, per-aggregate-ordered, replayable log. Hookdeck is retention-bound + ordered per connection → natural fit as **bus** (ingest, fan-out to projections, retries, replay-in-window). As **permanent store** only if long retention/export is available (internal knowledge?).
  - Candidate shape: Hookdeck = transport + short-term replay; Postgres/R2 = archive log fed by an "archive" destination; projections rebuild from archive.
  - Q for Alex: stock SaaS retention, or something that makes retention a non-issue?
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

## Workstreams (kicked off 2026-09-19)

Three parallel sessions, named agents: `solex-dev` (WS1), `solex-explore` (WS2), `solex-product` (WS3); `solex-architect` = cockpit. Profiles + protocol in `agents/`. Rules: each writes only its own file (above), commits in ctrl with `docs(hotel-backoffice/<ws>): …`, pulls before committing. Cross-WS findings go in the WS's own file under a "For other WSs" section; cockpit session merges into README.

Ordering: WS1 + WS3 can start now. WS2 needs Alex to say what the `:99` system is and walk through it (curl alone won't get far if it's a SPA / Vietnamese PMS). WS3 does a second pass after WS2 lands.

Later WS (not now): event-store design — Hookdeck-as-log vs bus + archive. Needs WS1 spike result + Hookdeck retention answer.

### WS1 · `solex-dev` — repo + hello-world spike → `stack.md`

> You are `solex-dev`. Read `~/git/hub/alexluong/ctrl/docs/projects/hotel-backoffice/agents/solex-dev/README.md`, then `../README.md` and `ctrl/docs/workflow.md`. You own `stack.md` only.
> Goal: a *spike*, not scaffolding. Prove Go on Cloudflare with no VM: hello-world Go HTTP service deployed on **Cloudflare Containers** fronted by a Worker, talking to Postgres via Hyperdrive (Neon or similar free tier). Fall back to Go→WASM Workers (`syumai/workers`) only if Containers is blocked; record why.
> Bootstrap repo `solex` with `/new-project` (private). Deliver: deployed URL, `fix`/`check` commands, cold-start + request latency numbers, dev loop (local run vs deploy), cost notes, and a stack recommendation with the tradeoffs. Ask Alex before creating paid resources.

### WS2 · `solex-explore` — analyze existing system → `existing-system.md`

> You are `solex-explore`. Read `~/git/hub/alexluong/ctrl/docs/projects/hotel-backoffice/agents/solex-explore/README.md`, then `../README.md`. You own `existing-system.md` only. Access details in `ctrl/secrets/hotel-backoffice.md` (never copy them into tracked files).
> Goal: understand the system the hotel uses today. Read `requirements.md` first — it's Excel-shaped; confirm whether such a workbook exists. Start by asking Alex what the `:99` system is. Try `curl` w/ the login; if it's a SPA or non-scrapable, drive the analysis via Alex's screenshots / screen-by-screen walkthrough / any export. Deliver: feature inventory, screens, data entities + fields, reports, integrations (OTA/channel manager/payments), what staff actually use vs ignore, pain points, and a "For other WSs" section (entities/events WS3 should model; anything WS1's stack must support, e.g. LAN/offline).

### WS3 · `solex-product` — domain discovery → `product.md`

> You are `solex-product`. Read `~/git/hub/alexluong/ctrl/docs/projects/hotel-backoffice/agents/solex-product/README.md`, then `../README.md` and `requirements.md` (client's own list — primary input), + `discovery.md` and `existing-system.md` if present. You own `product.md` only. No code.
> Goal: model the product. Interview Alex on the open questions first. Deliver: users + roles, jobs-to-be-done, bounded contexts, aggregates (Booking, Room, Rate, Guest, …) with their events and invariants (double-booking, date-range overlap, tz), core vs later scope, and what "semi-professional" means operationally. Write event names as the ES vocabulary. Flag where the model depends on WS2 findings; plan a second pass after WS2.

## Status

- 2026-07-10 — plan agreed, awaiting discovery brain-dump.
- 2026-09-19 — client's initial requirements received → `requirements.md`. Excel-shaped; confirms spreadsheet mental model. Owner/reception/housekeeping roles, money-heavy, expenses in scope.
- 2026-09-19 — named SoLex; early direction: event sourcing, simple full-stack on Cloudflare, maybe Hookdeck. Constraint: Go, no VM. Scope elaboration pending. Creds moved out of git (temporary creds, env is fine).
