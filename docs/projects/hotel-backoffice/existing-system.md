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
- **The tape chart is a receptionist tool, not an owner's report** (Alex, 2026-09-21): the room x date grid with draggable stay bars is where moves and extensions happen. Industry name: tape chart / rack chart; generic pattern: **resource timeline** (FullCalendar `resourceTimeline`, Bryntum, vis-timeline). Treat as a core interactive screen in the rebuild.
- **Per-night rates already exist by hand** — the price-chart tab holds one rate row per night of a stay. The client needs date-varying pricing today; a rate table would formalise what they already do manually.
- **Early check-in / late check-out are rate multipliers** (+0.3 / +0.5 / +1 of a night), chosen per booking. That is the concrete mechanic behind the stay rules Alex wants to change.
- **Commission is captured per booking** (% or absolute), not per channel - another reason a first-class Channel with its own commission is an improvement, not a port.
- **Several travellers per room-stay** - the guest table on the booking form takes N people, each with their own identity fields. Model RoomStay -> many Guests, not one.
- **Booking can exist without a room** (waiting list) — model room assignment as a separate step from booking; room *class* is bookable.
- **Discounts carry an approval trail** (requested / edited / approved, with users). If the owner wants control over discounting, that's a real feature, not decoration.
- **Every mutation is attributed** (created-by / edited-by / checked-in-by, per-booking "Show log"). An event-sourced rebuild gets this for free and should keep it visible.
- **Extra-service catalogue to carry over**: breakfast, early check-in, late check-out, airport transfer, laundry, minibar, damages, other — each with qty, price, discount, tax, service fee.
- **~11–13 user accounts exist** but only two personas matter (above); several accounts are vendor/admin (`administrator`, `itezcloud`).
- **Night audit is the formal day-close and it is switched off** — so "today's revenue" is computed ad-hoc from reports. The rebuild's day-boundary rule (charge roll at 23:59) needs an explicit decision.
- **Admin/config screens are permission-blocked for our account** — room, room type, service and product masters (and presumably users/permissions) are invisible. Need an admin login to document them; masters are currently inferred from dropdowns.
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

## Visual flow board (FigJam)

https://www.figma.com/board/9450fwvpLCLPmAmt4FBsQU — "SoLex — ezFolio user flow (existing system)" (Collie Studio drafts, 2026-09-20).

18 screenshots in five phase sections (booking → arrival → during the stay → departure & settlement →
owner's view), each frame sized to its own image, captioned underneath, connected left→right within a
phase, with a column of rebuild-relevant findings on the right.

Rebuilt 2026-09-20 after the visual pass. Changes: every frame was a uniform 460×420 crop of a
~1280×1270 screenshot — now each is 520 wide at its true aspect ratio. Four weak images were swapped
out: the empty unassigned-bookings list → vacancy forecast, the failed housekeeping map capture →
breakfast list, the 15,000px receivables ledger → hotel revenue (charge buckets × payment method),
the empty departures list → deposits. Wrap-around arrows between phases were dropped (phases read
top→bottom) and connectors straightened.

Screenshots contain live guest data (Alex: acceptable). Regenerate/extend from `../screens/` + `../tools/`.

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
| `sys-settings` | system settings |
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
