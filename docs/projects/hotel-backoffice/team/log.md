# Team log

Newest first. `YYYY-MM-DD — <agent>: what`.

- 2026-09-23 — product: N5/N6 ruled in product.md ef88dca (§10 6a/6b, StayNightsChanged, availability.changed in §12, mark_dirty reaction confirmed); dev told.
- 2026-09-23 — architect: slice 1 server side reviewed (83 green). B3 blocking: check-in must version availability (race w/ OOO). N5 early checkout / mark_dirty reaction, N6 assign OOO room → product + dev. `availability.changed` accepted; D-20 addendum (replay never touches PII tables).
- 2026-09-23 — product: §11a frozen (92cefea) + told dev; 5 forward-compatible widenings (booking kind union, requests.qty, stay nights.posted + guestIds, room.marked_dirty stayId?); all stream ids hotel-first in §6/§11a/§12.
- 2026-09-23 — architect: slice 1 machinery reviewed (upcast split, appendAcross); `<hotel>/availability:all` blessed; product to freeze §11a.
- 2026-09-23 — product: §6 aligned to D-12 amendment (actor text, tz) + diagram (6f63e4d). Standby for slice 1.
- 2026-09-23 — architect: slice 0 closed (ca19a48). D-12 amended: actor text column, upcaster fail-loud on fold path, commandId semantics, tz hardcoded TODO(D-7), hand-written migration. Dev → slice 1.
- 2026-09-23 — architect: N4 verified (rule refusals render; "disable only for no-op" rule in QA checklist).
- 2026-09-23 — architect: slice 0a B1/B2 fixes verified + local browser walkthrough green; N4 silent rule rejections → dev. Dev-user bypass accepted.
- 2026-09-23 — architect: slice 0a (Room flip) reviewed — 2 blocking (retry redecide; silent non-atomic fallback), 3 notes → dev. `team/qa.md`.
- 2026-09-23 — architect: review/QA loop added to protocol (Alex's ask); `team/qa.md` checklist; QA worktree `solex-qa` at origin/main, 19 tests green.
- 2026-09-23 — architect: Alex green light for rough end-to-end; slice plan 0–5 in dev profile rev 6; product on gap duty.
- 2026-09-23 — architect: Alex greenlit Room flip + staging log wipe ("i'll defer to you; staging is indeed throwaway data"). Relayed to dev.
- 2026-09-23 — dev: D-23 built (redaction.ts, PII cols in). Wipe of staging log waits on Alex's explicit yes, not architect's. Room flip waits on Alex greenlight.
- 2026-09-23 — architect: D-12 clarification — commandId UNIQUE for idempotency; money commands must be idempotent.
- 2026-09-23 — product: PII columns listed in §6 for D-23 denylist (1e7dfb5); role per (hotel,user) pair.
- 2026-09-23 — architect: dev landed D-11 auth (Better Auth, Alex-directed). Accepted: `system_operator` ≠ owner; User + staff = tier b w/ library-owned table; staging log wipe at Room flip (flagged); **D-23** redact by column name.
- 2026-09-23 — architect: D-8 clarification (reads never fold; one intent = one command = one batch; reactions inline once, projectors replayed). Product tagged §11 tiers (b9c1c28), OOO read confirmed.
- 2026-09-23 — architect: **D-22** (Alex) two tiers: ES for Booking/Stay/Ledger, CRUD+events for reference data. Room flips to tier (b). Dev + product pinged.
- 2026-09-23 — architect: **D-21** Alex delegates routine decisions to architect. D-11 (app-owned auth v1) + D-20 (PII outside log) accepted. Dev unblocked for Booking.
- 2026-09-23 — architect: D-20 (PII outside log) queued for Alex; D-11 revised lean = app-owned username/password v1, OIDC later (fits product's auth answers).
- 2026-09-23 — architect: product v1 merged; D-12…D-19 accepted (Alex's calls). D-10 (my payload-versioning) folded into D-12; D-11 auth stays Proposed. §10 Qs + tz Q closed. Product → standby/spec owner. Dev next: envelope columns, then Booking/Stay from §11. (Note: 3bf8996 was product's renumbering commit, landed under my message.)
- 2026-09-23 — architect: dev's ES skeleton merged (Alex-directed). D-8 accepted de facto; D-10 (payload versioning) + D-11 (auth) proposed; dev rev 4 = those two before Booking.
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
- 2026-09-23 — dev: console now follows the language picker too (was half VN / half EN — Alex caught it). Session notes + code map in stack.md, ready for a context compact. Open for me: D-10 on Alex's word, Booking waits on product v1 + D-11.
- 2026-09-23 — dev: i18n in (VN default + EN, server-resolved locale). Note for product: domain rule failures now return codes, not English sentences — keep that shape for new aggregates, it's what makes the UI translatable. VN wording needs a native pass.
- 2026-09-23 — dev: ES skeleton built and deployed (Alex asked for it directly, ahead of the standby in my profile). Event store w/ optimistic concurrency + same-batch projections + replay, Room as first aggregate, system console for browsing the log and every table, D-9 tenancy keyed in from the start. 7 unit tests, browser-verified on D1. `stack.md` updated. Console token in ctrl/secrets.
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

## 2026-09-23 · WS1 — authentication shipped (Better Auth), console token retired
Alex picked **Better Auth 1.7.5**, self-hosted, **username + password**. Built and deployed the
same session; `solex-stg.collie.studio` now signs in. Architect accepted under D-21, product's
D-18/D-20 answers arrived mid-build and changed one thing in flight (username sign-in for *all*
roles, email optional, no email dependency anywhere).

Shape: identity (`user`/`session`/`account`/`verification`) is **not** event-sourced — a password
hash must never reach an append-only log. Staff roles *will* be, once the staff aggregate lands,
because who-granted-whom-what is what an audit trail is for. `/system` gates on a
`system_operator` flag rather than a hotel role: system admin, not admin personas.

**`events.actor` is real now** — `user:<id>`, resolved to a display name at read time so history
stays true when a name changes. Events written before today still say `"reception"` and were left
alone. That was the point of the column.

Retired: the shared console token (`SYSTEM_CONSOLE_TOKEN` deleted from the Worker) and
`SYSTEM_CONSOLE_FALLBACK`, which made the console open locally and locked when deployed — a
dev/prod difference on an access-control path.

**Found and fixed a bug I introduced**: the console's table browser was printing live session
tokens and password hashes, which would have let an operator become another user. Redaction is by
column name so future tables are covered by default; `queries.test.ts` guards it. It is also the
strongest argument yet for dropping the generic table browser in favour of Drizzle Studio.

Worth knowing: Better Auth's scrypt costs ~80ms CPU, which **exceeds the Workers free tier's 10ms
limit entirely**. We are on paid, so it works. Checked before recommending, not after.

15 tests green (was 7). Notes: `agents/solex-dev/notes/2026-09-23-2130-auth.md`; design rationale
in `stack.md` §Authentication. Next per D-22: Room → CRUD tier, then D-12 envelope, then Booking.
