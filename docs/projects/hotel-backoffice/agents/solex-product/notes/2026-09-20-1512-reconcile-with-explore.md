# Reconcile aggregate sketch with explore's candidate core (D-4, D-5)

**Doing:** re-read `existing-system.md` (ezFolio map) + D-4/D-5. Revising my pre-interview sketch before Alex engages. Still no `product.md` — waiting.

## What explore settled (drop from interview)
- Users: **manager** (read-only dashboards/reports) + **receptionist** (does everything). Housekeeping off-system → room status is a reception action. Two roles, not three.
- Size: 58 rooms, ~50 in-house on a busy day, ~2/3 group/company. Receivables modest in VND, many debtors.
- Channels: manual today (suffix in guest name). Taxonomy OTA · TA · WALK-IN · CORP. Channel manager unused → manual entry, no sync. Commission is per booking (% or amount) today.
- Rates: no rate plans; typed per booking. Rate table = enhancement.
- Card data: never. Key cards: out. Restaurant POS, HK scheduling, multi-property: out.
- Migration: none (D-5). Model clean.
- Night audit off → day boundary rule is *ours* to decide.

## Revised aggregate sketch
- **Booking** (the hard one). Header: company?/contact, source channel, saler, display code/colour, deposit, confirmation/OTA ref, status. Body: `RoomTypeRequest[]` (type, qty, adults, children, rate/night, note) for dates [arrive, depart). Booking → N **RoomStay** (one per physical room-night span; guest list; own status BOOKED→CHECKED_IN→CHECKED_OUT | CANCELLED | NO_SHOW; room assigned or not). Walk-in = booking with one request qty 1, assigned immediately. Waiting list = RoomStays with no room.
  - Q for modeling: RoomStay as child entity inside Booking aggregate vs its own aggregate. Leaning **own aggregate** (check-in/out, room move, charges happen per stay; Booking is the commercial envelope). Invariant "no double assignment" then lives in a **Room-availability** check, not inside Booking → needs an ES-friendly answer (per-room stream, or reservation projection + optimistic check). Flag to dev/architect.
- **Room** (physical): housekeeping state VC/VD/OC/OD/OOO(+reason). Occupied/vacant derived from stays; clean/dirty/OOO are facts. Expected arr/dep = projection.
- **Folio** per RoomStay (or per Booking for group master folio — ezFolio has FolioID at booking level; group billing to company suggests **Booking-level folio w/ per-stay lines**). Charges: room nights, extras catalogue (breakfast, early/late, transfer, laundry, minibar, extra bed, damages, other) w/ qty/price/discount/tax/svc fee. Payments: cash/transfer/card-*method*(no card data)/deposit/prepaid/refund. Discount w/ approval trail. Balance = charges − payments.
- **Receivable**: at checkout, unpaid balance charged to a **Debtor** (company/OTA/TA) → open receivable w/ due date; settled by payments later. Own aggregate (lives past the stay). Debtor types: OTA / corporate / TA / group.
- **Company** (debtor + booking party): name, contact, type, default commission %, credit terms. Aggregate or master data — small, probably master data w/ events.
- **Guest** profile: reusable, mergeable, history count, class (normal/VIP). Merge = event. ID/passport data needed for PA18 → keep, no card.
- **Expense**: separate context, simple ledger (category, amount, date, who). Not in ezFolio; client wants it.
- Master data: RoomType, Floor, Room, Channel (+commission %), ExtraService catalogue, **RateTable** (room type × season/day-type — enhancement).
- Cross-cutting: every event carries actor → "Show log" for free.

## Remaining interview for Alex (short)
1. Group folio: bill company one invoice, or per room? Who pays what in a group (deposit vs per-guest extras)?
2. OTA commission: does the OTA collect and remit net (receivable from OTA) or hotel collects full and pays commission? Per-channel default % OK?
3. VAT / red invoice (hóa đơn đỏ) — in scope? Tax + service fee fields exist in ezFolio.
4. Day boundary / charge roll rule, early/late fees — decide now or later?
5. PA18 export — must keep? (legal)
6. Rate table shape: season × room type × day-of-week enough? USD secondary needed?
7. Cancellation/no-show charging policy per channel?
8. "Semi-professional": single hotel, receptionist-trusted, no approval workflows except discounts? Offline tolerance?
9. Dashboard "revenue today": by check-out (cash basis) or by night stayed (accrual)? Drives projections.

**Next:** when Alex engages → run the 9 above, then write `product.md` v1 and message architect with the aggregate list + the RoomStay/availability question.
