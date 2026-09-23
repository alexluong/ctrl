# SoLex — Product / Domain Model (WS3)

Owner: `solex-product`. **v0.1 draft, 2026-09-23** — built from `requirements.md` + `existing-system.md` (explore, through 2026-09-23) + D-4/D-5/D-6. Not yet reviewed with Alex; open policy points in §10. Event names here are the ES vocabulary; dev should not invent others.

## 1. Framing

- Rebuild of the *essence* of ezFolio for data ownership going forward (D-4, D-5). Core subset + the enhancements in `requirements.md`. Fresh start, no import.
- One property, 58 rooms (57 sellable), ~2/3 of business is group/company, high occupancy, Vietnam, VND cash-heavy.
- **Semi-professional** = one trusted receptionist persona does everything; owner reads; setup is rare and owner-done. No shifts, no night audit, no per-user permissions beyond the three roles, no approval workflows except discounts. Correctness of money and availability matters; POS, key cards, channel sync do not.
- **Multi-tenant by design, one tenant in practice (D-9).** Everything hangs off a `Hotel`; streams and projections keyed by hotel; no cross-hotel data in v1. Tenant creation/seeding via admin SDK/script, not UI. No self-signup, billing, or super-admin console in v1.

## 2. Users and roles

| role | what they do | access |
|---|---|---|
| **Receptionist** | bookings, assignment, check-in/out, charges, payments, room status, receivables follow-up, expenses entry | write everything |
| **Manager / owner** | "how is the hotel doing": dashboard, reports, approve discounts | read all + approvals |
| **Setup / admin** (D-6) | defines what the system is made of: rooms/types + prices, charge catalogues + prices, tax/service %, booking rules, hotel identity, channels/companies | Setup context only; rare (onboarding, price changes); the owner in practice |

Housekeeping, restaurant, etc. are off-system; reception acts on their behalf. Same operational screens for manager + receptionist, different defaults/density (explore). Setup is its own surface; whoever prices things can see and edit prices (ezFolio's rotted catalogue is the cautionary tale).

## 3. Jobs to be done

Receptionist: quote availability for a date range by room type → take a booking (individual: specific room; group: types × qty) → assign rooms → check in (register guests) → post charges during stay → move/extend stays → check out and settle (cash/transfer/card/to company debt) → keep room status current → chase receivables → record expenses.

Manager: today's state (vacant, arrivals, departures, revenue) · forward book (occupancy, revenue forecast) · revenue by bucket / channel / payment method · unpaid + receivables by debtor type · guest history · expenses / P&L-ish · approve discounts.

Setup/admin: onboard the hotel (identity, floors, rooms, types, bed types) · set and change prices (rate table, charge items) · curate catalogues (no duplicates, archive dead items) · set tax/service % per bucket · set booking rules (day boundary, overbooking, child age, default check-in/out times, ID enforcement) · register channels/companies with commission + terms.

## 4. Home screens (projections, not reports)

- **Room map** — now. Tiles by floor; color = derived status; tile → check-in, balance, post charge, set dirty/clean/OOO.
- **Tape chart** — over time. Room × date grid, stay bars; drag = move/extend (emits `RoomChanged` / `StayDatesChanged`); shows per-type availability inline for quoting.
Everything else hangs off these two.

## 5. Bounded contexts

| context | aggregates | notes |
|---|---|---|
| **Reservations** | Booking, Stay | commercial + stay lifecycle; availability check lives here |
| **Rooms** | Room | physical + housekeeping state (definitions come from Setup) |
| **Billing** | Folio, Receivable | charges, payments, routing, debt |
| **Guests** | Guest | profiles, merge, history, ID data for PA18 |
| **Setup** (D-6) | HotelProfile, RoomType/Floor/Room definitions, ChargeItem, RateTable, Company/Channel, BookingRules | what the system is made of; setup/admin persona; designed from explore's checklist, not ezFolio masters |
| **Expenses** | Expense | standalone cash-out ledger |

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

### Stay — one room for one span (settled w/ Alex 2026-09-23; ezFolio `reservation_room`, Opera "room stay")

Naming: **Booking / Stay** (not Reservation / Stay). Streams `booking:*`, `stay:*`.

```ts
type Stay = {
  id: StayId
  hotelId: HotelId
  bookingId: BookingId
  roomTypeId: RoomTypeId
  bedType: BedType
  roomId?: RoomId              // empty until assigned
  arrive: LocalDate
  depart: LocalDate            // exclusive; the plan — actual nights derive from timestamps (D-7)
  ratePerNight: Array<{ date: LocalDate; amount: Money }>   // per-night; one night can be discounted
  adults: number
  children: number             // < childAgeThreshold (Setup, default 6)
  guests: GuestId[]
  routing?: Partial<Record<Bucket, 'own' | 'master'>>       // group stays only; default from Booking's company
  status: 'booked' | 'checkedIn' | 'checkedOut' | 'cancelled' | 'noShow'
  checkedInAt?: Instant
  checkedOutAt?: Instant
}
```
Events: `stay.created` · `stay.room_assigned` · `stay.room_unassigned` · `stay.room_changed(from, to)` · `stay.dates_changed` · `stay.rate_set(date, amount)` · `stay.guest_added` · `stay.guest_removed` · `stay.routing_set(bucket, target)` · `stay.checked_in` · `stay.checked_out` · `stay.cancelled(reason)` · `stay.marked_no_show`.
Rules: check-in needs an assigned room that is not out of order · check-out needs own folio at 0 or moved to a receivable · dates change only before check-out · `rate_set` cannot target an already-posted night · no-show only from `booked`, after arrival date · cancel only if not checked in, reason required, charges moved off first (ezFolio guards).

Assumptions (Alex 2026-09-23: business calls, not system-breaking; adjust later):
- **Room move mid-stay**: same stay, `room_changed`, price unchanged by default; unposted nights editable after. Different room type → UI warns, no auto-reprice.
- **Extend**: same stay, `dates_changed`; new nights pre-filled from the rate table, editable before they post.

Dropped from v0: ezFolio flags `foc` (= rate 0), `isNet` (OTA, deferred), `locked` (no clear use).

### Availability (cross-aggregate rule, Reservations context)
- **Per-room**: a room may not have two stays with overlapping `[arrive, depart)` unless one is cancelled/no-show. Checked on `RoomAssigned` / `RoomChanged` / `StayDatesChanged`.
- **Per-type**: for each night, `stays of type (assigned or not, not cancelled) ≤ rooms of type in service` — unless overbooking policy allows an explicit receptionist override (`OverbookingOverridden` on the stay). Checked on `StayCreated` / `StayDatesChanged`.
- Same-day turnover (depart = arrive of next) is allowed by construction.
- **For dev/architect**: this is the one place ES needs a consistency boundary bigger than one aggregate. Options: (a) an `Inventory` aggregate per room (stream per room, assignment = event there); (b) single-writer per hotel (one DO) serialises all reservation commands — at 58 rooms and human write rates, (b) is fine and simplest. Recommend (b).

### Room — physical
Fields: number, floor, roomType, bedType; hk state `clean | dirty | inspected`; `ooo {reason}?`; note. Occupied/vacant + expected arrival/departure are *derived* from stays, never stored.
Events: `RoomDefined` · `RoomMarkedDirty` · `RoomMarkedClean` · `RoomMarkedInspected` · `RoomTakenOutOfOrder(reason)` · `RoomReturnedToService` · `RoomNoteSet`.
Auto: `StayCheckedOut` → `RoomMarkedDirty` (policy/projection reaction).
Derived status vocabulary for the map: VC · VD · VCI · OC · OD · OOO, + expected-arrival / expected-departure overlays.

### Folio — charges and payments
One folio per Stay (own) + one **master folio per group Booking**. A charge is posted *against a stay*; the stay's routing for that bucket decides which folio it lands on.
Charge shape (one, for all types): `{stayId, date, bucket, itemId?, description, qty, unitPrice, discount?, tax?, serviceFee?, note, actor}`.
Buckets (one enum, also = revenue report columns, folio tabs, routing switches): `room · roomSurcharge · minibar · laundry · compensation · extraService · telephone · restaurant`. Room charges are posted per night from the stay's rate (by the day-boundary reaction, §10). Early check-in / late check-out / breakfast / transfer / extra bed = `extraService` catalogue items (no multipliers).
Payment: `{date, method cash | bankTransfer | card | complimentary, amount, kind deposit | settlement | refund, ref?, actor}`. **Card = method only; no card data ever.**
Events: `ChargePosted` · `ChargeVoided(reason)` · `DiscountRequested(scope, pct|amount, reason)` · `DiscountApproved` · `DiscountRejected` · `PaymentReceived` · `PaymentRefunded` · `FolioTransferredToReceivable(debtorId, amount, dueDate)` · `FolioClosed`.
Invariants: balance = Σcharges − Σdiscounts − Σpayments(deposit+settlement) + Σrefunds; void, don't edit; close only at 0 balance or after transfer; master folio closes after all stays out; deposit before arrival is a payment of kind `deposit` on the (master or own) folio.

### Receivable — debt that outlives the stay
Fields: debtor (Company: OTA / TA / CORP / group contact), source folio, amount, dueDate, status `open | partial | settled | writtenOff`.
Events: `ReceivableOpened` · `ReceivablePaymentReceived(method, amount)` · `ReceivableWrittenOff(reason)` · `ReceivableSettled`.
Invariants: payments ≤ amount; overdue = open ∧ today > dueDate (derived).
OTA commission: computed as projection `commissionRate × room revenue` per booking/channel; whether the OTA remits net (receivable = net) or hotel pays out is policy (§10) — affects only how the Receivable amount is derived, not the model.

### Guest — reusable profile
Fields: name, gender, DOB, nationality, ID `{type CCCD | passport | licence | other, number, issueDate}`, visa?, phone, email, address, class `normal | vip1 | vip2 | returning`, note. History (stays, nights, spend) is a projection.
Events: `GuestProfileCreated` · `GuestProfileUpdated` · `GuestProfilesMerged(into, from)`.
Invariants: merge is one-way; ID number uniqueness is soft (warn, don't block) unless §10 says enforce.

### Setup context (D-6) — what the system is made of
Persona: setup/admin. Small, low-frequency event streams; every operational aggregate reads its definitions from here. Designed from explore's checklist of what actually carries values in ezFolio, not from its masters.
- `HotelProfile`: name, address, currency VND, USD display rate, default check-in/out times (14:00 / 12:00), print/signature names. Events `HotelProfileSet`.
- `Floor`, `RoomType` (code, name, bedTypes DBL|TWN, default pax), `Room` (number, floor, type, bedType) — `RoomDefined` lives here; hk state stays on Room in the Rooms context. Events `FloorDefined` · `RoomTypeDefined/Updated/Retired` · `RoomDefined/Updated/Retired` (retire, don't delete — history references it).
- `RateTable` (enhancement, replaces per-booking typed rates): `{roomType, bedType, dateRange | dayOfWeek, ratePerNight}` with a base rate per type as fallback. Resolves default `ratePerNight` on `StayCreated`; per-night override stays allowed. Events `RateDefined/Retired`.
- `ChargeItem`: bucket (the 8-bucket enum), name (VN + EN), unitPrice, active. Seeded list: breakfast adult/child, early check-in, late check-out, extra bed, airport transfer, laundry per garment, minibar items, damage (free-price), other. Events `ChargeItemDefined/Updated/Archived`. One list, curated — no free-text item names on posting.
- `ChargeBehaviour` per bucket: taxPct, serviceFeePct, netOrGross. All 0 / gross today; capability kept for VAT + 5% service. Events `ChargeBehaviourSet(bucket, …)`.
- `Company` (= channel/agent/corporate/debtor): name, kind `OTA | TA | CORP`, contact, defaultCommission (% or amount), commissionBasis (§10.5), paymentTerms (days), defaultGroupRouting (§10.8). Events `CompanyRegistered/Updated/Archived`.
- `BookingRules` (the §10 policy points once decided): dayBoundaryTime, overbookingMode `block | override`, childAgeThreshold (6), idEnforcement `optional | warn | require`, autoMarkDirtyOnCheckout, cancellationCharging. Events `BookingRulesSet`.
Invariants: room numbers unique; a room's type/bedType change doesn't rewrite past stays; archived items can't be posted but still render in history; rate ranges for one type/bedType may not overlap.

### Expense — cash-out ledger (not in ezFolio; client wants it)
Fields: date, category `groceries | incidental | hkOvertime | advance | other`, amount, method, payee?, note, actor. Events `ExpenseRecorded` · `ExpenseVoided`. Feeds P&L-ish dashboard only.

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
