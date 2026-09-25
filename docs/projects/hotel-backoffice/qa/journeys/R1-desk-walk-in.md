# R1 — Desk walk-in

**Purpose:** the front desk's most common job, from an empty room to a closed bill: room map → book → check in → minibar → check out and pay → the room is dirty.
**Persona:** Dao, front desk.
**Seed used:** room 302 (free); the Minibar category. The walk-in guest is typed on camera.
**Length:** 0:53. File `R1-desk-walk-in.webm`.

| # | At | Step (caption) | Notice |
|---|---|---|---|
| 1 | 0:02 | A walk-in wants a room tonight; which rooms are ready? | The room map's status filters, each with its count; "Ready" narrows the tiles. |
| 2 | 0:06 | Open 302 | The panel: state, guest (nobody), tonight's rate. No page change. |
| 3 | 0:12 | New booking: name, today, one night, room 302 → book | The room type picks the rate from the rate table; the form shows the number of nights and the price source. |
| 4 | 0:24 | Stay page → Check in | Tonight's room charge is on the bill the moment the guest is in. |
| 5 | 0:28 | 2 Cokes from the minibar → Add to bill | A line with category, quantity and unit price; the totals strip updates. |
| 6 | 0:38 | Next morning → Check out | The settle dialog opens with the balance already filled in; cash is chosen. |
| 7 | 0:45 | Paid and checked out | The bill is closed; Due is 0. |
| 8 | 0:50 | Back to the map | 302 is vacant and dirty, waiting for housekeeping. |

"Next morning" is a day-start shift off camera (see the README).

## In ezFolio today

Same job, the desk's path in ezFolio (`existing-system.md` § individual booking flow, § settlement, § charges; screens are local-only, PII).

1. **Lễ tân › Sơ đồ** (`screens/fd-room-map.png`): the status buttons with counts — SẴN SÀNG shows how many rooms are ready; click it to filter the tiles.
2. Click the tile → the **Chi tiết** modal (`fd-room-detail-panel.png`): room, rate, status, guest, **Còn lại**; the ĐẶT PHÒNG action or XEM CHI TIẾT opens the editor.
3. **Lễ tân › Khách lẻ** (`fd-walkin-form.png`): one 95-field form, no availability step; type name, dates, pick the room from the `Phòng` dropdown, rate typed in VND (the price chart tab holds one row per night). Press **Checkin** (not Đặt phòng) — the stay is created already CHECKIN. Tonight's room charge posts at `time_next_date` 23:59, not at check-in.
4. Minibar: back on the map, tile → **MINIBAR** button in the modal footer (`fd-minibar-invoice.png` is the register, not the entry point): item, qty, unit price, note.
5. Check-out: the editor's **Thao tác › Fast checkout** → the `quickout` dialog: one row per room, Còn lại · Phương thức thanh toán (Tiền mặt / Thẻ / Chuyển khoản / FOC / Công nợ) · Loại tiền · Số thẻ · Ngân hàng → Post, which also opens the invoice window to print.
6. The room: reception presses **DIRTY** on the tile by hand; nothing marks it dirty at check-out.

**What SoLex keeps / changes** (ux.md §4.2, §4.5, §4.7):
- Keeps the map as home, the status buttons with counts, the tile → quick panel with Còn lại and one quick-charge button per category, and the quickout-shaped settle dialog.
- Changes: one booking form with "Take the booking" / "Take and check in now" instead of a 95-field editor; tonight's room charge posts at check-in; check-out is refused while the bill owes, so the bill stays on the page rather than behind the Hóa đơn tab.
- Changes: the room goes dirty automatically at check-out (§10 rule 6, house rule); no card tab, ever.

## In ezFolio today

_(product to fill in)_
