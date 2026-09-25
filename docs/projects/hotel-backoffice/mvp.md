# SoLex — MVP cut (2026-09-25)

**Goal (Alex 2026-09-25): a demo-able MVP, not a production-ready app.** This file is the entry point from here on: what the MVP is, what to demo, the edge cases we knowingly decided, and the follow-ups we are *not* building now. `product.md` / `ux.md` stay as the full spec; `team/progress.md` is history. Architect maintains; Alex prunes via architect.

State: **every v1 function in `product.md` §11 is built** (one exception: `ChargeItem` catalogue, §4) (dev, 2026-09-25, solex `2f61ef9`, staging `eef708e5`); QA suite fully green (desk 154 + receptionist 12 e2e); no open QA finding. Phase now = **demo prep + UX review**, not features.

## 1. Core (what the MVP is)

| area | built | demo-worthy |
|---|---|---|
| Setup | room types (capacity), rooms, rates by date range, charge categories + standard list, booking sources, companies (default routing), staff/roles, hotel profile (business date roll), house rules (auto-dirty, ID at check-in, overbooking mode) | yes — once, briefly |
| Front desk | room map (tiles, filters, quick panel), tape chart (free by type row), individual + group booking (mixed types × qty, assign later), check-in (guests, IDs, occupancy), check-out with settle dialog (pay / to company), extend/shorten nights, per-night rate, move stay, cancel, no-show, deposits | **yes — the walk-in and the group are the demo** |
| Money | ledger-backed folio, nightly room charge (cron + lazy), post charge, take payment, move line between bills, group routing table (who pays for what), void / reprice / refund / forfeit / write-off, receivables (company statement, payment, write-off), expenses, print (bill, receipt) | yes — bill + company debt |
| Approvals (5.8) | desk asks from the same button; owner approves from Needs attention; grant + act in one batch | yes — one round trip |
| People | guests + contacts (booker ≠ sleeper), edit details, guest's stays, erase with tombstone (D-20, PII outside the log) | short, if the audience cares about PII |
| Owner | dashboard, revenue / occupancy reports, Needs attention (aged debt, long OOO, unassigned arrivals, overstays, waiting approvals) + badge | yes — the "owner morning" |
| Histories | guest / booking / stay+folio (merged) / room, one sentence per event | short |
| System | `/system` console (events, replay, tables), redaction by column name | no (unless the audience is technical) |
| i18n | EN working language; **vi complete** (pass 3 landed solex `2f61ef9`, staging `eef708e5`, `i18n:report` clean) | demo can run in vi or en |

## 2. Demo script (proposed; QA films each as a showcase journey, D-30)

1. **R1 Desk walk-in** (exists, re-filmed on current screens): map → book → check-in → minibar → check-out refused with balance → cash → closed bill → print.
2. **R2 Owner morning** (exists): dashboard → revenue → owed → company statement → bank-transfer payment → tile → void a line.
3. **R3 Group + company** (new): company with default routing → group booking 3 doubles + 1 twin, assign later → tape chart free row → assign → routing table (dinner to company, minibar to guest) → check-out to company → receivables.
4. **R4 Ask the owner** (new): receptionist reprices a line → "Ask the owner" → owner's Needs attention card → approve → bill shows the reprice; then a refuse with reason.
5. **R5 House rules** (new, short): overbooking warn → override recorded; ID required refuses a check-in; capacity refuses 4 adults in a double.

Player: https://claude.ai/artifact/PnZfbQDz5dZdxxef5U8JFr (R1+R2 today; republish when R3–R5 land).

## 3. Known edge cases (decided under D-21; say if wrong, otherwise they stand)

- **Deposit forfeit is cautious**: every refund on a bill counts against how much deposit can be kept. Can refuse a forfeit the hotel was entitled to; never keeps money it no longer holds.
- **Refunds capped at payments actually received** on that folio minus refunds and forfeits, not at the credit balance (forfeit term added 2026-09-25, review B14).
- **Reports date rule**: a voided charge leaves the revenue of the day it was earned; a refund shows in cash on the day refunded; the ledger records the day a thing happened.
- **Discount = reprice**: no discount field; a lower price is void + re-post in one batch, both visible, `repricedFrom` links them.
- **Approval re-decided at grant**: if the act refuses at grant time (bill closed meanwhile), nothing is written, request stays open to decline.
- **Overbooking**: only the nights a command *adds* are checked; supply-side commands (OOO, retire, re-type) never refuse; `warn` mode default, override recorded on the command. **Override ("Take it anyway") is offered on the new-booking form only**; check-in early nights, extend, and adding rooms to a group refuse under `warn` too (ruled 2026-09-25: stays so for the MVP, follow-up §4). Demo the warn/override on a new booking.
- **Capacity**: adults ≤ type capacity, children (under threshold) never counted, no override (extra bed = charge item + bigger capacity). Check-in checks the *room's* type.
- **ID at check-in (required mode)**: one document per party is enough.
- **Room charge stays with the guest who slept the night** when a stay changes room/guest mid-way.
- **Group routing**: the table is read-only per cell; a column select changes rooms still on the default; a room's own exception is set on the stay's page, not in the table, and keeps its value; "As agreed" resets the column's default rows and does **not** clear a room's own setting (ruled 2026-09-25: keep as built, a room-level choice is never undone by a group-level tidy-up).
- **Needs attention is derived, never stored**: rows leave when the fact stops being true; nothing to dismiss. Debt aged from the oldest unpaid line.
- **First-owner bootstrap**: empty hotel lets a system operator act as owner until the first staff row exists.
- **Money role split**: receptionist posts/pays/transfers/moves lines/petty cash; owner alone voids, refunds, forfeits, writes off, voids expenses (desk asks via 5.8).
- **Business date**: configurable roll (default 02:00); late arrivals count as the prior night.

## 4. Follow-ups (tracked, not built now)

**Product / features**
- [ ] Cash handover / day close (G27) — needs the client conversation; candidate `CloseShift {cashCounted}`.
- [ ] Tape chart drag to move / extend (G11).
- [ ] Notifications leaving the app (Zalo/Telegram/email) — async cursor consumer over the log; badge is the only notification today.
- [ ] Booking search beyond name/phone/company; list filters (partly done in 5.6 — verify in UX review).
- [ ] OTA channels / commission logic (D-13 deferred); channel manager.
- [ ] VAT / red invoice (D-16 deferred).
- [ ] PA18 guest declaration export (legal? ask client).
- [ ] `ChargeItem` catalogue (Setup item with category + unit price; §11 Define/Update/Retire; folio line `itemId`) — spec'd v1, never built; free-text posting covers the demo.
- [ ] Seasonal / day-of-week rates, rate plans beyond date-range rates (§10 rule 9).
- [ ] Custom roles / editable capability bundles in Setup (§2 later).
- [ ] Guest merge duplicates + VIP class (§6 Guest later).
- [ ] Ghép đoàn / merge a stay into a group (`booking.stay_merged_in` reserved, §6).
- [ ] Receivable due dates (today aged by days only, §10 deferred).
- [ ] `ExpenseCategory` as Setup data (fixed in code; screen if the client asks).
- [ ] Migration from ezFolio (D-5 fresh start; DB export from ezCloud only if migration comes up).
- [ ] Native-speaker Vietnamese wording pass with the client (D-27/D-29); translation itself is complete. The `approvalKind.*` fragments composed at render are the first thing to check with them.
- [ ] Overbooking override on the other paths (check-in early nights, extend, add rooms to a group) — commands accept `override`, only the new-booking form sends it.
- [ ] Remaining §10 dials with no UI yet? — none known; confirm in UX review.

**From the 2026-09-25 code review** (`review/2026-09-25-analysis.md` has the routing; waves 1–2 are being fixed now, the rest are these)
- [ ] commandId scoping: ULID-only client ids, reserved `night:` prefix, lookup by hotel (B11).
- [ ] Projection rebuild atomic (shadow tables or write lock); OOO rooms' assigned demand counted in overbooking; booking span bound; last-owner race; move/reprice revenue dates; expense backdating; free-text notes as PII in the log; same-id double submit answering a refusal (B15).
- [ ] One ledger write helper; accounts opened in the same batch as the command (A1, A2 — M).
- [ ] Read models (room map, booking view, history) on `Hotel` with scenario tests (A4 — M).
- [ ] UI permissions by capability (`useCan`), not role name — prerequisite for custom roles (A5 — S).
- [ ] Split `setup.tsx` / `stays.$id.tsx` / `bookings.index.tsx`; `useFormCommand` helper (A6 — M).
- [ ] Typed event unions per context (A7 — L).
- [ ] Rename login "accounts" → users; schema files by context (A8 — S).
- [ ] Comment sweep: 7 orphaned JSDoc blocks, 4 stale facts, changelog narration (A9 — S).
- [ ] Drop `roomType` legacy shims before production (A10 — S); shared `CommandResult`, wire schemas home, hotel-scoped store, `Hotel` surface cleanup, split i18n en/vi, `FolioRef` union on the wire (A11–A15).

**Production hardening (not MVP)**
- [ ] Staging auth before real data; production environment (D-26 says staging is throwaway, no third env yet).
- [ ] Cloudflare 7403 flake on D1 migrate step (retry passes) — deploy token/step.
- [ ] Backups / export of the event log; restore drill.
- [ ] OIDC / password policy (D-11 later); session hardening review.
- [ ] Hotel-local time zone rendering confirmed (`HotelProfile.timeZone`, Asia/Ho_Chi_Minh presumably).
- [ ] Staff internet reliability at the hotel (no LAN fallback on Cloudflare).
- [ ] Onboarding script for a real tenant (D-9 seeding via script).

**Process / docs**
- [ ] Prune: fold `progress.md` "Flag for Alex" into §3 here (done 2026-09-25); retire `team/questions.md` items that are follow-ups (moved to §5); `ux.md` §6 gap list is closed except G11/G27.
- [ ] Big UX review after Alex's staging pass (his call on format: staging click-through vs rrweb journeys). Product's parked ux.md §4 screen redraws in the Stay-template format: dropped in favour of rrweb journeys (D-30) unless the review asks for drawings.

## 5. Open questions (for the demo / the client)

- Who is the demo audience — the client or Alex alone? (Language is no longer a gate; vi is complete.)
- Demo on staging with seeded data, or the journeys player only? (Staging seeding = throwaway, architect may wipe.)
- Cash handover: how does the desk hand cash to the owner today, and does the app need to record it (G27)?
- Do they keep the PA18 export today, and is it required?
- OTA bookings: manual entry with a source is enough for now?
- Which of ezFolio's ~60 booking-editor fields does reception really use? (Only matters for the UX review.)
- Timeline / urgency for a first real use.
