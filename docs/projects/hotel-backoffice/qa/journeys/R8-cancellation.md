# R8: Cancellation path

**Purpose:** show what happens to the money when a guest doesn't come: a cancellation and a no-show, each deposit accounted for with a reason.
**Persona:** Oanh, the owner.
**Seed used:** Le Van Hung, set up off camera: due yesterday, paid a 500,000 cash deposit, never arrived.
**Length:** 1:06. File `R8-cancellation.webm`.

| # | Step (caption) | Notice |
|---|---|---|
| 1 | New booking: Tran Thi Lan, next week, 2 nights | No room is assigned yet ("Decide later"). |
| 2 | Deposit 1,000,000 by bank transfer, with its reference | The bill shows the guest 1,000,000 in credit. |
| 3 | The guest cancels: reason required → Cancel the stay | The nights go back on sale. The deposit's form ("Keep the deposit") appears only now. |
| 4 | Keep 300,000, with a reason | This is revenue on the day it is kept. The amount kept can never exceed what was taken. |
| 5 | Refund 700,000 by bank transfer, with a reason | Money goes back the way it came. The bill reaches 0 and closes, and every line keeps its reason. |
| 6 | Le Van Hung → Nobody came | This is only possible once the arrival day has passed. The nights are freed. |
| 7 | Keep the whole 500,000 | The no-show's bill closes. |
| 8 | Revenue report | "Deposit kept" appears as its own category, on the day the money was kept. |

N63 is fixed: a closed bill now says why it closed (cancelled, or nobody came).

## In ezFolio today

The deposit is a number on the booking and the money side of a cancellation is handled by hand (`existing-system.md` § deposits, § cancellation and no-show).

1. Deposit: **Đặt cọc** on the booking form (`screens/fd-walkin-form.png`, `fd-group-availability.png` header); it shows in the editor's money panel (Tổng / Đặt cọc / Trả trước / Còn lại) and on **Báo cáo › Đặt cọc** (`rpt-deposit.png`) with a method (cash / bank).
2. Cancel: editor › Thao tác › **Hủy đặt phòng**. Guards: a checked-in room cannot be cancelled; if charges were posted they must be moved to another room first; then a **mandatory reason** → status CANCEL (`fd-cancellations.png` is the list).
3. With a deposit, cancel forks: downgrade to BOOKED with a pre-check-in reason, or open `extra_service_invoice … add_prepayment=1&service_id=38` — i.e. **post the deposit as an extra-service line** so it becomes revenue. No forfeit cap, no reason on the line.
4. Refund: **no refund path in the UI**; money back is handled outside the system (cash drawer, bank), and the bill does not show it.
5. No-show: **Không đến** — a flag on the room-stay (`fd-noshow.png` list): no charge, no reason, allowed at any time; the deposit is kept or returned by hand as in 3–4.
6. Revenue: the kept deposit lands in the extra-service bucket of `rpt-fd-revenue.png` under whatever item 38 is called.

**What SoLex keeps / changes** (product.md §10 rule 3; ux.md §4.7, §4.10):
- Keeps: a deposit taken before arrival with its method; cancel with a mandatory reason and only for a stay nobody has checked into; a kept deposit is a revenue line, not a status.
- Changes: keeping the deposit is an explicit owner act (`ForfeitDeposit`) capped at what was actually taken, and the refund is a recorded line with a reason — both visible on the bill, both under "Deposit kept" / refunds in the reports; no more posting it as "service 38".
- Changes: no-show only after the arrival date has passed, and a closed bill says why it closed (N63); nothing is charged automatically for either.
