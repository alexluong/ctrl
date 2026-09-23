# SoLex — progress & history

Narrative record of what the team (and Alex) has done, by day. `log.md` is the terse feed; this is the readable version. Architect maintains; append per milestone.

## Where we are (2026-09-23)

**Phase: discovery complete → product modeling.** Existing system fully mapped; client requirements translated; 7 decisions recorded; product v0.1 drafted and waiting for Alex's session on schema / roles / actions / rules / events. Dev spike blocked only on `wrangler login`.

| WS | agent | state |
|---|---|---|
| Cockpit | solex-architect | active — merging, deciding, routing |
| WS1 stack → ES skeleton | solex-dev | **skeleton live** — events + projections + replay, Room aggregate, `/system` console; **auth live (D-11)**; building rough end-to-end in slices (dev profile rev 6): **0 foundation done 2026-09-23** (wipe pending Alex) → **1 occupancy loop done 2026-09-23** (grid, booking form, stay page; 110 tests; architect walkthrough green) — **Alex: review on staging** → **2 setup minimum done 2026-09-23** (room types, rates, guests/contacts + erasure, staff/roles, Setup screens; 173 tests) → 1 occupancy loop → 2 setup min → 3 money → 4 roles/audit → 5 long tail. Alex reviews staging after 1 and 3; architect reviews every slice (`team/qa.md`) |
| WS2 existing system | solex-explore | **delivered** (map, flow board, lifecycle & money); on standby for 5 Alex-walkthrough items |
| WS3 product | solex-product | **v1 delivered** (D-12…D-19, §10–12); standby, spec owner |

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
D-1 Go/no-VM/CF (superseded) · D-2 one owner per file · D-3 TS on plain Workers · D-4 rebuild for data ownership, core subset · D-5 fresh start, no migration · D-6 Setup scope + setup/admin persona · D-7 business date w/ configurable roll · D-8 D1 log + projections, no DO, Hookdeck deferred (built) · D-9 multi-tenant by design, one tenant · D-10 folded into D-12 · D-11 (proposed) auth · D-12 event naming + envelope · D-13 Booking v1 scope · D-14 Booking/Stay naming · D-15 night is the unit · D-16 money v1 · D-17 Ledger context · D-18 users/roles/apps · D-19 v1 screens · D-20 PII outside log · D-21 architect decides, Alex reviews · D-22 ES core (Booking/Stay/Ledger), event-notified CRUD for the rest · D-23 redact by column name · D-24 domain SDK `Hotel`, screens = tests · D-25 night posting = cron + lazy, idempotent. Full text: `decisions.md`.

## Flag for Alex (decided under D-21, glance when convenient)
- **Open a `solex-qa` session** — profile + start prompt in `agents/solex-qa/README.md`; plan seeded in `qa/cases.md` (49 cases, slices 0–3).
- **Slice 3 money ready for your staging pass** (the checkpoint I said mattered most): Thiết lập → "Thêm danh sách chuẩn" for charge categories (once), a room type + rate → Đặt phòng (price prefills) → Nhận phòng (tonight's room charge appears on the bill by itself) → add a minibar line → Trả phòng (should refuse with the balance) → Ghi nhận thanh toán tiền mặt → Trả phòng closes the bill. Then look at the bill and tell me what a Vietnamese receptionist would find odd.
- **Slice 2 also ready for your staging pass**: Thiết lập → add a room type ("Phòng đôi"), a rate for a date range, then Đặt phòng and watch the price prefill; try a date outside the range (should refuse: "Chưa có giá cho một số đêm"); Khách & liên hệ → erase a guest, then check its history in Hệ thống shows `{}` payloads. Vietnamese copy is dev's.
- **Slice 1 ready for your staging pass** (see `qa.md` 2026-09-23 walkthrough for the exact clicks): sign in → Phòng (a room in service) → Đặt phòng with a room → Nhận phòng with a guest name → try a second booking on the same room/night (should refuse) → Trả phòng early → Lịch phòng + board. Vietnamese copy is dev's, skim it.
- D-11 auth: app-owned username/password v1, OIDC later; staging login before real data.
- D-20 PII outside the event log (id refs, tombstone erasure).
- D-11 built: Better Auth; `/system` gated by `system_operator` flag, separate from hotel `owner` role.
- Staging event log wipe at the Room flip: **Alex 2026-09-23 (architect session): "i'll defer to you; staging is indeed throwaway data, at least at the moment"** → wipe approved, Room flip greenlit. Relayed to dev.
- Refunds are capped at payments actually received on that folio, not at the credit balance (landing 2). Conservative; say if the client refunds credit notes differently.
- Money role split is now concrete (D-17 built note): receptionist posts charges, takes payments, transfers to receivable; owner alone voids, refunds, writes off, voids expenses. Product added move-line-between-folios and record-petty-cash-expense to receptionist. Say if you want the line elsewhere.
- First-owner bootstrap (landing C): an empty hotel lets a system operator act as owner until the first staff member is added, then never again. Narrow by design; re-read if it ever feels wrong.
- D-23: console/exports redact by column-name denylist after dev caught live session tokens rendering in `/system`.

## What Alex still owns
- Hotel-local time zone (rendering); staging auth before real data (`questions.md`)
- 5 explore walkthrough items (`questions.md`) — not blocking
