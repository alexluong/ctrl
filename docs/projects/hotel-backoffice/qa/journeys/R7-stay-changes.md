# R7: Stay changes and rooms

**Purpose:** show that a booked stay can be changed night by night, and that each room has its own state: in use, out of order, dirty or clean.
**Persona:** Dao, front desk.
**Seed used:** Do Minh Khoa, set up off camera: checked into Twin 402 "last night" (using the day-start shift described in the README), booked for two nights.
**Length:** 1:06. File `R7-stay-changes.webm`.

| # | Step (caption) | Notice |
|---|---|---|
| 1 | Occupancy chart: "any twins free next weekend?" | The "Free of this type" row counts what is left of each room type per night, including nights already promised without a room. |
| 2 | Stay → Nights held → Add a night | The next date is prefilled and the rate comes from the rate table. |
| 3 | Change that one night's rate to 450,000 | A single night can be repriced on its own. |
| 4 | Give the last night back | Back to two nights. Last night is marked "on the bill" and does not change. |
| 5 | Move room: 402 → 401, from tonight | The night already slept stays in 402; tonight onward is in 401. 402 is marked dirty. |
| 6 | Room 402 → Take out of order, with a reason | On the map it shows as out of order, and it is removed from every availability count. |
| 7 | Return to service | Nothing else to set; the room's history records both steps. |
| 8 | Map → 402 → Mark clean | Housekeeping state comes from the map panel; the room is Ready again. |

## In ezFolio today

Every change here is done inside the booking editor or on the tape chart, and none of it leaves a trace beyond the current value (`existing-system.md` § mid-stay changes, § group booking flow, § room status).

1. "Any twins free next weekend?": **Lễ tân › Tình hình** (`screens/fd-room-situation.png`) — rooms grouped by type over 7/15/30 days, bottom rows used / free / %; or the availability matrix on **Khách đoàn** (`fd-group-availability.png`), which counts free rooms per type per night including bookings without a room.
2. Extend / shorten: open the stay in the editor (`fd-booking-detail.png`) and change the **departure date**; the per-night charge rows are regenerated for the new span, posted nights come back disabled (`is_post = 1`).
3. One night's rate: the **Lược đồ giá** (price chart) tab, one editable row per night, gated by `allowchangeprice`. It is an edit, not an event — the old value is gone.
4. Move room: **Lễ tân › Đổi phòng** (`fd-change-room.png`, `?page=change_room`): from room (occupied) → to room (vacant only), nothing else asked; already-posted nights stay on the folio; the move shows up in **Báo cáo › Đổi phòng** (`rpt-room-transfer.png`).
5. Out of order: **Buồng › Sơ đồ buồng / trạng thái phòng** (`hk-room-status.png`, `hk-room-map.png`) — status PHÒNG SỬA (`OOO`) set by hand; whether a reason is demanded was not observable. The room map's PHÒNG SỬA count drops it from supply.
6. Dirty / clean: **DIRTY** is a button on the room tile's modal (`fd-room-detail-panel.png`); the vocabulary is INSPECTED · CLEAN · DIRTY · OOO, transitions are manual on housekeeping's word.

**What SoLex keeps / changes** (ux.md §4.4, §4.7, §4.3):
- Keeps: the tape chart grouped by type with the free-per-type row and the used / free / % rows; move room = pick a free room from tonight; dirty and clean from the map panel.
- Changes: a night's price is an event (`SetNightRate`) and add / give back a night are explicit, so "why is this bill lighter than the rate card" is answerable (§6 Stay); posted nights stay immutable, which is ezFolio's one good instinct kept.
- Changes: out of order carries a reason and the room has its own page with a history (ezFolio has no room page); a move keeps the slept nights in the old room and marks it dirty.
