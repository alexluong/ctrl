# Team log

Newest first. `YYYY-MM-DD — <agent>: what`.

- 2026-09-23 — architect: D-9 (multi-tenant by design, one tenant) flipped to Accepted — Alex's call in product session. Dev FYI: hotelId on every stream/table.
- 2026-09-23 — product: D-8 availability-stream covers invariants iff every supply/demand command versions it in-batch; dropping DO from §6. Alex session live.
- 2026-09-23 — architect: dev spike merged. D-3 amended (TanStack Start, CF build target only). **D-8 proposed** (D1 log + projections, optimistic concurrency, no DO, Hookdeck deferred) — conflicts with product §6 DO; product pinged. Progress/README updated.
- 2026-09-23 — architect: explore's lifecycle/money answers merged into README. Exploration complete bar 5 Alex-walkthrough items. Product resumes after Alex confirms.
- 2026-09-23 — product: v0.1 (2e5789c) — Setup context (HotelProfile, Floor/RoomType/Room, RateTable, ChargeItem, ChargeBehaviour, Company, BookingRules). Waiting on Alex §10.
- 2026-09-23 — architect: D-6 recorded (Setup scope, 3 personas, admin login dropped). Product objective +0c.
- 2026-09-23 — explore: Alex closed the admin-login question. Setup/configuration becomes **its own scope with a third persona** (setup/admin: rooms + prices, item catalogues + prices, tax & service behaviour, booking rules) — WS3 designs it rather than reverse-engineering ezFolio's blocked masters.

- 2026-09-23 — architect: product v0 merged into README; 5 more policy points → questions.md (8 total); aggregates forwarded to dev for storage sanity-check.
- 2026-09-23 — architect: merged explore's 4 findings + Alex-settled items into README; 3 decisions queued in questions.md; product pinged (folio routing + charge shape affect aggregates).
- 2026-09-23 — explore: flow board delivered as `board/solex-flow.excalidraw` (gitignored; generator + spec committed under `tools/excalidraw/`). 9 sections, 22 screens, incl. **charges** and **admin config** which the FigJam board never got — Figma's Starter plan caps the MCP at 20 calls/month, so that board is frozen. Alex settled: hourly stays unused (daily only); early/late fees are catalogue items, not rate multipliers; room map + tape chart are the two hub screens for every role.
- 2026-09-20 — architect: WS2 reviewed + merged into README. Explore → standby. 6 new questions (day boundary is the one needing a decision). `.profile/` gitignored explicitly.
- 2026-09-20 — architect: D-5 recorded. Product objective updated for second pass on existing-system.md; group bookings flagged as the hard aggregate.
- 2026-09-19 — architect: D-4 recorded (PMS exists, data-ownership rebuild, core subset). Product objective updated. All 3 agents caught up.
- 2026-09-19 — explore: Alex: `:99` = the PMS the client uses now. Rebuild motive = data ownership; target = core subset + enhancements, not a feature-by-feature copy. WS2 = map it first, via a slow walkthrough with Alex.
- 2026-09-20 — explore: Alex: **rebuild starts fresh, migration deferred** — ezFolio's Excel export is broken (data-URL truncation) but that's not a blocker; data import handled later. Full UI map + group-booking flow now in `existing-system.md`.
- 2026-09-20 — explore: existing system = **ezCloud ezFolio** (Windows on-prem, Oracle, LAN-locked). ~20 screens mapped in `existing-system.md` w/ screenshots (gitignored). Key: no rate plans (rates typed per booking), channel manager present but unused (OTA channel typed into guest name), housekeeping module unused, night audit off, 58 rooms / ~96% occupancy today. Constraints from Alex: **no card data ever**, two personas (manager, receptionist), group/company bookings are core, key cards out of scope. Excel export path deferred.
- 2026-09-23 — dev: WS1 spike done. https://solex-stg.collie.studio live (TanStack Start + D1, $0). Repo `alexluong/solex` pushed. `stack.md` has the stack, the dev loop, latency, and the storage-shape take architect asked for. Two gotchas recorded: free TLS is one subdomain label deep, and staging is public with no auth.
- 2026-09-19 — architect: D-3 accepted (TS Workers, no Go). Dev profile objective rev 2. Containers/paid Q moot.
- 2026-09-19 — dev: caught up; blockers: wrangler login expired, Containers needs paid.
- 2026-09-19 — architect: project dir split, requirements translated, agents + team/ created. WS1/WS3 may start; WS2 waits on Alex for `:99` + workbook.

## 2026-09-23 · WS2 — lifecycle & money (architect's 10 Qs)
Answered `solex-architect`'s ten questions in `existing-system.md` §"Lifecycle & money — architect
Qs, 2026-09-23". Read-only throughout; the booking editor's money model came out of its own
`get_*` / `list_*` / `load_*` AJAX endpoints, which the guard already allows.

Settled: settlement is the `quickout` dialog (method/currency/card/bank per room-stay, methods
cash/card/transfer/FOC/**debt**); `Đóng` is the night audit closing a day's revenue, not folio
settlement; receivables are per-folio in `giveback_debit`, partial settlement supported, **no due
date**; **room charge posts per night with an `is_post` flag** so the in-house folio grows nightly
while the daily revenue report is occupancy × rate; **departure date is exclusive** so turnover days
aren't conflicts and `allow_over_room` is real overbooking; deposits are forfeited by hand as
service line 38; cancel is blocked once checked-in or once charges exist; no-show is a bare flag;
a master folio is just a folio holding several room-stays' lines, assembled with `Chuyển dịch vụ`.

Still open (need Alex's walkthrough, not probes): room-status transitions, how group rooms get
assigned, whether the OTA receivable is net of commission.

Board: fixed the TWO/THREE personas contradiction, added three money findings, rebuilt.
