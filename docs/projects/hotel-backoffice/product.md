# SoLex — Product / Domain Model (WS3)

Owner: `solex-product`. **v0.1 draft, 2026-09-23** — built from `requirements.md` + `existing-system.md` (explore, through 2026-09-23) + D-4/D-5/D-6. Not yet reviewed with Alex; open policy points in §10. Event names here are the ES vocabulary; dev should not invent others.

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
  | 'stay.assign' | 'stay.check_in' | 'stay.check_out' | 'stay.move' | 'stay.cancel'
  | 'folio.post_charge' | 'folio.void' | 'folio.move_line' | 'folio.take_payment' | 'folio.refund' | 'folio.transfer_to_receivable'
  | 'room.set_status' | 'room.set_out_of_order'
  | 'receivable.record_payment' | 'receivable.write_off'
  | 'expense.record' | 'expense.void'
  | 'reports.view' | 'guests.view'
  | 'setup.edit' | 'users.manage'
type Role = { id: RoleId; hotelId: HotelId; name: string; capabilities: Capability[] }
type User = { id: UserId; hotelId: HotelId; name: string; email: string; roleId: RoleId; status: 'active' | 'disabled' }
```
- Every command declares the capability it needs; the handler checks it against the actor. Audit = event `actor` + capability.
- **v1 ships two fixed bundles**: `receptionist` (Front Desk ops + receivable payments + expense record, assumed) and `owner` (all). Sensitive ones — void, refund, write-off, setup, users — sit in `owner` by default.
- Custom roles / editing bundles in Setup → later; the model already allows it because a role *is* a capability list.
- No approval workflows in v1 (discount approval → later ticket). Admin SDK (D-9) sits outside the apps, for seeding/tenant creation.

Housekeeping, restaurant, etc. are off-system; reception acts on their behalf.

## 3. Jobs to be done

Receptionist: quote availability for a date range by room type → take a booking (individual: specific room; group: types × qty) → assign rooms → check in (register guests) → post charges during stay → move/extend stays → check out and settle (cash/transfer/card/to company debt) → keep room status current → chase receivables → record expenses.

Manager: today's state (vacant, arrivals, departures, revenue) · forward book (occupancy, revenue forecast) · revenue by bucket / channel / payment method · unpaid + receivables by debtor type · guest history · expenses / P&L-ish · approve discounts.

Setup/admin: onboard the hotel (identity, floors, rooms, types, bed types) · set and change prices (rate table, charge items) · curate catalogues (no duplicates, archive dead items) · set tax/service % per bucket · set booking rules (day boundary, overbooking, child age, default check-in/out times, ID enforcement) · register channels/companies with commission + terms.

## 4. Home screens (projections, not reports)

- **Room map** — now. Tiles by floor; color = derived status; tile → check-in, balance, post charge, set dirty/clean/OOO.
- **Tape chart** — over time. Room × date grid, stay bars; drag = move/extend (emits `RoomChanged` / `StayDatesChanged`); shows per-type availability inline for quoting.
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
| **Setup** | HotelProfile, Floor, RoomType, Room definitions, RateTable, ChargeCategory + ChargeItem, BookingSource, ExpenseCategory, Company, BookingRules | reference data; upstream of everything, depends on nothing; seeded by admin SDK (D-9) |
| **Reservations** | Booking, Stay (nights), availability rule | the commercial + stay lifecycle |
| **Rooms** | Room housekeeping / out-of-order state | definition comes from Setup |
| **Billing** | charge / payment / transfer / deposit commands; folio + receivable *projections* | hotel vocabulary over the Ledger; no aggregates of its own |
| **Ledger** | Account, Entry | generic double-entry; knows nothing about hotels |
| **Guests** | Guest | thin profile, reused across stays |
| **Expenses** | expense commands | owner's cash-out; posts to Ledger |

How downstream uses Setup: (1) **lookup at command time** — e.g. posting item X copies X's current price onto the entry; later price changes never touch history. (2) **react to a Setup event** — only where supply changes: `room.retired` / `room.type_changed` version `availability:<hotel>` (D-8). Setup never reads downstream; its one guard ("can't retire a room with future nights") is a check in the command against the projection.

## 6. Aggregates, events, invariants

Format (agreed w/ Alex 2026-09-23): each thing = TypeScript type + events + rules. American English. Types are the contract for dev; field names are final unless a decision changes them.

### Conventions

**Dates vs timestamps.** `LocalDate` = calendar day, no time/zone (`2026-09-23`) — used for *nights*: arrive/depart, `businessDate`, rate ranges. `Instant` = exact UTC moment — used for *when things happened*: `occurredAt`, actual check-in/out. A night is not a moment; D-7 converts one to the other once, at write time. `HotelProfile.timeZone` (e.g. `Asia/Ho_Chi_Minh`) is the only zone in play. Stay covers nights `[arrive, depart)` (depart exclusive). Money = VND integer; USD display only.

**Event naming.** `<aggregate>.<past_tense_verb>`, lowercase, dotted, snake_case verbs: `booking.created`, `stay.room_assigned`, `folio.charge_posted`. Prefix = stream type; `folio.*` filters trivially.

**Event envelope** (every event, every stream):
```ts
type Event<T extends string = string, P = unknown> = {
  id: EventId                  // ulid — unique, time-sortable
  hotelId: HotelId             // tenant key (D-9)
  stream: string               // 'booking:<id>' — aggregate type + id
  version: number              // position in stream; UNIQUE(stream, version) (D-8)
  type: T                      // 'booking.created'
  schemaVersion: number        // per-type payload version; never edit old rows
  payload: P
  occurredAt: Instant
  businessDate: LocalDate      // hotel day it counts toward (D-7); stored, not re-derived
  actor: { kind: 'user'; userId: UserId } | { kind: 'system'; job: string }
  correlationId: string        // one per user action (one check-in → several events)
  causationId?: EventId
  commandId?: string           // client idempotency key; safe retries under D-8
}
```
No `metadata` grab-bag; no `aggregateType` (in `stream`).

### Booking — the commercial envelope (settled w/ Alex 2026-09-23)

A group = one Booking holding N Stays (company, contact, requested types × qty; rooms assigned later or now). An individual = one Booking with one Stay, room picked at creation. Same shape, no special case. Two-level on purpose: master folio, group cancel, "20 adults across 15 rooms not yet assigned" all need the envelope.

```ts
type Booking = {
  id: BookingId
  hotelId: HotelId
  kind: 'individual' | 'group'
  party: { companyId?: CompanyId; contactName: string; phone?: string }
  sourceId?: BookingSourceId   // Setup-defined list (walk-in, phone, Agoda…); lookup only, no logic
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
  routing?: Partial<Record<Bucket, 'own' | 'master'>>       // group stays only; default from Booking's company
  status: 'booked' | 'checkedIn' | 'checkedOut' | 'cancelled' | 'noShow'
  checkedInAt?: Instant
  checkedOutAt?: Instant
}
```
Events: `stay.created` · `stay.room_assigned(roomId, fromDate?)` · `stay.room_unassigned` · `stay.room_changed(fromDate, roomId)` · `stay.nights_changed(added[], removed[])` · `stay.rate_set(date, amount)` · `stay.guest_added` · `stay.guest_removed` · `stay.routing_set(bucket, target)` · `stay.checked_in` · `stay.checked_out` · `stay.cancelled(reason)` · `stay.marked_no_show` · `stay.overbooking_overridden`.
Rules: check-in needs tonight's room assigned and not out of order · check-out needs own folio at 0 or moved to a receivable · nights change only before check-out · posted nights are immutable (no rate/room change) · no-show only from `booked`, after arrival date · cancel only if not checked in, reason required, charges moved off first (ezFolio guards).

Assumptions (Alex 2026-09-23: business calls, not system-breaking; adjust later):
- **Room move mid-stay**: `room_changed` rewrites `roomId` on unposted nights from that date; rate unchanged by default, editable. Different room type → UI warns, no auto-reprice.
- **Extend**: `nights_changed` appends nights, pre-filled from the rate table, editable before they post.

Dropped from v0: ezFolio flags `foc` (= rate 0), `isNet` (OTA, deferred), `locked` (no clear use).

### Availability (cross-aggregate rule, Reservations context)
- **Per room**: no two stays may hold the same `(roomId, date)` (cancelled / no-show don't count). One rule, per night, no interval math. Same-day turnover is free by construction.
- **Per type**: for each night, `stays of that type (assigned or not, not cancelled) ≤ rooms of that type in service`. Overbooking policy = **warn + explicit override** (`stay.overbooking_overridden`), assumed because high occupancy means they sell to the edge.
- **Enforcement (D-8)**: one `availability:<hotel>` stream; every command that changes supply or demand versions it in the same batch — room assign/change/unassign, nights change, check-in with assignment, room out-of-order / back in service, room retire or type change (Setup), overbooking override.

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
Events: `room.marked_dirty` · `room.marked_clean` · `room.taken_out_of_order(reason)` · `room.returned_to_service` · `room.note_set`. (Definition events live in Setup: `room.defined/updated/retired`.)
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
// balance(account) = Σ its lines · entries immutable; undo = reversal entry · account closes only at 0
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

One **own folio** per Stay + one **master folio** per group Booking. A charge is posted *against a stay*; the stay's routing for that category decides which folio it lands on. Stay = one visit = one folio, as Alex put it.

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
  description: string
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
Events: `folio.opened` · `folio.charge_posted` · `folio.charge_voided(reason)` · `folio.charge_moved(chargeId, toFolioId)` (ezFolio "Chuyển dịch vụ") · `folio.payment_received` · `folio.payment_refunded` · `folio.transferred_to_receivable(companyId, amount)` · `folio.closed`.
Rules: never edit a charge — void and repost · a night's room charge posts once, at the roll (D-7), or at check-in for the current night · move charges only while both folios open · close only at 0 or after transfer · deposit = payment of kind `deposit` (master folio for groups, stay folio for individuals); forfeit = `folio.deposit_forfeited` posts a compensation charge against it.

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
Events: `receivable.opened` · `receivable.payment_received(method, amount, ref?)` · `receivable.settled` · `receivable.written_off(reason)`.
Rules: opened only from a folio transfer · payments ≤ amount · settled when paid in full.

### Guest — thin profile (settled w/ Alex 2026-09-23)

```ts
type Guest = { id: GuestId; hotelId: HotelId; name: string; phone?: string; email?: string; nationality?: string
  idDoc?: { type: 'cccd' | 'passport' | 'other'; number: string }; notes?: string }
```
Events: `guest.created` · `guest.updated`. Belongs to the hotel (D-9); reused across stays for history. ID capture optional in v1. Later: merge duplicates, PA18 police export, VIP class.

### Setup context (D-6) — what the hotel is made of

Reference data, retire-not-delete, seeded by admin SDK (D-9). Each has `<name>.defined / updated / retired` events for audit.
- `HotelProfile` — name, address, **timeZone**, `checkInTime` 14:00, `checkOutTime` 12:00, `businessDayStart` 02:00 (D-7)
- `Floor`, `RoomType` (name, capacity), `Room` (number, floor, type, bedType)
- `RateTable` — `{roomTypeId, bedType, dateRange | dayOfWeek, ratePerNight}`; no overlapping ranges
- `ChargeCategory` — seeded room · roomSurcharge · minibar · laundry · compensation · extraService · restaurant; `room` reserved
- `ChargeItem` — category, VN + EN name, unitPrice, active
- `BookingSource` — walk-in, phone, Agoda, … (lookup only)
- `ExpenseCategory` — groceries, incidental, hk overtime, advance, other
- `Company` — name, contact, kind, default group routing `{category → own | master}`; commission/terms → later
- `BookingRules` — childAgeThreshold 6, overbooking `warn` (override allowed), autoDirtyOnCheckout true, idEnforcement optional
Rules: unique room numbers per hotel; retired items not selectable; can't retire a room with future nights.

### Expense — owner's cash-out (settled w/ Alex 2026-09-23; posts to Ledger)

```ts
type ExpenseCommand = { businessDate: LocalDate; categoryId: ExpenseCategoryId; amount: Money; method: 'cash' | 'bankTransfer'; payee?: string; note?: string }
```
Events: `expense.recorded` · `expense.voided(reason)` → ledger entries. Projection: expenses by category / period.

## 7. The "Need" cascade (requirements §1) → events → projections

| step | trigger event | projection |
|---|---|---|
| room status change | `StayCheckedIn` / `StayCheckedOut` / `RoomMarked*` / `RoomTakenOutOfOrder` | **RoomMap** (per-room derived status + color) |
| dashboard updates | same + `StayCreated` | **DashboardToday** (vacant, arrivals, departures, in-house, unpaid) |
| occupancy % | stay events + room service events | **Occupancy** per night (used / sellable) |
| revenue forecast | stay events + `StayRateSet` | **ForwardBook** (rooms sold × rate per night, by type) |
| housekeeping knows checkout date | stay events | **HKSheet** (per room: state, depart date, notes) |
| reception knows room money | `ChargePosted` / `PaymentReceived` / `DiscountApproved` | **FolioBalance** (deposit / paid / outstanding per stay + master) |
| guest history | `StayCheckedOut` + guest events | **GuestHistory** (visits, nights, spend, class) |
| OTA commission | `StayCheckedOut` / `FolioClosed` | **CommissionByChannel** (rate × room revenue) |

Other projections: **TapeChart** (stays × rooms × dates + per-type availability), **Arrivals/Departures**, **WaitingList** (unassigned stays), **Revenue** by day/month/year × bucket × payment method × channel, **ReceivablesByDebtorType** (+ overdue), **Deposits**, **Breakfast list** (per occupied room, adults/children, nationality), **PA18 export** (in-house guests' ID data), **Expenses** by category/period, **AuditLog** per booking (all events with actor).

## 8. Core vs later

**Core (v1):** Setup context (onboarding + prices + rules) · individual + group booking with inline availability · waiting list + assignment · tape chart + room map · check-in/out · guests per stay (ID optional per §10) · one charge flow, 8 buckets, catalogue · folio own/master + routing · payments cash/transfer/card-method + deposits + refunds · receivables by debtor · discount approval trail · room hk state + OOO · dashboard + revenue/occupancy/receivables reports · expenses · audit log · Excel export of lists.
**Later:** PA18 export (if legally needed, §10) · breakfast list · airport pickup list · thank-you email · channel-manager sync · red invoice/VAT lines · multi-currency beyond USD display.
**Never:** card data · restaurant POS · hk staff scheduling · key cards · hourly/day-use · multi-property.

## 9. Dependencies on WS2 / for other WSs

- Model mirrors ezFolio's `reservation → reservation_room → traveller` chain deliberately (staff mental model), but names and shape are ours (D-5).
- ezFolio item masters never seen and no longer pursued (D-6) — Setup context is designed fresh from explore's checklist; seed values (rooms, types, items, prices) come from Alex/client at onboarding.
- **For dev**: single-writer DO per hotel for the Reservations context (availability rule); D1 for projections; bucket enum + event names above are the contract. No card fields anywhere.
- **For architect**: policy points §10 need Alex; two are already in `team/questions.md`.

## 10. Policy points (model as configurable; decide with Alex)

1. **Day boundary** — room charge for night N posts at fixed local time (ezFolio 23:59) vs at check-out. Affects "revenue today" basis (accrual per night vs cash at checkout). Recommend: post per night at a fixed roll time; dashboard shows both.
2. **Overbooking** — hard block vs receptionist override with event. Recommend override (turnover days hit >100% today).
3. **Guest ID at check-in** — enforce vs optional with warning. Depends on PA18 need.
4. **PA18** — legally required? If yes, ID enforcement follows.
5. **OTA commission basis** — OTA remits net (receivable = net) vs hotel pays commission out. Per Company setting.
6. **VAT / red invoice** — out for v1 unless client says otherwise; tax/service % kept per ChargeItem at 0.
7. **Cancellation / no-show charging** — per-channel policy or manual charge? Recommend manual `compensation` charge for v1.
8. **Group billing default** — all buckets to master (today's usage) vs room-only to master (corporate norm). Default per Company.

## Status

- 2026-09-19 — not started.
- 2026-09-23 — v0 draft from requirements + explore's ezFolio map. Aggregate list sent to architect.
- 2026-09-23 — v0.1: D-6 folded — setup/admin persona, Catalogue → Setup context (HotelProfile, Room/Type/Floor defs, RateTable, ChargeItem, ChargeBehaviour, Company, BookingRules). Awaiting Alex on §10.
