# Prep for the Alex session: lifecycle & money findings folded into my head, not yet product.md

Architect: exploration done; don't start v1 until Alex comes. Agenda: 1 schema · 2 roles · 3 actions/interfaces · 4 rules/policy (+ hotel day) · 5 events shape. Decisions → team/decisions.md as Proposed.

## What explore's lifecycle findings change in v0.1
- **Nights, not dates.** Stay = business dates [arrival_bd, departure_bd); departure exclusive. Double booking = overlapping nights. My invariant text already used [arrive, depart) — good, but rename to business dates.
- **Hotel day / business date** replaces "day boundary". `businessDayStart` config (~02:00–05:00, client to confirm). Night N posts at roll (or at check-in for the current night). Posted nights immutable. Nights *charged* derived from actual check-in/out timestamps + thresholds; typed dates = plan. Mismatch → events (`EarlyCheckInCharged`, `LateCheckOutCharged`, `ExtraNightPosted`). Resolves §10.1: room revenue = posted; "revenue today" must say posted vs occupancy×rate.
- **Price change is an event** (`StayRateSet(date, amount, reason)`) — already have it; add: cannot target a posted night.
- **Settlement**: no payment screen in ezFolio; checkout dialog one method per stay; debt = method that opens a receivable. Rebuild: separate *settle* (method, amount) from *remainder → Receivable*. Partial settle at checkout falls out. Keep my model; note split by folio is unnecessary since Payment already has amount.
- **Receivable grain = folio**, no due date today. I proposed dueDate from Company.paymentTerms — keep as enhancement; overdue = age otherwise.
- **Folio is constructed**: lines can move between folios (`ChargeMoved(from, to)`); routing switches = automatic version. Add `ChargeMoved` event; master folio = folio carrying lines from many stays. Naming trap: ezFolio "FolioID" = reservation id.
- **Deposit**: a payment of kind deposit (my model) + cached total; forfeit on cancel = manual charge today → rebuild: `DepositForfeited` event posting to a `compensation`/`other` bucket line, or refund path (`PaymentRefunded`) — ezFolio has neither.
- **Cancel guards**: not if checked in; charges must be moved off first; reason mandatory. No-show = flag. Adopt guards as invariants. Groups cancel per stay.
- **Waiting list unused in practice** — rooms assigned at booking; keep late-binding in model but default UX assigns immediately (`lay_phong_can_ngay`-ish auto-assign as option).
- **Room move doesn't reprice**; extend regenerates unposted nights only. Matches.
- **OTAs are debtors**: guest pays channel, hotel bills OTA; gross vs net open (§10.5).
- Every status verb per room-stay → partial arrivals/departures normal. Matches RoomStay-as-aggregate.

## Section plan for v1 (drive with Alex, agenda order)
1. Schema: walk aggregates + fields; confirm Booking/RoomStay split, Folio own/master, Receivable grain.
2. Roles: 3 personas, what each can do (table).
3. Actions/interfaces: command list per persona × screen (room map, tape chart, booking form, checkout dialog, setup).
4. Rules: hotel day (business date model), overbooking, ID, OTA basis, cancel/no-show, group routing default, VAT, deposit forfeit/refund.
5. Events shape: event vs state; per-aggregate streams; actor/time envelope; single-writer per hotel.

**Next:** wait for Alex.
