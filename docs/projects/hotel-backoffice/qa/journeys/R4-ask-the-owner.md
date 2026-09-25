# R4 — Ask the owner

**Purpose:** a receptionist cannot change money alone. The desk asks, the owner decides from one card, and the answer comes back to the line.
**Personas:** Dao, a real receptionist account; Oanh, owner.
**Seed used:** 101 Tran Van Nam with 2 × Mineral water at 15,000; 103 Le Thi Hanh with 2 × Saigon beer. Dao's account is created and signed in off camera.
**Length:** 1:21. File `R4-ask-the-owner.webm`.

| # | At | Step (caption) | Notice |
|---|---|---|---|
| 1 | 0:02 | Dao (receptionist): 101 is a regular; Oanh agreed 10,000 a bottle | The receptionist's nav has no Setup, Reports or Accounts. |
| 2 | 0:10 | Ask to reprice → 10,000, with a reason | The receptionist's buttons read "Ask to reprice" and "Ask to take off", not Reprice and Void. |
| 3 | 0:19 | The line waits for the owner | Marked "waiting for the owner"; nothing has changed on the bill; no second ask is possible. |
| 4 | 0:22 | 103: Ask to take off the beers, with a reason | The same flow for a void. |
| 5 | 0:38 | Oanh: the Reports link has a badge | The count of requests is the notification; nothing leaves the app. |
| 6 | 0:41 | Needs attention cards | Who asks, what for, which line, amount, room (links to the stay), guest, and the reason (see N47). |
| 7 | 0:44 | Approve the reprice | The card leaves. |
| 8 | 0:47 | Refuse the beers, with a reason | A reason is required; the desk will read it. |
| 9 | 0:59 | Dao: 101's bill | The old line is struck through with the reason; a new line is at 2 × 10,000. |
| 10 | 1:08 | Dao: 103's bill | "The owner said no — <reason>" on the line; the beers stay on the bill, and the desk may ask again. |

Open on screen: N47 (the reprice card shows the line's current amount, not the price asked), N57 (the ask and the answer are not in the stay's history, a product question).

## In ezFolio today

There is no ask-and-approve round trip in ezFolio; the money change is done by whoever holds the permission (`existing-system.md` § mid-stay changes, § visual pass facts).

1. The receptionist opens the room from the map → XEM CHI TIẾT → editor (`screens/fd-booking-detail.png`) → **Hóa đơn chi tiết**.
2. A cheaper price: the *Money* panel's discount (% or VND) + a **reason** field, or `update_reduce_amount` — a post-hoc discount on the room-stay behind an explicit edit toggle, gated by `allowchangeprice`. A service line's price is edited in place.
3. Taking a line off: the service line is deleted from the register (`fd-minibar-invoice.png`, `fd-extra-service.png`); no reason, no trace on the bill.
4. Control after the fact only: **Báo cáo › Giảm giá phòng** (`rpt-room-discount.png`) lists discounts with a requested / edited / approved trail and the users — a report the owner reads later, not a gate the desk hits.
5. Who may: the same reception login does it, unless the admin has turned the flag off for that account; then the receptionist asks the owner in person or on Zalo and the owner edits it.

**What SoLex keeps / changes** (product.md §11 Approvals, D-28; ux.md §4.14):
- Keeps: a discount is a price change on the line with a reason, and the trail of who asked / who approved that ezFolio's discount report already shows.
- Changes: the receptionist's button on the same line reads "Ask to reprice" / "Ask to take off"; the line waits, marked, and cannot be asked twice; the owner answers from a Needs attention card and the act runs in the same batch as the grant (§11). Refusal carries a reason the desk reads on the line.
- Changes: void and reprice are owner capabilities (§10 rule 10); a reprice is void + re-post, both visible, so the month-end sees every discount — there is no discount field or percentage box.

## In ezFolio today

_(product to fill in)_
