# R2 — Owner morning

**Purpose:** the owner's daily check: what happened, who owes money, and fixing a wrong line with a trace.
**Persona:** Oanh, owner.
**Seed used:** Blue Sea Travel Co. owes one night (Pham Quoc Bao, 201); room 103's bill has "Laundry (wrong room)".
**Length:** 0:54. File `R2-owner-morning.webm`.

| # | Step (caption) | Notice |
|---|---|---|
| 1 | Dashboard | Today at a glance: occupancy, arrivals, what was sold, and the Needs attention list. |
| 2 | Revenue report | Revenue by category and by payment method. |
| 3 | Who owes money? → Blue Sea's statement | Outstanding per company, and the lines behind it. |
| 4 | Record the bank-transfer payment, with its reference | The company's balance goes to 0. |
| 5 | Room 103 via map → panel → stay | Three clicks from the map to a guest's bill. |
| 6 | Void the wrong laundry line, with a reason | The reason is required. The line stays, struck through with the reason, and leaves the total. |
| 7 | The stay's history | Booked, checked in, every bill line: who did it and when. |
| 8 | Room 103's own page | Who is in it tonight, the next arrival, housekeeping, and the room's own change log. |

The line voided here is laundry, never a room night (see Do not demo in the README).

## In ezFolio today

The owner's morning is spread over reports and the desk's editor (`existing-system.md` § 06–08, § receivable lifecycle, § mid-stay changes).

1. "How full are we": **Lễ tân › Sơ đồ** count buttons (`screens/fd-room-map.png`) and **Tình hình** bottom rows — used / free / % occupancy (`fd-room-situation.png`). There is no dashboard; the two hub screens are the glance.
2. Revenue: **Báo cáo › Doanh thu lễ tân** (`rpt-fd-revenue.png`) — fixed column groups per charge bucket (room, minibar, laundry, extra service, …), one date; **Doanh thu phòng hàng ngày** (`rpt-room-revenue-daily.png`) is occupied rooms × rate, a projection, not posted charges.
3. Who owes: **Báo cáo › Công nợ chi tiết / tổng hợp** (`rpt-debit-detail.png`, `rpt-debit-summary.png`): debtor dropdown (OTAs and companies mixed) + date range, one row per booking, Excel export and a signature block.
4. Record the payment: **Cập nhật công nợ** (`rpt-debit-update.png`, `giveback_debit`) → the row's Thanh toán link → amount (prefilled with the remainder, editable) · payment method · note → Lưu. Partial is allowed; there is no due date.
5. The wrong line: map tile → XEM CHI TIẾT → editor **Hóa đơn chi tiết** tab (`fd-booking-detail.png`); a service line is deleted or edited in place — no reason, no strike-through; a price change is an edit to the per-night price chart (`update_reduce_amount` for a post-hoc discount).
6. History: **Show log** at the bottom of the editor (time · type · description). Room-level history does not exist; `rpt-room-transfer.png` lists moves.

**What SoLex keeps / changes** (ux.md §4.10, §4.14, §4.9):
- Keeps the dashboard's top row in the map's vocabulary (Đang ở · Dự kiến đến · Dự kiến đi · Trống bẩn · Phòng sửa), receivables as company list → statement with rows that read as bookings, payment recorded from the statement with amount prefilled.
- Changes: a void is an event with a required reason; the line stays struck through and leaves the total, never deleted (§10 rule 10, owner only). Revenue "today" is posted charges, and the report says so.
- Changes: Needs attention is new (ezFolio has no inbox); every page ends in its own history, not one log per booking.

## In ezFolio today

_(product to fill in)_
