# SoLex correctness review (reviewer B), 2026-09-25

Scope: solex `9b30ff9` (= `2f61ef9` + e2e/style). Dimension: correctness only (money, availability, concurrency, auth, PII, projections, dates, input). Style/organisation is reviewer A's. Method: read every command path end to end (`src/server/hotel/*`, domain rules, store/log, projections, API adapters, auth/session). Suspected bugs were reproduced with throwaway `vitest` scenarios run in a scratch copy of the repo; the repo itself was not touched. Baseline: unit suite 517/517 green.

**CONFIRMED** means a scenario reproduced it, or the code path is short and unambiguous and I traced all of it. **PLAUSIBLE** means I could not trigger it deterministically.

## 1. Overall assessment

The core is well built. Every ledger entry is checked to balance, a folio's balance is always the sum of its lines (never a stored running total), and every command re-reads and re-decides on each retry. The `commandId` dedupe works, including for the night roll (the cron, the lazy roll and check-in are safe to fire at the same time). Replaying the log gave the same folios and nights in every scenario I tried. The bugs are mostly in the **rules around the edges of a stay**, not in the ledger. They lead to real wrong money in common hotel situations:

- a guest who checks out a day early is charged for, and still holds, the night they did not sleep;
- repricing an earlier night re-bills it;
- checking out with the guest in credit locks the credit away where it cannot be refunded;
- moving an in-house guest rewrites the nights they already slept.

All four are in the paths the demo walks, or next to them.

**Before the demo:** fix #1–#4, and avoid voiding a room line of an in-house guest (#8) until that behaviour is decided.

**Before real use**, also:
- gate the read side by role (#5);
- stop an owner from taking over the system operator account (#6);
- version availability on group demand (#7);
- make approval refunds carry the payment method (#10);
- tighten transfer-to-receivable (#9);
- scope `commandId` (#11).

The concurrency design (D-8/D-12) holds. The concurrency holes I found are in places that skip it: group creation, opening accounts lazily, and the approval grant's precomputed append.

## 2. Findings (ranked)

### #1 Early check-out charges and keeps the departure-day night (high, CONFIRMED)
- **Where:** `stay/domain.ts:620` (`firstFreed = addDays(businessDate, 1)`), `hotel/night.ts:142` (the roll posts every night `<= today`), `hotelDay.ts:31` (default roll hour 0).
- **Scenario:** Booking 23→25 (2 nights), check-in 23rd. On the 24th at 10:00 the guest leaves. The cron/lazy roll has already posted night 24 (at 00:00 by default, 02:00 with the configured roll). Check-out removes nights from the 25th onward only. Result: balance 1,300,000 instead of 650,000, and night 24 stays held by a checked-out stay. Rebooking that room for tonight is refused with `stay.roomTaken` (reproduced). The desk has to collect money for a night not slept, or get the owner to void it, and the room still cannot be sold tonight.
- **Conflict with the spec:** D-7's own formula says nights = business dates in `[arrival_bd, departure_bd)`, which excludes the 24th. §10 6a's "current night stays charged" reads as the opposite. This needs a one-line product ruling.
- **Fix direction:** at check-out, if the time is before `checkOutTime` (or before the evening), treat the current business date as the departure date. Free it and reverse its room charge in the same batch. Alternatively, switch the roll to post the night that just ended (night-audit style) and have check-in post tonight.

### #2 Repricing a past room night re-bills it (high, CONFIRMED)
- **Where:** `hotel/folios.ts:590` (the reposted line gets `ctx.businessDate()`, not the original night's date), `store/folio.ts` voided-charge projector (un-posts the original night), `night.ts:48-78` (`roomChargeExists` is keyed by `(stay, businessDate)`).
- **Scenario:** In-house stay 23→25. On the 24th the owner reprices night 23 from 650k to 500k (the only way to give a discount). The void un-posts night 23, and the new 500k line is dated the 24th. The next roll (hourly cron) finds night 23 "unposted" and posts 650k again. Balance goes 1,150,000 → **1,800,000** (reproduced). The discount becomes a surcharge, and the revenue report moves 500k onto the wrong day.
- **Fix direction:** repost with the original charge's `businessDate` (the reversal can stay dated today), at least for the `room` category. Add a test that reprices a past night and then rolls.

### #3 Check-out in credit closes the folio and strands the credit (high, CONFIRMED)
- **Where:** `stay/domain.ts:618` (`folioBalance <= 0`), `hotel/stays.ts:510` (emits `folio.closed` + `ledger.account_closed` with no zero check; `decide.closeAccount`'s `balance === 0` rule is bypassed).
- **Scenario:** Deposit 1,000,000 on a 650,000 stay → balance −350,000. Check-out succeeds and closes the account at −350,000. A refund is then refused with `ledger.accountClosed` (reproduced). The guest's change can no longer be recorded, and a closed account now carries a balance, which breaks the "account closes only at 0" rule.
- **Spec:** "own folio 0 or moved to a receivable". `CloseBooking` already requires `=== 0` for the master folio.
- **Fix direction:** refuse with `stay.folioInCredit` (so the settle dialog offers the refund), or refund and close in one batch.

### #4 Moving an in-house guest rewrites slept/posted nights and tests past nights (high, CONFIRMED)
- **Where:** `hotel/stays.ts:124` (`from = input.fromDate ?? state.arrive`), the UI's "Move room" (`routes/stays.$id.tsx:143`), which never sends `fromDate`, the `stay.room_assigned` projector (`store/projections.ts`, `date >= fromDate`), and `stays.ts:137` (`roomServiceable: true`).
- **Scenario:** A is in 201 from the 23rd. On the 24th the desk moves A to 202, which is free from tonight but held another guest on the 23rd. The move is refused with `stay.roomTaken`. Moving A to 203 succeeds, and every night including the posted 23rd now says room 203 (reproduced). The room history, the tape chart and occupancy-by-room are all rewritten, and 201 is never marked dirty.
- **Also:** an in-house guest can be moved into an out-of-order room (check-in refuses that), and `roomId` is never checked to exist.
- **Spec:** D-15 and §11 `MoveStay` say unposted nights from a date, with posted nights immutable.
- **Fix direction:** for `checkedIn` stays, default `fromDate` to today and refuse if `fromDate` is before today or any affected night is posted. Refuse an out-of-order target for tonight, check the room exists, and mark the old room dirty.

### #5 The read side has no role gate: a former staff member can read all guest PII (high for real use, low for the demo; CONFIRMED)
- **Where:** `hotel/current.ts:80-101` (a `role: null` user gets a full `Hotel`), and read server functions such as `api/people.ts:50` `getPeople`, `api/folio.ts` `getFolio`, `api/users.ts:47` `getAccounts`, `getUserHistory`, bookings and calendar. None call `ctx.must`. Only the UI hides the links (`__root.tsx`).
- **Scenario:** Per D-18, `staff.deactivate` ends sessions but the person keeps the login. They sign in again, get `role: null`, and call `getPeople` → names, phones and ID numbers of every guest. The same works for any account with no membership. Receptionists can call `getAccounts` (usernames, e-mails, operator flags), which the UI treats as owner-only.
- **Fix direction:** refuse every read in `currentHotel()` when `role === null` (bootstrap excepted), and put `ctx.must("users.manage")` on the account reads.

### #6 An owner can reset or rename any account, including the system operator's (med, CONFIRMED by reading)
- **Where:** `hotel/users.ts:88-160` (`update`, `resetPassword`). Neither checks that the target is staff of this hotel or is not `systemOperator`. `users.list()` is global.
- **Scenario:** The owner resets Alex's operator password, signs in as the operator, and gets `/system` (the raw log, rebuild). D-11 says owner and operator "neither implies the other". With more than one hotel, an owner could also take over another hotel's users.
- **Fix direction:** refuse when the target has `systemOperator` or has no membership in `ctx.hotelId`.

### #7 Group create and "add rooms" don't version the availability stream, so concurrent group sales oversell silently (med, CONFIRMED)
- **Where:** `hotel/bookings.ts:278` (versions availability only `if (roomId)`), `bookings.ts:502` (`changeRequests` versions only when stays are removed).
- **Scenario:** One double left. Two desks create 1-double groups at the same moment. Both pass `guardOverbooking` and both commit. `freeByType` shows −1, and no `stay.overbooking_overridden` is recorded (reproduced). This breaks D-8's condition that every demand-changing command versions availability.
- **Fix direction:** always append `availability.changed` when stays are created or added.

### #8 Voiding an in-house room night is silently undone within the hour (med, CONFIRMED)
- **Where:** the voided-charge projector un-posts the night, and `night.ts` plus the hourly cron (`wrangler.jsonc` `0 * * * *`, `server-entry.ts`) repost it.
- **Scenario:** In the R2-style demo, "void a line" on a room charge of a checked-in guest. The line comes back at the full rate on the next cron tick or new Worker instance. D-25 intended this ("a voided night can re-post"), but nothing tells the owner, and a comp done by void quietly reverts.
- **Fix direction:** refuse void on `room` lines of in-house stays (point to reprice instead), or say "will re-post at the roll" on the confirm. Also include this in the demo script notes.

### #9 Transfer-to-receivable has no cap and no company check (med, CONFIRMED)
- **Where:** `hotel/folios.ts:891` (`amount = input.amount ?? balance`, no `amount <= balance`); `api/folio.ts` `transferInput.amount` is optional ≥ 0; `companyId` is any string.
- **Scenario:** The settle dialog lets the desk type an amount (`ui/settle.tsx:169`). Transferring 9,650,000 on a 650,000 bill leaves the folio at −9,000,000 and the "company" `nobody-inc` owing 9,500,000 (reproduced). A typo creates debt, and a credit folio can then be refunded in cash.
- **Spec:** §11 says "amount ≤ balance".
- **Fix direction:** refuse when `amount > balance`, and require the company to exist and not be retired.

### #10 Approval refunds always pay out in cash, and requests skip the underlying rules (med, CONFIRMED)
- **Where:** `hotel/approvals.ts:125` (`method: "cash"`); the request payload has no `method` (`api/approval.ts`, `ui/folio.tsx:169`, which drops the method the desk picked). `approvals.request` checks only kind, reason and "one open per subject", not "subject exists and open" or "refund ≤ payments" (§11).
- **Scenario:** The guest paid by bank transfer. The desk asks for a 150k refund by transfer, the owner grants it, and the ledger credits **cash** (reproduced). The cash drawer is 150k short at hand-over.
- **Related:** open requests expire only at check-out, not on `CloseBooking` or when a receivable settles (§11 reaction). `openFor({stayId})` also matches any open void on the same stay, so a pending void blocks a refund request (`approval.alreadyOpen`).
- **Fix direction:** carry `method` in `approval.requested` and run the underlying rule checks at request time. Add the missing expiries.

### #11 A client-chosen `commandId` can suppress a night's room charge (med, CONFIRMED)
- **Where:** `night.ts:45` (deterministic `night:<stay>:<date>:<n>`), `store/log.ts:175-187`/`243-246` (lookup by `command_id` alone: not by hotel, actor or type), and `commandId` accepted as any 1–64 character string (`api/*`).
- **Scenario:** Any staff member sends a cheap command (for example mark room dirty) with `commandId = "night:<stayId>:<tomorrow>:0"`. Tomorrow's roll finds that id "already done" and reports `posted: 1`, but nothing is charged. Night 24 stayed unposted in the reproduction. This is unbillable nights with no trace that looks like fraud.
- **Fix direction:** require client ids to be ULIDs (or prefix them per actor), reserve the `night:` prefix server-side, and scope the lookup by hotel. Also check that the returned events are of the expected type.

### #12 Cancelling a group fails once any room was a no-show or checked out (med, CONFIRMED)
- **Where:** `hotel/bookings.ts:541-549` calls `stayDecide.cancel` on **every** stay; `stay/domain.ts:655` throws `stay.notCancellable` for anything but `booked`/`cancelled`.
- **Scenario:** A 2-room group, one room marked no-show, the rest called off. `CancelBooking` is refused with `stay.notCancellable` (reproduced). The desk has no way to cancel the group.
- **Fix direction:** skip terminal stays (`noShow`, `checkedOut`) in the loop. `bookingDecide.cancel` already guards the checked-in case.

### #13 First-owner bootstrap can lock the hotel out of owner functions (med, CONFIRMED by reading)
- **Where:** `auth/session.ts:57,86` (bootstrap ends at the first `hotel_staff` row, whatever its role); `staff/domain.ts:222` (`add` allows any role first).
- **Scenario:** On a wiped staging (D-26), the operator's first hire is a receptionist. Bootstrap ends, there is no owner, and nobody holds `users.manage` or `setup.edit`. Recovery needs direct DB access.
- **Fix direction:** refuse `staff.add` of a non-owner while the hotel has no active owner, or keep bootstrap open until an active owner exists.

### #14 A refund can hand back a deposit the hotel already kept (low–med, CONFIRMED)
- **Where:** `folio/domain.ts:383`, where the refund cap `refundable` = payments − refunds and ignores forfeits.
- **Scenario:** No-show, deposit 1,000,000, forfeit 600,000, then refund 1,000,000. The refund is accepted, and the no-show folio now "owes" 600,000 with forfeit revenue still booked (reproduced). This is the mirror image of mvp §3's "never keeps money it no longer holds". It is literally within the "capped at payments" ruling, so it needs flagging, not overriding.
- **Fix direction:** on terminal stays, cap the refund at the credit balance, or subtract live forfeits.

### #15 Lower-severity holes (grouped)
- **Money commands decide before reading stream versions (PLAUSIBLE).** `folios.ts:176`, `receivables.ts:61`: `decide()` reads the projections first, then `states` folds the versions. A write that lands between them is appended at the new version against a stale decision (for example two refunds or two receivable payments slipping past the cap). The ~ms window is widened by the `ensure*` round trips inside `decide`. Not reproduced (the race test held). Fix: read the account versions first, as `checkOut` already does.
- **Lazy account opening races (CONFIRMED).** Two first payments on a fresh folio at once: the second fails with the internal `ledger.accountExists` code (`hotel/ledger.ts` `ensureAccount` → `openAccount`). Fix: make `openAccount` a no-op when the account exists.
- **Charges on a ghost or finished stay (CONFIRMED).** `postCharge`/`takePayment` accept a nonexistent `stayId` and open `folio:ghost` (`folios.ts:296`), and never check stay status. `CancelStay` ignores the "charges moved off first" rule.
- **D-25 roll-hour guard not built.** Changing `rollHour` while tonight is unposted is not refused (`hotel/setup.ts:564`). The default roll is 00:00 (`hotelDay.ts:31`), not the 02:00 in mvp §3, so a 01:00 walk-in counts as today on a hotel with no profile row.
- **Rebuild is not atomic (PLAUSIBLE).** `store/log.ts:285` truncates the tables, then replays one statement at a time. Commands running meanwhile decide against empty tables (balance 0 → check-out passes, `roomFree` true). On D1, per-invocation query limits could stop a large rebuild midway and leave the tables truncated. Fix: rebuild into shadow tables and swap, or lock writes during the rebuild.
- **Out-of-order rooms hide their assigned demand (CONFIRMED by reading).** `freeByType` (`availability.ts:63`) drops nights assigned to a currently out-of-order room from demand as well as supply, so the overbooking check undercounts by the number of guests who still need moving.
- **Unbounded stay length.** `arrive`/`depart` have no bound (for example depart 2062 × qty 50 × 20 requests) → a huge batch or a Worker timeout. Nights can also be added before `arrive` on in-house stays, and the roll then back-posts them.
- **Last-owner guard not serialised (PLAUSIBLE).** It reads other staff rows outside their streams; two owners deactivating each other at once can leave zero owners.
- **Revenue dates.** `moveCharge` and `repriceCharge` book the new entry today, so moving yesterday's minibar line moves yesterday's revenue to today. Receptionists can backdate or future-date expenses (`businessDate` is client-supplied).
- **PII in the permanent log (CONFIRMED by reading).** `booking.created` / `booking.notes_changed` carry free-text `notes` (`booking/domain.ts:230`), and the `/system` event browser and the `events` table view don't redact payloads (`system/queries.ts`). Guest names and phones typed into notes can never be erased, which works against D-20. Void/approval reasons and charge descriptions have the same exposure, to a lesser degree.
- **Same-id double submit can read as a refusal (PLAUSIBLE).** `handleAcross` checks the `commandId` once before the loop. A same-id request that reaches `plan()` after its twin committed runs the rules and can answer `alreadyVoided` instead of the original success (S1 held in my interleaving). Fix: on a `RuleError` with a `commandId`, re-check `eventsOfCommand` before throwing.

## 3. Invariants checked and found holding

- **Ledger:** every entry is checked Σ = 0 with safe-integer lines (`checkBalanced`). Folio, receivable and cash balances are always Σ lines, never stored. Undo is always a reversal entry. A closed account refuses postings (`ledger.accountClosed`); #3 is the only bypass.
- **Replay:** rebuilding gives an identical folio statement and nights after check-in + roll + reprice + payment (reproduced), and existing tests agree. Rebuild excludes `guests`/`contacts`/tier (b) tables, so an erased person stays erased.
- **Idempotency:** a same-`commandId` double void and double post-charge in flight produce one set of events (reproduced). The night roll fired four ways concurrently posts once (existing test). The `commandId` sits on the first event of the whole command.
- **Retries** re-run `plan()` against fresh state everywhere I looked, except the approval grant's precomputed append. That fails safe: on a clash the grant throws and nothing is written.
- **Approvals:** grant + act are one batch (`also` stream); the act re-decides at grant; a refused act writes nothing and leaves the request open (§3). A double grant is prevented by the approval stream version plus the act's own rule.
- **Overbooking:** only the nights a command adds are checked; supply-side commands (out-of-order, return to service, `SetRoomType`) never refuse but do version availability; an override needs the flag, and `stay.overbook` under `warn`; `refuse` ignores the flag; the override is recorded per type (§3, G34).
- **Per-room double hold** is a hard `stay.roomTaken` at create, assign, check-in early nights and `ChangeNights`, decided under the availability version. Check-in and out-of-order serialise on the availability stream.
- **Capacity:** adults ≤ capacity at create, requests, `SetOccupancy` and check-in (against the **room's** type); children not counted (§3).
- **ID at check-in:** one document per party is enough (§3).
- **Posted nights** are immutable for `SetNightRate` and `ChangeNights`. A late arrival drops only unposted earlier nights; an early arrival adds nights at the first night's rate.
- **The room charge stays with the guest who slept the night:** `moveCharge` refuses a room line to another stay's folio but allows master ↔ own stay (§3).
- **Report dates:** a voided charge leaves revenue on its earned day (`coalesce(reversed.businessDate, …)`); refunds show on the day refunded (§3).
- **Forfeit cap** = deposits − refunds − forfeits, allowed only on cancelled or no-show stays or a cancelled group's master (§3). Refunds are capped at payments (§3; see #14).
- **Discount = reprice:** void + repost in one batch with `repricedFrom` (§3). #2 is about the repost's date, not the mechanism.
- **Every write command calls `ctx.must`** server-side. The owner-only money acts (void, reprice, refund, forfeit, write-off, expense void) are not in the receptionist bundle; `/system` rebuild requires `systemOperator`; a `system` room charge can't be forged through the API because zod strips `system`.
- **Tenancy:** every projection or tier (b) query filters by `hotelId`. The exceptions are the auth tables (global by design) and the `commandId`/correlation lookups (#11).
- **D-20:** `guest.*` and `contact.*` payloads are `{}` or field names only; ids only in stay and booking events (notes excepted, #15). `/system` table browsing redacts by column name.
- **Dates:** business dates are computed via `Intl` in the hotel zone; the UI formats `LocalDate`s in UTC (no off-by-one); timestamps use the hotel zone. The dev bypass is compiled out of the Cloudflare build.

## 4. Test coverage gaps worth adding

- [ ] Early check-out the morning after: balance and room availability for tonight (#1)
- [ ] Reprice a *past* room night, then roll: balance unchanged by the roll (#2)
- [ ] Check-out with a credit balance: refused, or refund + close in one batch (#3)
- [ ] Move a checked-in guest mid-stay: posted nights keep their room; target busy only in the past is allowed; out-of-order target refused (#4)
- [ ] `role: null` user calling each read server function gets `auth.forbidden` (#5)
- [ ] Owner `resetPassword` on a system operator / non-member refused (#6)
- [ ] Two concurrent group creates for the last room: one refused (#7)
- [ ] Void of an in-house room night, then cron: the documented outcome asserted (#8)
- [ ] Transfer amount > balance refused; unknown company refused (#9)
- [ ] Approval refund by bank transfer: ledger hits `bank` (#10)
- [ ] Crafted `night:`-prefixed `commandId` refused (#11)
- [ ] Cancel a group with one no-show stay (#12)
- [ ] First staff row must be an owner (#13)
- [ ] Refund after forfeit on a no-show (#14)
- [ ] Concurrent first payment on a fresh folio: both succeed (#15)
- [ ] Refund/receivable race with the version read before the projection read (#15)
- [ ] Rebuild while a command is in flight (or behind a write lock) (#15)
- [ ] Booking span upper bound; `ChangeNights` adding nights before `arrive` on an in-house stay (#15)
- [ ] Out-of-order room with an assigned future stay counts in the overbooking check (#15)
