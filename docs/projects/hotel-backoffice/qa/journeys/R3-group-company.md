# R3 — Group + company

**Purpose:** a company's tour group from agreement to invoice: who pays for what, set once and applied per room.
**Personas:** Oanh, owner (the agreement, and receivables at the end); Dao, front desk (everything else).
**Seed used:** Blue Sea Travel Co.; Double rooms 203, 301, 303 and Twin 401, all free tonight. R2 has already settled room 201's company debt, so the final total is the group alone.
**Length:** 1:53. File `R3-group-company.webm`.

| # | Step (caption) | Notice |
|---|---|---|
| 1 | Setup → Blue Sea's card: the company pays for Restaurant and Minibar | A company's standing agreement, one select per charge category. The room night goes to the group's bill by default. |
| 2 | New booking: A group, billed to Blue Sea, 3 Double | "Booking for" comes first; a group gets a room count, not a room number. |
| 3 | Another kind of room: 1 Twin | Mixed room types on one booking (G20). |
| 4 | Book | Each line shows how many rooms of that type are free tonight, and the grid below counts nights. |
| 5 | The booking page | One booking, four stays with no room number yet, one group bill. |
| 6 | Who pays for what | The company's agreement is already applied. Each row is a room; each column says Guest or Group. |
| 7 | Minibar → the guest's own bill, for this group only | The header select changes the whole group; the company's agreement is unchanged. |
| 8 | Occupancy chart | Free squares per room and night, and "Nights without a room" for the group. |
| 9 | Assign a room → 301 → Check in | From the unassigned list to the stay's page. |
| 10 | 301 is the tour leader: that room's own Laundry → the group's bill | A single room's exception is set on its own page; the group table marks it "set for this room". |
| 10b | (the other three rooms, off camera) | 203, 303 and 401 are assigned and checked in the same way. |
| 11 | 301: dinner 360,000 (Restaurant) and 2 beers (Minibar) | Dinner goes to the group's bill; the beers stay on the room's. The room's bill says up front which categories go to the group's bill, with a link to it (N54 fixed). |
| 12 | Next morning: 301 checks out and pays for the beers in cash | The settle dialog asks only for the room's own share. |
| 13 | (the other three check out, off camera) | Nothing is left on their own bills. |
| 14 | The group's bill | Four room nights and the dinner: 2,410,000. The table above shows 301 · Laundry as Group, marked. |
| 15 | Move to the company → Finish | The company is already picked from the booking; the bill closes at 0. |
| 16 | Oanh: Owed → Blue Sea's statement | The group's total is on the company's account, ready to invoice. |

Open on screen: N51/N52 (room lines read "Tiền phòng <ISO date>"; the statement line shows the company's id). These are ruled and pending with dev.

## In ezFolio today

The corporate group is ezFolio's main business and its most involved path (`existing-system.md` § group booking flow, § group folio routing, § master folio, § group lifecycle).

1. The company: **Kinh doanh › Công ty** (`screens/sales-companies.png`) — Agent/Company rows with a Nguồn of OTA / TA / CORP. No standing "who pays for what" lives here; routing is set per booking.
2. **Lễ tân › Khách đoàn** (`fd-group-availability.png`, `cmd=check_availability`): the room-type × night matrix with free rooms per night and per-night used / free / %; the left half is the entry — per type a row of adults · children · price · qty. Header: company lookup, contact, deposit, display code + colour, Nguồn. **Kiểm tra phòng trống** recomputes, **Đặt phòng** creates N room-stays with no room numbers.
3. Routing: open one of the group's rooms in the editor (`fd-booking-detail.png`) → the nine-checkbox matrix (HĐ phòng · nhà hàng · DV mở rộng · … · Tiền đặt cọc · Các khoản khác) decides which buckets settle on the group's master bill — set per room-stay, all nine on for a "one bill" group.
4. Assign: **Danh sách đặt phòng chưa gán** (`fd-waiting-list.png`) is the queue by room type; in practice it is empty — rooms are assigned at booking or on the tape chart (`fd-room-situation.png`); `lay_phong_can_ngay` auto-assigns the soonest-needed room.
5. Check-in, charges, check-out are per room-stay in the editor, exactly as in R1; dinner posted from the tile's EXTRA SERVICE button routes to the master by the matrix.
6. The master bill: a folio assembled by **Chuyển dịch vụ** (move lines between rooms) or by the matrix at posting time; listed on the editor's **FO** tab; settled in quickout with method **Công nợ**, which is what creates the receivable row against the company (`rpt-debit-update.png`).
7. Invoice: **Báo cáo › Công nợ chi tiết** (`rpt-debit-detail.png`), one row per booking with rooms · nights · Tổng, Excel export.

**What SoLex keeps / changes** (ux.md §4.5, §4.6, §4.10):
- Keeps: group = types × qty with live free-per-type (G20), "Booking for" a group with a room count, the routing idea per charge category, Công nợ → company as the last settle option, statement rows that read as bookings.
- Changes: the company's agreement is stored once in Setup as the default routing (§10 rule 8) and applied to every group stay; the booking page shows the whole table (rooms × categories) and one select changes the group (G32) — ezFolio sets nine checkboxes per room.
- Changes: "Move to the company" is an explicit transfer on the group's bill, not a payment method that doubles as "open a receivable"; the master is closed at 0 by `CloseBooking`, and there is no Đóng day-close (parked, G27).

## In ezFolio today

_(product to fill in)_
