# R9: Back office

**Purpose:** show the owner's side of the office: money going out, the reports, printing, people's data (including erasure), and staff leaving.
**Persona:** Oanh, the owner.
**Seed used:** set up off camera: Vu Quang Minh, who stayed in 303 and has checked out, and a seasonal receptionist account ("Tuan (seasonal)"). Tran Van Nam in 101 comes from the main seed.
**Length:** 1:17. File `R9-back-office.webm`.

| # | Step (caption) | Notice |
|---|---|---|
| 1 | Expenses: the plumber, 350,000 cash, Incidental | Money out, by category and method; the total for the period is shown. |
| 2 | The same expense entered twice → void the second, with a reason | The voided entry stays in the list, struck through with its reason, and leaves the total. |
| 3 | Revenue report | By category, by booking source, and by payment method (cash, bank, card). |
| 4 | Occupancy report | Night by night: rooms sold, rooms in service, and occupancy by type. |
| 5 | Room 101's printed bill | The hotel's letterhead; voided lines left off; totals, paid, and balance due. |
| 6 | People → Tran Van Nam → phone and nationality → Save | A "Guest updated" row appears in the person's history. |
| 7 | People → Vu Quang Minh → Erase data | The page reads "Erased". The stay and the bill remain; the history keeps its events but not the name. |
| 8 | Accounts → Tuan (seasonal) → Mark as former staff | Signed out and unable to sign in; "Bring back" is offered. |

Gaps on screen:
- No receipt print exists yet; only the bill and the group invoice print.
- N64: erasing a guest leaves the same name on the booking's contact record (a product question).

## In ezFolio today

Half of this journey has no ezFolio counterpart; the other half is spread over Reports and Hệ thống (`existing-system.md` § 06–08, § visual pass facts, § screen index).

1. Expenses: **none.** ezFolio has no money-out module; the client asked for one. Petty cash lives in a notebook.
2. Revenue: **Báo cáo › Doanh thu lễ tân** (`screens/rpt-fd-revenue.png`) — fixed column per charge bucket, one date; **Doanh thu theo hoá đơn** (`rpt-revenue-by-invoice.png`) per folio; nothing by booking source or by payment method.
3. Occupancy: **Công suất theo thời gian** (`fd-occupancy-over-time.png`) and **Dự báo phòng trống theo loại** (`fd-forecast-by-type.png`) — the forecast is the same engine as the group matrix.
4. Print: quickout's Post opens the invoice window (`show_invoice_new&folio_id=`); templates live on the **Biểu mẫu** settings tab (admin-only). Reports print via the browser and export to Excel.
5. People: **Quản lý khách ở** (`fd-traveller-list.png`, `traveller`) — one profile per person with gender, DOB, ID, nationality; **Lịch sử khách** (`fd-guest-history.png`); **Merge Profile** under Reports; **PA18** export (`fd-pa18-export.png`) for the police declaration. Editing is in place; **there is no erase**, and a profile's ID number lives in the row for ever.
6. Staff: `?page=employee` under Hệ thống (not walked); housekeeping rosters on `hk-employee-schedule.png`. Leaving = the admin disables or deletes the login; history is whatever the booking logs say.

**What SoLex keeps / changes** (ux.md §4.11, §4.8, §4.13, §4.14):
- Keeps: revenue by the same buckets the client reads today, a printed bill with the hotel's letterhead, one profile per person with ID and nationality.
- Changes: expenses are new (by category and method, voidable with a reason, in the same ledger as revenue); revenue also by source and by payment method, occupancy by type per night (§7 projections).
- Changes: erase is ours (D-20: the row is overwritten, the log keeps a tombstone, the stay and bill remain); a former staff member keeps their history and can be brought back (§2), instead of a deleted login.
