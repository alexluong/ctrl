# SoLex — Existing System (WS2)

Owner: WS2 session. Access: `ctrl/secrets/hotel-backoffice.md` (do not copy here).

## What it is

The hotel management software (PMS) the client uses today, reached on port `:99` (public + LAN URLs). Confirmed by Alex 2026-09-19.

**Why rebuild (Alex, 2026-09-19):** the client wants a custom version mainly to **own their data**. Goal is to rebuild the *essence* of the current system: a core subset plus enhancements, not a feature-by-feature copy. Alex knows what the client needs; WS2's job is to map the current system so the core can be chosen from it.

**Product:** **ezHotel** from ezCloud (ezcloud.vn / ezhotel.vn, a Vietnamese vendor). Hosted by the vendor or the hotel (TBD). Server-rendered PHP-style app: `/?page=<module>&cmd=…&status=…`, anchors `#menu_<group>_<id>`. Plain HTTP. Login form: `user_id`, `password`. UI is Vietnamese with an EN toggle. The home page shows "Current date" and "System date" separately, which points to night-audit-driven business dates.

**Method:** walk through it with Alex, slowly, screen by screen. Map first, then judge what's core.

## Menu map (from nav, 2026-09-19; not yet opened)

Top nav: Kinh doanh (Sales) · Lễ tân (Front desk) · Buồng (Housekeeping) · Nhà hàng (Restaurant) · Báo cáo (Reports) · Kiểm toán (Audit) · Hệ thống (System) · In (Print).

**Sales (menu_3)**: Công ty / companies → `customer`

**Front desk (menu_21)**
- Room map `room_map` · room status/occupancy `monthly_room_report`
- New booking: walk-in `reservation&cmd=add&status=CHECKIN&reservation_type_id=2` · group `reservation&cmd=check_availability`
- Lists (`reservation&status=`): WILL_CHECKIN, WILL_CHECKOUT, CHECKIN (arrivals today), CHECKOUT (departures today), INHOUSE, CANCEL, NOSHOW; search `reservation`; summary `reservation_summary`
- Change room `change_room` · unassigned bookings `waiting_list` · pickup/drop-off `pickup_see_off`
- Guests: `traveller` (in-house guest mgmt) · `extract_pa18` (PA18 = police temporary-residence declaration export; VN legal requirement)
- Services: laundry, minibar, restaurant charge-to-room, extra bed `extra_bed_invoice`, extended/extra services `extra_service_invoice`, damages `equipment_invoice`
- Stats: forecast by room type `room_focast_type`, occupancy over time `room_focast`, breakfast `breakfast_report`, guest history `guest_history`

**Housekeeping (menu_4)**: HK room map `room_map_hk_new` · room status `hk_room_status` · minibar · laundry · damages · lost & found `forgot_object` · expected arrivals/departures · staff scheduling `employee_hk_report`

**Restaurant (menu_5)**: POS: table map, split/merge tables, table reservations (booked/checked-in/checked-out/cancelled/free), deposits `deposit_bar`, table utilisation; revenue by staff/invoice/item/category/area; shift handover; discounts; deleted items; charge to front desk; debtor report; goods catalogue; Excel export of goods

**Reports (menu_88)**: merge guest profiles `customer_manager` · front-desk revenue `room_order_revenue_report` · by invoice `order_revenue_by_user_report` · daily room revenue `room_revenue_daily_report` · deposit revenue `deposit_report` · receivables detail/summary `detail_debit_report`/`summary_debit_report` · receivables update `giveback_debit` · room discounts · room transfers

**Audit (menu_313)**: night audit `night_audit`

**System (menu_22)**: settings `setting`

First read: a full PMS (front desk + housekeeping + restaurant POS + receivables + night audit). The client's wishlist in `requirements.md` overlaps front desk, housekeeping, revenue and receivables. No restaurant POS or PA18 in the wishlist; PA18 may still be legally needed. No expense module visible (the client wants one).

## Screens walked (2026-09-20)

Screenshots: `../screens/<slug>.png` (gitignored — they contain guest PII). **Naming:** `<area>-<screen>[-<variant>]`, area ∈ `fd` (front desk) · `hk` (housekeeping) · `rest` (restaurant) · `rpt` (reports) · `sys` (system) · `audit`. Index of captures at the end of this file. Tooling: `../tools/` (read-only guard: non-GET blocked except data-fetch `json=1` POSTs).

Product logo inside the app is **ezFolio** (ezCloud's PMS; login page brands ezCloud/ezHotel). Vendor support contact shown on login.

### 01 · Front desk › Room map (`room_map`)
Grid of room tiles by floor, one tile = `<room type code> / <bed type>` + room number, colour = status. Top bar = date picker + status filter buttons with live counts; on 20/09/2026: **TẤT CẢ 58** (total rooms), SẴN SÀNG 2 (ready), DỰ KIẾN ĐẾN 5 (expected arrival), ĐANG Ở 50 (in house), DỰ KIẾN ĐI 0, CÓ KHÁCH BẨN 0 (occupied+dirty), TRỐNG BẨN 2 (vacant dirty), PHÒNG SỬA 1 (out of order). Also: FILTER, **ĐỌC THẺ / XÓA THẺ** (read / erase key card → door-lock system integration), print.
Statuses match the client's wishlist list exactly (Dirty / Vacant-clean / Expected arrival / Expected departure / Out of order) — the wishlist is describing *this screen*.

### 02 · Front desk › Room situation (`monthly_room_report`, "Room View")
Room-by-date availability calendar (1/7/15/30-day or custom window), rooms grouped by **room type**, floor multi-select, "colour by booking" toggle. Bottom rows: rooms used / rooms free / **% occupancy** per day. On 20/09/2026: 55 used, 2 free, 96.5% today, falling to ~30% within a week and <10% two weeks out. Cells show the booking's guest/label.
Loads its grid over a POST `json=1` endpoint (not a plain page) — relevant if we ever scrape history.

### 03 · Front desk › In-house list (`reservation&status=INHOUSE`)
The booking list screen; `status=` switches it (BOOKED / CHECKIN / CHECKOUT / WILL_CHECKIN / WILL_CHECKOUT / INHOUSE / CANCEL / NOSHOW + history variants). 50 in-house, of which **"khách lẻ" (individual/walk-in) 17** — rest are group/company.
Columns: `# (booking id) · Tên (guest) · Mã QT · Phòng · Loại (room type) · Giá VND · Đêm (nights) · Ngày đến · Ngày đi · Nguồn (source) · Mã hiển thị / Công ty (display code / company) · Ghi chú (notes: free text + "Yêu cầu" requests) · Tài khoản (audit: C: created-by, B: booked-by, CI: checked-in-by) · Saler`.
Filters: date range, room type, room, booking code, **nationality**, price operator (>/>=/</<=/=), group-only, company, guest name, status checkboxes.
Actions: search, view report, printable report, print all, **Export to Excel**, per-row checkboxes (bulk ops).

Notable: rates are per booking in VND (e.g. 1,100,000/night); source codes seen in labels — TA, AGD (Agoda), CTRIP, VNTRIP, plus company names; several long/repeat bookings under one contact name.

### 04 · Front desk › Room detail panel (room map tile → `showDetail`)
Room map is AngularJS; a tile opens a modal, not a URL. Modal "Chi tiết" shows room, rate, arrival, departure, nights, status, guest name, company, editable note, **Còn lại** (balance outstanding), tabs CHECKIN ROOM / ADVANCE POST ROOM CHARGE, a "ĐẶT PHÒNG" (book) action, and quick-action buttons **DIRTY · MINIBAR · LAUNDRY · COMPENSATION · EXTRA SERVICE** (posting charges straight from the map — this is how reception posts extras).

### 05 · Front desk › Booking / folio editor (`reservation&cmd=edit&id=<reservation_id>&r_r_id=<reservation_room_id>`)
The core screen, reached from the room detail modal ("XEM CHI TIẾT"). Tabs at top: **Bản khai báo thông tin** (guest declaration → PA18), **Hóa đơn chi tiết** (detailed invoice/folio), **Đặt phòng** (booking), Lưu (save), Thao tác (actions).
Panels and fields:
- *Guest*: last/first name, gender, DOB, guest class (`individual` / VIP 1 / VIP 2 / Guest return), address; **Mã QT**, ID type (CMND / Passport / driver licence / other) + number + issue date, visa + issue/expiry, children count, arrival/departure date+time; **flight tab** (arrival/departure flight no, times), **card tab** (card holder, number, expiry, type, CVV); contact phone, email, note. Actions: add guest, delete, refresh, **Ghép đoàn** (merge into group).
- *Booking*: **FolioID**, display code + colour, **Công ty** (company) + contact person + email, note, saler, arrival/departure, **NL/TE** (adults/children), room, nights, rate (VND + USD), **Net ++**, package, lock, status (Checkin / Checkout / Booked / Cancel / Close), **Nguồn** (source), **Hoa hồng** (commission, % or $), confirmation no.
- *Money*: FOC flag, exchange rate, discount (% or VND) + reason, tax, service fee, room charge, services, **Tổng / Đặt cọc / Trả trước / Còn lại** (total / deposit / prepaid / balance), Payment · Add SV · List SV · FO tabs.
- *Guests on the booking*: table (name, gender, DOB, phone, email, address, note, Mã QT, ID, issue date, arrival, departure).
- **Show log** — per-booking audit log (time · type · description).

Note: with the read-only guard on, the editor renders its shell but leaves values blank — it populates over POSTs, one of which (`create_routing`) may write, so it stays blocked. The field list above is complete; actual values for a booking need either a relaxed guard or a manual look by Alex.

### 06 · Reports › Receivables detail (`detail_debit_report`)
"BÁO CÁO CHI TIẾT CÔNG NỢ". Filters: **company/debtor** (dropdown) + date range. Columns: STT · Mã đặt phòng (booking code) · **REF** (OTA/external ref) · Mã hiển thị · Công ty/Tên khách · guests A/C (adults/children) · room · #rooms · nights · arrival · departure · **Tổng** · note. Footer total + a printed signature block (Người lập biểu / Trưởng bộ phận / Giám đốc). **Export to Excel**.
Debtor dropdown mixes **OTAs** (BOOKING.COM, EXPEDIA, Asiabooking, …) with **corporates and tour operators** (~dozens of named companies). Sept 2026 outstanding: ~11.7M VND across 24 bookings — receivables volume is modest, the *variety* of debtors is the complexity.
Source tags seen on guest names: AGD (Agoda), CTRIP, TVLK (Traveloka), EXP (Expedia), plus company short names — the hotel encodes channel in the guest-name string. That's a data-quality smell the rebuild should fix with a real channel field.

### 07 · Reports › Receivables summary (`summary_debit_report`)
Same idea, one date. Columns add the settlement side: **Tổng nợ · Đã thanh toán · Còn lại · Phương thức TT (payment method) · Date time paid · Người dùng (user)**. Empty for 20/09. Export to Excel + signature block.

### 08 · Reports › Daily room revenue (`room_revenue_daily_report`)
"BÁO CÁO DOANH THU PHÒNG HÀNG NGÀY", one hotel (portal dropdown implies multi-property support) + one date. Row per occupied room: company · display code · guest name · gender · DOB · Mã QT · ID no · **room · rate · arrival time+date · departure time+date**. ~53 rows for 20/09. Rates observed 750,000–1,026,000 VND depending on room type.
Data-quality observations: many rows have guest gender defaulted (Nữ), blank DOB/ID, and `?` in Mã QT; a large share of tonight's rooms sit under **one contact label** (a single agent/company name with a phone number in it) with 3-night stays and check-in timestamps at 01:00–06:00 — likely a block booking entered as one repeated label rather than per-guest data.
- `reservation` (id, e.g. 5843) → `reservation_room` (`r_r_id`, e.g. 7447) → `traveller` (guest profile id, `?page=traveller&id=…`). So: a booking holds one or more room-stays; guests are separate profiles reused across stays (there's a "Merge Profile" tool in Reports).
- Backend looks like **Oracle** (date tooltips `18-SEP-26`, `NVL(...)` in sort links). Sort links put raw SQL `ORDER BY` in the query string.
- Money is VND with a USD/exchange-rate secondary; commission is per booking.

## The two hub screens (2026-09-21)

Alex's call, and it reframes the map: **the room map and the tape chart are the two screens that
matter most**, because they are the only two that answer "what is the state of the hotel" — one
for *now*, one *over time*. Everything else in this document is a detour off one of them.
Every role uses both; they use them differently.

| | **Room map** (`room_map`) | **Tape chart** (`monthly_room_report`) |
|---|---|---|
| Answers | state of the hotel **right now** | state of the hotel **over time** |
| Shape | tiles by floor, colour = status | room x date grid, one bar per stay |
| Receptionist | the default screen. Click a tile to check in, see the balance, post a charge | move a stay, extend it, find a gap that fits a caller |
| Manager / owner | glance answer to "how full are we today" (58 / 50 in-house / 5 arriving / 2 ready) | the forward book: occupancy % and rooms sold per night, weeks out |
| Housekeeping (off-system) | which rooms are dirty, read out to them by reception | not used |

Names for the second one: **tape chart** is the PMS term (Opera, Cloudbeds; Mews says Timeline;
older systems "room rack" / "rack chart"). The generic UI pattern is a **resource timeline** —
rows are resources, x-axis is time, bars are bookings, drag to move or resize. That is the phrase
to search when looking for implementations: FullCalendar `resourceTimeline`, Bryntum Scheduler,
vis-timeline, DHTMLX Scheduler.

**For the rebuild**: these two are the home screens, not reports. If only two screens shipped,
these are the two. Both need to be role-aware rather than role-specific — same data, different
default actions and different density per role.

## The group booking flow, properly (2026-09-20)

Correcting an earlier mistake: I had presented the *vacancy forecast report*
(`empty_room_forecast`) as the screen reception quotes from. It isn't. It's a report.
The real quoting path is an availability **engine built into the booking form itself**,
and it produces the same numbers — verified: forecast for 21/09 (VIP 1 · STD2 4 · SUPT 6 ·
SUPD 6 · DLX5 16 · DLXT 2 · DLX6 5 · SUI 0) matches the engine's 21/09 column exactly.

### Two different entry points, and they are not variations of one screen

| Menu | URL | What it is |
|---|---|---|
| **Khách lẻ** (individual) | `?page=reservation&cmd=add&status=CHECKIN&reservation_type_id=2` | Straight into an empty folio editor, already `CHECKIN`. The walk-in path. No availability step at all. |
| **Khách đoàn** (group) | `?page=reservation&cmd=check_availability` | The availability engine + the booking form, one screen. |

So "check availability" is not an optional lookup — for group/company business it *is* the
booking screen. WS3: these are two distinct use cases, not one form with a toggle.

### The engine — `cmd=check_availability`

A room-type × night matrix. `arrival_time` / `departure_time` / `night` drive it, and they work
as GET params (`&arrival_time=21/09/2026&departure_time=28/09/2026&night=7`), so it can be
queried read-only — no form POST needed. See `../tools/availprobe.mjs`.

For each of the 8 room types it returns free rooms **per night** across the whole range, plus
per-night totals: rooms used, rooms free, occupancy %. Weekend columns are highlighted red.
A cell reading `1(1)` = 1 available, 1 out of order (VIP has 2 rooms; 101 is permanently under
repair). Reception reads down a column and quotes against the **tightest night** in the range —
e.g. for 21–28/09, SUPT/TWN runs 6 · 3 · 3 · 4 · 2 · 2 · 2, so only 2 twins are sellable for the
whole week even though night one has 6.

The left half of the same table is the booking entry: per room type, a row of
`adult · child · price VND · price USD · room_quantity · note`. Field names are
`adult_<room_type_id>_<bed_type_id>` — VIP=16, STD2=9, SUPT=10, SUPD=11, DLX5=12, DLX6=13,
DLXT=14, SUI=15; bed type 1=DBL, 2=TWN. **Confirms the aggregate**: a group booking is
`(company, contact, saler, source, deposit, display code/colour)` + N × `(room type, bed type,
qty, adults, children, rate)`. No room numbers anywhere on this screen.

Header fields: from/to with times (14:00 / 12:00 defaults), nights, company (lookup),
saler, contact person, deposit, display code, phone, email, account number, and
`Nguồn` = OTA(21) · TA(1) · WALK-IN(61) · CORP(161). Then two buttons:
**Kiểm tra phòng trống** (recompute) and **Đặt phòng** (create). Same form, same POST target —
only the submit button name differs. We never pressed the second one.

### Group folio routing — the piece I had missed entirely

Inside a room that belongs to a group (`?page=reservation&cmd=edit&id=<res>&r_r_id=<room>`)
there is a nine-checkbox matrix deciding **which charge categories settle on the group's master
bill** rather than the guest's own folio:

`HĐ phòng` (room) · `HĐ buồng` (housekeeping) · `HĐ nhà hàng` (restaurant) ·
`HĐ DV mở rộng` (extended services) · `HĐ điện thoại` (phone) · `Hóa đơn Massage` ·
`HĐ phụ` (sub-invoice) · `Tiền đặt cọc` (deposits) · `Các khoản khác` (other amounts)

On the 31-room MR TÙNG group all nine are on — one bill for everything. This is what the
`create_routing=1` call builds, and it's why that booking renders blank under our read-only
guard. **This is a core group-billing concept and it belongs in the rebuild**: a room-stay's
charges route either to its own folio or to a master folio, per charge category. The company
being billed for rooms while guests pay their own minibar is the normal corporate case.

Related per-room flags found on the same form: `paybygroup`, `foc_all` (whole stay
complimentary), `is_net` (net ++ vs gross rate), `lock_reservation_room`, `close`,
`color-display-of-team` (the group's colour on the room calendar), `roomrate` (a rate-plan
dropdown, set to `---` — again, no rate plans in use), `traveller_level_id` (guest class),
`method_payment`, and `Ghép đoàn` = merge this room into an existing group.

Room-stay statuses, from the `T.Thái` control: `Checkin · Checkout · Khách đặt (booked) ·
Hủy bỏ (cancelled) · Đóng (closed)`.

### Also seen

`?page=reservation&cmd=edit&id=4589` without `r_r_id` returns a raw Oracle error to the browser:
`ORA-00936: missing expression — select block_id from reservation_room where id=`.
Unparameterised SQL built by string concatenation, echoed to the user. Consistent with the
PHP errors already noted on `?page=employee`. Not our problem to fix, but it says something
about what the client is running today.

## The individual booking flow (2026-09-21)

`Khách lẻ` → `?page=reservation&cmd=add&status=<STATUS>&reservation_type_id=2`.
Screenshot: `fd-walkin-form`.

**There is no availability step and no separate check-in screen.** One form, 95 fields across
12 tabs, ending in one of two buttons in the top right:

- **Đặt phòng** → the room-stay is created `BOOKED` (a future reservation)
- **Checkin** → created and immediately `CHECKIN` (the walk-in case)

The `status=` in the URL makes no difference to what renders — both buttons are always there.
The status is decided by which button reception presses. WS3: this is *one* use case with two
exits, not two screens.

### How it differs from the group flow

| | Individual | Group |
|---|---|---|
| Availability | none — reception already knows | room-type × night matrix, inline |
| What's picked | **a specific room**, from a `Phòng` dropdown | room **type** + quantity |
| Assignment | immediate | deferred (waiting list) |
| Quantity | always 1 | N per type |
| Commit | `Đặt phòng` **or** `Checkin` | `Đặt phòng` only |

So room assignment is early-bound for individuals and late-bound for groups. Same underlying
`reservation_room`; different capture order. A booking made here can be pulled into a group
later — `Ghép đoàn` (merge) and the `block_id` dropdown are both on this form.

### Things on this form that matter for the rebuild

- **Per-night rate override.** The `Lược đồ giá` (price chart) tab holds one row per night
  (`date_1`, `date_2`, …). So a single stay can carry a different rate each night, by hand —
  the closest thing to a rate plan in the system, and evidence the client already needs
  date-varying pricing.
- **Early check-in / late check-out are rate multipliers, not flags**: `0 / +0.3 / +0.5 / +1`
  of a night's rate. This is the concrete mechanic behind the "stay rules" Alex flagged as a
  change target — it's a surcharge fraction, decided per booking.
- **Guest class** `traveller_level_id`: individual · VIP 1 · VIP 2 · Guest return. Separately
  `card_vip_type`: SILVER · GOLD · DIAMOND · PLATIUM · COMPANY.
- **Card data, in full, including CVV** — `card_holder_name`, `card_number`,
  `card_exprire_date`, `card_type_id` (bank list: Agribank, Maritime, Vietcombank, BIDV,
  Bắc Á, Sacombank, VISA), `cvs_code`. Confirms the PCI surface we are deliberately not
  rebuilding.
- **Flight details** (`Chuyến bay` tab): inbound/outbound flight number, date and time.
  This is what feeds the airport pickup / see-off list.
- **Full ISO nationality list** (`nationality_id`) — required by PA18 and by the breakfast
  nationality roll-up, and empty on almost every real booking.
- Money controls: `FOC` / `foc_all` (complimentary), `discount_percent`, `discount_money`,
  `discount_vip`, a discount **reason** field, tax, service fee, and `Hoa hồng` (commission,
  % or absolute) — commission is per booking, not per channel.
- `is_net` (net ++ vs gross), `lock_reservation_room`, `Package` dropdown (empty),
  `roomrate` (empty — no rate plans), source = CORP · WALK-IN · OTA · TA.
- A guest table at the bottom: **several travellers per room-stay** (`Thêm khách`), each with
  their own name, gender, DOB, ID, nationality and dates.

### The tape chart

`fd-room-situation` / `hk-room-status` (`monthly_room_report`) is a **tape chart** — the standard
PMS name for a room × date grid with stay bars (Opera and Cloudbeds both use it; Mews calls it
Timeline, older systems "room rack" / "rack chart"). Generic UI pattern: a **resource timeline**
(rows = resources, x = time, bars = bookings, drag to move/extend) — the term to search for
implementations, e.g. FullCalendar `resourceTimeline`, Bryntum Scheduler, vis-timeline, DHTMLX.

It is **not just an owner's report** (Alex, 2026-09-21): dragging a bar moves or extends a
reservation, which makes it a primary receptionist surface — arguably *the* one, since it shows
availability, assignment and length-of-stay in one view. The rebuild should treat it as a core
interactive screen, not a chart.

## Charges and the config behind them (2026-09-21)

### The charge types

Eight buckets, and they are fixed — they are the columns of the hotel revenue report
(`rpt-fd-revenue`) and the nine switches of the group routing matrix:

| Bucket | Posted from | List screen |
|---|---|---|
| Room | the booking itself (rate x nights) | `rpt-room-revenue-daily` |
| Room surcharge | early check-in / late check-out multipliers on the booking | — |
| Minibar | room tile → MINIBAR | `minibar_invoice` |
| Laundry | room tile → LAUNDRY | `laundry_invoice` |
| Compensation / damages | room tile → COMPENSATION | `equipment_invoice` |
| Extended service (DV mở rộng) | room tile → EXTRA SERVICE | `extra_service_invoice` |
| Telephone | PBX integration (`Số giây / block` in settings) | — |
| Restaurant | restaurant POS (dormant) | `restaurant_*` |

**The posting entry point is the room map tile**, not the invoice pages. Clicking a tile opens
the detail modal (`fd-room-detail-panel`) whose footer is exactly:
`DIRTY · MINIBAR · LAUNDRY · COMPENSATION · EXTRA SERVICE`. The `*_invoice` pages are the
*registers* — search/filter/see what's been posted — and their `cmd=add` route is permission-denied
for our reception account, which suggests posting really is meant to happen from the room.

Charges carry: room, date, item(s) + quantity, unit price, total, the booking's RE code, who
created it, who last edited it, and a free-text note. Minibar and laundry lines are itemised
(a single invoice can hold several items with quantities); extra services are one line each.

### The item catalogues — recovered from the data, since the masters are locked

- **Minibar** is modelled as **one minibar per room** (`minibar_id` = `Minibar101`, `Minibar103`,
  … 58 of them), not as a single product list. So it's a stock location per room, which is why
  "unlimited import" is a setting. Items seen: Nước Suối, Bò Húc, Mì Ly, Cocacola, Bia Tiger.
- **Laundry** items are per-garment: Quần Tây, Áo Sơ Mi, Quần Đùi, Vớ, Áo Lót, Quần Bò, Quần Lót,
  Quần Ngắn, Áo Thun. There is an express-laundry surcharge rate in settings.
- **Extended services** — 19 items in two groups (`ROOM`, `EXTRA_SERVICE`). The list is a mess
  and worth seeing, because it is the argument for a managed catalogue:
  `Card Fee` · `Phí thẻ` (the same thing, twice) · `Check out lately` · `Checkout Later`
  (again, twice) · `Check in early` · `Ô tô sân bay/Taxi airport` · `Taxi` · `Transportation`
  (three overlapping) · `dịch vụ` ("service") · `Cái Mới` ("new thing") · `Ăn Sáng` ·
  `Business center` · `Vé máy bay/ Air ticket` · `Restaurant` · `Refund` ·
  `Giam tru tien dien thoai` · `Dịch vụ khác / Other`.
- **Note the overlap**: early check-in / late check-out exist *both* as rate multipliers on the
  booking form (+0.3 / +0.5 / +1 of a night) *and* as extra-service catalogue items. Two ways to
  charge the same thing, which is why the same fee shows up in different buckets.

### The config flow — it exists, and it is split in two

**1. Item masters — separate pages, all permission-blocked for reception.**
Probing confirms these pages exist (they return "Bạn không có quyền truy nhập phần này" rather
than an empty shell — see `../tools/pageprobe.mjs`):

`room` · `room_type` · `product` · `minibar` · `minibar_product` · `laundry` · `service` ·
`extra_service` · `category` · `package` · `currency` · `restaurant_product`

These are where rooms, room types, minibar items, laundry items and service items with their
prices are maintained. **We cannot see any of them** on a reception account, and we are not going
to chase an admin login for it (Alex, 2026-09-23). The masters are inferrable from the data and the
posting dropdowns, and the rebuild is designing its own setup surface anyway — see
*Setup / configuration is its own scope* below.

**2. Charge behaviour — in Settings (`?page=setting`), and reception *can* see it.**
The settings page has **26 tabs**, not the 8 recorded earlier. The relevant ones:

- **Thuế - Dịch vụ** (`sys-charge-config`) — per charge type: service charge %, tax %, and a
  net/gross flag. One row each for reception/room, minibar, laundry, extended service, tour,
  karaoke, restaurant, SPA, VIP card, breakfast. **Every tax and service charge is 0** and
  everything is `is_net=1` — they charge gross, with no VAT line. Also holds
  `laundry_express_rate` (express surcharge) and breakfast adult/child default price + serve time.
- **Nghỉ giờ** (`sys-hourly-pricing`) — **the only genuine price table in the system**: an
  hourly/day-use policy list, `1 gio = 400,000` and `2 gio = 500,000` VND, with "add price policy".
  Day-use stays are a product line nobody has mentioned yet.
- **Cấu hình đặt phòng** (`sys-booking-rules`) — the booking rules, and several are decisions the
  rebuild has to make explicitly:
  `time_next_date = 23:59` (the day boundary — when room charge rolls),
  `auto_count_adult` / `auto_count_children` with `min_tre_em = 6` (under 6 is a child),
  **`allow_over_room` = on (overbooking is permitted)**, `send_email_when_checkout` (thank-you
  mail), `lay_phong_can_ngay` (auto-assign the room needed soonest), `room_view_by_time`.
- **Chức năng phần mềm** — module switches: minibar, restaurant, karaoke, SPA, tour, tennis, golf,
  pool, gym, football, badminton, warehouse, VAT, passport reader, card module, lock connector,
  auto-lock. Confirms how much of ezFolio is switched off here.
- Per-type tabs also exist for Minibar, Giặt là, DV mở rộng, Tour/nhóm, Karaoke, Nhà hàng, SPA,
  Thẻ vip, Breakfast, plus Sơ đồ phòng / Sơ đồ buồng (map colours), Thông tin mặc định khi nhập
  khách (guest-entry defaults: gender, ID type, nationality), ezHotel booking-engine connection,
  Golf config, ezCMS channel-manager config, PA18, Giao diện, Biểu mẫu (print templates).

### What this means for the rebuild

- **A charge is `(room-stay, date, item, qty, unit price, bucket, note, who)`** — one shape across
  minibar / laundry / damages / services. ezFolio has four near-identical screens for it; the
  rebuild needs one posting flow with an item type, reachable from the room.
- **The item catalogue is the config surface the client actually needs**: rooms + room types with
  prices, minibar items, laundry items, service items. Today it is admin-only and invisible to the
  people doing the work, and the extra-service list shows what happens without curation. The rebuild
  designs this fresh rather than copying ezFolio's version — see *Setup / configuration is its own
  scope*.
- **Tax and service charge are per charge type, and currently all zero.** Keep the capability
  (VN hotels commonly run 5% service + 8–10% VAT) but do not assume they use it.
- **Early/late fees are charged as catalogue items in practice** (Alex, 2026-09-21) — the extra-service
  entries, not the booking-form multipliers. The multipliers are unused. Rebuild: early check-in /
  late check-out are ordinary catalogue charges.
- **Day-use / hourly stays are configured but not used** (Alex, 2026-09-21: SoLex sells daily only). The `1 gio` / `2 gio` policies are leftover config. Out of scope for the rebuild.
- **Overbooking is allowed today** (`allow_over_room`), and the tape chart sells >100% occupancy
  on turnover days. The rebuild needs an explicit stance.

## Lifecycle & money — architect Qs, 2026-09-23

Answers to `solex-architect`'s ten questions. Everything below is **observed** — read out of the
live booking editor's markup, its read-only AJAX endpoints, and the receivables screens — unless
marked *inferred* or *open*. Nothing was clicked that writes. Method: the booking editor loads its
numbers over `save_reservation_room.php?<verb>=1`; the read-only guard lets `get_*` / `list_*` /
`load_*` through and blocks the rest, so the whole money model could be read without touching it.

### 1 · Settlement — there is no payment screen, there is a checkout dialog

There is no `payment` / `cashier` / `invoice` page (probed: all return the empty shell). Settlement
happens **inside the booking editor**, and there are two buttons:

- **`Checkout`** — the careful path. Runs `check_deposit_before_checkout`, forces
  `departure_date = today`, reloads the balance, `check_total_room()`, then saves with
  `status = CHECKOUT`.
- **`Fast checkout`** — the same deposit check, then opens the **`quickout` dialog**, which *is*
  the payment act. One row **per room-stay**:
  `Phòng · SL Còn (balance) · Phương thức thanh toán · Loại tiền (VND/USD) · Số thẻ · Ngân hàng`,
  with the exchange rate in the header. **Post** fires
  `save_reservation_room.php?quickOut=1&id=<res>&r_r_id=<room-stay>&payment_type=&card_number=&bank_id=&currency=`
  and then opens the folio/invoice window.

**Payment methods** are a real list (`list_pay_out=1`): `2 Tiền mặt` (cash) · `3 Thẻ tín dụng`
(card) · `6 Chuyển khoản` (transfer) · `9 FOC` · **`10 Công nợ` (debt)**. Banks/card types are a
separate catalogue (`get_card_type=1`: AGRIBANK, VCB, BIDV, SACOMBANK, VISA, MASTER, JCB, HSBC …)
each carrying `allow_payment` and `bank_fee`.

- **Split payment**: the dialog is one row per room, one method per room — so a *group* splits by
  room, but **a single room's balance cannot be split across two methods in this dialog**. Splitting
  one room's bill is done the other way round, by splitting the **folio** first (see #4).
- **Partial / unpaid balance → `10 Công nợ`.** That is the debt method, and it is what creates the
  receivable. There is no separate "create receivable" action.
- **Checkout vs Đóng are different things.** `Checkout` is the room-stay's status. **`Đóng` (Close)
  is the night audit closing a day's revenue** — the audit's own strings are
  `Danh sách phòng chưa đóng doanh thu` ("rooms whose revenue isn't closed"), `Đóng tất cả`,
  `need_to_close_all_revenue_in_date_to_continue`, `need_to_close_all_debit_in_date_to_continue`.
  So **Closed ≠ folio settled**; closed = the accounting day is sealed and can't be reopened. A
  checked-out room can be closed while still carrying a receivable.

### 2 · Receivable lifecycle

`?page=giveback_debit` ("CẬP NHẬT CÔNG NỢ") is the ledger, and it is a per-folio list, not
per-booking:

`STT · Mã đặt phòng (reservation) · Số RE (folio id) · Công ty/Tên khách · Tổng nợ · Đã thanh toán ·
Còn lại · Ngày tạo + user · Thanh toán`

- **Grain: one row per folio**, linked to `?page=reservation&cmd=show_invoice_new&folio_id=<n>`,
  and to the room-stay it came from. One booking with two rooms shows up as two rows.
- **Created** by checking out with `payment_type = 10 Công nợ`. `Ngày tạo` + the user stamp are the
  only provenance.
- **Settled** by the per-row action →
  `?page=giveback_debit&detail=1&id=<r_r_id>&total_debit=<amount>`, a small form:
  **amount (prefilled with the remaining, editable) · pay item · payment method
  (Tiền mặt / Thẻ / Bank tranfer) · note → Lưu**.
- **Partial settlement: yes** — the amount is editable and the list keeps `Tổng nợ / Đã thanh toán /
  Còn lại` separately.
- **No due date anywhere.** No due-date column, no due-date field. "Overdue" is age only — the Sept
  ledger has rows created in April still unpaid next to rows from yesterday.
- **Who**: the same reception login. There is no separate AR role.
- **Rebuild note**: the debt payment method is doing double duty as "close the folio" and "open a
  receivable". Worth separating: *settle* (method, amount, date) and *the unsettled remainder is the
  receivable*, which also gives partial settlement at checkout for free.

### 7 · Nightly room-charge posting — confirmed, it posts per night

`get_room_charge=1&id=&r_r_id=` returns **one row per night**, each with `in_date`, `change_price`
and an **`is_post` flag**. For a live 18/09→28/09 stay read on 23/09:

| night | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 |
|---|---|---|---|---|---|---|---|---|---|---|
| `is_post` | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |

Every night is 1,100,000. Five posted, tonight and the rest not yet. And the folio agrees:
`load_if_room_payment_total` → `totalroom: 5,500,000` = **5 × 1,100,000 = the posted nights only**,
`totalservice: 20,000`, `total / remaining: 5,520,000`, `deposit: 0`, `payment: 0`.

So: **the room charge for night N posts at the end of day N** (`time_next_date = 23:59`), and
**the in-house folio genuinely grows nightly**. A guest's balance mid-stay is nights-so-far, not
the whole stay.

Two consequences:

- The `Advance Post Room Charge` tab exists precisely because of this: it lists the *unposted*
  future nights with checkboxes (posted ones come back `dis: 1`, disabled) and posts them early
  via `save_post_room_charge_group=1`. That's how you take money before the nights have run.
- **The daily room revenue report is not the folio.** It lists occupied rooms × rate for the date,
  including tonight's room whose charge has not posted yet. So `rpt-room-revenue-daily` is an
  *occupancy projection*; the folio is *posted charges*. They agree at the end of the day and
  disagree all day. For the rebuild's "revenue today", **say which one you mean.**
  (This resolves §10 #1: room revenue is posted, not computed at checkout.)

### 8 · Date semantics — nights, departure date exclusive

Same booking: `arrival_time 18/09/2026`, `departure_time 28/09/2026`, and exactly **10 charge rows,
18/09 … 27/09**. The departure date has no charge row.

- **Departure date is exclusive.** The room is sold for nights, not dates.
- **The availability engine counts nights** — consistent with the room-type × night matrix.
- So **"double booking" = same room, overlapping nights**, not overlapping dates. A stay departing
  the 23rd and one arriving the 23rd are not in conflict, which is why the tape chart looks
  >100% on turnover days without anything being wrong.
- **`allow_over_room` is therefore about genuine overbooking** — selling more room-nights than
  exist on a night — not about turnover-day arithmetic. It is on.

### 5 · Deposits

- The deposit is **a number on the booking** (`Đặt cọc`), surfaced as `deposit` in
  `load_if_room_payment_total` and as a column on the unassigned-bookings list. It is checked
  before both cancel (`check_deposit_2`) and checkout (`check_deposit_before_checkout`) — checkout
  is *blocked* if that check fails.
- **On cancellation it is forfeited by hand, as a charge.** When a room with a deposit is
  cancelled, ezFolio offers two doors: downgrade to `BOOKED` with a pre-checkin reason, or open
  `?page=extra_service_invoice&deposit=1&cmd=add&add_prepayment=1&service_id=38` — i.e. **post the
  deposit as an extra-service line (service 38)** so it becomes revenue. There is no automatic
  forfeit and no refund path in the UI.
- *Open*: whether the deposit carries its own method/date as a payment record, or is only the
  number plus the `rpt-deposit` report row. The report shows method (cash / bank), so *inferred*:
  a deposit is recorded as a payment, and the booking caches the total.

### 6 · Cancellation and no-show

**Cancel** (`Hủy đặt phòng`) is guarded, and the guards are the interesting part:

- `Phòng đã CHECKIN không thể hủy` — **a checked-in room cannot be cancelled.**
- `Phòng đã dùng dịch vụ — bạn phải chuyển dịch vụ sang phòng khác thì mới được CANCEL phòng` —
  **if charges have been posted, you must move them to another room first.** Cancel is only for
  a clean room-stay.
- If a deposit exists → the pre-checkin / forfeit fork above.
- Otherwise: confirm with a **mandatory reason** → `status = CANCEL`, saved.
- There is a further guard on days already stayed.

**No cancellation charge is posted.** Status change plus a reason, and the deposit handled
manually.

**No-show** (`Không đến`) is thinner still: `save_reservation_room.php?no_show=1&r_r_id=&noshow=1`
— **a flag on the room-stay**, no charge, no reason. It appears as an `is_NOSHOW` filter on the
reservation list.

**Groups**: cancel is per room-stay, so a partial cancel is "cancel these N room-stays" rather than
"reduce qty". *Open*: the 149 Sept cancellations against what base — the cancellation list doesn't
show a denominator and I won't guess one.

### 3 · Group lifecycle after booking

- **`?page=waiting_list` — "DANH SÁCH ĐẶT PHÒNG CHƯA GÁN"** (bookings not yet assigned to a room)
  is the assignment queue. Columns: Folio ID · Mã hiển thị · Tên KH · **Hạng phòng (room type, not
  room)** · dates · status (BOOKED/CANCEL) · **Đặt cọc** · X/N · note.
  Note this is a *different* page from `?page=reservation&cmd=waiting_list`, which is the ordinary
  reservation list with `is_BOOKED / is_CHECKIN / is_NOSHOW / is_CHECKOUT` filters and an `Đoàn`
  (group) filter.
- **It is empty for the whole of September.** So in practice rooms are assigned at booking time and
  nothing waits. The room-type-only state exists in the model but isn't lived in. `lay_phong_can_ngay`
  (auto-assign the room needed soonest) is on, which fits.
- **Check-in is per room-stay**, not per group — every status verb in the editor operates on one
  `r_r_id`. So partial arrivals and early departures of individual rooms are the normal case, not
  an exception. Same for cancel and no-show.
- **The rooming list is largely not entered** — consistent with the 31-room group under one repeated
  contact label. The guest tab exists per room-stay; nobody fills it.
- *Open, for Alex by walkthrough*: whether reception assigns a group's rooms from the tape chart or
  by editing each room-stay. Both are possible; the drag on `hk_room_status` is the likely answer.

### 4 · Master folio

**A folio is a bill you construct, not a fixed per-booking object.**

- `sp_FOLIO.php?list_folio=1&r_r_id=` returns `{old: [], new: []}` — folios are created on demand,
  and the booking I read has none.
- The **FO tab** lists them (`STT · Mô tả · Tổng · Còn lại · Xem hóa đơn` → `view_folio(id)`).
- **`Chuyển dịch vụ`** (the `#folio` button) opens a two-pane multiselect: pick a room, pick which
  service lines move onto it, save via `save_invoice_info.php?…&t=<type>&tid=&nid=&rid=&nidold=`.
  So **splitting and merging bills is done by moving charge lines between rooms/invoices.**
- That is the master folio: **one folio carrying lines from several room-stays**, assembled this
  way, and reached in the receivables ledger as one `Số RE` row against the company. The nine
  group-routing switches are the automatic version of the same move, applied at posting time.
- **Settlement of the master** is then ordinary: it is a folio with a balance, so it either gets a
  method at checkout or becomes one `Công nợ` row against the company. The corporate case is
  therefore *straight to a company receivable* in practice — which is exactly what the debit
  ledger shows, corporates and OTAs side by side.
- Careful with the label: **the booking form's "FolioID" is the reservation id** (booking 5843 shows
  "Folio id: 5843"). The ledger's **`Số RE` is the real folio/invoice number** and is a different
  sequence. Two different things wearing one name.

### 9 · Room status

The status vocabulary is `INSPECTED` (`readyen`) · `CLEAN` (`houseuseen`) · `DIRTY` · `OOO`
(`repairen`), and the room map / tape chart (`?page=hk_room_status` — note the tape chart lives
under **Buồng**, housekeeping, not front desk) colour by it.

*Partly open.* What I can say: **DIRTY is a manual quick-action on the room tile** — it sits in the
tile footer next to MINIBAR / LAUNDRY / COMPENSATION / EXTRA SERVICE, so reception marks it. That
strongly suggests the transitions are **manual, driven by reception on housekeeping's word**, which
matches a hotel with no housekeeping logins in daily use. Whether checkout auto-dirties, whether
check-in requires clean, whether INSPECTED is ever used, and whether OOO demands a reason are
**observable only by doing it** — they need Alex's walkthrough, not another probe.

### 10 · Mid-stay changes

- **Move room**: `?page=change_room` — a `from room (occupied)` → `to room (vacant only)` picker,
  nothing else. No rate question, no date question. Already-posted nights stay on the folio; the
  move is recorded and shows up in `rpt-room-transfer`. So **a room move does not re-price.**
- **Extend / shorten**: change the departure date on the booking; the per-night charge rows are
  regenerated for the new span. **Already-posted nights are not touched** — they carry `is_post=1`
  and come back disabled.
- **Change rate**: there is no rate-change *event*. The **price chart** (`Price chart` tab) is a
  per-night editable price list, gated by an `allowchangeprice` flag; each night's `change_price`
  is just edited. There is also `update_reduce_amount` — a post-hoc discount on the room-stay,
  editable after the fact, behind an explicit "edit" toggle.
- **Rebuild note**: this is the weak spot in their model. A night's price is mutable state with no
  history, so "why is this folio 200k lighter than the rate card" is unanswerable after the fact.
  Nights already posted being immutable is the one good instinct here — keep it, and make a price
  change an event rather than an edit.

### The two small ones

- **(a)** Fixed — the board's findings panel said "TWO REAL PERSONAS" in one place and "THREE
  PERSONAS, NOT TWO" in another. The first now reads three.
- **(b) OTA payment — partly answered, partly open.** OTAs (BOOKING.COM, EXPEDIA, Agoda, Ctrip,
  Traveloka) appear **as debtors in the receivables ledger**, alongside corporates. So for those
  bookings **the guest does not pay the hotel — the hotel bills the OTA**, i.e. prepaid at the
  channel. Whether the receivable is booked **net of commission** is *open*: the booking carries a
  separate `Hoa hồng` (commission, % or amount) field, which suggests the folio is **gross with
  commission tracked alongside**, but I have not tied one Agoda receivable to one folio total to
  prove it. One invoice compared against its booking's commission settles it — a good question for
  Alex rather than another probe.

### What's still open

| # | Open | How it gets closed |
|---|---|---|
| 3 | Whether group rooms are assigned by tape-chart drag or per room-stay edit | Alex walkthrough |
| 5 | Whether a deposit is a payment record with its own method/date | `rpt-deposit` columns, or Alex |
| 6 | Cancellation base rate (149 in Sept against how many bookings) | count the reservation list |
| 9 | Auto vs manual status transitions; INSPECTED and OOO in practice | Alex walkthrough — not probeable read-only |
| b | OTA receivable gross or net of commission | compare one Agoda folio to its booking |

## For other WSs
- **No card data. Ever.** (Alex, 2026-09-20) ezFolio stores card holder / number / expiry / CVV on the booking. The rebuild deliberately does not — no PCI surface. WS3: leave card capture out of the model; WS1: no card fields in the schema.
- **Group / company bookings are a large share of business** (Alex, 2026-09-20; ~2/3 of in-house rooms today are group or company). Model Company, group booking, "merge into group", and receivables by debtor type as core, not later.
- Entity chain to mirror: Reservation → ReservationRoom (per-room stay) → Guest profile (reusable, mergeable).
- Legally-driven: guest declaration / PA18 export exists in the current system. Confirm whether the rebuild must keep it.
- Key-card (door lock) integration exists in ezFolio; **out of scope for the rebuild, possible later feature** (Alex, 2026-09-20).
- **Channel/OTA is encoded in the guest-name string** (AGD/CTRIP/TVLK/EXP suffixes), not a field. Alex confirms (2026-09-20) channel handling is **a manual process today — an explicit improvement target** for the rebuild (systematic channel + commission, not typed suffixes). Rebuild needs a first-class Channel + per-channel commission; migration must parse or re-key these.
- Reports are print-shaped (signature blocks) and every one has **Export to Excel** — Excel is the hotel's real interchange format, and the likeliest data-extraction path.
- Portal/hotel dropdown on reports ⇒ ezFolio is multi-property; SoLex is one property. Rebuild can stay single-property.
- **No rate plans in use** — rates are typed per booking. Rebuild should introduce a rate table (room type × season/day-type) to satisfy "enter room → auto rate"; treat as an *enhancement*, not a like-for-like.
- **Deployment reality of today's system**: Windows server on-prem, LAN IP allowlist, local door-lock file, plain HTTP, vendor-hosted public port. The rebuild on Cloudflare removes the LAN dependency — confirm staff have reliable internet, and that losing the local door-lock hook is acceptable (it is, per Alex: key cards out of scope for now).
- **Source taxonomy to keep**: OTA · TA · WALK-IN · CORP.
- **Real user personas (Alex, 2026-09-20)** — ezFolio ships many role-based modules, but in practice SoLex has **two**:
  - **Manager/owner** — read-only in effect: how is the hotel doing (bookings, reports).
  - **Receptionist** — does everything in the system. Check-in/out is the bulk, but also bookings, charges, payments, receivables.
  Housekeeping, restaurant and the rest operate **off-system** (paper/verbal) and ask reception to make changes. WS3: model two roles, not seven; housekeeping screens are reception-facing, not staff-facing.
- **Stay rules (check-in/out times, charge roll-over, surcharges) are a change target**, not a spec — Alex flagged 2026-09-20; decide later, map first.
- **Channel-manager capability exists but is unused** (ezCMS: Siteminder/Staah). If the client ever wants OTA sync, that's a separate integration, not a port.
- **Housekeeping module is unused** (no staff assigned, no shifts). Rebuild: keep room status changes (clean/dirty/OOO + reason) on the reception-facing map; skip staff scheduling until someone asks.
- **Status vocabulary to reuse**: VC / VD / OC / OD / OOO (+ expected-arrival, expected-departure as derived views).
- **Guest history already exists** with a repeat-stay count and guest class (normal/VIP) — cheap to carry over, and it covers the client's "Guest History" step.
- **Group booking shape**: company + contact + saler + source + deposit + display code/colour, then *per room type × bed type*: quantity, adults, children, rate (VND/USD), note. Rooms assigned later. This is the aggregate WS3 must get right: `Booking(company, dates, [RoomTypeRequest(type, bedType, qty, pax, rate)])` → N `RoomStay`s → assigned `Room`s.
- **Group folio routing is core, not a nicety** (2026-09-20): each room-stay carries nine switches deciding which charge categories settle on the group's master bill vs the guest's own folio (room · housekeeping · restaurant · extended services · phone · massage · sub-invoice · deposits · other). The corporate case — company pays rooms, guest pays incidentals — depends on it. WS3: model `charge.routedTo = ownFolio | masterFolio` per category.
- **Availability is a per-night, per-room-type matrix, and it is part of the booking form** — not a report reception consults first. Quoting means reading down the columns and taking the tightest night. WS3: the booking screen must show availability for the whole requested range, per type, inline.
- **Two booking use cases, not one** (2026-09-21): *individual* picks a specific room and can commit straight to CHECKIN (walk-in) or BOOKED; *group* picks room types with quantities and always defers assignment. Same `reservation_room` underneath; opposite capture order. An individual booking can be merged into a group afterwards.
- **The room map and the tape chart are the two most important screens** (Alex, 2026-09-21) — the only two that answer "what is the state of the hotel", one for now and one over time. Every role uses both, differently (see *The two hub screens*). They are the rebuild's home screens; if only two screens shipped, these are the two.
- **The tape chart is a receptionist tool, not an owner's report**: the room x date grid with draggable stay bars is where moves and extensions happen. Industry name: tape chart / rack chart; generic pattern: **resource timeline** (FullCalendar `resourceTimeline`, Bryntum, vis-timeline). Treat as a core interactive screen.
- **Role differs by density and default action, not by screen.** Both personas want the same two surfaces; the receptionist needs click-to-act, the manager needs the totals. Build one screen with role-aware defaults rather than two screens.
- **Per-night rates already exist by hand** — the price-chart tab holds one rate row per night of a stay. The client needs date-varying pricing today; a rate table would formalise what they already do manually.
- **Early check-in / late check-out**: the booking form offers rate multipliers (+0.3 / +0.5 / +1 of a night), but in practice they are charged as extra-service catalogue items (Alex, 2026-09-21).
- **Commission is captured per booking** (% or absolute), not per channel - another reason a first-class Channel with its own commission is an improvement, not a port.
- **Several travellers per room-stay** - the guest table on the booking form takes N people, each with their own identity fields. Model RoomStay -> many Guests, not one.
- **Booking can exist without a room** (waiting list) — model room assignment as a separate step from booking; room *class* is bookable.
- **Discounts carry an approval trail** (requested / edited / approved, with users). If the owner wants control over discounting, that's a real feature, not decoration.
- **Every mutation is attributed** (created-by / edited-by / checked-in-by, per-booking "Show log"). An event-sourced rebuild gets this for free and should keep it visible.
- **Extra-service catalogue to carry over**: breakfast, early check-in, late check-out, airport transfer, laundry, minibar, damages, other — each with qty, price, discount, tax, service fee.
- **~11–13 user accounts exist** but only two personas matter (above); several accounts are vendor/admin (`administrator`, `itezcloud`).
- **Night audit is the formal day-close and it is switched off** — so "today's revenue" is computed ad-hoc from reports. The rebuild's day-boundary rule (charge roll at 23:59) needs an explicit decision.
- **The config flow is split in two** (2026-09-21): *item masters* (`room`, `room_type`, `product`, `minibar`, `minibar_product`, `laundry`, `service`, `extra_service`, `category`, `package`, `currency`, `restaurant_product`) are separate pages, all permission-blocked; *charge behaviour* (tax %, service charge %, net/gross, express rate, breakfast price, hourly price policy, booking rules) is in Settings and reception can see it. WS3: the item catalogue is the config surface the client actually needs.
- **A charge has one shape across all types**: `(room-stay, date, item, qty, unit price, bucket, note, who)`. ezFolio has four near-identical screens (minibar / laundry / damages / extended service); build one posting flow with an item type, entered from the room.
- **Posting happens from the room map tile**, not the invoice pages — the tile modal footer is DIRTY / MINIBAR / LAUNDRY / COMPENSATION / EXTRA SERVICE. The `*_invoice` pages are registers.
- **Early/late fees are catalogue items** (Alex, 2026-09-21). The booking-form multipliers (+0.3 / +0.5 / +1) exist but aren't used. Rebuild: model early check-in / late check-out as ordinary catalogue charges; drop the multiplier mechanic.
- **Day-use / hourly stays: configured, not used** (`Nghỉ giờ`: 1 hour 400k, 2 hours 500k). Alex, 2026-09-21: SoLex is daily only. Out of scope.
- **Overbooking is switched on** (`allow_over_room`), and the day boundary is `time_next_date = 23:59`. Both need an explicit decision.
- **Child age threshold is 6** (`min_tre_em`), adults/children auto-counted from the guest list.
- **All tax and service charges are 0 and everything is net** — they charge gross with no VAT line. Keep the capability, don't assume the usage.
- **Setup / configuration is its own scope, with its own persona** (Alex, 2026-09-23). ezFolio's masters are permission-blocked and we are *not* pursuing an admin login: the rebuild builds this surface itself. That adds a third persona to the two operational ones:
  - **Manager/owner** — reads how the hotel is doing.
  - **Receptionist** — runs the day.
  - **Setup/admin** — defines what the system is made of: rooms and room types with their prices, the minibar / laundry / extra-service catalogues with prices, tax and service-charge behaviour, and the booking rules (day boundary, overbooking, child age). Used rarely, mostly at onboarding and when prices change; likely the owner rather than a separate person.
  Everything WS2 could observe about this surface is in *Charges and the config behind them*: the split between item masters and charge behaviour, the eight buckets, and the settings that actually carry values. The ezFolio screens are a reference for *what needs configuring*, not a design to copy — their extra-service catalogue is the argument against copying it.
- **Candidate core for the rebuild** (WS3 decides; this is WS2's read of what is actually used): bookings incl. group/company + waiting list · room assignment & room status · check-in / check-out · folio with extras (minibar, laundry, extra bed, breakfast, late/early, transfer, damages) · payments incl. deposits · receivables by debtor · guest profiles w/ history · revenue + occupancy reporting · PA18 export · user attribution/audit. **Out**: restaurant POS, housekeeping scheduling, key cards, golf, multi-property, channel-manager sync (later), card storage (never).
- **Cancellation and no-show are statuses, not deletions** — keep them as events on the room-stay (matters for OTA no-show charging and for honest occupancy history).
- **Breakfast is counted per stay** (vouchers, adults, children) and printed daily — small but load-bearing for the restaurant handoff.
- **Migration is deferred — the rebuild starts fresh** (Alex, 2026-09-20). Broken export is not a blocker; data import gets figured out after the fact. WS1/WS3: design the schema for the domain, not for an import. Scraping stays available as a fallback (every screen is server-rendered) and the option to ask ezCloud for a DB export stays open but is not on the critical path.
- **Identity capture is broken in practice, not just thin** (visual pass, 2026-09-20): ID number is `?` on
  every row of the daily revenue report, DOB blank, gender defaulted. PA18 is a legal export built on data
  nobody enters. WS3: decide whether the rebuild enforces identity at check-in.
- **Channel + external booking reference already exist per booking**, encoded as company + "Mã hiển thị"
  (real OTA refs: CTRIP / Traveloka / Agoda / Expedia). Promote both to first-class fields — the data is
  there, the model isn't.
- Open, parked: *which* of the ~60 booking-editor fields reception actually uses daily. Worth answering before scoping the booking form; not a blocker now (Alex, 2026-09-20).

## Visual pass over every screenshot (2026-09-20)

Until now most screens were mapped from *extracted text* (headings, table headers, controls) rather than
from the image. This pass opened all 41 PNGs in `../screens/` visually. Two outputs: capture quality
(which images are usable), and facts that only the rendering revealed.

### Facts that only the images showed

- **The app surfaces raw DB connection errors to reception.** `fd-booking-list-inhouse` carries a red
  banner: `Error: Lỗi kết nối Database` sitting on top of a fully-rendered list. Staff are trained to
  ignore it. Reliability of the current system is worse than the feature map suggests.
- **Guest identity data is essentially not captured.** On `rpt-room-revenue-daily` (51 rooms), the
  ID-number column is `?` for every row, DOB is blank, and gender is defaulted. PA18 is a legal
  obligation and the data behind it is not there. The rebuild should decide whether identity capture is
  enforced at check-in or stays optional — it is a product decision, not a schema detail.
- **The folio's revenue buckets are fixed and visible** (`rpt-fd-revenue` column groups):
  room · room surcharge · minibar · laundry · compensation/damages · extended service · telephone ·
  SoLex Restaurant. Settlement splits into cash VND · cash USD · card VND · card USD · bank transfer ·
  complimentary · debt. Refunds appear as negative rows (`-425,000`, note "Hoàn lại tiền").
  This is the charge/settlement model to mirror.
- **Deposits are per reservation, pre-arrival, with a payment method** (`rpt-deposit`): cash / bank
  transfer / card, status BOOKED → CHECKIN → CHECKOUT, ~167M VND collected in September. Some rows carry
  an OTA reference (`VNTRIP2026C8SG`).
- **OTA identity *is* in the data, just not as a field.** `rpt-debit-detail` groups receivables by
  `CTRIP / TVLK (Traveloka) / AGD (Agoda) / EXP (Expedia) / WELDCOM / HNH`, and the "Mã hiển thị" column
  holds real OTA reference numbers (`20261123657918`, `1128150653526780`, `1770008125`).
  `sales-companies` lists Booking.com, Asiabooking etc. as Agent/Company rows with a `Nguồn` of OTA/TA/CORP.
  So the manual process Alex described still produces a per-booking channel + external reference —
  the rebuild should promote both to first-class fields rather than invent them.
- **Housekeeping status vocabulary, confirmed from the legend** on `hk-employee-schedule`:
  `OD` occupied dirty · `OC` occupied clean · `VD` vacant dirty · `VC` vacant clean ·
  `VCI` vacant clean inspected · `OOO` out of order. The same report carries arrive/depart clock times
  and free-text room notes ("14H OUT", "phòng sếp", "RỂ Ở").
- **Room-map colour legend**: green = ready · grey = dirty · orange = occupied & dirty · white = occupied
  & clean · black = under repair.
- **Restaurant module is dormant, not just out of scope.** All 30 tables on `rest-table-map` are empty and
  `rest-revenue-by-item` returns zero rows for the day — yet `rpt-fd-revenue` still reserves a
  "SoLex Restaurant" column on every folio. Confirms: skip the POS, keep a restaurant charge line.
- **Breakfast is derived, not booked** (`fd-breakfast`): one row per occupied room for the date, split
  into actual (50 rooms / 50 guests / 38 adults) and expected (`Dự kiến ăn sáng`, 4 rooms / 8 guests),
  with a nationality roll-up at the bottom (VN 31 / other 19). Nationality is tracked for breakfast
  and PA18, and nowhere else.
- **Concrete config values** from `sys-settings` › Thông tin khách sạn: default check-in 14:00,
  check-out 12:00, Sunday and Saturday surcharge fields (both 0), bank fee 0, rounding to 2 decimals,
  payment difference under 500 VND ignored, day-cut window `[00:00-23:59]`, default walk-in group code
  `Walk -n`, shift-close/night-audit toggle **off**, IP allowlist `[192.168.9.]`, currency VND.
  Property: SOLEX HOTEL, 31 Núi Thành, P.13, Q. Tân Bình, TP HCM. Other config tabs exist but are
  permission-blocked: reception config · accounts · tax & service · software functions · PA18 ·
  interface · templates.
- **Occupancy runs high and is seasonal-lumpy** (`fd-occupancy-over-time`, September): 8.77% to 108.77%
  daily occupancy (>100% = same-day turnover), 57 sellable rooms, 1 permanently out of order,
  month total 767M VND room revenue, ADR ~800k, 149 cancellations in the month.

### Capture quality

Usable as-is (26): `fd-room-map`, `fd-room-situation`, `fd-booking-list-inhouse`, `fd-room-detail-panel`,
`fd-arrivals-today`, `fd-cancellations`, `fd-guest-history`, `fd-traveller-list`, `fd-reservation-summary`,
`fd-group-availability`, `fd-extra-service`, `fd-minibar-invoice`, `fd-laundry-invoice`, `fd-breakfast`,
`fd-forecast-by-type`, `fd-occupancy-over-time`, `hk-room-status`, `hk-employee-schedule`,
`rest-table-map`, `rpt-room-revenue-daily`, `rpt-debit-detail`, `rpt-deposit`, `rpt-fd-revenue`,
`rpt-revenue-by-invoice`, `sales-companies`, `sys-settings`.

Empty — the screen rendered correctly but had **zero rows** on 20/09 (9):
`fd-departures-today`, `fd-waiting-list`, `fd-noshow`, `fd-pickup-seeoff`, `hk-lost-found`,
`rest-revenue-by-item`, `rpt-debit-summary`, `rpt-room-transfer`, `rpt-room-discount`.
Useful as evidence of *what the hotel doesn't do*; misleading if presented as a flow step.
Re-capture over a wider date range if they're needed on the board.

Blank forms — correct, but nothing is filled in (4):
`fd-booking-detail` (the folio editor renders with all fields empty — the read-only guard blocks the
`create_routing=1` POST that loads live values; this is our limitation, not the app's),
`fd-change-room`, `fd-pa18-export` (five action buttons, no output), `audit-night-audit`
(useful anyway: it prints the seven-point audit checklist).

Bad captures (2):
- `hk-room-map` — only the "Thao tác" sidebar rendered; the room grid never painted. **Re-capture.**
- `rpt-debit-update` — 1265 × 14,965 px, ~419 rows. Illegible at any board scale. Crop or skip.

## Visual flow board

**Excalidraw (current):** `board/solex-flow.excalidraw` — gitignored, because the board embeds the
screenshots and those carry live guest data. Generated from `tools/excalidraw/flow.json` by
`tools/excalidraw/build.py`; both are committed, so the board can be rebuilt on any machine that
has the screenshots. Open it with the VS Code extension `pomdtr.excalidraw-editor` so edits save
straight back into the file.

**What the board contains** — 9 framed sections, 22 screenshots, arrows only inside the phases
that are genuinely sequential, and text panels carrying the modelling notes:

| # | Section | Screens | The panel says |
|---|---|---|---|
| 1 | The two hub screens | room map · tape chart | why these two, and how each role reads them |
| 2 | Receptionist · 1 · Booking | group availability · walk-in form · companies | the group vs individual aggregate shape |
| 3 | Receptionist · 2 · Arrival | arrivals → tile modal → in-house | — |
| 4 | Receptionist · 3 · During the stay | room move · breakfast · HK sheet | — |
| 5 | Receptionist · 3b · Charges | tile modal → minibar → laundry → revenue buckets | the eight buckets, the catalogue mess, the one charge shape |
| 6 | Receptionist · 4 · Departure & settlement | deposits → folio → receivables | group folio routing (nine switches) |
| 7 | Manager / owner | occupancy trend · daily room revenue · guest history | — |
| 8 | Setup / admin · config | charge config · booking rules · hotel info | what setup has to cover, and why not to copy theirs |
| 9 | What matters for the rebuild | — | core vs out, and the hard findings |

Sections 5 and 8 exist only here — the FigJam board never got them.

**Status: this is the WS2 deliverable in visual form.** It is a map of the *existing* system, not a
design. Nothing on it is a proposal. The flows are what the screens show plus what the field and
permission probes proved; where a step could not be observed read-only (posting a charge, saving a
booking) the board says so rather than inventing the click path.


Rebuild it with:

    cd docs/projects/hotel-backoffice/tools/excalidraw
    python3 build.py flow.json ../../board/solex-flow.excalidraw

**FigJam (frozen):** https://www.figma.com/board/9450fwvpLCLPmAmt4FBsQU — the earlier version of
the same board. Abandoned mid-update: Figma's Starter plan caps the MCP at **20 tool calls per
month**, which is about one editing session, so the charges and config sections were never added
there. The pending script is kept at `tools/figjam/add-charges-config.js` if that board is ever
revived on a paid seat. Treat the Excalidraw file as the source of truth.

## Screen index
| slug | screen |
|---|---|
| `fd-room-map` | front desk room map |
| `fd-room-situation` | room × date availability calendar |
| `fd-booking-list-inhouse` | booking list, in-house filter |
| `fd-room-detail-panel` | room map tile modal |
| `fd-booking-detail` | booking / folio editor (blank) |
| `fd-walkin-form` | individual booking form — Đặt phòng / Checkin |
| `rpt-debit-detail` | receivables detail |
| `rpt-debit-summary` | receivables summary |
| `rpt-room-revenue-daily` | daily room revenue |
| `sys-settings` | system settings (26 tabs) |
| `sys-charge-config` | tax / service charge / net, per charge type |
| `sys-hourly-pricing` | day-use price policies — the only price table |
| `sys-booking-rules` | day boundary, overbooking, child age, auto-assign |
| `hk-room-map` | housekeeping room map |
| `hk-room-status` | housekeeping room status calendar |
| `hk-employee-schedule` | daily room assignment |
| `fd-guest-history` | guest history |
| `fd-arrivals-today` / `fd-departures-today` | arrivals / departures lists |
| `fd-waiting-list` | unassigned bookings |
| `fd-reservation-summary` | booking summary by source/user |
| `rpt-deposit` / `rpt-fd-revenue` / `rpt-revenue-by-invoice` | deposits, hotel revenue, revenue by folio |
| `rpt-debit-update` | receivables ledger (419 rows) |
| `rpt-room-discount` / `rpt-room-transfer` | discounts (w/ approval trail), room moves |
| `audit-night-audit` | night audit |
| `sales-companies` / `fd-traveller-list` / `fd-pa18-export` | companies, in-house persons, PA18 |
| `fd-minibar-invoice` / `fd-laundry-invoice` / `fd-extra-service` | incidental charges |
| `fd-forecast-by-type` | vacancy forecast by room type |
| `fd-group-availability` | group booking / availability grid |
| `fd-change-room` / `fd-cancellations` / `fd-noshow` | room move, cancellations, no-shows |
| `hk-lost-found` / `fd-pickup-seeoff` / `fd-breakfast` | lost & found, airport transfers, breakfast list |
| `fd-occupancy-over-time` | occupancy trend |
| `rest-table-map` / `rest-revenue-by-item` | restaurant (out of scope) |

## Status

- 2026-09-19 — scope confirmed w/ Alex; logged in, identified ezHotel/ezFolio, nav mapped.
- 2026-09-20 — walked front-desk trio: room map, room situation, in-house list. Tooling committed to `tools/`.
- 2026-09-20 — room detail modal + booking/folio editor mapped; entity chain reservation → reservation_room → traveller; screen naming convention adopted.
- 2026-09-20 — visual pass over all 41 screenshots: capture quality triaged, folio revenue/settlement buckets, HK status vocabulary, config values and the identity-data gap recorded.
- 2026-09-20 — group booking flow dug out properly: `cmd=check_availability` engine (GET-drivable), the room-type x night matrix, and the nine-way group folio routing matrix.
- 2026-09-21 — individual booking flow mapped (one form, two exits); tape chart named and reclassified as a receptionist screen.
- 2026-09-21 — board restructured: hub section for the room map + tape chart, then receptionist vs manager tracks.
- 2026-09-21 — charges flow mapped (8 buckets, posting from the room tile, catalogues recovered from data); config flow located: masters blocked, charge behaviour visible in Settings' 26 tabs.
- 2026-09-21 — Alex: hourly stays not used (daily only); early/late charged as catalogue items, not multipliers.
- 2026-09-23 — board moved to Excalidraw (file-based, no API cap); regenerated in full incl. the charges and config sections FigJam never got.
- 2026-09-23 — admin-login question closed by Alex: setup/configuration becomes its own scope with a third persona, designed rather than reverse-engineered.
