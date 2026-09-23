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
  | 'stay.assign' | 'stay.check_in' | 'stay.check_out' | 'stay.move' | 'stay.cancel'
  | 'folio.post_charge' | 'folio.void' | 'folio.move_line' | 'folio.take_payment' | 'folio.refund' | 'folio.transfer_to_receivable'
  | 'room.set_status' | 'room.set_out_of_order'
  | 'receivable.record_payment' | 'receivable.write_off'
  | 'expense.record' | 'expense.void'
  | 'reports.view' | 'guests.view'
  | 'setup.edit' | 'users.manage'
type Role = { id: RoleId; hotelId: HotelId; name: string; capabilities: Capability[] }
// role hangs off the (hotel, user) membership pair, not the user: a person can be owner at one hotel and receptionist at another later (D-9)
type User = { id: UserId; hotelId: HotelId; name: string; username: string; email?: string; roleId: RoleId; status: 'active' | 'disabled' }
// identity (password, sessions) lives in Better Auth's mutable tables (D-11), NOT in the event log; membership + role changes are events (`user.*`). Sign-in by username for all roles, email optional; password reset by owner. Deactivated users stay in history, render as "(former)".
```
- Every command declares the capability it needs; the handler checks it against the actor. Audit = event `actor` + capability.
- **v1 ships two fixed bundles**: `receptionist` (Front Desk ops + receivable payments + expense record, assumed) and `owner` (all). Sensitive ones — void, refund, write-off, setup, users — sit in `owner` by default.
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
| **New booking** | individual: room + dates + guest → done (one stay, assigned). Group: company, dates, types × qty, assign now (default) or later |
| **Booking page** | edit party / notes, add / remove stays, assign rooms, cancel w/ reason, master folio |
| **Stay page** | guests, nights (room + rate per night), check in, check out, move, extend, cancel / no-show, own folio |
| **Folio** | lines; post charge (catalogue item or free text); void [owner]; move line to another folio; take payment (cash / transfer / card); deposit; refund [owner]; transfer remainder to company; close; **print** |
| **Arrivals / departures today** | lists off the map; one-click check in / out |
| **Search** | booking / stay by guest name, phone, company |

### Back Office app
| screen | actions |
|---|---|
| **Dashboard** | today: occupancy, arrivals, departures, revenue posted, cash in; forward book |
| **Receivables** | by company; record payment; write off [owner] |
| **Expenses** | record, void; by category / period |
| **Reports** [owner] | revenue by category / source / method; occupancy over time; guest history |

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
| **Setup** | HotelProfile, Floor, RoomType, Room definitions, RateTable, ChargeCategory + ChargeItem, BookingSource, ExpenseCategory, Company, BookingRules | reference data; upstream of everything, depends on nothing; seeded by admin SDK (D-9) |
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
Rules: **check-in normalizes the stay to today**: tonight (current business date) must be a night of the stay — early arrival (before `arrive`) adds nights `[today, arrive)` at the first night's rate, room must be free for them, availability versioned, warn + allow; late arrival drops unposted nights before today (posted ones stay). Emitted as `stay.nights_changed` before `stay.checked_in`. So a checked-in stay always holds ≥ 1 night and same-day in/out still charges tonight · check-in needs tonight's room assigned and not out of order · check-out needs own folio at 0 or moved to a receivable · **early check-out** (before last night) drops every unposted night after the current business date in the same batch (`stay.nights_changed {removed}` then `stay.checked_out`) so they go back on sale — never implicit in `checked_out` · nights change only before check-out · posted nights are immutable (no rate/room change) · no-show only from `booked`, after arrival date · cancel only if not checked in, reason required, charges moved off first (ezFolio guards).

Assumptions (Alex 2026-09-23: business calls, not system-breaking; adjust later):
- **Room move mid-stay**: `room_changed` rewrites `roomId` on unposted nights from that date; rate unchanged by default, editable. Different room type → UI warns, no auto-reprice.
- **Extend**: `nights_changed` appends nights, pre-filled from the rate table, editable before they post.

Dropped from v0: ezFolio flags `foc` (= rate 0), `isNet` (OTA, deferred), `locked` (no clear use).

### Availability (cross-aggregate rule, Reservations context)
- **Per room**: no two stays may hold the same `(roomId, date)` (cancelled / no-show don't count). One rule, per night, no interval math. Same-day turnover is free by construction.
- **Per type**: for each night, `stays of that type (assigned or not, not cancelled) ≤ rooms of that type in service`. Overbooking policy = **warn + explicit override** (`stay.overbooking_overridden`), assumed because high occupancy means they sell to the edge.
- **Enforcement (D-8)**: one `<hotelId>/availability:all` stream; every command that changes supply or demand versions it in the same batch — room assign/change/unassign, nights change, early check-out, check-in with assignment, room out-of-order / back in service, room retire or type change (Setup), overbooking override. Its only event is `availability.changed {cause}` — serialisation only, nothing folds it.
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
**PII columns (D-20 / D-23 redaction denylist):** `guests.name`, `guests.phone`, `guests.email`, `guests.nationality`, `guests.id_doc_type`, `guests.id_doc_number`, `guests.notes`; `contacts.name`, `contacts.phone`; `users.name`, `users.email`. Not PII: ids, timestamps, status. `guest.updated` payload carries changed *field names*, never values.

Events: `guest.created` · `guest.updated` · `guest.erased` — **PII never enters event payloads** (D-20). Events carry `guestId` only; name/phone/idDoc live in a mutable `guests` table. Erasure = overwrite the row, log keeps a tombstone; replay still works. Same for `Booking.party.contactName/phone` → stored as a `contact` row referenced by id. Belongs to the hotel (D-9); reused across stays for history. ID capture optional in v1. Later: merge duplicates, PA18 police export, VIP class.

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
Rules: unique room numbers per hotel; retired items not selectable; can't retire a room with future nights; **can't retire a room type while any non-retired room references it** (refuse `roomType.inUse`; retire or re-type the rooms first — mirrors the room rule, and a retired type with live rooms would break availability counts); room type id = slug of name (`phong-doi`); rate ranges half-open `[from, to)`.

### Expense — owner's cash-out (settled w/ Alex 2026-09-23; posts to Ledger)

```ts
type ExpenseCommand = { businessDate: LocalDate; categoryId: ExpenseCategoryId; amount: Money; method: 'cash' | 'bankTransfer'; payee?: string; note?: string }
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
| **ForwardBook** | per future night: rooms sold × rate, by type | StayNights | forecast |
| **Revenue** | by business date × category × source × payment method | `ledger.*` + Setup lookups | reports |
| **Expenses** | by category × period | `expense.*` | Back Office |
| **GuestHistory** | per guest: visits, nights, spend | `stay.*`, `ledger.*` | guest page |
| **History** | per room / stay / folio: events with actor + time | all | "Show log" tabs (audit) |

Later: WaitingList (unassigned stays), Breakfast list, PA18 export, CommissionByChannel, Deposits ledger.

## 8. Scope

**v1:** Setup (onboarding, prices, catalogues, rules, users/roles) · individual + group booking with inline availability · assignment now or later · tape chart + room map · check-in/out · guests per stay (ID optional) · one charge flow over Setup-defined categories · folio own/master + routing · payments cash / transfer / card-method, deposits, refunds · receivables by company · room hk state + OOO · dashboard, revenue / occupancy / receivables reports · expenses · history/audit tabs · folio print · search.
**Later:** OTA support (commission, gross/net, sync) · discount approvals · VAT / red invoice · receivable due dates · group label/color · registration card print · PA18 export · breakfast / pickup lists · thank-you email · merge stay into group · inspected hk state · custom roles · per-staff activity report · multi-currency beyond USD display.
**Never:** card data · restaurant POS · hk staff scheduling · key cards · hourly / day-use.

## 9. Dependencies on WS2 / for other WSs

- Model mirrors ezFolio's `reservation → reservation_room → traveller` chain deliberately (staff mental model), but names and shape are ours (D-5).
- ezFolio item masters never seen and no longer pursued (D-6) — Setup context is designed fresh from explore's checklist; seed values (rooms, types, items, prices) come from Alex/client at onboarding.
- **For dev**: storage per D-8 (D1 event log + projections, optimistic concurrency, `availability:<hotel>` stream, no Durable Object); types §6 + commands §11 + events §12 are the contract. No card fields anywhere.
- **For architect**: policy points §10 need Alex; two are already in `team/questions.md`.

## 10. Rules and policy (settled w/ Alex 2026-09-23; all live in Setup `BookingRules` / `HotelProfile` or as capability defaults, so the client can flip them)

| # | rule | v1 |
|---|---|---|
| 1 | Hotel day | D-7. Business date rolls at `businessDayStart` 02:00. Room charge posts at the roll, or at check-in for the current night. Check-in before `checkInTime` 14:00 → optional early check-in item; checkout after `checkOutTime` 12:00 → optional late checkout item; after next roll → extra night (`stay.nights_changed`). Actual instants decide; typed dates are the plan. |
| 2 | Overbooking | warn + explicit override (D-15) |
| 3 | Cancellation / no-show | no automatic charge. Receptionist posts a compensation charge by hand if agreed. Deposit forfeit = explicit `ForfeitDeposit`. Cancel guards: not if checked in; reason required; charges moved off first. |
| 4 | Guest ID | optional; PA18 export later |
| 5 | Children | under `childAgeThreshold` (6) free, not counted against capacity |
| 6 | Room after checkout | auto `room.marked_dirty {cause: checkout, stayId}` (reaction, in-batch) |
| 6a | Early check-out | shortens the stay: unposted nights after today's business date removed (`stay.nights_changed`) and freed for sale; current night stays charged. Explicit event, not implied by `checked_out`. |
| 6c | Early / late check-in | Check-in makes today the first unposted night: early arrival adds nights `[today, arrive)` (warn + allow, room must be free), late arrival drops unposted nights before today. A checked-in stay never has zero nights; check-out before the first night cannot happen (tonight is always held and charged). Guest who leaves same day still pays tonight; day-use is out of scope. |
| 6b | Out-of-order room | assign to future nights: warn + allow. Check-in: refuse. Taking a room OOO under assigned nights: warn + allow. |
| 7 | Check-out with balance | blocked unless remainder transferred to a company receivable |
| 8 | Group billing default | routing from `Company.defaultRouting` (room → master, rest → own); editable per stay |
| 9 | Rates | prefilled from `RateTable` (ranges half-open `[from, to)`); no table rate and no desk-typed price → **refuse** `rate.notFound`, never silently 0 (D-21); 0 only when typed (FOC); editable until the night posts; posted nights immutable. Day-of-week rates later. |
| 10 | Sensitive money actions | void, refund, write-off, transfer = `owner` capabilities by default |

Deferred: OTA commission / gross-net · VAT / red invoice · discount approvals · receivable due dates.

## 11. Command catalogue (canonical list of actions; dev builds and tests from this)

Command = one intent. `needs` = capability. `checks` = rules beyond "hotel matches, entity exists". `emits` = events (Ledger entries implied for money). **Tier (D-22)**: **a** = event-sourced (log is truth, state = fold, version guard); **b** = event-notified (CRUD row is truth, write still appends an event to the same log, no fold). Rule of thumb: would we replay it to rebuild state? no → b.

### Reservations — tier **a** (Booking, Stay streams; availability stream)
| command | needs | checks | emits |
|---|---|---|---|
| `CreateBooking {kind, party, sourceId?, arrive, depart, requests[], notes?}` | `booking.create` | arrive < depart · qty ≥ 1 · availability per type (warn/override) · individual: room given + free | `booking.created`, `stay.created`×N, `folio.opened` (master if group, own per stay) |
| `ChangeBookingParty / Notes / Requests` | `booking.edit` | open · requests: availability | `booking.party_changed` / `notes_changed` / `requests_changed` (+ `stay.created`/`stay.cancelled`) |
| `CancelBooking {reason}` | `booking.cancel` | no stay checked in | `booking.cancelled`, `stay.cancelled`×N |
| `CloseBooking` | `booking.edit` | all stays terminal · master folio 0 or transferred | `booking.closed`, `folio.closed` |
| `AssignRoom {stayId, roomId, fromDate?}` | `stay.assign` | room type matches (warn) · room free those nights · OOO (warn) · versions availability | `stay.room_assigned` |
| `UnassignRoom {stayId}` | `stay.assign` | status booked | `stay.room_unassigned` |
| `MoveStay {stayId, fromDate, roomId}` | `stay.move` | not checked out · unposted nights only · room free · versions availability | `stay.room_changed` |
| `ChangeNights {stayId, add[], remove[]}` | `stay.assign` | not checked out · removed nights unposted · availability | `stay.nights_changed` |
| `SetNightRate {stayId, date, amount}` | `booking.edit` | night unposted | `stay.rate_set` |
| `AddGuest / RemoveGuest {stayId, guestId}` | `booking.edit` | not checked out | `stay.guest_added` / `guest_removed` |
| `SetRouting {stayId, categoryId, target}` | `booking.edit` | group stay | `stay.routing_set` |
| `CheckIn {stayId, guests[]?}` | `stay.check_in` | booked · tonight's room assigned, not OOO · early arrival: room free `[today, arrive)` (warn) | `stay.nights_changed` if today ∉ nights (versions availability), `stay.checked_in`, `folio.charge_posted` (tonight's room) |
| `CheckOut {stayId}` | `stay.check_out` | checkedIn · own folio 0 or transferred | `stay.nights_changed {removed}` if leaving early (versions availability), `stay.checked_out`, `folio.closed`, `room.marked_dirty` |
| `CancelStay {stayId, reason}` | `stay.cancel` | booked · folio has no unmoved charges | `stay.cancelled` |
| `MarkNoShow {stayId}` | `stay.cancel` | booked · after arrival date | `stay.marked_no_show` |
| `OverrideOverbooking {stayId}` | `stay.assign` (owner by default) | – | `stay.overbooking_overridden` |

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
| `MoveCharge {chargeId, toFolioId}` | `folio.move_line` | both folios open | `folio.charge_moved` → reversal + new entry |
| `TakePayment {folioId, method, amount, kind deposit|settlement, ref?}` | `folio.take_payment` | folio open · amount > 0 | `folio.payment_received` → entry |
| `Refund {folioId, method, amount, reason}` | `folio.refund` | ≤ payments | `folio.payment_refunded` → entry |
| `ForfeitDeposit {folioId, amount, reason}` | `folio.post_charge` | deposit exists | `folio.deposit_forfeited` (= compensation charge) |
| `TransferToReceivable {folioId, companyId, amount?}` | `folio.transfer_to_receivable` | folio open · amount ≤ balance | `folio.transferred_to_receivable`, `receivable.opened` → entry |
| `CloseFolio {folioId}` | `folio.take_payment` | balance 0 | `folio.closed`, `ledger.account_closed` |
| `RecordReceivablePayment {receivableId, method, amount, ref?}` | `receivable.record_payment` | open/partial · ≤ remaining | `receivable.payment_received` (+ `settled`) → entry |
| `WriteOffReceivable {receivableId, reason}` | `receivable.write_off` | open/partial | `receivable.written_off` → entry |
| `PostNightlyRoomCharges` (system, at roll) | system | per checked-in stay, tonight unposted | `folio.charge_posted`×N, night.posted = true |

### Guests · Expenses · Setup · Users — Guests, Setup, Users tier **b**; Expenses tier **a** via Ledger (the expense *is* an entry; `expense.*` rides on the ledger stream)
| command | needs | emits |
|---|---|---|
| `CreateGuest / UpdateGuest` | `booking.edit` | `guest.created` / `updated` |
| `RecordExpense {businessDate, categoryId, amount, method, payee?, note?}` / `VoidExpense` | `expense.record` / `expense.void` | `expense.recorded` / `voided` → entry |
| `Define / Update / Retire <SetupItem>` (Floor, RoomType, Room, RateTable, ChargeCategory, ChargeItem, BookingSource, ExpenseCategory, Company), `SetHotelProfile`, `SetBookingRules` | `setup.edit` | `<item>.defined / updated / retired`; Room retire/type change also versions availability |
| `CreateUser / UpdateUser / DisableUser`, `SetUserRole` | `users.manage` | `user.created / updated / disabled / role_set` |

~40 commands. Screens (§3) are compositions of these; nothing in the UI does what a command can't.

## 11a. Slice 1 payloads — occupancy loop (pinned 2026-09-23 for dev; walk-in individual only)

**Frozen 92cefea.** Amendment 2026-09-23 (additive only): `StayNightsChanged` added for early check-out; `TakeOutOfOrder` stream line; OOO-at-assign = warn. No existing shape changed.

Exact shapes for the first slice. **Frozen 2026-09-23** after last pass. Group bookings, money, and Setup come in later slices; payload *types* already admit them (unions, arrays) so no schemaVersion bump is needed — slice 1 restricts by *rule*, not by type. Ids are ulids as strings. `LocalDate` = `'YYYY-MM-DD'` in hotel-local calendar; `Instant` = ISO-8601 UTC; `Money` = integer VND. Stream ids are hotel-first: `<hotelId>/<type>:<id>`, availability = `<hotelId>/availability:all`.

```ts
// ---- commands (input the handler receives; hotelId + actor come from the session, not the body)

type CreateBooking = {
  commandId: string                       // idempotency
  kind: 'individual' | 'group'            // slice 1 rejects 'group' by rule, not by type
  contact: { name: string; phone?: string }   // handler upserts a contacts row, stores contactId only
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

Envelope + naming per §6 conventions (D-12). **Two tiers (D-22)**: `booking.*` `stay.*` `ledger.*` (+ `folio.*` `receivable.*` `expense.*` as Ledger-derived) are state — folded on replay. `room.*` `guest.*` `setup.*` `user.*` are **notifications**: emitted on every CRUD write for history tabs and projections, never folded; the row is truth. Streams: `booking:*` `stay:*` `room:*` `folio:*` `receivable:*` `ledger:*` `guest:*` `expense:*` `setup:*` `user:*` + `availability:all` (serialisation only, D-8; its sole event `availability.changed {cause}` is never folded). **Stream ids are hotel-first per D-9: `<hotelId>/booking:<id>`, `<hotelId>/availability:all`.**

`booking.` created · requests_changed · party_changed · notes_changed · cancelled · closed · stay_merged_in (reserved)
`stay.` created · room_assigned · room_unassigned · room_changed · nights_changed · rate_set · guest_added · guest_removed · routing_set · checked_in · checked_out · cancelled · marked_no_show · overbooking_overridden
`room.` defined · updated · retired · marked_clean · marked_dirty · taken_out_of_order · returned_to_service · note_set
`availability.` changed {cause} — version bump only
`folio.` opened · charge_posted · charge_voided · charge_moved · payment_received · payment_refunded · deposit_forfeited · transferred_to_receivable · closed
`receivable.` opened · payment_received · settled · written_off
`ledger.` account_opened · entry_posted · entry_reversed · account_closed
`guest.` created · updated · erased (tombstone, D-20)
`expense.` recorded · voided
`setup.` `<item>.defined / updated / retired` · hotel_profile_set · booking_rules_set
`user.` created · updated · disabled · role_set · password_reset(byUserId) — access events; visible in History to owner only

## Status

- 2026-09-19 — not started.
- 2026-09-23 — v0 draft from requirements + explore's ezFolio map. Aggregate list sent to architect.
- 2026-09-23 — v0.1: D-6 folded — setup/admin persona, Catalogue → Setup context (HotelProfile, Room/Type/Floor defs, RateTable, ChargeItem, ChargeBehaviour, Company, BookingRules). Awaiting Alex on §10.
- 2026-09-23 · **v1** — full session w/ Alex: multi-tenant (D-9), naming/envelope (D-12), Booking (D-13), Stay+nights (D-14/15), money + Ledger (D-16/17), roles/authz (D-18), screens (D-19), rules §10, command catalogue §11, event index §12.
