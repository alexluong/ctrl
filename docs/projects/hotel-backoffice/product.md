# SoLex — Product / Domain Model (WS3)

Owner: `solex-product`. **v1, 2026-09-23** — walked with Alex section by section (D-9…D-19 Proposed in `team/decisions.md`). Built from `requirements.md` + `existing-system.md` + D-4..D-8. Types in §6, commands in §11, events in §12 are the contract; dev should not invent others. Later-scope items are listed inline as "Later"/"Deferred". **Review page** (same content, tabbed): https://claude.ai/artifact/R42cHB8apsv7UuT7MGAnNg — regenerate from this file when it changes.

## 1. Framing

- Rebuild of the *essence* of ezFolio for data ownership going forward (D-4, D-5). Core subset + the enhancements in `requirements.md`. Fresh start, no import.
- One property, 58 rooms (57 sellable), ~2/3 of business is group/company, high occupancy, Vietnam, VND cash-heavy.
- **Semi-professional** = one trusted receptionist persona does everything; owner reads; setup is rare and owner-done. No shifts, no night audit, no per-user permissions beyond the three roles, no approval workflows except discounts. Correctness of money and availability matters; POS, key cards, channel sync do not.
- **Multi-tenant by design, one tenant in practice (D-9).** Everything hangs off a `Hotel`; streams and projections keyed by hotel; no cross-hotel data in v1. Tenant creation/seeding via admin SDK/script, not UI. No self-signup, billing, or super-admin console in v1.

## 2. Users, roles, apps (settled w/ Alex 2026-09-23)

**Users** are individual accounts, one per person, belonging to one hotel (D-9). Several receptionists share the *role*, not a login; every event carries `actor.userId`, so "who did what" is free.

**Apps, not per-role screens** (Odoo-style). The product is a few apps; a role = which apps you can open. The owner gets the same Front Desk as reception, plus more apps.

| app | contains | receptionist | owner |
|---|---|---|---|
| **Front Desk** | room map, tape chart, bookings, check-in/out, charges, payments, room status | ✓ | ✓ |
| **Back Office** | receivables, expenses, reports / dashboard, guest history | ✓ receivables + expenses (assumed; client to confirm); reports owner-only | ✓ |
| **Setup** | the whole Setup context | – | ✓ |

**Authz is capability-based, enforced per command** (Alex: role/authz matters). Apps only hide what you can't do; the server checks.

```ts
type Capability =
  | 'booking.create' | 'booking.edit' | 'booking.cancel'
  | 'stay.assign' | 'stay.check_in' | 'stay.check_out' | 'stay.move' | 'stay.cancel' | 'stay.overbook'   // G34: owner by default
  | 'folio.post_charge' | 'folio.void' | 'folio.move_line' | 'folio.take_payment' | 'folio.refund' | 'folio.forfeit' | 'folio.transfer_to_receivable'
  | 'room.set_status' | 'room.set_out_of_order'
  | 'receivable.record_payment' | 'receivable.write_off'
  | 'expense.record' | 'expense.void'
  | 'reports.view' | 'guests.view' | 'guests.erase'   // erase: owner only (D-20)
  | 'approval.decide'                                  // owner; 5.8. No `approval.request`: the desk bundle requests by definition
  | 'setup.edit' | 'users.manage'
type Role = { id: RoleId; hotelId: HotelId; name: string; capabilities: Capability[] }
// role hangs off the (hotel, user) membership pair, not the user: a person can be owner at one hotel and receptionist at another later (D-9)
type User = { id: UserId; hotelId: HotelId; name: string; username: string; email?: string; roleId: RoleId; status: 'active' | 'disabled' }
// identity (password, sessions) lives in Better Auth's mutable tables (D-11), NOT in the event log; identity-level changes are `user.*` events; membership + role per (hotel, user) are `staff.*` events on `<hotelId>/staff:<userId>` (D-22 addendum). Sign-in by username for all roles, email optional; password reset by owner. Deactivated staff stay in history, render as "(former)".
// staff rules: the last active owner cannot be demoted or deactivated (`staff.lastOwner`) — the one lockout in the system; re-adding a former member is refused (`staff.alreadyStaff`), use Reactivate so one person has one history. `room.set_out_of_order` stays a receptionist capability: AC dies at 23:00, desk pulls the room, nobody wakes the owner; it is the only receptionist power that moves supply, by design.
```
- Every command declares the capability it needs; the handler checks it against the actor. Audit = event `actor` + capability.
- **v1 ships two fixed bundles** (as built, slice 3):
  - `receptionist`: `booking.create/edit/cancel` · `stay.assign/check_in/check_out/move/cancel` · `room.set_status/set_out_of_order` · `folio.post_charge/move_line/take_payment/transfer_to_receivable` · `receivable.record_payment` · `expense.record` (petty cash: desk buys water, records it — client-flag assumption) · `guests.view`
  - `owner`: everything above + `folio.void/refund/forfeit` · `receivable.write_off` · `expense.void` · `reports.view` · `setup.edit` · `users.manage` · `guests.erase` · `approval.decide` (5.8)
  - No `ledger.*` capability: ledger ops are internal, reached only through folio / receivable / expense commands.
- Custom roles / editing bundles in Setup → later; the model already allows it because a role *is* a capability list.
- No approval workflows in v1 (discount approval → later ticket). Admin SDK (D-9) sits outside the apps, for seeding/tenant creation.

Housekeeping, restaurant, etc. are off-system; reception acts on their behalf.

## 3. Actions and interfaces (settled w/ Alex 2026-09-23)

Screen → actions → command. Immediate scope only; capability in brackets where not obvious.

### Front Desk app
| screen | actions |
|---|---|
| **Room map** (home) | every room's state *now*; tile → check in, post charge, take payment, mark clean/dirty, out of order |
| **Tape chart** | rooms × dates; per-type availability inline; drag a stay = move room / extend (`stay.room_changed` / `stay.nights_changed`); click empty cell → new booking |
| **New booking** | individual: room + dates + guest → done (one stay, assigned). Group: company, dates, types × qty, assign now (default) or later. **Source** (select of live `BookingSource`, ezFolio's Nguồn; sits next to "Billed to"): default `walk-in`; when a company is picked and the source is still the default, flip it to `company`; never blank. Shown on the bookings list column and the booking header |
| **Booking page** | edit party / notes, add / remove stays, assign rooms, cancel w/ reason, master folio; **group routing table** (rooms × categories, ezFolio's group panel, D-27) = `SetRouting` per stay, applied only to stays still on the company default — a per-stay override stays (ux.md G32, 5.7) |
| **Stay page** | guests, nights (room + rate per night), check in, check out, move, extend, cancel / no-show, own folio. **Check out opens a settle dialog** (ezFolio's quickout shape, D-27): balance · method · amount · ref, last option "Công nợ → company" = `TakePayment` *or* `TransferToReceivable`, **then** `CheckOut` — two commands in sequence, never one batch; if `CheckOut` refuses, the payment stands and the dialog says so; the dialog never decides whether check-out is allowed (ux.md G31, 5.7) |
| **Folio** | lines; post charge (catalogue item or free text); void [owner]; reprice [owner] (= void + repost at a new price, the only "discount"); move line to another folio; take payment (cash / transfer / card); deposit; refund [owner]; transfer remainder to company; close; **print** (the bill; the group invoice from the booking page). **Receipt** = a printed acknowledgement of one payment (letterhead · payment id · business date · method · reference · amount · for which stay/booking · balance after) — wanted, because a deposit is taken before there is a bill to print (ezFolio's Đặt cọc report is the desk's stand-in); a "Print receipt" link per payment line. Ruled 2026-09-25 (QA R9): in scope, **follow-up after the demo**, not an MVP gate — the bill already lists every payment. **5.8 desk request:** the same void / reprice / refund controls render for the desk as **"Xin duyệt"** with the same reason field → `RequestApproval`; the line / bill then carries a badge *đang chờ duyệt* / *từ chối: <reason>* (`approval.*` on the folio view). No new screen. Same on Receivables for write-off |
| **Arrivals / departures today** | lists off the map; one-click check in / out |
| **Search** | booking / stay by guest name, phone, company |

### Back Office app
| screen | actions |
|---|---|
| **Dashboard** | today: occupancy, arrivals, departures, revenue posted, cash in; forward book |
| **Receivables** | by company; record payment; write off [owner] |
| **Expenses** | record, void; by category / period |
| **Reports** [owner] | revenue by category / source / method; occupancy over time; guest history |

### Home & inbox (Alex 2026-09-24: "have we thought about notification? … or at least a home page?" — answer was no; this is the spec, additive per D-27: ezFolio has no inbox, nothing moves)
| persona | home | shows |
|---|---|---|
| **desk** | Room map (§4) | tiles + today strip = status buttons with live counts (arrivals · departures · in-house · dirty · OOO; ux.md G6). No inbox: the map *is* the desk's to-do list. |
| **owner** | Dashboard (§7 `DashboardToday`) + **Needs attention** list | numbers on top, list below; nav shows a badge = open `NeedsAttention` rows. |

**`NeedsAttention`** = a projection over facts already in the log, one row per item, cleared when the fact stops being true (never "dismissed"; if the owner wants it gone, they fix it). Thresholds live in Setup `BookingRules` with defaults:
```ts
type AttentionItem = {
  kind: 'receivable.aged' | 'room.ooo_long' | 'stay.unassigned_tomorrow' | 'stay.overstay_balance' | 'approval.pending'
  subject: { stayId?: StayId; bookingId?: BookingId; roomId?: RoomId; companyId?: CompanyId; approvalId?: ApprovalId }
  since: LocalDate; amount?: Money; detail: string   // detail rendered read-side from ids; never PII in the row (D-20)
}
```
| kind | true when | default | fed by |
|---|---|---|---|
| `receivable.aged` | company open amount unpaid for > `receivableAgeDays` | 30 days | `Receivables` |
| `room.ooo_long` | room out of order for > `oooDays` | 7 days | `room.taken_out_of_order` / `returned_to_service` |
| `stay.unassigned_tomorrow` | stay booked, no room, arrives tomorrow or today | – | `StayNights` (rows with no room) |
| `stay.overstay_balance` | stay checked in, depart date < today, folio balance > 0 | – | `StayNights`, `FolioView` |
| `approval.pending` | an `approval.requested` with no grant / decline (5.8) | – | `approval.*` |
Owner-only in v1 (dashboard ruling); the desk's share of these (unassigned tomorrow, overstay) is already visible on the calendar and the map. Nothing here sends anything; see Notifications (§8). **Owner approval card (5.8):** an `approval.pending` row opens one card — what (kind + the line / bill / company), who asked, amount, reason, **[Duyệt]** → `GrantApproval`, **[Từ chối + reason]** → `DeclineApproval`. The badge count *is* the notification: the owner opens the app.

### Setup app [owner]
CRUD per Setup item (§6), retire not delete. Users + roles management.

Later: registration card print, discount approval flow, group label/color on tape chart, breakfast / pickup lists, PA18 export, thank-you email.

## 4. Home screens (projections, not reports)

- **Room map** — now. Tiles by floor; color = derived status; tile → check-in, balance, post charge, set dirty/clean/OOO.
- **Tape chart** — over time. Room × night grid drawn from `Night` rows; a moved stay shows as two bars; drag emits `stay.room_changed` / `stay.nights_changed`; per-type availability inline for quoting.
Everything else hangs off these two.

## 5. Bounded contexts (settled w/ Alex 2026-09-23)

A context = one area of the business with its own vocabulary and rules. Dependencies flow one way, downward:

```
Setup ──▶ Reservations (Booking, Stay, availability)
  │   ──▶ Rooms (housekeeping state)
  │   ──▶ Billing (charges, payments, receivables) ──▶ Ledger (accounts, entries)
  │   ──▶ Guests
  └── ──▶ Expenses ─────────────────────────────────▶ Ledger
```

| context | owns | notes |
|---|---|---|
| **Setup** | HotelProfile, Floor, RoomType, Room definitions, RateTable, ChargeCategory + ChargeItem, BookingSource, Company, BookingRules (ExpenseCategory: v1 fixed in code, Setup screen if the client asks) | reference data; upstream of everything, depends on nothing; seeded by admin SDK (D-9) |
| **Reservations** | Booking, Stay (nights), availability rule | the commercial + stay lifecycle |
| **Rooms** | Room housekeeping / out-of-order state | definition comes from Setup |
| **Billing** | charge / payment / transfer / deposit commands; folio + receivable *projections* | hotel vocabulary over the Ledger; no aggregates of its own |
| **Ledger** | Account, Entry | generic double-entry; knows nothing about hotels |
| **Guests** | Guest | thin profile, reused across stays |
| **Expenses** | expense commands | owner's cash-out; posts to Ledger |

How downstream uses Setup: (1) **lookup at command time** — e.g. posting item X copies X's current price onto the entry; later price changes never touch history. (2) **react to a Setup event** — only where supply changes: `room.retired` / `room.type_changed` version `availability:<hotel>` (D-8). Setup never reads downstream; its one guard ("can't retire a room with future nights") is a check in the command against the projection.

## 6. Aggregates, events, invariants

**Shape of the system: CQRS + event sourcing.** Commands (§11) are the write side: validated intents that, if the rules pass, append events (§12) to a stream. Projections (§4, §7) are the read side: tables rebuilt from events, what every screen reads. Nothing writes a projection directly. Vocabulary: *command* = what someone wants to do · *event* = what happened · *aggregate* = the thing whose rules decide (Booking, Stay, Room, Ledger account…) · *projection* / *read model* = a query-shaped table.

Format (agreed w/ Alex 2026-09-23): each thing = TypeScript type + events + rules. American English. Types are the contract for dev; field names are final unless a decision changes them.

### Conventions

**Dates vs timestamps.** `LocalDate` = calendar day, no time/zone (`2026-09-23`) — used for *nights*: arrive/depart, `businessDate`, rate ranges. `Instant` = exact UTC moment — used for *when things happened*: `occurredAt`, actual check-in/out. A night is not a moment; D-7 converts one to the other once, at write time. `HotelProfile.timeZone` is the only zone in play; hardcoded `Asia/Ho_Chi_Minh` until Setup lands (TODO D-7), `businessDate` computed in it. Stay covers nights `[arrive, depart)` (depart exclusive). Money = VND integer; USD display only.

**Event naming.** `<aggregate>.<past_tense_verb>`, lowercase, dotted, snake_case verbs: `booking.created`, `stay.room_assigned`, `folio.charge_posted`. Prefix = stream type; `folio.*` filters trivially.

**Event envelope** (every event, every stream):
```ts
type Event<T extends string = string, P = unknown> = {
  id: EventId                  // ulid — unique, time-sortable
  hotelId: HotelId             // tenant key (D-9)
  stream: string               // '<hotelId>/booking:<id>' — hotel-first, then aggregate type + id
  version: number              // position in stream; UNIQUE(stream, version) (D-8)
  type: T                      // 'booking.created'
  schemaVersion: number        // per-type payload version; never edit old rows
  payload: P
  occurredAt: Instant
  businessDate: LocalDate      // hotel day it counts toward (D-7); stored, not re-derived
  actor: `user:${UserId}` | `system:${string}`   // one text value, two variants (D-12 amendment); resolved to a display name at read time
  correlationId: string        // one per user action (one check-in → several events)
  causationId?: EventId
  commandId?: string           // client idempotency key; safe retries under D-8
}
```
No `metadata` grab-bag; no `aggregateType` (in `stream`).

**Not everything is event-sourced (D-22).** Tier a (Booking, Stay, Ledger): the log is truth. Tier b (Room, Setup items, Guest/Contact, User): a mutable row is truth and every write still emits an event with the same envelope, so history and projections see one log. §11 tags each command.

### Booking — the commercial envelope (settled w/ Alex 2026-09-23)

A group = one Booking holding N Stays (company, contact, requested types × qty; rooms assigned later or now). An individual = one Booking with one Stay, room picked at creation. Same shape, no special case. Two-level on purpose: master folio, group cancel, "20 adults across 15 rooms not yet assigned" all need the envelope.

```ts
type Booking = {
  id: BookingId
  hotelId: HotelId
  kind: 'individual' | 'group'
  party: { companyId?: CompanyId; contactId: ContactId }   // contact PII in mutable table, not in events (D-20)
  sourceId: BookingSourceId    // channel the booking came through; Setup list (below); lookup only, no logic. Command defaults it to `walk-in` when absent (payload stays `sourceId?` under the §11a freeze) so revenue-by-source never has a "not recorded" row
  arrive: LocalDate
  depart: LocalDate            // exclusive
  requests: Array<{ roomTypeId: RoomTypeId; bedType: BedType; qty: number; adults: number; children: number; ratePerNight: Money }>
  notes?: string
  status: 'open' | 'cancelled' | 'closed'
}
```
Events: `booking.created` · `booking.requests_changed` · `booking.party_changed` · `booking.notes_changed` · `booking.cancelled(reason)` · `booking.closed` · `booking.stay_merged_in(stayId, fromBookingId)` (reserved; ezFolio "Ghép đoàn", deferred).
Rules: arrive < depart · every request qty ≥ 1 · cancel cascades to all stays not yet checked in · close only when every stay is terminal and the master folio is 0 or moved to a receivable · individual = one request qty 1, stay assigned at creation · group = N requests; UI defaults to assign-now (waiting list unused in practice) but late binding stays possible.

**Deposit is not on Booking** — it is a folio payment of kind `deposit` (master folio for groups, stay folio for individuals). "Deposit expected" = a note in v1.

**Deferred from Booking (later tickets):** OTA support (commission, gross/net, channel sync, external confirmation ref) · sales rep / "saler" · group label + color on tape chart · merge stay into group.

### Stay — one guest visit, night by night (settled w/ Alex 2026-09-23; ezFolio `reservation_room`, Opera "room stay")

Naming: **Booking / Stay** (not Reservation / RoomStay). Streams `booking:*`, `stay:*`.

**The night is the unit.** A Stay is a list of nights; each night carries its room and its rate. A room move does *not* split the Stay (guest sees one visit, one bill, one checkout); it changes the room on the remaining nights.

```ts
type Night = {                 // value inside Stay, not its own aggregate: no life of its own
  date: LocalDate              // business date (D-7)
  roomId?: RoomId              // empty until assigned; may differ night to night after a move
  rate: Money
  posted: boolean              // room charge already on the folio → night immutable
}
type Stay = {
  id: StayId
  hotelId: HotelId
  bookingId: BookingId
  roomTypeId: RoomTypeId
  bedType: BedType
  nights: Night[]
  // arrive = first night, depart = last night + 1 — derived, not stored
  // projections (tape chart, occupancy, forecast) are (roomId, date) rows derived from nights
  adults: number
  children: number             // < childAgeThreshold (Setup, default 6)
  guests: GuestId[]
  routing?: Partial<Record<ChargeCategoryId, 'own' | 'master'>>   // group stays only; keyed by charge category; default from Company.defaultRouting, else room → master, rest → own
  status: 'booked' | 'checkedIn' | 'checkedOut' | 'cancelled' | 'noShow'
  checkedInAt?: Instant
  checkedOutAt?: Instant
}
```
Events: `stay.created` · `stay.room_assigned(roomId, fromDate?)` · `stay.room_unassigned` · `stay.room_changed(fromDate, roomId)` · `stay.nights_changed(added[], removed[])` · `stay.rate_set(date, amount)` · `stay.guest_added` · `stay.guest_removed` · `stay.routing_set(categoryId, target)` · `stay.checked_in` · `stay.checked_out` · `stay.cancelled(reason)` · `stay.marked_no_show` · `stay.overbooking_overridden(roomTypeId, nights[])` · `stay.occupancy_set(adults, children)`.
Rules: **check-in normalizes the stay to today**: tonight (current business date) must be a night of the stay — early arrival (before `arrive`) adds nights `[today, arrive)` at the first night's rate, room must be free for them, availability versioned, warn + allow; late arrival drops unposted nights before today (posted ones stay). Emitted as `stay.nights_changed` before `stay.checked_in`. So a checked-in stay holds ≥ 1 night while in house; same-day in/out pays that one night (6a minimum one night) · check-in needs tonight's room assigned and not out of order · check-out guards the stay's **own** folio only (0 or moved to a receivable); the master folio is guarded at `CloseBooking`, seen and settled on the booking page · **early check-out** (before `depart`) drops every night from the current business date on **except the arrival night**, in the same batch (`stay.nights_changed {removed}`, reversal of the current night's posted room charge, then `stay.checked_out`) so they go back on sale and the guest pays only nights slept, minimum one (§10 6a, review B1) — never implicit in `checked_out` · nights change only before check-out · posted nights are immutable (no rate/room change) · no-show only from `booked`, after arrival date · cancel only if not checked in, reason required, charges moved off first (ezFolio guards).

Assumptions (Alex 2026-09-23: business calls, not system-breaking; adjust later):
- **Room move mid-stay**: `room_changed` rewrites `roomId` on unposted nights from that date; rate unchanged by default, editable. Different room type → UI warns, no auto-reprice.
- **Extend**: `nights_changed` appends nights, pre-filled from the rate table, editable before they post.

Dropped from v0: ezFolio flags `foc` (= rate 0), `isNet` (OTA, deferred), `locked` (no clear use).

### Availability (cross-aggregate rule, Reservations context)
- **Per room**: no two stays may hold the same `(roomId, date)` (cancelled / no-show don't count). One rule, per night, no interval math. Same-day turnover is free by construction.
- **Per type**: for each night, `stays of that type (assigned or not, not cancelled) ≤ rooms of that type in service`. Overbooking policy = **warn + explicit override** (`stay.overbooking_overridden`), assumed because high occupancy means they sell to the edge.
- **Enforcement (D-8)**: one `<hotelId>/availability:all` stream; every command that changes supply or demand versions it in the same batch — room assign/change/unassign, nights change, early check-out, check-in with assignment, room out-of-order / back in service, room retire or type change (Setup), overbooking override. Its only event is `availability.changed {cause}` — serialisation only, nothing folds it.
- **G34 Overbooking check (5.7, after G33)**: a command that *adds demand* — `CreateBooking`, `ChangeBookingRequests` (added lines), `ChangeNights {add}`, `CheckIn` (early-arrival nights) — computes, for each `(roomTypeId, night)` it adds, `free = rooms of that type in service (not retired, not currently OOO) − stays of that type holding that night (status booked / checkedIn / checkedOut)` **after** the command. Any `free < 0` → refuse `availability.overbooked {roomTypeId, date, short}` (first offending night; `short` = how many rooms over). Only the nights the command adds are checked: a type already over elsewhere never blocks an unrelated edit. **Override** = the same command re-sent with `override: true` (no separate command — at `CreateBooking` the stay does not exist yet, and the desk's flow is one "Take anyway" button that resends). Who may override follows `BookingRules.overbooking`: `refuse` → nobody, flag ignored; `warn` (default) → actor needs `stay.overbook` (owner by default); `allow` → the command's own capability is enough. With override the command emits `stay.overbooking_overridden {roomTypeId, nights[]}` on every stay that pushed a night negative, same batch, after `stay.created` / `nights_changed`. Never silent: `allow` still needs the flag, so the log always shows who chose to oversell. **Supply-side commands never refuse** (`TakeOutOfOrder`, `RetireRoom`, `SetRoomType`): they can leave a type negative; the calendar's free-of-type row shows it red and the desk resolves it by moving or cancelling. Per-room double holds stay a hard refuse (`stay.roomTaken`) — overbooking is a *type* concept. `OverrideOverbooking {stayId}` (earlier catalogue row) is retired unbuilt.
- **G35 Capacity (5.7, with G34)**: `adults ≤ RoomType.capacity` per stay. `children` is by definition the count under `childAgeThreshold` and is never counted (§10 rule 5); a child at or over the threshold is typed as an adult. Registered `guests[]` are identity records, not the count (a child may be registered, a second adult may refuse ID). Checked at `CreateBooking` / `ChangeBookingRequests` (per request line, against the requested type), `SetOccupancy`, and `CheckIn` (against the **assigned room's** type — a stay moved into a smaller type fails at the door, not at assign, which already warns on a type mismatch). Refuse `stay.overCapacity {roomTypeId, capacity, adults}`. No override in v1: an extra bed is a later charge item + `capacity` bump, not a rule bend. `RoomType.capacity` already exists in Setup (solex `setup.capacity`).
- **Out-of-order rooms**: OOO is supply, not a lock. Assigning an OOO room to future nights → **warn, allow** (it may be back by then); `TakeOutOfOrder` under assigned nights → warn, allow. Hard stop is **check-in** only: tonight's room must be in service. Overbooking count treats OOO rooms as out of supply.

### Room — physical (settled w/ Alex 2026-09-23)

```ts
type Room = {
  id: RoomId; hotelId: HotelId
  number: string; floor: string; roomTypeId: RoomTypeId; bedType: BedType   // definition from Setup
  housekeeping: 'clean' | 'dirty'    // 'inspected' → later
  outOfOrder?: { reason: string; since: Instant }
  note?: string
}
// occupied / vacant / arriving / departing are DERIVED from stays' nights, never stored
```
Events: `room.marked_dirty` · `room.marked_clean` · `room.taken_out_of_order(reason)` · `room.returned_to_service` · `room.note_set`. (Definition events live in Setup: `room.defined/updated/retired/type_changed`; `SetRoomType` §11, 5.7.)
Auto: `stay.checked_out` → `room.marked_dirty` (policy reaction).
Map vocabulary (derived): vacant clean · vacant dirty · occupied clean · occupied dirty · out of order, + arriving / departing overlays.

### Ledger — generic double-entry core (settled w/ Alex 2026-09-23)

Folios, receivables and expenses are three views of one thing: accounts in a ledger. The Ledger context is hotel-agnostic; Billing and Expenses are hotel vocabulary over it. Reception never sees debit/credit.

```ts
type Account = {
  id: AccountId; hotelId: HotelId
  kind: 'folio' | 'receivable' | 'cash' | 'bank' | 'revenue' | 'expense'
  ref?: { stayId?: StayId; bookingId?: BookingId; companyId?: CompanyId; categoryId?: string }
  status: 'open' | 'closed'
}
type Entry = {
  id: EntryId; hotelId: HotelId
  businessDate: LocalDate
  kind: 'charge' | 'payment' | 'refund' | 'transfer' | 'expense' | 'reversal'
  lines: Array<{ accountId: AccountId; amount: Money }>   // + debit, − credit; Σ = 0
  ref?: { stayId?; chargeId?; entryId? /* reversed */ }
  memo?: string
}
// balance(account) = Σ its lines, never folded/stored · entries immutable; undo = reversal entry · account closes only at 0
// memo: what a person typed, as typed. A memo the *system* writes is never a sentence in one language: it is `{key, params}` with ids (`companyId`, `stayId`, dates) and is rendered when read — on screen in the reader's language, on a printed bill in the hotel's (`HotelProfile.locale`, default `vi`). The log holds facts; sentences are a projection (same principle as D-20 field names). Never store a slug or an id where a name is meant to appear — look the name up at render, so a renamed company prints right.
// streams are per account: <hotelId>/ledger:<kind>:<id> (ledger:folio:<stayId>, ledger:receivable:<companyId>, ledger:cash…). An entry touching N accounts is appended to all N streams
// (same entryId + correlationId, full entry in each payload); projections dedupe by entryId.
```
Events: `ledger.account_opened` · `ledger.entry_posted` · `ledger.entry_reversed(entryId, reason)` · `ledger.account_closed`.

| hotel action | ledger entry |
|---|---|
| post charge to stay | debit folio(stay or master, per routing) / credit revenue:category |
| payment received | debit cash or bank / credit folio |
| deposit | same as payment, kind `deposit` on the folio projection |
| refund | debit folio / credit cash or bank |
| transfer remainder to company | debit receivable:company / credit folio |
| company pays receivable | debit cash or bank / credit receivable:company |
| expense | debit expense:category / credit cash or bank |
| void charge | reversal entry |

What it buys: one balance rule, one immutable money log; "cash today", "revenue by category", "receivables by company", P&L-ish are the same query. Cash drawer / bank reconciliation come free later.

### Folio — charges and payments (Billing; **projection + commands over Ledger**, settled w/ Alex 2026-09-23)

One **own folio** per Stay + one **master folio** per *group* Booking only (individual bookings: no master, no routing, own folio takes everything; company traveller → transfer-to-receivable at check-out). A charge is posted *against a stay*; for a group stay, its routing for that category decides which folio it lands on. Stay = one visit = one folio, as Alex put it.

```ts
type Folio = {
  id: FolioId; hotelId: HotelId
  owner: { kind: 'stay'; stayId: StayId } | { kind: 'booking'; bookingId: BookingId }   // own vs master
  status: 'open' | 'closed'
  // balance = Σ charges − Σ voided − Σ payments + Σ refunds  (derived)
}

type ChargeCategoryId = string   // Setup-defined list (`ChargeCategory`), seeded: room · roomSurcharge · minibar · laundry · compensation · extraService · restaurant. `room` is reserved: only the system posts it (nightly, D-7).

type Charge = {
  id: ChargeId; folioId: FolioId; stayId: StayId
  businessDate: LocalDate      // which hotel day it counts for (D-7); occurredAt comes from the event
  categoryId: ChargeCategoryId
  itemId?: ChargeItemId        // Setup catalogue item; free text if absent
  description: string          // what the desk typed, stored as typed (free text or the catalogue item's name at post time)
  text?: { key: string; params: Record<string, string | number> }   // system-written lines only (night roll, early-check-out reversal, forfeit, transfer memo): a message key + facts, rendered in the reader's language; `description` is then empty. Ruled 2026-09-25 (QA N51/N52)
  qty: number; unitPrice: Money
  voided?: { reason: string; at: Instant }
}

type Payment = {
  id: PaymentId; folioId: FolioId
  businessDate: LocalDate
  method: 'cash' | 'bankTransfer' | 'card'   // card = the word only. No card data. Ever.
  kind: 'deposit' | 'settlement' | 'refund'
  amount: Money
  ref?: string                 // transfer reference
}
```
Folio accounts open **lazily** on the first charge or payment, with derived ids — own `ledger:folio:<stayId>`, master `ledger:folio:master:<bookingId>` — never at CreateBooking (empty = zero to every reader; derived ids make retry safe). As built (slice 3): `room` category posts only via the night roll · refunds capped at payments received on that folio, not at the credit balance · deposit = a payment before any charge, allowed.

Events: `folio.opened` (first line, lazy) · `folio.charge_posted` · `folio.charge_voided(reason)` · `folio.charge_moved(chargeId, toFolioId)` (ezFolio "Chuyển dịch vụ") · `folio.payment_received` · `folio.payment_refunded` · `folio.transferred_to_receivable(companyId, amount)` · `folio.closed`.
Rules: never edit a charge — void and repost · a night's room charge posts once, at the roll (D-7), or at check-in for the current night · move charges only while both folios open · close only at 0 or after transfer · deposit = payment of kind `deposit` (master folio for groups, stay folio for individuals); forfeit = `folio.deposit_forfeited` posts a charge under the reserved system category `depositForfeit` against it — owner-only (`folio.forfeit`, 5.4): keeping money the guest handed over sits with void / refund.

Simplifications vs ezFolio: dropped `telephone` category (dead) · discount = negative-priced line or void + repost, **no approval workflow in v1** (later ticket) · tax/service % not modelled as lines (VAT / red invoice → later) · FOC = rate 0, not a payment method · `debt` is not a payment method, it is the transfer-to-receivable action.

### Receivable — debt that outlives the stay (Billing; **projection over a Ledger receivable account**, settled w/ Alex 2026-09-23)

```ts
type Receivable = {
  id: ReceivableId; hotelId: HotelId
  debtorCompanyId: CompanyId
  folioId: FolioId             // grain = one folio
  amount: Money
  status: 'open' | 'partial' | 'settled' | 'writtenOff'
  // no due date in v1 (ezFolio has none; overdue = age)
}
```
Receivable accounts open lazily like folios: first transfer emits `ledger.account_opened` on `<hotelId>/ledger:receivable:<companyId>`; no separate `receivable.opened`.

Events: `receivable.payment_received(method, amount, ref?)` · `receivable.settled` · `receivable.written_off(reason)`.
Rules: opened only from a folio transfer · payments ≤ amount · settled when paid in full.

### Guest — thin profile (settled w/ Alex 2026-09-23)

```ts
type Guest = { id: GuestId; hotelId: HotelId; name: string; phone?: string; email?: string; nationality?: string
  idDoc?: { type: 'cccd' | 'passport' | 'other'; number: string }; notes?: string }
```
**PII columns (D-20 / D-23 redaction denylist):** `guests.name`, `guests.phone`, `guests.email`, `guests.nationality`, `guests.id_doc_type`, `guests.id_doc_number`, `guests.notes`; `contacts.name`, `contacts.phone`; `users.name`, `users.email`. Not PII: ids, timestamps, status. `guest.updated` payload carries changed *field names*, never values. **PII never appears in a URL** (access logs keep every URL): every form is `method=post` (a pre-hydration submit must not fall back to a GET query string); guest search sends its term in the request body, results held in client state, so no shareable search URL. Opaque ids (`stayId`, `bookingId`) in URLs are fine. (QA N11/N12, 2026-09-24)

Events: `guest.created` · `guest.updated` · `guest.erased` — **PII never enters event payloads** (D-20). Events carry `guestId` only; name/phone/idDoc live in a mutable `guests` table. Erasure = overwrite the row, log keeps a tombstone; replay still works. Belongs to the hotel (D-9); reused across stays for history. ID capture optional in v1. All Guest fields captured from slice 2 (all optional but name). Later: merge duplicates, PA18 police export, VIP class.

**Contact — who booked (settled 2026-09-23).** Separate from Guest on purpose: ~2/3 of business is company/group, the booker (secretary, agent, company) is usually not a sleeper. Not folded into Guest.
```ts
type Contact = { id: ContactId; hotelId: HotelId; name: string; phone?: string; companyId?: CompanyId }
```
Events mirror Guest: `contact.created` · `contact.updated` (field names only) · `contact.erased` (tombstone), stream `<hotelId>/contact:<id>`, tier b. Same D-20 erasure path. Commands `CreateContact / UpdateContact / EraseContact`. **Reuse**: `CreateBooking.contactId?` picks an existing contact; without it a new row is minted (typo fix = `UpdateContact`, never edit the booking). Phone match on the booking form is a *suggestion* ("same phone as Nguyen Van A — reuse?"), never an auto-merge; the search box lands with the booking form. **Erase does not cascade** (ruled 2026-09-25, QA N64): `EraseGuest` leaves the contact and vice versa — a contact may be a secretary who booked for many. After an erase the person page says a contact (or guest) with the same phone — or, without a phone, the same exact name — still exists and links to it; the owner erases that one on purpose. Matching by name alone never triggers anything automatic.

### Setup context (D-6) — what the hotel is made of

Reference data, retire-not-delete, seeded by admin SDK (D-9). Each has `<name>.defined / updated / retired` events for audit.
- `HotelProfile` — name, address, **timeZone**, `locale` `vi` (the language of anything the hotel hands a guest: printed bill, receipt; screens follow the reader), `checkInTime` 14:00, `checkOutTime` 12:00, `businessDayStart` 02:00 (D-7)
- `Floor`, `RoomType` (name, capacity), `Room` (number, floor, type, bedType)
- `RateTable` — `{roomTypeId, bedType, dateRange | dayOfWeek, ratePerNight}`; no overlapping ranges
- `ChargeCategory` — seeded room · roomSurcharge · minibar · laundry · compensation · extraService · restaurant; reserved system-only (never pickable by hand): `room` (night roll), `depositForfeit` (ForfeitDeposit), `writeOff` (expense side)
- `ChargeItem` — category, VN + EN name, unitPrice, active
- `BookingSource` — **tier b Setup entity, retire not delete** (channels change; the client adds an OTA without a deploy): `{ id: BookingSourceId; hotelId; name: string; kind: 'direct' | 'ota' | 'agent' | 'company'; retired?: true }`; id = slug of the name like RoomType. `kind` is the coarse bucket ezFolio calls Nguồn (WALK-IN · OTA · TA · CORP, counts seen 61 · 21 · 1 · 161) so reports roll up the same way the client is used to; `name` is the channel. **v1 seed** (from the OTAs actually in the client's debtor list, existing-system.md 06): `walk-in` (direct) · `phone` (direct) · `zalo-facebook` (direct) · `agoda` · `booking-com` · `expedia` · `traveloka` · `trip-com` (all `ota`) · `agent` (agent; the travel-agency catch-all) · `company` (company). "Repeat guest" is not a source — it is a guest fact, GuestHistory. Source ≠ payer: an OTA that settles later is *also* a `Company` (that is how ezFolio's receivable list mixes Agoda with corporates); `sourceId` says where the booking came from, `party.companyId` says who is billed. Events: `setup.booking_source.defined / updated / retired`; retire refused while… nothing — old bookings keep the id, the form just stops offering it. Built in 5.7 with G28.
- `ExpenseCategory` — **v1: fixed in code, not Setup data; Setup screen if the client asks** (D-21). Ids: `groceries`, `incidental`, `hkOvertime`, `advance`, `other`, + system-only `writeOff` (written-off receivables land there; not pickable by hand)
- `Company` — tier b Setup entity, built first in slice 5: `{ id: CompanyId; hotelId; name: string; defaultRouting?: Partial<Record<ChargeCategoryId, 'own' | 'master'>> }`. `companyId` on Booking.party, Contact and transfer-to-receivable references it; no free-text company names. Kind/contact/commission/terms → later
- `BookingRules` — childAgeThreshold 6, `overbooking: 'refuse' | 'warn' | 'allow'` default `warn` (G34: who may send `override: true`), autoDirtyOnCheckout true, idEnforcement optional
Rules: unique room numbers per hotel; retired items not selectable; can't retire a room with future nights; **can't retire a room type while any non-retired room references it** (refuse `roomType.inUse`; retire or re-type the rooms first — mirrors the room rule, and a retired type with live rooms would break availability counts); room type id = slug of name (`phong-doi`); rate ranges half-open `[from, to)`.

### Expense — owner's cash-out (settled w/ Alex 2026-09-23; posts to Ledger)

```ts
type ExpenseCommand = { businessDate: LocalDate; categoryId: ExpenseCategoryId; amount: Money; method: 'cash' | 'bankTransfer'; description: string; reference?: string }   // description required (payee goes here — an unnamed advance is unauditable)
```
Events: `expense.recorded` · `expense.voided(reason)` → ledger entries. Projection: expenses by category / period.

## 7. Projections / queries (read side)

Every screen reads a projection; projections are rebuilt from events (§12). Synchronous, same batch as the append (D-8).

| projection | rows | fed by | serves |
|---|---|---|---|
| **RoomMap** | per room: hk state, OOO, occupied?, arriving?, departing?, balance | `stay.*`, `room.*`, `folio.*` | Front Desk home |
| **StayNights** | `(roomId, date) → stayId, rate, posted` | `stay.*` | tape chart, availability, occupancy |
| **Availability** | per type per night: sellable, booked, free | StayNights + `room.*` + Setup | quoting, overbooking check |
| **ArrivalsDepartures** | today's arriving / departing stays | `stay.*` | daily lists |
| **BookingList** | bookings + stays + party + status; searchable by guest / phone / company | `booking.*`, `stay.*`, guests | search, booking page |
| **FolioView** | per folio: lines (charges, payments), balance | `folio.*` | folio screen, print |
| **Receivables** | per company: open amount, age, payments | `receivable.*` | Back Office |
| **DashboardToday** | occupancy %, arrivals, departures, in-house, revenue posted, cash in, unpaid | StayNights, `ledger.*` | Back Office home |
| **UnpostedNights** (derived query, no watermark) | in-house nights for today's business date with no live room charge | StayNights, `folio.charge_posted/voided` | lazy night roll posts exactly these on any request after the roll — self-healing after outages (D-25); Setup guard on `businessDayStart` = "is this empty?" |
| **ForwardBook** | per future night: rooms sold × rate, by type | StayNights | forecast |
| **Revenue** | by business date × category × source × payment method | `ledger.*` + Setup lookups | reports |
| **Expenses** | by category × period | `expense.*` | Back Office |
| **GuestHistory** | per guest: visits, nights, spend | `stay.*`, `ledger.*` | guest page |
| **History** | per room / stay / folio: events with actor + time | all | "Show log" tabs (audit) |
| **NeedsAttention** | one row per open item (§3 Home & inbox): aged receivable, long OOO, unassigned arriving tomorrow, overstay with balance, pending approval | `Receivables`, `room.*`, `StayNights`, `FolioView`, `approval.*` | owner home list + nav badge count |

Later: WaitingList (unassigned stays), Breakfast list, PA18 export, CommissionByChannel, Deposits ledger.

## 8. Scope

**v1:** Setup (onboarding, prices, catalogues, rules, users/roles) · individual + group booking with inline availability · assignment now or later · tape chart + room map · check-in/out · guests per stay (ID optional) · one charge flow over Setup-defined categories · folio own/master + routing · payments cash / transfer / card-method, deposits, refunds · receivables by company · room hk state + OOO · dashboard, revenue / occupancy / receivables reports · expenses · history/audit tabs · folio print · search.
**Later:** **cash handover / day close** (today: manual — desk collects the day's cash and hands it to the owner daily; Alex 2026-09-24: "not sure how to handle this, may need a discussion with team"; candidate shape = `CloseShift {cashCounted}` → expected cash-in since last close vs counted, variance event, owner-visible; the Ledger already has the cash account so it is a report + one command; needs client conversation first) · OTA support (commission, gross/net, sync) · VAT / red invoice · receivable due dates · group label/color · registration card print · PA18 export · breakfast / pickup lists · thank-you email · merge stay into group · inspected hk state · custom roles · per-staff activity report · multi-currency beyond USD display.
**Never:** card data · restaurant POS · hk staff scheduling · key cards · hourly / day-use.

**Approval flow → slice 5.8, v1 (Alex 2026-09-24: "keep it simple, but actionable"). Spec in §11 Approvals.** One rule: *an owner-only money act the desk cannot do becomes a request from the same button.*

**Notifications (deferred, one paragraph).** Anything that leaves the app — Zalo, Telegram, email, SMS — is an **async cursor consumer** over the same event log (`WHERE seq > last_seq`, D-8 clarification iv), never inline in a command, never a source of truth: the log says what happened, the consumer decides whom to tell. Sits in the Hookdeck / Queues slot D-8 already reserves for "slow or external consumers". First candidates when the client asks: `approval.requested` → owner's Zalo (5.8 ships without it: the badge count is the notification); `NeedsAttention` new row → owner daily digest; `stay.checked_in` → nothing (the map shows it). Payloads carry ids, the consumer resolves names at send time (D-20). Not designed further until the approval flow or a client ask forces it.

## 9. Dependencies on WS2 / for other WSs

- Model mirrors ezFolio's `reservation → reservation_room → traveller` chain deliberately (staff mental model), but names and shape are ours (D-5).
- ezFolio item masters never seen and no longer pursued (D-6) — Setup context is designed fresh from explore's checklist; seed values (rooms, types, items, prices) come from Alex/client at onboarding.
- **For dev**: storage per D-8 (D1 event log + projections, optimistic concurrency, `availability:<hotel>` stream, no Durable Object); types §6 + commands §11 + events §12 are the contract. No card fields anywhere.
- **For architect**: policy points §10 need Alex; two are already in `team/questions.md`.

## 10. Rules and policy (settled w/ Alex 2026-09-23; all live in Setup `BookingRules` / `HotelProfile` or as capability defaults, so the client can flip them)

| # | rule | v1 |
|---|---|---|
| 1 | Hotel day | D-7 + D-25. Business date rolls at `businessDayStart` 02:00. Room charge posts via `PostNightlyRoomCharges` (actor `system:night_roll`), idempotent per `(stayId, businessDate)` (entry id `night:<stayId>:<date>:<attempt>`, so a voided night can be re-posted), fired by an hourly cron (Workers scheduled trigger; each hotel posts when its own roll hour has passed) **and** lazily on the first request after the roll, both deriving "in-house nights with no live room charge" (no watermark, self-healing, idempotent so the two never double-post); check-in posts tonight through the same command. Changing `businessDayStart` is owner-only and refused while any night of the current business date is unposted. Check-in before `checkInTime` 14:00 → optional early check-in item; checkout after `checkOutTime` 12:00 → optional late checkout item; after next roll → extra night (`stay.nights_changed`). Actual instants decide; typed dates are the plan. |
| 2 | Overbooking | warn + explicit override (D-15). G34 §6 Availability: per type per night, refuse `availability.overbooked` unless the command is re-sent with `override: true` by someone holding `stay.overbook` (`BookingRules.overbooking` = `refuse` / `warn` / `allow`). |
| 3 | Cancellation / no-show | no automatic charge. Receptionist posts a compensation charge by hand if agreed. Deposit forfeit = explicit `ForfeitDeposit` [owner, 5.4]. Cancel guards: not if checked in; reason required; charges moved off first. |
| 4 | Guest ID | optional; PA18 export later |
| 5 | Children | under `childAgeThreshold` (6) free, not counted against capacity. G35 §6 Availability: `adults ≤ RoomType.capacity`, refuse `stay.overCapacity` at create / requests / `SetOccupancy` / check-in. |
| 6 | Room after checkout | auto `room.marked_dirty {cause: checkout, stayId}` (reaction, in-batch) |
| 6a | Early check-out | nights are `[arrive, depart)` (D-7): the departure date is not a night. **Minimum one night**: a checked-in stay always keeps its first (arrival) night. Checking out on business date D before the planned `depart` removes every night `≥ D` **except the arrival night**, in the same batch: `stay.nights_changed {removed}` frees them for sale and, where the current night is among them (D > arrival), its posted room charge is **reversed** (`folio.charge_voided {cause: earlyCheckOut}`) so the guest pays only the nights slept. Same-day in/out (D = arrival night) keeps and pays that one night and frees every later night: a three-night booking leaving on day one holds night one, gives back two and three. The room was used; day-use pricing is out of scope. Explicit events, never implied by `checked_out`. Leaving after `checkOutTime` on the last day is a **late check-out fee = catalogue item**, never an extra night (rule 1); staying past the next roll is the extra night. (Review B1, 2026-09-25.) |
| 6c | Early / late check-in | Check-in makes today the first unposted night: early arrival adds nights `[today, arrive)` (warn + allow, room must be free), late arrival drops unposted nights before today. A checked-in stay never has zero nights: the arrival night is posted at check-in and is the one night 6a never removes; every later night is given back on early check-out. Same-day in/out pays that night (room used); day-use pricing is out of scope. |
| 6b | Out-of-order room | assign to future nights: warn + allow. Check-in: refuse. Taking a room OOO under assigned nights: warn + allow. |
| 7 | Check-out with balance | stay's own folio: blocked unless 0 or remainder transferred to a company receivable. Master folio not checked here. |
| 7a | Close booking | **Individual**: closes automatically in the same batch when its last stay checks out or is cancelled (no master, own folio already settled). **Group**: only by explicit `CloseBooking`, refused while any stay is open or the master folio balance > 0 (settle or transfer on the booking page). |
| 8 | Group billing default | **Group bookings only.** Routing keyed by `ChargeCategoryId`: `Company.defaultRouting` if set, else room → master, everything else → own — the *seed* for each group stay's routing, settable per stay per category (`SetRouting`). An individual booking has no master folio and no routing: every charge lands on the stay's own folio; a company traveller's bill reaches the company via transfer-to-receivable at check-out. |
| 9 | Rates | prefilled from `RateTable` (ranges half-open `[from, to)`); no table rate and no desk-typed price → **refuse** `rate.notFound`, never silently 0 (D-21); 0 only when typed (FOC); editable until the night posts; posted nights immutable. Day-of-week rates later. |
| 10 | Sensitive money actions | void, refund, write-off, transfer = `owner` capabilities by default. Caps: refund ≤ payments − refunds − forfeits; forfeit ≤ deposits − refunds − forfeits — money the hotel no longer holds can be neither returned nor kept (B14). |

Deferred: OTA commission / gross-net · VAT / red invoice · discount approvals · receivable due dates.

## 11. Command catalogue (canonical list of actions; dev builds and tests from this)

Command = one intent. `needs` = capability. `checks` = rules beyond "hotel matches, entity exists". `emits` = events (Ledger entries implied for money). **Tier (D-22)**: **a** = event-sourced (log is truth, state = fold, version guard); **b** = event-notified (CRUD row is truth, write still appends an event to the same log, no fold). Rule of thumb: would we replay it to rebuild state? no → b.

### Reservations — tier **a** (Booking, Stay streams; availability stream)
| command | needs | checks | emits |
|---|---|---|---|
| `CreateBooking {kind, party, sourceId?, arrive, depart, requests[], notes?, override?}` | `booking.create` (+ `stay.overbook` when overriding) | arrive < depart · qty ≥ 1 · G34 `availability.overbooked` unless `override` · G35 adults ≤ capacity per line · individual: room given + free | `booking.created`, `stay.created`×N (folios open lazily on first line, derived ids) |
| `ChangeBookingParty / Notes / Requests {…, override?}` | `booking.edit` | open · requests: G34 on added lines, G35 per line | `booking.party_changed` / `notes_changed` / `requests_changed` (+ `stay.created`/`stay.cancelled`) |
| `CancelBooking {reason}` | `booking.cancel` | no stay checked in | `booking.cancelled`, `stay.cancelled`×N |
| `CloseBooking` (group only; individual closes itself on last stay terminal) | `booking.edit` | all stays terminal · master folio 0 or transferred | `booking.closed`, `folio.closed` |
| `AssignRoom {stayId, roomId, fromDate?}` | `stay.assign` | room type matches (warn) · room free those nights · OOO (warn) · versions availability | `stay.room_assigned` |
| `UnassignRoom {stayId}` | `stay.assign` | status booked | `stay.room_unassigned` |
| `MoveStay {stayId, fromDate, roomId}` | `stay.move` | not checked out · unposted nights only · room free · versions availability | `stay.room_changed` |
| `ChangeNights {stayId, add[], remove[], override?}` | `stay.assign` | not checked out · removed nights unposted · G34 on `add[]` | `stay.nights_changed` |
| `SetNightRate {stayId, date, amount}` | `booking.edit` | night unposted | `stay.rate_set` |
| `AddGuest / RemoveGuest {stayId, guestId}` | `booking.edit` | not checked out | `stay.guest_added` / `guest_removed` |
| `SetOccupancy {stayId, adults, children}` (G35) | `booking.edit` | not checked out · adults ≥ 1 · adults ≤ capacity of the stay's type (`stay.overCapacity`) | `stay.occupancy_set` |
| `SetRouting {stayId, categoryId, target}` | `booking.edit` | group stay | `stay.routing_set` |
| `CheckIn {stayId, guests[]?, override?}` | `stay.check_in` | booked · tonight's room assigned, not OOO · early arrival: room free `[today, arrive)`, G34 on the added nights · G35 adults ≤ capacity of the **room's** type | `stay.nights_changed` if today ∉ nights (versions availability), `stay.checked_in`, `folio.charge_posted` (tonight's room) |
| `CheckOut {stayId}` | `stay.check_out` | checkedIn · own folio 0 or transferred **after** the early-check-out reversal below | `stay.nights_changed {removed: nights ≥ today, never the first night}` + `folio.charge_voided` (today's room line) if leaving before `depart` and today > first night (versions availability), `stay.checked_out`, `folio.closed`, `room.marked_dirty` |
| `CancelStay {stayId, reason}` | `stay.cancel` | booked · folio has no unmoved charges | `stay.cancelled` |
| `MarkNoShow {stayId}` (5.4) | `stay.cancel` | booked · after arrival date | `stay.marked_no_show` |
| ~~`OverrideOverbooking {stayId}`~~ retired (G34): override is `override: true` on the adding command, needs `stay.overbook` | | | `stay.overbooking_overridden {roomTypeId, nights[]}` emitted by that command |

### Rooms — tier **b** (Room row is truth; every write emits `room.*`). `TakeOutOfOrder` / `ReturnToService` and Setup room retire / type change **still version `availability:<hotel>`** in the same batch (D-8): the row is tier b, the supply change is not.
| command | needs | checks | emits |
|---|---|---|---|
| `SetHousekeeping {roomId, clean|dirty}` | `room.set_status` | – | `room.marked_clean` / `marked_dirty` |
| `TakeOutOfOrder {roomId, reason}` / `ReturnToService` | `room.set_out_of_order` | no checked-in stay tonight · versions availability | `room.taken_out_of_order` / `returned_to_service` |
| `SetRoomNote` | `room.set_status` | – | `room.note_set` |

### Billing (over Ledger) — tier **a** (Ledger streams; folio / receivable = projections)
| command | needs | checks | emits |
|---|---|---|---|
| `PostCharge {stayId, categoryId, itemId?, description?, qty, unitPrice}` | `folio.post_charge` | target folio open (per routing) · category ≠ room | `folio.charge_posted` → `ledger.entry_posted` |
| `VoidCharge {chargeId, reason}` | `folio.void` | folio open | `folio.charge_voided` → `ledger.entry_reversed` |
| `RepriceCharge {chargeId, unitPrice, reason}` (5.8; the only "discount": no discount concept in the ledger) | `folio.void` | folio open · unitPrice ≥ 0 · ≠ current | `folio.charge_voided` + `folio.charge_posted {…, repricedFrom: chargeId}` → reversal + entry, one batch |
| `MoveCharge {chargeId, toFolioId}` | `folio.move_line` | both folios open | `folio.charge_moved` → reversal + new entry |
| `TakePayment {folioId, method, amount, kind deposit|settlement, ref?}` | `folio.take_payment` | folio open · amount > 0 | `folio.payment_received` → entry |
| `Refund {folioId, method, amount, reason}` | `folio.refund` | amount ≤ payments − refunds − forfeits (mirror of the forfeit cap; review B14) | `folio.payment_refunded` → entry; closes the folio in the same batch if it lands on 0 and the stay is terminal |
| `ForfeitDeposit {folioId, amount, reason}` (5.4) | `folio.forfeit` (owner) | stay cancelled / no-show, or a cancelled group's master · amount ≤ deposits − refunds − forfeits | `folio.deposit_forfeited` (a charge under system category `depositForfeit`) → entry; if a refund or forfeit brings the folio to 0 it closes in the same batch (`folio.closed`, `ledger.account_closed`) |
| `TransferToReceivable {folioId, companyId, amount?}` | `folio.transfer_to_receivable` | folio open · amount ≤ balance | `folio.transferred_to_receivable` (+ `ledger.account_opened` on first transfer for that company) → entry |
| `CloseFolio {folioId}` | `folio.take_payment` | balance 0 | `folio.closed`, `ledger.account_closed` |
| `RecordReceivablePayment {receivableId, method, amount, ref?}` | `receivable.record_payment` | open/partial · ≤ remaining | `receivable.payment_received` (+ `settled`) → entry |
| `WriteOffReceivable {receivableId, reason}` | `receivable.write_off` | open/partial | `receivable.written_off` → entry |
| `PostNightlyRoomCharges {businessDate}` (system: cron at roll + lazy on first request after; also called by CheckIn for tonight) | system | idempotent per (stayId, businessDate) · per checked-in stay, tonight unposted (D-25) | `folio.charge_posted`×N, night.posted = true |

### Guests · Expenses · Setup · Users — Guests, Setup, Users tier **b**; Expenses tier **a** via Ledger (the expense *is* an entry; `expense.*` rides on the ledger stream)
| command | needs | emits |
|---|---|---|
| `CreateGuest / UpdateGuest / EraseGuest` | `booking.edit` (erase: `guests.erase`, owner only) | `guest.created` / `updated` / `erased` |
| `CreateContact / UpdateContact / EraseContact` | `booking.edit` (erase: `guests.erase`, owner only) | `contact.created` / `updated` / `erased` |
| `RecordExpense {businessDate, categoryId, amount, method, description, reference?}` / `VoidExpense` | `expense.record` / `expense.void` | `expense.recorded` / `voided` → entry |
| `Define / Update / Retire <SetupItem>` (Floor, RoomType, Room, RateTable, ChargeCategory, ChargeItem, BookingSource), `SetHotelProfile`, `SetBookingRules` | `setup.edit` | `<item>.defined / updated / retired`; Room retire/type change also versions availability |
| `SetRoomType {roomId, roomTypeId}` (5.7, with G14/G15 edits; G8) | `setup.edit` | `room.type_changed {roomId, roomTypeId}`; versions availability (supply bucket moves). Refused if the type is unknown or retired (`setup.roomTypeInvalid`). **Allowed with a checked-in stay**: the stay's nights already carry their price; the type is a label + future-availability bucket. Until 5.7: define the room again under the right type, retire the old one |
| `DefineCompany {name, defaultRouting?} / UpdateCompany / RetireCompany` | `setup.edit` | `company.defined / updated / retired`; retire refused while the company has a live stay or an unsettled master folio (`company.inUse`) |
| `CreateUser / UpdateUser / ResetPassword` | `users.manage` | `user.created / updated / password_reset` on `<hotelId>/user:<id>`; `user.created` carries the username, never the name (D-20); ResetPassword ends the person's live sessions |
| ~~`DisableUser`~~ **deferred** | – | identity ≠ access: `DeactivateStaff` ends the position and live sessions, so an account with no membership signing in to an empty shell is harmless. If a lock is ever needed: `disabledAt` on the account checked at sign-in, never a delete (D-18 built note). |
| `AddStaff {userId, role}` / `ChangeStaffRole {userId, role}` / `DeactivateStaff` / `ReactivateStaff` | `users.manage` | `staff.added / role_changed {role, from} / deactivated / reactivated` — refuse `staff.lastOwner`, `staff.alreadyStaff` |

### Approvals — tier **a**, stream `<hotelId>/approval:<id>` (slice 5.8, after 5.7; v1 unless Alex says later)
One rule: **an owner-only money act the desk cannot do becomes a request from the same button.** Kinds = exactly the owner-only money commands: `void` (VoidCharge) · `reprice` (RepriceCharge) · `refund` (Refund) · `forfeit` (ForfeitDeposit, 5.4) · `writeOff` (WriteOffReceivable). No discount kind: PostCharge already refuses `unitPrice < 0` (`folio.priceInvalid`), so there is no free discount path; `reprice` *is* the discount approval.
```ts
type ApprovalKind = 'void' | 'reprice' | 'refund' | 'forfeit' | 'writeOff'
type ApprovalSubject = { chargeId: ChargeId } | { folioId: FolioId } | { receivableId: ReceivableId }   // the subject carries the amount; only refund / forfeit / writeOff carry one explicitly
type Approval = { id: ApprovalId; hotelId; kind; subject; stayId?: StayId; bookingId?: BookingId; amount?: Money; unitPrice?: Money; reason: string;
                  status: 'open' | 'granted' | 'declined' | 'expired'; requestedBy: UserId; decidedBy?: UserId; decidedAt?: Instant }
```
| command | needs | checks | emits |
|---|---|---|---|
| `RequestApproval {kind, subject, amount? \| unitPrice?, reason}` | the desk bundle (no capability: whoever *cannot* run the underlying command may request it; an owner just runs the command) | subject exists and open (folio open / receivable unsettled) · **one open request per subject** (`approval.alreadyOpen`) · same payload rules as the underlying command (refund ≤ payments, reprice ≠ current) | `approval.requested {kind, subject, stayId?, bookingId?, amount?, unitPrice?, reason}` |
| `GrantApproval {approvalId}` | `approval.decide` | status open · underlying command still valid (re-checked now, not at request time) | `approval.granted` **+ the underlying command's events in the same batch**, each carrying `approvalId` (e.g. `folio.charge_voided {…, approvalId}`), actor = the owner, `causationId` = the grant. If the underlying command refuses, nothing is written and the card shows the refusal; the request stays open |
| `DeclineApproval {approvalId, reason}` | `approval.decide` | status open | `approval.declined {reason}` |
| *(reaction)* `CheckOut` of the stay, `CloseBooking` for master-folio subjects, `receivable.settled` for write-offs | – | any open request on the subject | `approval.expired {cause: 'checked_out' \| 'booking_closed' \| 'settled'}` — nothing is ever applied after the guest left |
Projections: `FolioView` / `Receivables` line badge from `approval.*` (open → *đang chờ duyệt*, declined → *từ chối: reason*, granted → the line simply changes); `NeedsAttention.approval.pending`; `History` on the stay shows the request and the decision. Exactly-once on grant = the stream version guard + `commandId` (D-8); that is why this is tier a, not a row.

**5.8 landings:** (1) domain — `Approval` aggregate, four kinds, `RepriceCharge`, expiry reactions, projections; (2) owner — Needs attention row → card → Duyệt / Từ chối; (3) desk — the three folio controls + receivables write-off render as Xin duyệt when the actor lacks the capability, badges on lines / bill. Each landing is testable alone; (3) can ship before (2) with the owner deciding from the stay page's History if needed.

~42 commands. Screens (§3) are compositions of these; nothing in the UI does what a command can't.

## 11a. Slice 1 payloads — occupancy loop (pinned 2026-09-23 for dev; walk-in individual only)

**Frozen 92cefea.** Amendment 2026-09-23 (additive only): `StayNightsChanged` added for early check-out; `TakeOutOfOrder` stream line; OOO-at-assign = warn. No existing shape changed.

Exact shapes for the first slice. **Frozen 2026-09-23** after last pass. Group bookings, money, and Setup come in later slices; payload *types* already admit them (unions, arrays) so no schemaVersion bump is needed — slice 1 restricts by *rule*, not by type. Ids are ulids as strings. `LocalDate` = `'YYYY-MM-DD'` in hotel-local calendar; `Instant` = ISO-8601 UTC; `Money` = integer VND. Stream ids are hotel-first: `<hotelId>/<type>:<id>`, availability = `<hotelId>/availability:all`.

```ts
// ---- commands (input the handler receives; hotelId + actor come from the session, not the body)

type CreateBooking = {
  commandId: string                       // idempotency
  kind: 'individual' | 'group'            // slice 1 rejects 'group' by rule, not by type
  contact: { name: string; phone?: string }   // handler mints a contacts row, stores contactId only
  contactId?: string                      // slice 2 widening: reuse an existing contact instead of minting
  sourceId?: string
  arrive: LocalDate
  depart: LocalDate                       // exclusive; depart > arrive
  request: { roomTypeId: string; bedType: string; adults: number; children: number; ratePerNight: number }
  roomId?: string                         // walk-in usually picks the room now; may be left for AssignRoom
  notes?: string
}
// minimum a receptionist must type: contact.name, arrive, depart, roomTypeId, adults. Everything else defaults
// (bedType from room, ratePerNight from RateTable else refuse rate.notFound unless typed (D-21), children 0).

type AssignRoom   = { commandId; stayId: string; roomId: string; fromDate?: LocalDate }   // fromDate default = first unposted night
type CheckIn      = { commandId; stayId: string; guests?: Array<{ name: string; idDoc?: { type: 'cccd'|'passport'|'other'; number: string } }> }
                    // guests upserted to guests rows; event carries guestIds only
type CheckOut     = { commandId; stayId: string }        // slice 1: folio check skipped (no money yet) — re-enabled in slice 3
type CancelStay   = { commandId; stayId: string; reason: string }
type CancelBooking= { commandId; bookingId: string; reason: string }
type SetHousekeeping = { commandId; roomId: string; state: 'clean' | 'dirty' }

// ---- event payloads (envelope per D-12 wraps these)

type BookingCreated = {
  bookingId: string; kind: 'individual' | 'group'; party: { contactId: string; companyId?: string }
  sourceId?: string; arrive: LocalDate; depart: LocalDate
  requests: Array<{ roomTypeId: string; bedType: string; qty: number; adults: number; children: number; ratePerNight: number }>
  notes?: string
}
type StayCreated = {
  stayId: string; bookingId: string; roomTypeId: string; bedType: string
  nights: Array<{ date: LocalDate; roomId?: string; rate: number; posted: boolean }>   // slice 1 always posted:false
  adults: number; children: number; guestIds: string[]                                   // slice 1 always []
}
type StayRoomAssigned  = { stayId: string; roomId: string; fromDate: LocalDate }
type StayCheckedIn     = { stayId: string; at: Instant; roomId: string; guestIds: string[] }
type StayNightsChanged = { stayId: string; added: Array<{ date: LocalDate; roomId?: string; rate: number }>; removed: LocalDate[] }   // early check-out emits removed only
type StayCheckedOut    = { stayId: string; at: Instant }
type StayCancelled     = { stayId: string; reason: string }
type BookingCancelled  = { bookingId: string; reason: string }
type RoomMarkedDirty   = { roomId: string; cause: 'checkout' | 'manual'; stayId?: string }   // tier b notification; stayId when cause = checkout
type RoomMarkedClean   = { roomId: string }

// ---- streams touched per command (same batch)
// (all stream ids prefixed <hotelId>/)
// CreateBooking : booking:<id> (booking.created) · stay:<id> (stay.created) · availability:all (version++ if roomId given)
// AssignRoom    : stay:<id> · availability:all
// CheckIn       : stay:<id> (stay.nights_changed {added: [today..arrive-1] | removed: unposted < today} if today ∉ nights, then stay.checked_in) · availability:all if nights changed · (slice 3 adds folio charge)
// CheckOut      : stay:<id> (stay.nights_changed {added: [], removed: [dates > businessDate(at)]} if any, then stay.checked_out) · availability:all if nights removed · rooms row update + room.marked_dirty {cause:'checkout', stayId} (reaction, in-batch, not on replay)
// TakeOutOfOrder: rooms row + room.taken_out_of_order · availability:all (supply change; warn if a stay holds the room)
// CancelStay    : stay:<id> · availability:all
// CancelBooking : booking:<id> · stay:<id> ×N · availability:all
```

Rules active in slice 1: arrive < depart · room free on every night `[arrive, depart)` · room not OOO at check-in (OOO at assign = warn only) · cancel only from `booked` · check-out only from `checkedIn` · early check-out frees nights after today's business date (`stay.nights_changed`, all nights unposted in slice 1) · check-in normalizes nights to include today (early arrival adds, late arrival drops before-today) so a checked-in stay always has ≥ 1 night. Overbooking per type: warn only (override event in slice 2).

## 12. Event index

Envelope + naming per §6 conventions (D-12). **Two tiers (D-22)**: `booking.*` `stay.*` `ledger.*` (+ `folio.*` `receivable.*` `expense.*` as Ledger-derived) are state — folded on replay. `room.*` `guest.*` `contact.*` `setup.*` `user.*` `staff.*` are **notifications**: emitted on every CRUD write for history tabs and projections, never folded; the row is truth. Streams: `booking:*` `stay:*` `room:*` `ledger:<kind>:<id>` (one per ledger account — folio, receivable, cash, bank, revenue, expense; an entry is appended to every account stream it touches, deduped by entryId) `guest:*` `contact:*` `expense:*` `setup:*` `user:*` `staff:*` + `availability:all` (serialisation only, D-8; its sole event `availability.changed {cause}` is never folded). **Stream ids are hotel-first per D-9: `<hotelId>/booking:<id>`, `<hotelId>/availability:all`.**

`booking.` created · requests_changed · party_changed · notes_changed · cancelled · closed · stay_merged_in (reserved)
`stay.` created · room_assigned · room_unassigned · room_changed · nights_changed · rate_set · guest_added · guest_removed · occupancy_set · routing_set · checked_in · checked_out · cancelled · marked_no_show · overbooking_overridden
`room.` defined · updated · retired · type_changed · marked_clean · marked_dirty · taken_out_of_order · returned_to_service · note_set
`availability.` changed {cause} — version bump only
`folio.` opened · charge_posted · charge_voided · charge_moved · payment_received · payment_refunded · deposit_forfeited · transferred_to_receivable · closed
`receivable.` payment_received · settled · written_off — account opens via `ledger.account_opened`, lazily
`ledger.` account_opened · entry_posted · entry_reversed · account_closed — on `<hotelId>/ledger:<kind>:<id>`; entry events carry the full entry, appear once per touched account
`guest.` created · updated · erased (tombstone, D-20)
`contact.` created · updated · erased — same shape as guest; booker ≠ sleeper, kept separate
`expense.` recorded · voided
`setup.` `<item>.defined / updated / retired` · hotel_profile_set · booking_rules_set
`user.` created · updated · password_reset(byUserId) — identity events; visible in History to owner only
`staff.` added {userId, role} · role_changed {userId, role, from} · deactivated · reactivated — membership per (hotel, user), stream `<hotelId>/staff:<userId>`; no names in payloads
`approval.` requested {kind, subject, stayId?, bookingId?, amount?, unitPrice?, reason} · granted · declined {reason} · expired {cause} — 5.8, stream `<hotelId>/approval:<id>`; granted is followed in the same batch by the underlying command's events carrying `approvalId`

## Status

- 2026-09-19 — not started.
- 2026-09-23 — v0 draft from requirements + explore's ezFolio map. Aggregate list sent to architect.
- 2026-09-23 — v0.1: D-6 folded — setup/admin persona, Catalogue → Setup context (HotelProfile, Room/Type/Floor defs, RateTable, ChargeItem, ChargeBehaviour, Company, BookingRules). Awaiting Alex on §10.
- 2026-09-23 · **v1** — full session w/ Alex: multi-tenant (D-9), naming/envelope (D-12), Booking (D-13), Stay+nights (D-14/15), money + Ledger (D-16/17), roles/authz (D-18), screens (D-19), rules §10, command catalogue §11, event index §12.
