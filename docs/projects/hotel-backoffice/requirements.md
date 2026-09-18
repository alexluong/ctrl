# SoLex — Initial Product Requirements (from client)

Received 2026-09-19, verbatim Vietnamese at the bottom. English translation + structure by Claude; translation choices flagged inline. Treat as **the client's mental model**, not a finalized spec — it's shaped like an Excel workbook (a "DASHBOARD" + 7 "sheets"), which strongly suggests the current/intended process is spreadsheet-based. WS3 should model from this; WS2 should confirm whether an Excel like this already exists.

## 1. The core flow ("Need")

One room-status change should cascade through everything:

1. Change room status
2. → Dashboard updates
3. → Occupancy % goes up
4. → Revenue forecast goes up
5. → Housekeeping knows the check-out date
6. → Reception knows room revenue (deposit / outstanding / paid)
7. → Guest history updates
8. → OTA commission auto-calculated

> ES note: this reads as a single event (`RoomStatusChanged` / `BookingCheckedIn`) fanning out to ~7 projections. Strong fit for event sourcing.

## 2. Automation wishes

- Conditional colouring: occupied → red, vacant → green, overdue receivable → dark red
- Enter room number → auto-fill rate, room type, floor
- Pick a date range (day/month/year) for quick reports
- Enter check-in + check-out → auto nights. Enter rate → auto amount. Enter deposit → auto balance due

## 3. Dashboard questions (what the owner wants to see at a glance)

- Vacant rooms today?
- Revenue today?
- Revenue this month?
- Which OTA brings the most guests?
- Which bookings are unpaid?
- Receivables by: group guests / walk-in (individual) / corporate / OTA?
- Room status overview?
- Occupancy rate?
- Revenue by payment method: cash / bank transfer / card?
- Bookings checking in soon?
- Bookings checking out soon?

## 4. Data "sheets"

### 4.1 Setup (master data)

- Room list
- Room types
- Floors
- Room statuses: Dirty, Vacant-clean, Expected arrival, Expected departure, Out of order (maintenance)
- Guest sources (channels)
- Guest info (name, phone, source, …)
- Amounts (rates — *ambiguous: "Số tiền" = "amount"; likely rate table*)
- Check-in / check-out date-times

### 4.2 Booking

| field | note |
|---|---|
| Booking ID | internal |
| Reservation No | external / OTA ref? (two IDs listed — confirm) |
| Booking date | |
| Check-in | |
| Check-out | |
| Nights | derived |
| Guest name | |
| Phone | |
| Email | |
| Nationality | |
| CCCD | Vietnamese national ID number |
| OTA | source channel |
| Room type | |
| Room no | |
| Guest | *listed separately from name — probably guest count / pax* |
| Deposit | |
| Payment | |
| Status / Notes | |

### 4.3 Room status board

- Room numbers, displayed by floor
- Statuses: Dirty, Vacant-clean, Expected arrival, Expected departure, Out of order
- Colour-coded

### 4.4 Revenue (day / month / year)

Line items: Room revenue, Extra bed, Late check-out / early check-in, Laundry, Minibar, Parking, Damage, Other

### 4.5 Payment

Booking, date received, Cash, Bank transfer, Card, Refund, Deposit, Balance

### 4.6 Accounts receivable (công nợ)

Debtor types: Corporate, OTA, Group guests. Fields: Collected, Outstanding, Due date, Overdue

### 4.7 Expense report

Market/groceries (chợ), Incidental expenses, Housekeeping overtime, Advances (tạm ứng)

## 5. Claude's first read (for WS3)

- **Entities implied**: Room, RoomType, Floor, RoomStatus, Guest, Booking, Channel/OTA, Payment, Charge (revenue line item), Receivable, Expense.
- **Roles implied**: Owner (dashboard), Reception (bookings, payments), Housekeeping (status board, check-outs).
- **Money is central**: deposit/balance/receivables/payment-method breakdown appear repeatedly. Cash-heavy (Vietnam). Receivables by debtor type = B2B/group business exists.
- **OTA commission auto-calc** needs per-channel commission rates — not in Setup sheet, add.
- **Expenses** are in scope from day one (owner wants P&L-ish view), not just bookings.
- **No mention of**: rate plans by season, multi-night rate changes, invoices/VAT (red invoice), channel-manager sync, guest-facing anything. Ask.
- Nights/amount/balance "auto-calc" = they've been doing this by hand. Confirms Excel/paper today.

---

## Original (verbatim, Vietnamese)

```
Need:

Đổi trạng thái phòng
↓
Dashboard đổi
↓
Occupancy  ( tỷ lệ lấp đầy %) tăng
↓
Revenue Forecast ( Doanh thu) tăng
↓
Housekeeping biết ngày check out
↓
Reception biết doanh thu phòng ( cọc/ nợ/ thanh toán..)
↓
Guest History cập nhật
↓
OTA Commission tự tính

_________________

✅ Tự đổi màu theo điều kiện. Ví dụ: Phòng đang ở → đỏ, Phòng trống → xanh, Công nợ quá hạn → đỏ đậm
✅ Nhập số phòng là tự hiện giá phòng, loại phòng, tầng…
✅ Chọn khoảng thời gian (ngày/tháng/năm) để xem báo cáo nhanh
✅ Nhập Check-in và Check-out → tự tính số đêm. Nhập giá phòng → tự tính tiền.  Nhập tiền cọc→ tự tính còn phải thu
DASHBOARD EXCEL:

✅ Hôm nay còn bao nhiêu phòng trống?
✅ Doanh thu hôm nay bao nhiêu?
✅ Doanh thu tháng bao nhiêu?
✅ OTA nào mang khách nhiều nhất?
✅ Booking nào chưa thanh toán?
✅ Công nợ khách đoàn/ khách lẻ/ khách công ty/ OTA?
✅ Tình hình phòng?
✅ Tỷ lệ lấp đầy?
✅ Doanh thu tiền mặt/ chuyển khoản/ cà thẻ?
✅ Bao nhiêu booking sắp check-in?
✅ Bao nhiêu booking sắp check-out?

Sheet :

1. SETUP
✅ Danh sách phòng
✅ Loại phòng
✅ Tầng
✅ Tình hình phòng ( Bẩn, Trống sạch, Dự kiến đến, Dự kiến đi, Phòng sửa)
✅ Nguồn khách
✅ Thông tin khách ( Tên, sđt, nguồn, …)
✅ Số tiền
✅ Ngày giờ IN/OUT

2. BOOKING
✅Booking ID
✅Reservation No
✅Ngày đặt
✅Check in
✅Check out
✅Số đêm
✅Tên khách
✅SĐT
✅Email
✅Quốc tịch
✅CCCD
✅OTA
✅Room Type
✅Room No
✅Guest
✅Deposit
✅Payment
✅Status/ Notes

3. ROOM STATUS
Số phòng/ Hiển thị theo tầng
Bẩn, Trống sạch, Dự kiến đến, Dự kiến đi, Phòng sửa
Có thể tô màu.

4. REVENUE
Doanh thu ngày/ tháng/ năm
✅Room Revenue
✅Extra bed
✅Late check-out/ Early check-in
✅Laundry
✅Mini bar
✅Parking
✅Damage
Khác

5. PAYMENT
✅Booking
✅Ngày thu
Cash
Banking
Card
Refund
Deposit
Balance

6. ACCOUNT RECEIVABLE ( công nợ)
✅Công ty
✅OTA
✅Khách đoàn
Đã thu
Chưa thu
Ngày đến hạn
Quá hạn

7. EXPENSE REPORT ( Chi phí)
✅ Chợ
✅ Chi phí phát sinh
✅ Dọn phòng OT
✅ Tạm ứng
```
