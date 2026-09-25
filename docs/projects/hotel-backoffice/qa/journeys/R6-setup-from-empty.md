# R6: Setup from empty

**Purpose:** show that one owner can take an empty SoLex to "ready to sell" in a single sitting.
**Persona:** Oanh, the owner.
**Seed used:** none. R6 runs on its own empty database and server (the `empty` project in `journeys.config.ts`).
**Length:** 1:31. File `R6-setup-from-empty.webm`.

| # | Step (caption) | Notice |
|---|---|---|
| 1 | Empty hotel | The room map says there are no rooms yet; every count is 0. |
| 2 | Setup → This hotel: name, address, phone; business day starts 02:00 | The day start decides which business day a late-night event belongs to. The letterhead is printed on every bill. |
| 3 | Room types: Double (sleeps 2), Family (sleeps 4) | Capacity is set per type; it is what refuses a 4-person Double in R5. |
| 4 | Rooms 101, 102 (Double) and 201 (Family), with floor | The type is picked from the types defined above. |
| 5 | Rates by date range: Double 500,000 until the holidays, 650,000 for the holiday weeks; Family 800,000 | Ranges for one type may not overlap. A booking takes the price of the range each night falls in. |
| 6 | Charge categories: "Add the standard list" | Compensation, Extra service, Laundry, Minibar, Restaurant and Room surcharge, plus Room and Deposit kept (both system categories). |
| 7 | Booking sources: Agoda (OTA) | Until a source exists, every booking counts as a walk-in. |
| 8 | Company: Blue Sea Travel Co., with tax code | Companies are what a bill can be moved to (R3). |
| 9 | Accounts: Oanh takes the owner's position; Dao gets a receptionist account | The password field is masked; there is no sign-up page. |
| 10 | Room map | Three rooms, all Ready. |

## In ezFolio today

Setup is split between admin-only masters and a 26-tab settings page, and reception cannot see the masters at all (`existing-system.md` § config flow, § visual pass facts).

1. **Hệ thống › setting** (`screens/sys-settings.png`) › Thông tin khách sạn: property name and address, default check-in 14:00 / check-out 12:00, day-cut window `[00:00–23:59]`, currency, rounding, weekend surcharge fields (0). This is the letterhead and the day boundary.
2. Room types and rooms: the `room_type` and `room` master pages — admin-only ("Bạn không có quyền truy nhập phần này" for reception); types carry a code (DLX5, SUPT …) and a bed type, no capacity that is enforced.
3. Rates: **there is no rate table.** Price is typed per booking (`fd-walkin-form.png`, the price chart tab holds one row per night); the `roomrate` plan dropdown is empty; the only real price list is hourly day-use (`sys-hourly-pricing.png`), unused.
4. Charge buckets are fixed in code (eight, the columns of `rpt-fd-revenue.png`); behaviour per bucket is on **Thuế – Dịch vụ** (`sys-charge-config.png`, tax and service both 0, everything net); item catalogues (`minibar_product`, `laundry`, `extra_service`) are admin-only masters and the extra-service list is duplicated and uncurated.
5. Booking sources: the fixed Nguồn list OTA · TA · WALK-IN · CORP on the booking form; no screen adds one.
6. Companies: **Kinh doanh › Công ty** (`sales-companies.png`) — Agent/Company rows with tax code and a Nguồn.
7. Rules: **Cấu hình đặt phòng** (`sys-booking-rules.png`) — day boundary, child age 6, overbooking on, auto-assign.
8. Staff: `?page=employee` under Hệ thống (not walked; it throws PHP errors on load) — logins are created there by the admin.

**What SoLex keeps / changes** (ux.md §4.12, §4.13):
- Keeps: the same dials (day start, check-in/out times, child age, overbooking) and companies with a tax code; the standard charge list seeds the eight buckets the client's revenue report already uses.
- Changes: one Setup page the owner can open (ezFolio's masters are invisible to the people doing the work); a **rate table by date range** per type, so a booking takes its price instead of the desk typing it every time (§10 rule 9).
- Changes: capacity is on the type and enforced (G35); booking sources are a list the owner edits (G28); an account is separate from a position (§2), and there is no sign-up page.
