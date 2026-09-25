# SoLex — MVP cut (2026-09-25)

**Goal (Alex 2026-09-25): a demo-able MVP, not a production-ready app.** This file is the entry point from here on: what the MVP is, what to demo, the edge cases we knowingly decided, and the follow-ups we are *not* building now. `product.md` / `ux.md` stay as the full spec; `team/progress.md` is history. Architect maintains; Alex prunes via architect.

State: **every v1 function in `product.md` §11 is built** (dev, 2026-09-25, solex `8130240`, staging `e00bc289`); QA suite fully green (desk 154 + receptionist 12 e2e); no open QA finding. Phase now = **demo prep + UX review**, not features.

## 1. Core (what the MVP is)

| area | built | demo-worthy |
|---|---|---|
| Setup | room types (capacity), rooms, rates by date range, charge categories + standard list, booking sources, companies (default routing), staff/roles, hotel profile (business date roll), house rules (auto-dirty, ID at check-in, overbooking mode) | yes — once, briefly |
| Front desk | room map (tiles, filters, quick panel), tape chart (free by type row), individual + group booking (mixed types × qty, assign later), check-in (guests, IDs, occupancy), check-out with settle dialog (pay / to company), extend/shorten nights, per-night rate, move stay, cancel, no-show, deposits | **yes — the walk-in and the group are the demo** |
| Money | ledger-backed folio, nightly room charge (cron + lazy), post charge, take payment, move line between bills, group routing table (who pays for what), void / reprice / refund / forfeit / write-off, receivables (company statement, payment, write-off), expenses, print (bill, receipt) | yes — bill + company debt |
| Approvals (5.8) | desk asks from the same button; owner approves from Needs attention; grant + act in one batch | yes — one round trip |
| Owner | dashboard, revenue / occupancy reports, Needs attention (aged debt, long OOO, unassigned arrivals, overstays, waiting approvals) + badge | yes — the "owner morning" |
| Histories | guest / booking / stay+folio (merged) / room, one sentence per event | short |
| System | `/system` console (events, replay, tables), redaction by column name | no (unless the audience is technical) |
| i18n | EN working language; vi translated through pass 2; **92 keys still English** (dev handover `agents/solex-dev/notes/2026-09-25-vi-pass-3-handover.md`) | needed if the demo is in Vietnamese |

## 2. Demo script (proposed; QA films each as a showcase journey, D-30)

1. **R1 Desk walk-in** (exists, re-filmed on current screens): map → book → check-in → minibar → check-out refused with balance → cash → closed bill → print.
2. **R2 Owner morning** (exists): dashboard → revenue → owed → company statement → bank-transfer payment → tile → void a line.
3. **R3 Group + company** (new): company with default routing → group booking 3 doubles + 1 twin, assign later → tape chart free row → assign → routing table (dinner to company, minibar to guest) → check-out to company → receivables.
4. **R4 Ask the owner** (new): receptionist reprices a line → "Ask the owner" → owner's Needs attention card → approve → bill shows the reprice; then a refuse with reason.
5. **R5 House rules** (new, short): overbooking warn → override recorded; ID required refuses a check-in; capacity refuses 4 adults in a double.

Player: https://claude.ai/artifact/PnZfbQDz5dZdxxef5U8JFr (R1+R2 today; republish when R3–R5 land).

## 3. Known edge cases (decided under D-21; say if wrong, otherwise they stand)

- **Deposit forfeit is cautious**: every refund on a bill counts against how much deposit can be kept. Can refuse a forfeit the hotel was entitled to; never keeps money it no longer holds.
- **Refunds capped at payments actually received** on that folio, not at the credit balance.
- **Reports date rule**: a voided charge leaves the revenue of the day it was earned; a refund shows in cash on the day refunded; the ledger records the day a thing happened.
- **Discount = reprice**: no discount field; a lower price is void + re-post in one batch, both visible, `repricedFrom` links them.
- **Approval re-decided at grant**: if the act refuses at grant time (bill closed meanwhile), nothing is written, request stays open to decline.
- **Overbooking**: only the nights a command *adds* are checked; supply-side commands (OOO, retire, re-type) never refuse; `warn` mode default, override recorded on the command.
- **Capacity**: adults ≤ type capacity, children (under threshold) never counted, no override (extra bed = charge item + bigger capacity). Check-in checks the *room's* type.
- **ID at check-in (required mode)**: one document per party is enough.
- **Room charge stays with the guest who slept the night** when a stay changes room/guest mid-way.
- **Group routing**: column select changes rooms still on the default; rooms set individually keep their override; "As agreed" clears the column.
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
- [ ] Seasonal rates / rate plans beyond date-range rates.
- [ ] Migration from ezFolio (D-5 fresh start; DB export from ezCloud only if migration comes up).
- [ ] Vietnamese pass 3 (92 keys) + a native-speaker wording pass with the client (D-27/D-29).
- [ ] Remaining §10 dials with no UI yet? — none known; confirm in UX review.

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
- [ ] Big UX review after Alex's staging pass (his call on format: staging click-through vs rrweb journeys).

## 5. Open questions (for the demo / the client)

- Who is the demo audience and language — the client (vi) or Alex alone (en)? Decides whether vi pass 3 is a gate.
- Demo on staging with seeded data, or the journeys player only? (Staging seeding = throwaway, architect may wipe.)
- Cash handover: how does the desk hand cash to the owner today, and does the app need to record it (G27)?
- Do they keep the PA18 export today, and is it required?
- OTA bookings: manual entry with a source is enough for now?
- Which of ezFolio's ~60 booking-editor fields does reception really use? (Only matters for the UX review.)
- Timeline / urgency for a first real use.
