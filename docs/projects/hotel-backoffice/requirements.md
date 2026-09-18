# SoLex — Initial Product Requirements (from client)

Received 2026-09-19. Raw, untouched original: `client/2026-09-19-requirements-raw.md`. English translation + structure by Claude; translation choices flagged inline. Treat as **the client's mental model**, not a finalized spec — it's shaped like an Excel workbook (a "DASHBOARD" + 7 "sheets"), which strongly suggests the current/intended process is spreadsheet-based. WS3 should model from this; WS2 should confirm whether an Excel like this already exists.

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

Raw client text, untouched: `client/2026-09-19-requirements-raw.md`.
