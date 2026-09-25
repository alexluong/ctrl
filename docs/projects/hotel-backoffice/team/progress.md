# SoLex — progress & history

Narrative record of what the team (and Alex) has done, by day. `log.md` is the terse feed; this is the readable version. Architect maintains; append per milestone.

## Where we are (2026-09-25)

**Phase: v1 functionality complete → demo-able MVP.** Every command in `product.md` §11 has a screen (5.7 command coverage + 5.8 approvals landed 2026-09-25: G29 house rules, G32 group routing table, G33 Needs attention, G34 overbooking, G35 capacity, reprice, approvals in three landings). QA suite fully green on `8130240` (desk 154 + receptionist 12), N33–N45 closed, staging `e00bc289`. Alex 2026-09-25: goal is a demo-able MVP, not production; prune docs, track follow-ups → `mvp.md` is the entry point. Next: showcase journeys R3–R5 (D-30), vi pass 3 if the demo is in Vietnamese, then Alex's big UX review.

| WS | agent | state |
|---|---|---|
| Cockpit | solex-architect | active — merging, deciding, routing |
| WS1 stack → ES skeleton | solex-dev | **skeleton live** — events + projections + replay, Room aggregate, `/system` console; **auth live (D-11)**; building rough end-to-end in slices (dev profile rev 6): **0 foundation done 2026-09-23** (wipe confirmed by Alex in dev's session 2026-09-24) → **1 occupancy loop done 2026-09-23** (grid, booking form, stay page; 110 tests; architect walkthrough green) — **Alex: review on staging** → **2 setup minimum done 2026-09-23** (room types, rates, guests/contacts + erasure, staff/roles, Setup screens; 173 tests) → **3 money done 2026-09-24** (ledger, folios, night roll, check-out guard, receivables, expenses, form sweep; 255 unit + 27 e2e; staging 98e73650) — **Alex: review on staging** → **4 roles/history done 2026-09-24** (accounts, roles on /accounts, sessions end in-batch, histories for guest/booking/stay/folio/room; 276 scenarios; staging d006aa47) → **5 long tail in progress** (5.1a Company done; 5.1 group booking done 2026-09-24 (3 landings; 322 scenarios; staging fd74a805); 5.2 cron + HotelProfile done 2026-09-24 (staging 42ef30f3); 5.3 dashboard + reports done 2026-09-24 (staging 424f6139); 5.4 deposits + no-show done 2026-09-24 (staging d8da2b08); 5.5 print done 2026-09-24 (staging d96ba0c4); 5.6 polish done 2026-09-24 (every P row of ux.md §6; 371 green); 5.7 command coverage in progress (G14 landing 1 cancel booking done; slice-4 debts N21/N22 done, staging 23c4346e, 375 green; G14 landing 2 done, staging d4c4c896, 390 green; G15, G20, BookingSource, SetRoomType, G16, G22 done, staging a2476da4, 437 green; G28 done (439 green); G29 booking rules in progress, then G32 → G33 → G34 overbooking → G35 capacity (spec'd, product 847ff15) → G20 group grid → SetRoomType → G16/G22 → G28 defaultRouting → G29 → G32 routing table → G33 owner home + Needs attention); then 5.8 approvals → 1 occupancy loop → 2 setup min → 3 money → 4 roles/audit → 5 long tail. Alex reviews staging after 1 and 3; architect reviews every slice (`team/qa.md`) |
| WS2 existing system | solex-explore | **delivered** (map, flow board, lifecycle & money); on standby for 5 Alex-walkthrough items |
| WS3 product | solex-product | **v1 delivered** (D-12…D-19, §10–12); spec owner; **2026-09-24: UX wireframe by persona in progress** (`ux.md` + `diagrams/solex-ux.excalidraw`, Alex's ask) |

## Timeline

### Before 2026-09-19
- 2026-07-10 — Alex + Claude: hotel back office picked as the "Go at scale" learning project; discovery questions written; waiting on brain-dump.
- 2026-08-12 — existing-system URL + login accidentally pasted into the project doc in an unrelated commit.

### 2026-09-19 — setup day
**Alex:** named the project **SoLex**; set early direction (event sourcing, simple full-stack on Cloudflare, maybe Hookdeck); decided Go → **TS Workers** (D-3) after dev found Containers needed a paid plan; created three sessions and named them; asked for per-agent profiles, personal notes, shared team notes; supplied the client's requirements (Vietnamese); confirmed the `:99` system is the client's current PMS and that the rebuild is about **data ownership**, core subset + enhancements (D-4).
**Architect:** moved creds to gitignored `secrets/`, scrubbed git history (filter-repo + force push); rewrote the project doc; split into a directory with one owned file per workstream; translated requirements (`requirements.md`, raw copy in `client/`); built the agent system (`agents/<name>/README.md` profile + timestamped `notes/`, `team/` decisions·questions·log·protocol); wrote kickoff prompts; sent kickoffs; recorded D-1…D-4.
**Dev:** caught up; flagged wrangler auth + Containers paid plan; replanned for TS Workers + D1.
**Explore:** caught up; tooling check (curl, npx playwright); identified the PMS as ezCloud **ezFolio**; mapped nav.
**Product:** caught up; pre-interview aggregate sketch.

### 2026-09-20 — mapping day
**Alex:** slow walkthrough with explore; settled hard constraints — **no card data ever**, key cards out, two personas (manager + receptionist), group/company bookings core, stay rules are a change target; decided **fresh start, migration deferred** after explore found ezFolio's Excel export broken (D-5).
**Explore:** walked ~30 screens read-only (room map, tape chart, in-house, booking/folio editor, receivables, revenue, HK, guest history, money, audit, restaurant); found the real group-booking flow (availability engine, room-type × qty, late assignment); found channel typed into guest names, no rate plans, night audit off, admin screens permission-blocked; built a FigJam board; delivered `existing-system.md` v1 with a "For other WSs" section.
**Product:** reconciled its sketch against the map.
**Architect:** merged WS2 into README; explore → standby; 6 new questions (day boundary flagged as the decision that matters).

### 2026-09-21–22 — flows and the board
**Alex:** answered explore on hourly stays (not used), early/late fees (catalogue items, drop rate multipliers); named room map + tape chart as the two home screens.
**Explore:** individual booking flow (one form, two exits); named the tape chart / resource-timeline pattern; charges flow + config behind it (one charge shape, 8 buckets; item catalogues recovered from data; config split in two); FigJam hit Figma's 20-calls/month cap → wrote an **Excalidraw generator** (`tools/excalidraw/`).

### 2026-09-23 — closing discovery
**Alex:** closed the admin-login chase; declared **Setup/config its own scope with a third persona** (D-6); raised the **hotel day** problem (late arrivals should count as prior night) → configurable business date (D-7); set the agenda for the product session: schema → roles → actions/interfaces → rules → events; ran it with product (D-9, D-12…D-19); asked dev in-session for the ES skeleton + event browser + system console; proposed the Ledger context.
**Explore:** full Excalidraw board replaces FigJam (9 sections, 22 screens); four model-changing findings (group folio routing, two booking use cases, one charge shape, config split); Setup checklist; then answered architect's **10 lifecycle & money questions** read-only via the editor's endpoints: nightly posting confirmed, departure exclusive, debt-as-payment-method opens per-folio receivables, folios are constructed, deposit forfeit manual, cancel guards, no rate-change history. 5 items left for Alex walkthrough.
**Product:** `product.md` v0 (roles, contexts, 7 aggregates, events, invariants, cascade, scope, 8 policy points); v0.1 adds Setup context; then the **full session with Alex → v1**: event envelope, Booking/Stay naming, night-as-unit, money + a generic double-entry Ledger (Alex's idea), capability-based roles, three apps, screen inventory, §10 rules closed, §11 command catalogue, §12 event index.
**Dev:** Alex ran `wrangler login` and chose **TanStack Start**, local SQLite for dev, Cloudflare as build target only; dev shipped the spike — repo `alexluong/solex`, https://solex-stg.collie.studio (Workers + D1, $0), browser-verified on Node/SQLite, local workerd/D1 and deployed; recorded TLS one-label trap and SSR hydration tz bug; wrote the storage desk exercise → recommends D1 for log + projections with optimistic concurrency, no DO, Hookdeck deferred. Later same day, at Alex's in-session request, built the **ES skeleton**: events table, same-batch projections, replay, Room aggregate, multi-tenant from line one (D-9), `/system` console; 7 tests, browser-verified on D1.
**Architect:** merged each wave into README; queued 8 policy points; asked dev for a storage sanity-check (DO per hotel vs D1); reviewed the board and sent the 10 questions; recorded D-6, D-7; wrote the business-date model; set product's agenda; merged dev's spike → D-3 amended, D-8 proposed, product pinged to reconcile §6.

## Decisions so far
D-1 Go/no-VM/CF (superseded) · D-2 one owner per file · D-3 TS on plain Workers · D-4 rebuild for data ownership, core subset · D-5 fresh start, no migration · D-6 Setup scope + setup/admin persona · D-7 business date w/ configurable roll · D-8 D1 log + projections, no DO, Hookdeck deferred (built) · D-9 multi-tenant by design, one tenant · D-10 folded into D-12 · D-11 (proposed) auth · D-12 event naming + envelope (f: commandId replay in `commit`) · D-13 Booking v1 scope · D-14 Booking/Stay naming · D-15 night is the unit · D-16 money v1 · D-17 Ledger context · D-18 users/roles/apps · D-19 v1 screens · D-20 PII outside log · D-21 architect decides, Alex reviews · D-22 ES core (Booking/Stay/Ledger), event-notified CRUD for the rest · D-23 redact by column name · D-24 domain SDK `Hotel`, screens = tests · D-25 night posting = cron + lazy, idempotent · D-26 staging throwaway until production; architect may wipe, no third env · D-27 familiar over novel (ezFolio-shaped UX); VN wording iterates with client · D-28 approvals = request from the same button, owner grants in Needs attention (slice 5.8) · D-29 English is the working language; Vietnamese = product's translation pass. Full text: `decisions.md`.

## Flag for Alex
Moved to `mvp.md` §3 (known edge cases) and §4 (follow-ups) on 2026-09-25. Review artifacts: journeys player https://claude.ai/artifact/RrF94hDrGJ8QWPaecge4xN · ezFolio-shaped mockups https://claude.ai/artifact/L2ivkCzKDWwXoCFcmF6bKP.

## What Alex still owns
- Hotel-local time zone (rendering); staging auth before real data (`questions.md`)
- 5 explore walkthrough items (`questions.md`) — not blocking
