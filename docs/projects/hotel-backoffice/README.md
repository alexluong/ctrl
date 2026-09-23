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
| `agents/<name>/` | per-agent: `README.md` profile (role, owned files, current objective, log) + `notes/YYYY-MM-DD-HHMM-<slug>.md` personal journal, one file per entry — **read yours at session start** | that agent (profile objective: architect) |
| `team/` | shared: `decisions.md`, `questions.md`, `log.md`, `progress.md` (narrative history) — any agent appends, dated + signed | all |
| `requirements.md` | client's initial requirements (2026-09-19), EN translation + structure + first read | cockpit |
| `client/` | raw client inputs, untouched, dated filenames (`2026-09-19-requirements-raw.md`) | frozen — never edit |

Secrets (existing-system URL/login): `ctrl/secrets/hotel-backoffice.md` (gitignored, MBP only).

## Core idea

- Back-office tool: manage bookings for a hotel
- Scope beyond that TBD — Alex to elaborate on scope + how to proceed (pending as of 2026-09-19)

## Direction (2026-09-19)

**Decided (D-3):** TypeScript on plain Cloudflare Workers. Go dropped — simplicity wins. **Amended 2026-09-23:** TanStack Start + Drizzle + SQLite; Cloudflare = build target only, dev loop is Node + local SQLite. Staging live: https://solex-stg.collie.studio (`stack.md`).
**Decided (D-9):** multi-tenant by design, one tenant in practice — everything keyed by `Hotel`, no cross-hotel data v1, tenant seeding via script, no self-signup/billing/super-admin.
**Decided (D-8, de facto):** D1 for event log *and* projections, optimistic concurrency on `(stream_id, version)`, no Durable Object, projections in the same atomic batch, Hookdeck deferred. Built + deployed 2026-09-23 at Alex's direction.
**Decided (D-12…D-19, product session 2026-09-23):** event naming `agg.past_verb` + full envelope (ulid, hotelId, stream, version, type, schemaVersion, occurredAt, businessDate, actor, correlation/causation/commandId) · Booking v1 minimal, no OTA logic · **Booking/Stay** naming · **night is the unit** (Stay = nights[] w/ room+rate+posted; availability = no two stays share (roomId, date)) · money v1 (own+master folios, Setup charge categories, receivable per folio, no due date) · **generic double-entry Ledger** under Billing/Expenses (Folio/Receivable = projections) · users per person, roles = capability bundles (`receptionist`, `owner`), three apps (Front Desk, Back Office, Setup) · v1 screen inventory. §10 rules, §11 ~40 commands, §12 event index in `product.md`.
**Proposed:** D-11 auth (OIDC stance from `docs/stack.md`; IdP = Alex's pick). D-10 folded into D-12.
**Decided (D-4):** client already has a PMS (**ezFolio** by ezCloud, the `:99` system). SoLex = rebuild driven by **data ownership**; core subset + enhancements, not feature parity. WS2 maps the PMS first via slow walkthrough w/ Alex.
**Decided (D-5):** fresh start, migration deferred — ezFolio has no working export. Schema for the domain, not for an import.
See `team/decisions.md`. Older Go notes below kept for context.


- **Event sourcing** architecture — bookings/reservations as an event log, state derived from projections
- **Simple full-stack app**, probably deployed on **Cloudflare** (Workers/Pages + D1/R2/Durable Objects TBD)
- **Hookdeck** as the event system / source-of-truth-ish (Alex's intent, 2026-09-19; Hookdeck repos local — see `docs/machine.md`) — **2026-09-23: dev's D-8 says no role for the log (a DB's job, now D1); at most OTA-webhook ingest later.** Bullets below kept for context.
  - Open concern: ES needs a permanent, per-aggregate-ordered, replayable log. Hookdeck is retention-bound + ordered per connection → natural fit as **bus** (ingest, fan-out to projections, retries, replay-in-window). As **permanent store** only if long retention/export is available (internal knowledge?).
  - Candidate shape: Hookdeck = transport + short-term replay; Postgres/R2 = archive log fed by an "archive" destination; projections rebuild from archive.
  - Q for Alex: stock SaaS retention, or something that makes retention a non-issue?
- ~~**Constraints (2026-09-19):** wants Go~~ (superseded by D-3 — TS), wants to ship, does **not** want to run/deploy on a VM. Cloudflare = "simple, no hosting to worry about." Supersedes the collielab-VM assumption in `docs/stack.md` for this project.
- Go-on-Cloudflare options to evaluate (not decided):
  - **Cloudflare Containers** — plain Go binary in a container, fronted by a Worker; closest to "just Go," no VM. Storage via Hyperdrive→Postgres (Neon/Supabase) or D1 through the Worker.
  - **Workers via Go→WASM** (`syumai/workers`, TinyGo) — Workers-native (D1/KV/DO bindings) but rough edges, limited stdlib, cold starts.
  - **TS Worker + Go elsewhere** — fallback if Go-on-CF fights back; keeps Go for domain/ES core.
- Secrets: env/gitignored is fine for now — existing-system creds are temporary.

## Existing system — ezFolio (WS2 done 2026-09-20, full map in `existing-system.md`)

- ezCloud **ezFolio**: vendor-hosted Windows/PHP/Oracle, LAN allowlist, plain HTTP. Multi-property hotel+restaurant+golf product; SoLex uses a narrow slice. 58 rooms, ~96% occupancy, rates 750k–1,026k VND.
- **Group/company bookings ≈ 2/3 of in-house rooms.** Shape: company + contact + saler + deposit, then per room type qty/pax/rate; rooms assigned later (waiting list). Booking exists without a room; room *class* is bookable. → the hard aggregate.
- **No rate plans** — rates typed per booking. Client's "auto rate" = new capability (rate table room type × season), not a port.
- **Channel typed into guest names** (AGD/CTRIP/TVLK/EXP). Improvement target: first-class Channel + commission. Channel-manager integration exists, unused.
- **Night audit off** → no day close; "today's revenue" is ad-hoc. Day-boundary rule needs a decision (charge roll 23:59 in config).
- Everything attributed (created/edited/checked-in-by, per-booking log); discounts have request→edit→approve trail. ES gets this free.
- Personas (D-6): **manager** (reads) · **receptionist** (runs the day) · **setup/admin** (rooms/types/prices, catalogues, tax/service %, booking rules, hotel identity — rare, owner in practice). Housekeeping/restaurant off-system. Status vocab VC/VD/OC/OD/OOO. Source taxonomy OTA/TA/WALK-IN/CORP.
- Hard constraints: **no card data ever**; key cards out; stay rules are a change target.
- Candidate core: bookings incl. group + waiting list · room assignment/status · check-in/out · folio + extras · payments/deposits · receivables by debtor · guest profiles/history · revenue/occupancy reports · PA18 export · audit. **Out**: restaurant, HK scheduling, key cards, golf, multi-property, CM sync (later), cards (never).
- **Group folio routing** (2026-09-23): each room-stay in a group has per-category switches → charge settles on group **master** bill or guest's **own** folio (room · HK · restaurant · ext. services · phone · massage · sub-invoice · deposits · other). Corporate case = company pays room, guest pays incidentals. Model: `charge.routedTo = own | master`, per bucket.
- **Two booking use cases**: individual = pick a room, one form, exits "book" or "check-in"; group = availability engine (room type × night matrix), rooms late-bound. Same room-stay underneath; individual can be merged into a group later.
- **One charge shape, eight buckets**: (room-stay, date, item, qty, unit price, bucket, note, who). Buckets: room · room surcharge · minibar · laundry · compensation · ext. service · telephone · restaurant — same list = revenue columns = folio tabs = routing switches. Posted from the room map tile. Minibar = stock per room (58).
- **Config split**: item masters (room, room_type, product, minibar, laundry, service, …) all permission-blocked → no pricing config documented. Settings visible (26 tabs): tax 0%, service charge 0%, all net.
- **Settled by Alex (2026-09-23)**: room map + tape chart = the two home screens (tape chart = receptionist tool, drag to move/extend). Daily stays only, no hourly. Early/late = catalogue items; drop the +0.3/+0.5/+1 rate multipliers. Personas unchanged.
- Facts: child age threshold 6, adults/children auto-counted from guest list. Overbooking ON today (tape chart sells >100% on turnover days). Guest ID field is "?" on all 51 revenue rows while PA18 depends on it.
- **Lifecycle & money (2026-09-23, explore, all read-only verified):**
  - **Nightly posting confirmed**: room charge for night N posts at 23:59 (`is_post` per night); in-house folio grows nightly; "advance post" exists. `rpt-room-revenue-daily` = occupancy × rate, not posted charges — they reconcile at 23:59. "Revenue today" must say which.
  - **Departure date exclusive**, nights not dates: 18→28/09 = 10 charge rows. Double-booking = overlapping *nights*; turnover days are fine. So `allow_over_room` ON = genuine overbooking.
  - **Settlement**: no payment page; checkout = `quickout` dialog in the editor, one row per room-stay, one method each (cash 2 · card 3 · transfer 6 · FOC 9 · **debt 10**). Debt method = what opens a receivable. Split payment → split the folio. **Đóng (closed) = night-audit day close, not settlement.**
  - **Receivable**: per *folio* (Số RE), not per booking. Settle = amount (partial ok) + method + note. **No due date** — overdue is age only.
  - **Folio is constructed, not fixed**: charge lines can be moved between rooms/folios (`Chuyển dịch vụ`); master folio = one folio carrying many room-stays' lines; routing switches = the automatic version. Master settles like any folio → company receivable. Naming trap: form "FolioID" = reservation id; ledger "Số RE" = real folio no.
  - **Deposit** = a number on the booking, checked before cancel/checkout. On cancel, forfeited *by hand* as an extra-service charge line. No refund path.
  - **Cancel**: guarded (not if checked in; charges must be moved off first; reason mandatory), no charge posted. **No-show** = bare flag. Groups cancel per room-stay; partial cancel = cancel N stays.
  - **Waiting list is empty all September** — rooms are assigned at booking time in practice. Every status verb is per room-stay → partial arrivals/departures are normal; rooming list mostly never entered.
  - **Mid-stay**: room move = from→to only, no repricing; extend/shorten regenerates night rows, posted ones immutable; **no rate-change event** — per-night price is mutable state w/o history. Keep "posted nights immutable", make price change an event.
  - OTAs appear as *debtors* → guest pays channel, hotel bills OTA. Gross vs net of commission unconfirmed.
- Flow board: `board/solex-flow.excalidraw` (gitignored — live guest data), regenerate via `tools/excalidraw/build.py`. FigJam copy frozen (Figma plan caps MCP at 20 calls/month) — Excalidraw is source of truth.
- ~~Admin login~~ closed (D-6): masters inferred from live data are enough; Setup is designed from a checklist, not copied. Parked: which of ~60 booking fields are used daily, data volume/history.

## Notes

- Best fit for the **"Go at larger scope/scale" learning goal** — real domain modeling (reservations, room inventory, rates, calendars), real users, real data integrity concerns. (Revisit if Cloudflare/TS wins.)
- "Semi-professional" — clarify what that means for reliability/support expectations
- Cross-refs: `docs/stack.md` (guest capability tokens, tenancy/roles, Keto-if-ever), `docs/projects/collie-ui/` (hotel app = DS portability test; needs `Table`; React vs Go/templ open)
- Existing hotel system: URLs + login in `secrets/hotel-backoffice.md` (gitignored, machine-local; canonical in Vaultwarden). Unlabeled — confirm what it is (current PMS?).

## Open questions (discovery needed)

- Which hotel / whose? Relationship, and who are the actual users (front desk? owner?)
- Size: rooms, bookings/day?
- ~~Current process~~ → existing PMS (`:99`). Which parts do staff actually use? What data must be owned/migrated?
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

Ordering: ~~WS1 + WS3 can start now. WS2 needs Alex…~~ **WS2 complete 2026-09-20. WS3 v0 complete 2026-09-23** (`product.md`: 7 aggregates, event vocabulary, 8 policy points). **WS1 spike + ES skeleton shipped 2026-09-23.** **WS3 v1 complete 2026-09-23** (D-12…D-19, §10 rules, §11 command catalogue, §12 event index). Next: dev adds D-12 envelope columns, then Booking/Stay from §11; D-11 auth needs Alex's IdP.

~~Later WS (not now): event-store design — Hookdeck-as-log vs bus + archive.~~ Collapsed into D-8 (2026-09-23) if accepted.

### WS1 · `solex-dev` — repo + Workers/TS hello-world spike → `stack.md`

> You are `solex-dev`. Read `~/git/hub/alexluong/ctrl/docs/projects/hotel-backoffice/agents/solex-dev/README.md`, then `../README.md` and `ctrl/docs/workflow.md`. You own `stack.md` only.
> Goal: a *spike*, not scaffolding. Objective is in your profile (rev 2, D-3): TS Worker + D1 hello-world, UI plumbing, dev loop, deploy.
> Bootstrap repo `solex` with `/new-project` (private). Deliver: deployed URL, `fix`/`check` commands, cold-start + request latency numbers, dev loop (local run vs deploy), cost notes, and a stack recommendation with the tradeoffs. Ask Alex before creating paid resources.

### WS2 · `solex-explore` — analyze existing system → `existing-system.md`

> You are `solex-explore`. Read `~/git/hub/alexluong/ctrl/docs/projects/hotel-backoffice/agents/solex-explore/README.md`, then `../README.md`. You own `existing-system.md` only. Access details in `ctrl/secrets/hotel-backoffice.md` (never copy them into tracked files).
> Goal: understand the system the hotel uses today. Read `requirements.md` first — it's Excel-shaped; confirm whether such a workbook exists. Start by asking Alex what the `:99` system is. Try `curl` w/ the login; if it's a SPA or non-scrapable, drive the analysis via Alex's screenshots / screen-by-screen walkthrough / any export. Deliver: feature inventory, screens, data entities + fields, reports, integrations (OTA/channel manager/payments), what staff actually use vs ignore, pain points, and a "For other WSs" section (entities/events WS3 should model; anything WS1's stack must support, e.g. LAN/offline).

### WS3 · `solex-product` — domain discovery → `product.md`

> You are `solex-product`. Read `~/git/hub/alexluong/ctrl/docs/projects/hotel-backoffice/agents/solex-product/README.md`, then `../README.md` and `requirements.md` (client's own list — primary input), + `discovery.md` and `existing-system.md` if present. You own `product.md` only. No code.
> Goal: model the product. Interview Alex on the open questions first. Deliver: users + roles, jobs-to-be-done, bounded contexts, aggregates (Booking, Room, Rate, Guest, …) with their events and invariants (double-booking, date-range overlap, tz), core vs later scope, and what "semi-professional" means operationally. Write event names as the ES vocabulary. Flag where the model depends on WS2 findings; plan a second pass after WS2.

## Status

- 2026-07-10 — plan agreed, awaiting discovery brain-dump.
- 2026-09-23 — **product v1** (96d3b04): Alex session done — D-12…D-19 accepted. Ledger context is Alex's idea. Command catalogue is canonical for dev. §10 policy points all closed (OTA/VAT/discounts/due dates deferred).
- 2026-09-23 — **ES skeleton live** on staging: events table + same-batch projections + replay, Room aggregate, `/system` console (log browser, tables, replay). D-8 built as proposed → accepted de facto; D-9 folded in. Next aggregate = Booking; envelope per D-12, auth D-11 proposed.
- 2026-09-23 — **WS1 spike shipped** (9f54e73): TanStack Start + Drizzle + SQLite/D1 on Workers, https://solex-stg.collie.studio, $0. D-3 amended (CF = build target only). **D-8 proposed**: D1 log + projections, no DO, Hookdeck deferred. New Qs: hotel-local tz, staging auth.
- 2026-09-23 — **D-7: hotel day = configurable business date; nights from timestamps + rules.** Closes day-boundary Q.
- 2026-09-23 — explore answered architect's 10 lifecycle/money Qs (5e143b4): nightly posting, exclusive departure, debt-as-method, per-folio receivables, constructed folios, manual deposit forfeit. 5 items left for Alex walkthrough. **Exploration essentially complete.**
- 2026-09-23 — product v0.1: Setup context added, in v1 core. **Blocked on Alex: §10 policy points.**
- 2026-09-23 — **D-6: Setup is its own scope + third persona; no admin login.** Product to add Setup context.
- 2026-09-23 — **product.md v0** (product). Aggregates: Booking→RoomStay, Room, Folio (own+master), Receivable, Guest, Catalogue, Expense. Key architectural ask: availability is cross-aggregate → single-writer DO per hotel for Reservations, not per-room streams. 8 policy points → questions.md.
- 2026-09-23 — explore: flow board + 4 model-changing findings (group folio routing, two booking use cases, one charge shape / 8 buckets, config split). 3 decisions queued for Alex.
- 2026-09-20 — **WS2 complete** (explore). Summary above. Explore on standby for re-reads / admin screens.
- 2026-09-20 — **D-5: fresh start, migration deferred.** `existing-system.md` landed: ~30-screen ezFolio map, group-booking flow, candidate core, hard constraints (no card data; personas manager + receptionist; group/company bookings core; key cards out). Product second pass unblocked.
- 2026-09-19 — **D-4: `:99` = current PMS; rebuild for data ownership, core subset + enhancements.** All 3 agents caught up, waiting on Alex.
- 2026-09-19 — **D-3: TS on plain Workers, Go dropped.** Dev spike rescoped.
- 2026-09-19 — client's initial requirements received → `requirements.md`. Excel-shaped; confirms spreadsheet mental model. Owner/reception/housekeeping roles, money-heavy, expenses in scope.
- 2026-09-19 — named SoLex; early direction: event sourcing, simple full-stack on Cloudflare, maybe Hookdeck. Constraint: Go, no VM. Scope elaboration pending. Creds moved out of git (temporary creds, env is fine).
