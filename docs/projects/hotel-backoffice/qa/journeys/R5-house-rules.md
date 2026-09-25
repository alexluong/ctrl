# R5 — House rules

**Purpose:** what the hotel refuses, and who may override it: overbooking (the owner may, and it is recorded), ID at check-in, and room capacity.
**Persona:** Oanh, owner.
**Seed used:** the Twin type with 2 rooms (401–402); Double room 102, free tonight; Doubles sleep 2.
**Length:** 1:06. File `R5-house-rules.webm`.

| # | Step (caption) | Notice |
|---|---|---|
| 1 | Setup → House rules | Overbooking is "The owner's to allow" (the default); ID at check-in is set to "Required". |
| 2 | New group booking: 3 Twin tomorrow, and the hotel has 2 | The form already shows "2 free, 3 asked" in red before submit. |
| 3 | Book → refused: "1 short on <date>" | The refusal names the night and the shortfall; "Take it anyway" is offered to the owner. |
| 4 | Take it anyway | The booking is made; its history records "Sold past the rooms of that type" with the night and who did it. |
| 5 | Walk-in for 102 → Check in with no ID | Refused: the hotel needs an ID from somebody in the room. |
| 6 | Name and CCCD number, as on the card → Check in | Checked in; the ID is on the guest's record. The booking's name is already in the first row (N46 fixed). |
| 7 | A family of 4 in one Double → book | Refused: "That room sleeps 2. You have asked for 4." Capacity has no override. |

"Take it anyway" exists only on the new-booking form (see Do not demo in the README).

## In ezFolio today

The rules exist as flags on one settings tab, and most of them do not refuse anything (`existing-system.md` § config flow, § date semantics, § individual booking flow).

1. **Hệ thống › Cấu hình đặt phòng** (`screens/sys-booking-rules.png`): `allow_over_room` = on (overbooking permitted for everybody), `min_tre_em = 6` (under 6 is a child), `time_next_date = 23:59` (day boundary), `auto_count_adult / children`, `lay_phong_can_ngay`. Auto-dirty, ID enforcement and "needs attention after N days" do not exist.
2. Overbooking: **Khách đoàn** (`fd-group-availability.png`) shows free rooms per night in the matrix; reception reads down the column and quotes against the tightest night by eye. Asking for 3 twins with 2 free goes through — the tape chart then shows more than 100 % (`fd-room-situation.png`), and nothing records who chose to oversell.
3. ID at check-in: the editor's **Bản khai báo thông tin** tab (`fd-booking-detail.png`): ID type (CMND / Passport / driver licence / other) + number + issue date, per guest in the guests table. Optional in practice — the daily room revenue report shows blank IDs and `?` in Mã QT on most rows (`rpt-room-revenue-daily.png`). PA18 export (`fd-pa18-export.png`) is where it would matter.
4. Capacity: room types carry no enforced capacity; NL/TE (adults / children) are typed on the booking and nothing compares them to the room. A family of four in a double is a note, not a refusal.

**What SoLex keeps / changes** (product.md §10 rules 2, 4, 5; §6 Availability G34/G35; ux.md §4.12):
- Keeps: one House rules page under Setup with the same dials (child age, day boundary, overbooking), and "2 free, 3 asked" shown on the group form like the matrix's tightest night.
- Changes: overbooking is a refusal with the night and the shortfall named; "Take it anyway" is the owner's by default (`stay.overbook`) and the booking's history records it — ezFolio's flag is all-or-nothing and silent.
- Changes: ID at check-in and room capacity are rules the hotel can switch on (ID) or that always hold (capacity: adults ≤ type capacity, children never counted); ezFolio only stores the fields.
