"""Generates diagrams/solex-domain.excalidraw from the model in product.md v1.
Run: python3 gen-solex-domain.py   (from this directory). Edit the DATA section, re-run, commit both files.
"""
import json, random, time, textwrap, os
random.seed(7)
els = []
NOW = int(time.time() * 1000)
CW = 0.62          # monospace char width factor (fontFamily 3)
LH = 1.25

def base(t, x, y, w, h, **k):
    d = dict(id=f"{t}{len(els)}_{random.randint(1000, 99999)}", type=t, x=x, y=y, width=w, height=h, angle=0,
             strokeColor="#1e1e1e", backgroundColor="transparent", fillStyle="solid", strokeWidth=1,
             strokeStyle="solid", roughness=0, opacity=100, groupIds=[], frameId=None, roundness=None,
             seed=random.randint(1, 2**31), version=1, versionNonce=random.randint(1, 2**31), isDeleted=False,
             boundElements=None, updated=NOW, link=None, locked=False)
    d.update(k); els.append(d); return d

def rect(x, y, w, h, bg="transparent", stroke="#1e1e1e", dash=False, sw=1):
    return base("rectangle", x, y, w, h, backgroundColor=bg, strokeColor=stroke, roundness={"type": 3},
                strokeStyle="dashed" if dash else "solid", strokeWidth=sw)

def tsize(s, size):
    lines = s.split("\n")
    return max(len(l) for l in lines) * size * CW, len(lines) * size * LH

def text(x, y, s, size=12, color="#1e1e1e", bold=False):
    w, h = tsize(s, size)
    return base("text", x, y, w, h, text=s, fontSize=size, fontFamily=1 if bold else 3, textAlign="left",
                verticalAlign="top", containerId=None, originalText=s, lineHeight=LH, strokeColor=color, autoResize=True)

def arrow(x1, y1, x2, y2, color="#1e1e1e", dash=False):
    return base("arrow", x1, y1, abs(x2 - x1) or 1, abs(y2 - y1) or 1, points=[[0, 0], [x2 - x1, y2 - y1]],
                startBinding=None, endBinding=None, startArrowhead=None, endArrowhead="arrow",
                strokeColor=color, strokeStyle="dashed" if dash else "solid", roundness={"type": 2}, lastCommittedPoint=None)

# card kinds: badge label, badge fill, box style — so a card reads as command / event / type / projection at a glance
KIND = {
    "type":       dict(label="TYPE",       fill="#495057", bg="#ffffff", dash=False, sw=1),
    "command":    dict(label="COMMAND",    fill="#1971c2", bg="#ffffff", dash=False, sw=2),
    "event":      dict(label="EVENT",      fill="#e8590c", bg="#fff9f4", dash=True,  sw=1),
    "projection": dict(label="PROJECTION", fill="#2f9e44", bg="#f6fdf7", dash=False, sw=1),
    "note":       dict(label="",           fill="#ffffff", bg="#ffffff", dash=False, sw=1),
}

def card(x, y, key, title, body, size=11, minw=0, pad=12, title_size=14, kind="type"):
    """Box sized to its text, with a kind badge before the title. Returns (w, h)."""
    k = KIND[kind]
    bsize = max(8, title_size - 4)
    lw, lh = tsize(k["label"], bsize)
    badge_w, badge_h = (lw + 10, lh + 4) if k["label"] else (-8, 0)
    tw, th = tsize(title, title_size)
    th = max(th, badge_h)
    bw, bh = tsize(body, size) if body else (0, 0)
    w = max(badge_w + 8 + tw, bw, minw) + 2 * pad
    h = pad + th + (8 + bh if body else 0) + pad
    rect(x, y, w, h, bg=k["bg"], stroke=C[key], dash=k["dash"], sw=k["sw"])
    if k["label"]:
        rect(x + pad, y + pad, badge_w, badge_h, bg=k["fill"], stroke=k["fill"])
        text(x + pad + 5, y + pad + 2, k["label"], size=bsize, color="#ffffff", bold=True)
    text(x + pad + badge_w + 8, y + pad, title, size=title_size, color=C[key], bold=True)
    if body:
        text(x + pad, y + pad + th + 8, body, size=size)
    return w, h

def wrap(s, width):
    out = []
    for para in s.split("\n"):
        out.extend(textwrap.wrap(para, width) or [""])
    return "\n".join(out)

C = dict(setup="#6b4fbb", res="#0e7c86", rooms="#2f7d32", bill="#b3541e", ledger="#7a4a10", guest="#8a3b6b", exp="#4a5d8a", users="#555555", sys="#333333")
BG = dict(setup="#f1edfc", res="#e3f4f5", rooms="#e8f4e8", bill="#fdeee3", ledger="#f7eedc", guest="#f8e8f1", exp="#e8edf8", users="#eeeeee", sys="#f4f4f4")

# ======================= DATA =======================
TIER = dict(res="a", rooms="b", bill="a (Ledger)", ledger="a", guest="b", exp="a (Ledger)", setup="b", users="b")

TYPES = {
 "res": [
  ("Booking", "id, hotelId, kind: individual | group\nparty { companyId?, contactId }   PII by id (D-20)\nsourceId?  (Setup BookingSource, lookup only)\narrive, depart  (depart exclusive)\nrequests[]: { roomTypeId, bedType, qty, adults,\n              children, ratePerNight }\nnotes?\nstatus: open | cancelled | closed\n\nrules: arrive < depart · qty >= 1 · cancel cascades to\nstays not checked in · close only when all stays terminal\nand master folio 0 or transferred · individual = 1 stay,\nroom assigned at creation"),
  ("Stay  (1 booking -> N stays)", "id, hotelId, bookingId, roomTypeId, bedType\nnights: Night[]                 <- THE UNIT (D-15)\n  Night { date, roomId?, rate, posted }\n  arrive / depart derived · a room move rewrites roomId\n  on unposted nights, never splits the Stay\nadults, children (< 6 free), guests: GuestId[]\nrouting? { categoryId -> own | master }   (group only)\nstatus: booked | checkedIn | checkedOut | cancelled | noShow\ncheckedInAt?, checkedOutAt?\n\nrules: check-in needs tonight's room, not OOO · check-out\nneeds own folio 0 or transferred · posted nights immutable ·\nno-show only from booked after arrival · cancel only if\nnot checked in, reason required, charges moved off first"),
  ("Availability  (one availability:<hotel> stream, D-8)", "per room: no two stays share (roomId, date)\nper type per night: booked <= rooms in service,\n  warn + explicit override\nevery command touching supply or demand versions\nthe stream in the same batch"),
 ],
 "rooms": [
  ("Room", "id, hotelId, number, floor, roomTypeId, bedType\nhousekeeping: clean | dirty      (inspected -> later)\noutOfOrder? { reason, since }\nnote?\n\noccupied / vacant / arriving / departing are DERIVED\nfrom stays' nights, never stored\nrow is truth (tier b); OOO still versions availability"),
 ],
 "bill": [
  ("Folio  (projection over a ledger account)", "id, hotelId\nowner: { stay } (own)  |  { booking } (master)\nstatus: open | closed\nbalance = sum(charges) - voided - payments + refunds\n\nCharge { stayId, businessDate, categoryId, itemId?,\n  description, qty, unitPrice, voided? }\nPayment { businessDate, method: cash | bankTransfer\n  | card (word only, no card data), kind: deposit |\n  settlement | refund, amount, ref? }\n\none own folio per Stay + one master per group Booking;\ncharge posted against a stay, routed by category"),
  ("Receivable  (projection over a ledger account)", "id, hotelId, debtorCompanyId, folioId (grain = folio)\namount\nstatus: open | partial | settled | writtenOff\nno due date in v1 · overdue = age"),
 ],
 "ledger": [
  ("Account", "id, hotelId\nkind: folio | receivable | cash | bank | revenue | expense\nref? { stayId?, bookingId?, companyId?, categoryId? }\nstatus: open | closed\nbalance = sum(lines) · closes only at 0"),
  ("Entry", "id, hotelId, businessDate\nkind: charge | payment | refund | transfer | expense | reversal\nlines[]: { accountId, amount }    + debit, - credit, sum = 0\nref? { stayId?, chargeId?, entryId? }, memo?\nimmutable · undo = reversal entry\n\ncharge    debit folio            / credit revenue:category\npayment   debit cash|bank        / credit folio\nrefund    debit folio            / credit cash|bank\ntransfer  debit receivable:co    / credit folio\nreceivable paid  debit cash|bank / credit receivable:co\nexpense   debit expense:category / credit cash|bank\nvoid      reversal"),
 ],
 "guest": [
  ("Guest  (mutable row, PII lives here)", "id, hotelId, name, phone?, email?, nationality?\nidDoc? { type: cccd | passport | other, number }\nnotes?\n\nevents carry guestId only (D-20)\nerasure = overwrite row + guest.erased tombstone"),
  ("Contact", "id, hotelId, name, phone?\nreferenced by Booking.party.contactId"),
 ],
 "exp": [
  ("ExpenseCommand  (the expense IS a ledger entry)", "businessDate, categoryId (Setup ExpenseCategory)\namount, method: cash | bankTransfer\npayee?, note?"),
 ],
 "setup": [
  ("HotelProfile", "name, address, timeZone (Asia/Ho_Chi_Minh)\ncheckInTime 14:00, checkOutTime 12:00\nbusinessDayStart 02:00   (D-7)"),
  ("Floor · RoomType · Room def", "type: name, capacity\nroom: number, floor, type, bedType\nunique numbers per hotel · retire not delete\nretire / type change versions availability"),
  ("RateTable", "roomTypeId, bedType\ndateRange | dayOfWeek\nratePerNight · no overlapping ranges"),
  ("ChargeCategory · ChargeItem", "categories seeded: room* roomSurcharge minibar\n  laundry compensation extraService restaurant\n  (* reserved: only the system posts room)\nitem: categoryId, VN + EN name, unitPrice, active"),
  ("BookingSource · ExpenseCategory", "sources: walk-in, phone, Agoda ...  (lookup only)\nexpense: groceries, incidental, hkOvertime,\n  advance, other"),
  ("Company", "name, contact, kind\ndefaultRouting { categoryId -> own | master }\ncommission / payment terms -> later"),
  ("BookingRules", "childAgeThreshold 6\noverbooking: warn (override allowed)\nautoDirtyOnCheckout true\nidEnforcement optional"),
 ],
 "users": [
  ("User", "id, hotelId, name, username, email?\nroleId, status: active | disabled\nidentity (password, sessions) in auth tables,\nNOT in the event log (D-11) · admin-created\nsign-in by username for all roles · owner resets"),
  ("Role  (a capability bundle)", "id, hotelId, name, capabilities[]\nv1 fixed: receptionist, owner · custom later\nevery command declares the capability it needs;\nserver checks it against the actor"),
 ],
}

# command: (name + input, needs, checks, emits)
COMMANDS = {
 "res": [
  ("CreateBooking {kind, party, sourceId?, arrive, depart, requests[], notes?}", "booking.create", "arrive < depart · qty >= 1 · availability per type (warn / override) · individual: room given + free", "booking.created · stay.created xN · folio.opened (master if group, own per stay)"),
  ("ChangeBookingParty / ChangeBookingNotes / ChangeBookingRequests", "booking.edit", "booking open · requests: availability", "booking.party_changed / notes_changed / requests_changed (+ stay.created / stay.cancelled)"),
  ("CancelBooking {bookingId, reason}", "booking.cancel", "no stay checked in", "booking.cancelled · stay.cancelled xN"),
  ("CloseBooking {bookingId}", "booking.edit", "all stays terminal · master folio 0 or transferred", "booking.closed · folio.closed"),
  ("AssignRoom {stayId, roomId, fromDate?}", "stay.assign", "type matches (warn) · room free those nights · not OOO · versions availability", "stay.room_assigned"),
  ("UnassignRoom {stayId}", "stay.assign", "status booked", "stay.room_unassigned"),
  ("MoveStay {stayId, fromDate, roomId}", "stay.move", "not checked out · unposted nights only · room free · versions availability", "stay.room_changed"),
  ("ChangeNights {stayId, add[], remove[]}", "stay.assign", "not checked out · removed nights unposted · availability", "stay.nights_changed"),
  ("SetNightRate {stayId, date, amount}", "booking.edit", "night unposted", "stay.rate_set"),
  ("AddGuest / RemoveGuest {stayId, guestId}", "booking.edit", "not checked out", "stay.guest_added / stay.guest_removed"),
  ("SetRouting {stayId, categoryId, own | master}", "booking.edit", "group stay", "stay.routing_set"),
  ("CheckIn {stayId, guests[]?}", "stay.check_in", "booked · tonight's room assigned, not OOO", "stay.checked_in · folio.charge_posted (tonight's room)"),
  ("CheckOut {stayId}", "stay.check_out", "checkedIn · own folio 0 or transferred", "stay.checked_out · folio.closed · room.marked_dirty (reaction)"),
  ("CancelStay {stayId, reason}", "stay.cancel", "booked · folio has no unmoved charges", "stay.cancelled"),
  ("MarkNoShow {stayId}", "stay.cancel", "booked · after arrival date", "stay.marked_no_show"),
  ("OverrideOverbooking {stayId}", "stay.assign  (owner by default)", "-", "stay.overbooking_overridden"),
 ],
 "rooms": [
  ("SetHousekeeping {roomId, clean | dirty}", "room.set_status", "-", "room.marked_clean / room.marked_dirty"),
  ("TakeOutOfOrder {roomId, reason}", "room.set_out_of_order", "no checked-in stay tonight · versions availability", "room.taken_out_of_order"),
  ("ReturnToService {roomId}", "room.set_out_of_order", "versions availability", "room.returned_to_service"),
  ("SetRoomNote {roomId, note}", "room.set_status", "-", "room.note_set"),
 ],
 "bill": [
  ("PostCharge {stayId, categoryId, itemId?, description?, qty, unitPrice}", "folio.post_charge", "target folio open (per routing) · category != room", "folio.charge_posted -> ledger.entry_posted"),
  ("VoidCharge {chargeId, reason}", "folio.void  (owner)", "folio open", "folio.charge_voided -> ledger.entry_reversed"),
  ("MoveCharge {chargeId, toFolioId}", "folio.move_line", "both folios open", "folio.charge_moved -> reversal + new entry"),
  ("TakePayment {folioId, method, amount, kind: deposit | settlement, ref?}", "folio.take_payment", "folio open · amount > 0", "folio.payment_received -> entry"),
  ("Refund {folioId, method, amount, reason}", "folio.refund  (owner)", "<= payments", "folio.payment_refunded -> entry"),
  ("ForfeitDeposit {folioId, amount, reason}", "folio.post_charge", "deposit exists", "folio.deposit_forfeited (= compensation charge)"),
  ("TransferToReceivable {folioId, companyId, amount?}", "folio.transfer_to_receivable  (owner)", "folio open · amount <= balance", "folio.transferred_to_receivable · receivable.opened -> entry"),
  ("CloseFolio {folioId}", "folio.take_payment", "balance 0", "folio.closed · ledger.account_closed"),
  ("RecordReceivablePayment {receivableId, method, amount, ref?}", "receivable.record_payment", "open / partial · <= remaining", "receivable.payment_received (+ receivable.settled) -> entry"),
  ("WriteOffReceivable {receivableId, reason}", "receivable.write_off  (owner)", "open / partial", "receivable.written_off -> entry"),
  ("PostNightlyRoomCharges   [system, at the 02:00 roll]", "system", "per checked-in stay, tonight unposted", "folio.charge_posted xN · night.posted = true"),
 ],
 "ledger": [
  ("(no user-facing commands)", "-", "Billing and Expenses post entries; Ledger enforces sum(lines) = 0, immutability, close at 0", "ledger.account_opened · entry_posted · entry_reversed · account_closed"),
 ],
 "guest": [
  ("CreateGuest / UpdateGuest {...}", "booking.edit", "-", "guest.created / guest.updated"),
  ("EraseGuest {guestId}", "owner", "no open stay", "guest.erased (tombstone; row overwritten)"),
 ],
 "exp": [
  ("RecordExpense {businessDate, categoryId, amount, method, payee?, note?}", "expense.record", "amount > 0", "expense.recorded -> ledger.entry_posted"),
  ("VoidExpense {expenseId, reason}", "expense.void", "-", "expense.voided -> ledger.entry_reversed"),
 ],
 "setup": [
  ("Define / Update / Retire <SetupItem>  (Floor, RoomType, Room, RateTable, ChargeCategory, ChargeItem, BookingSource, ExpenseCategory, Company)", "setup.edit", "unique room numbers · no overlapping rate ranges · can't retire a room with future nights · retired items not selectable", "<item>.defined / updated / retired · room retire or type change versions availability"),
  ("SetHotelProfile {...}", "setup.edit", "-", "setup.hotel_profile_set"),
  ("SetBookingRules {...}", "setup.edit", "-", "setup.booking_rules_set"),
 ],
 "users": [
  ("CreateUser / UpdateUser / DisableUser", "users.manage", "disabled users keep history, render as (former)", "user.created / updated / disabled"),
  ("SetUserRole {userId, roleId}", "users.manage", "-", "user.role_set"),
 ],
}

# event: (name, payload / note)
EVENTS = {
 "res": [
  ("booking.created", "booking snapshot (kind, party ids, sourceId?, arrive, depart, requests[], notes?)"),
  ("booking.requests_changed", "requests[]"),
  ("booking.party_changed", "party { companyId?, contactId }"),
  ("booking.notes_changed", "notes"),
  ("booking.cancelled", "reason"),
  ("booking.closed", "-"),
  ("booking.stay_merged_in", "stayId, fromBookingId   (reserved, later)"),
  ("stay.created", "stay snapshot (bookingId, roomTypeId, bedType, nights[], adults, children, routing?)"),
  ("stay.room_assigned", "roomId, fromDate?"),
  ("stay.room_unassigned", "-"),
  ("stay.room_changed", "fromDate, roomId"),
  ("stay.nights_changed", "added[] { date, rate }, removed[] dates"),
  ("stay.rate_set", "date, amount"),
  ("stay.guest_added", "guestId"),
  ("stay.guest_removed", "guestId"),
  ("stay.routing_set", "categoryId, target: own | master"),
  ("stay.checked_in", "at (Instant), roomId, guests[]"),
  ("stay.checked_out", "at (Instant)"),
  ("stay.cancelled", "reason"),
  ("stay.marked_no_show", "-"),
  ("stay.overbooking_overridden", "roomTypeId, dates[]"),
 ],
 "rooms": [
  ("room.marked_clean", "-"),
  ("room.marked_dirty", "cause: checkout | manual"),
  ("room.taken_out_of_order", "reason"),
  ("room.returned_to_service", "-"),
  ("room.note_set", "note"),
 ],
 "bill": [
  ("folio.opened", "owner: stay | booking"),
  ("folio.charge_posted", "chargeId, stayId, businessDate, categoryId, itemId?, description, qty, unitPrice, entryId"),
  ("folio.charge_voided", "chargeId, reason, reversalEntryId"),
  ("folio.charge_moved", "chargeId, fromFolioId, toFolioId, entryIds"),
  ("folio.payment_received", "paymentId, method, kind: deposit | settlement, amount, ref?, entryId"),
  ("folio.payment_refunded", "paymentId, method, amount, reason, entryId"),
  ("folio.deposit_forfeited", "amount, reason, chargeId"),
  ("folio.transferred_to_receivable", "companyId, amount, receivableId, entryId"),
  ("folio.closed", "-"),
  ("receivable.opened", "debtorCompanyId, folioId, amount"),
  ("receivable.payment_received", "method, amount, ref?, entryId"),
  ("receivable.settled", "-"),
  ("receivable.written_off", "reason, entryId"),
 ],
 "ledger": [
  ("ledger.account_opened", "accountId, kind, ref?"),
  ("ledger.entry_posted", "entryId, businessDate, kind, lines[] { accountId, amount }, ref?, memo?"),
  ("ledger.entry_reversed", "entryId, reversalEntryId, reason"),
  ("ledger.account_closed", "accountId"),
 ],
 "guest": [
  ("guest.created", "guestId   (no PII in payload)"),
  ("guest.updated", "guestId, changedFields[] (names of fields, not values)"),
  ("guest.erased", "guestId   (tombstone; row overwritten)"),
 ],
 "exp": [
  ("expense.recorded", "expenseId, businessDate, categoryId, amount, method, payee?, entryId"),
  ("expense.voided", "expenseId, reason, reversalEntryId"),
 ],
 "setup": [
  ("setup.<item>.defined", "item snapshot"),
  ("setup.<item>.updated", "item snapshot / changed fields"),
  ("setup.<item>.retired", "-"),
  ("setup.hotel_profile_set", "profile snapshot"),
  ("setup.booking_rules_set", "rules snapshot"),
 ],
 "users": [
  ("user.created", "userId, username, roleId"),
  ("user.updated", "userId, changedFields[]"),
  ("user.disabled", "userId"),
  ("user.role_set", "userId, roleId"),
  ("user.password_reset", "userId, byUserId   (access event; visible to owner)"),
 ],
}

ROWS = [
 ("res", "Reservations", "Booking = the envelope · Stay = one guest visit, night by night · availability rule lives here"),
 ("rooms", "Rooms", "physical + housekeeping state · row is truth, every write emits an event"),
 ("bill", "Billing", "hotel vocabulary over the Ledger · Folio and Receivable are projections + commands, not aggregates"),
 ("ledger", "Ledger", "generic double-entry · knows nothing about hotels · one balance rule, one money log (D-17)"),
 ("guest", "Guests", "thin profile · PII in mutable tables, never in event payloads (D-20)"),
 ("exp", "Expenses", "owner's cash-out · each expense is a ledger entry"),
 ("setup", "Setup", "what the hotel is made of · upstream of everything, depends on nothing · retire never delete · seeded by admin SDK (D-9)"),
 ("users", "Users & roles", "per-person accounts scoped to a hotel · capability-based authz per command (D-18)"),
]

# ======================= LAYOUT =======================
X0 = 40
COL_TYPES_W = 640
COL_CMD_W = 1180
CMD_CARD_W = 370
GAP = 24
ROW_W = COL_TYPES_W + COL_CMD_W + GAP * 3

y = 30
text(X0, y, "SoLex — domain model v1", size=32, bold=True); y += 48
text(X0, y, "CQRS + event sourcing, two tiers (D-22).  tier a = event-sourced: the log is truth, state is a fold (Booking, Stay, Ledger).  tier b = event-notified: a mutable row is truth, every write still\n"
            "appends an event with the same envelope to the same log for history + projections, nothing folds it (Room, Setup, Guest, User).  Source of truth: product.md v1 (2026-09-23).", size=12, color="#555555"); y += 52
# legend: one sample card per kind
text(X0, y, "Card kinds", size=12, color="#555555", bold=True); y += 20
lx = X0
for kd, ttl, bdy in [("type", "Aggregate / row", "fields, rules"), ("command", "DoSomething {input}", "capability · checks · emits"),
                     ("event", "aggregate.past_tense", "payload"), ("projection", "ReadModel", "what it answers -> screen")]:
    w, h = card(lx, y, "sys", ttl, bdy, size=10, title_size=12, kind=kd); lx += w + 16
y += h + 36

# ---- mini-map of contexts + flow strip, side by side
text(X0, y, "Contexts and dependencies (arrows = depends on / references; dashed = event reaction)", size=16, bold=True)
text(X0 + 1000, y, "Write side -> read side", size=16, bold=True)
y += 34
mm_y = y
mm = {}
def mbox(key, label, x, yy, w=150, h=44):
    rect(x, yy, w, h, bg=BG[key], stroke=C[key], sw=2)
    text(x + 10, yy + 12, label, size=13, color=C[key], bold=True)
    mm[key] = (x, yy, w, h)
mbox("setup", "Setup  [b]", X0, mm_y, 900, 44)
mbox("res", "Reservations [a]", X0, mm_y + 90)
mbox("rooms", "Rooms [b]", X0 + 190, mm_y + 90)
mbox("guest", "Guests [b]", X0 + 380, mm_y + 90)
mbox("users", "Users [b]", X0 + 570, mm_y + 90)
mbox("bill", "Billing [a]", X0, mm_y + 180)
mbox("exp", "Expenses [a]", X0 + 380, mm_y + 180)
mbox("ledger", "Ledger [a]", X0 + 190, mm_y + 270)
for k in ("res", "rooms", "guest", "users"):
    x, yy, w, h = mm[k]; arrow(x + w / 2, mm_y + 44, x + w / 2, yy, color=C["setup"])
arrow(X0 + 75, mm_y + 134, X0 + 75, mm_y + 180, color=C["res"]); text(X0 + 82, mm_y + 148, "charges against a stay", size=10, color=C["res"])
arrow(X0 + 150, mm_y + 202, X0 + 265, mm_y + 270, color=C["bill"]); text(X0 + 160, mm_y + 250, "entries", size=10, color=C["bill"])
arrow(X0 + 455, mm_y + 224, X0 + 340, mm_y + 292, color=C["exp"]); text(X0 + 350, mm_y + 236, "entries", size=10, color=C["exp"])
arrow(X0 + 265, mm_y + 134, X0 + 265, mm_y + 270, color=C["rooms"], dash=True); text(X0 + 272, mm_y + 200, "OOO versions availability", size=10, color=C["rooms"])
arrow(X0 + 190, mm_y + 112, X0 + 150, mm_y + 112, color=C["rooms"], dash=True); text(X0 + 150, mm_y + 60 + 86, "", size=10)
arrow(X0 + 380, mm_y + 112, X0 + 150, mm_y + 116, color=C["guest"], dash=True); text(X0 + 200, mm_y + 70, "guestId / contactId refs only", size=10, color=C["guest"])
arrow(X0 + 640, mm_y + 134, X0 + 640, mm_y + 330, color=C["users"], dash=True); text(X0 + 648, mm_y + 300, "actor on every event", size=10, color=C["users"])

fx = X0 + 1000; fy = mm_y
steps = [("Command", "one intent, ~45 in the catalogue\ne.g. CheckIn {stayId}"), ("Capability check", "role = capability bundle\nserver-side, every command"), ("Rules / invariants", "the aggregate (tier a) or the\nrow guard (tier b) decides"), ("Events appended", "envelope: id, hotelId, stream, version,\ntype, schemaVersion, occurredAt,\nbusinessDate, actor (user:<id> | system:<job>),\ncorrelationId..."), ("Projections rebuilt", "same batch, synchronous (D-8)\nrebuild = re-fold the log"), ("Screens read projections", "Front Desk · Back Office · Setup")]
for i, (t, b) in enumerate(steps):
    w, h = card(fx, fy, "sys", t, b, size=11, minw=270, kind="note")
    if i < len(steps) - 1:
        arrow(fx + w / 2, fy + h, fx + w / 2, fy + h + 14)
    fy += h + 14
y = max(mm_y + 340, fy) + 40

# ---- one band per context: Types | Commands | Events
for key, title, sub in ROWS:
    band_y = y
    text(X0 + 16, band_y + 14, f"{title}   [tier {TIER[key]}]", size=22, color=C[key], bold=True)
    text(X0 + 16, band_y + 46, sub, size=12, color="#555555")
    inner_y = band_y + 80
    # types column
    tx = X0 + GAP; ty = inner_y
    text(tx, ty, "TYPES", size=11, color=C[key], bold=True); ty += 22
    for t, b in TYPES[key]:
        w, h = card(tx, ty, key, t, b, size=11, minw=COL_TYPES_W - 2 * 12, kind="type")
        ty += h + 12
    types_bottom = ty
    # commands column (cards in a grid, 3 per row)
    cx0 = X0 + GAP + COL_TYPES_W + GAP; cy = inner_y
    text(cx0, cy, "COMMANDS   (capability = who may call · checks = refused if false · emits = events appended in one batch)", size=11, color=C[key], bold=True); cy += 22
    per_row = 3
    col_h = [0] * per_row
    row_y = cy
    for i, (name, needs, checks, emits) in enumerate(COMMANDS[key]):
        col = i % per_row
        if col == 0 and i > 0:
            row_y += max(col_h) + 12; col_h = [0] * per_row
        cx = cx0 + col * (CMD_CARD_W + 12)
        body = "capability  " + wrap(needs, 40).replace("\n", "\n            ") + "\nchecks      " + wrap(checks, 40).replace("\n", "\n            ") + "\nemits       " + wrap(emits, 40).replace("\n", "\n            ")
        title_w = wrap(name, 44)
        w, h = card(cx, row_y, key, title_w, body, size=10.5, minw=CMD_CARD_W - 24, title_size=12, kind="command")
        col_h[col] = max(col_h[col], h)
    cmd_bottom = row_y + max(col_h) + 16
    # events under commands, one card each
    ey = cmd_bottom
    text(cx0, ey, "EVENTS   (name · payload; envelope adds id, hotelId, stream, version, occurredAt, businessDate, actor, correlationId)", size=11, color=C[key], bold=True); ey += 22
    per_row_e = 4
    EV_W = (COL_CMD_W - 12 - (per_row_e - 1) * 12) // per_row_e
    col_h = [0] * per_row_e
    row_y = ey
    for i, (name, payload) in enumerate(EVENTS[key]):
        col = i % per_row_e
        if col == 0 and i > 0:
            row_y += max(col_h) + 10; col_h = [0] * per_row_e
        ex = cx0 + col * (EV_W + 12)
        w, h = card(ex, row_y, key, name, "payload  " + wrap(payload, 30).replace("\n", "\n         "), size=10, minw=EV_W - 24, title_size=11.5, pad=10, kind="event")
        col_h[col] = max(col_h[col], h)
    ey = row_y + max(col_h) + 10
    bottom = max(types_bottom, ey) + GAP
    band_h = bottom - band_y
    # band rect behind (insert at front so it sits under): move to front of list is complex -> draw band first by inserting
    band = rect(X0, band_y, ROW_W, band_h, bg=BG[key], stroke=C[key], sw=2)
    els.remove(band); els.insert(0, band)   # send to back
    y = bottom + 36

# ---- projections, apps, scope
text(X0, y, "Projections (read models — every screen reads one of these)", size=22, bold=True); y += 40
proj = [
 ("RoomMap", "per room now: hk state, OOO,\noccupied?, arriving?, departing?, balance", "Front Desk home"),
 ("StayNights", "(roomId, date) -> stayId, rate, posted", "tape chart, availability, occupancy"),
 ("Availability", "per type per night: sellable, booked, free", "quoting, overbooking check"),
 ("ArrivalsDepartures", "today's arriving / departing stays", "daily lists"),
 ("BookingList", "bookings + stays + party + status\nsearch by guest / phone / company", "search, booking page"),
 ("FolioView", "per folio: lines, balance", "folio screen, print"),
 ("Receivables", "per company: open amount, age, payments", "Back Office"),
 ("DashboardToday", "occupancy %, arrivals, departures, in-house,\nrevenue posted, cash in, unpaid", "Back Office home"),
 ("ForwardBook", "per future night: rooms sold x rate, by type", "forecast"),
 ("Revenue", "business date x category x source x method", "reports"),
 ("Expenses", "by category x period", "Back Office"),
 ("GuestHistory", "per guest: visits, nights, spend", "guest page"),
 ("History", "per room / stay / folio: events with actor + time", "'Show log' tabs = audit"),
]
px = X0; py = y; rowh = 0
for i, (n, b, s) in enumerate(proj):
    w, h = card(px, py, "sys", n, b + "\n-> " + s, size=11, minw=330, kind="projection")
    rowh = max(rowh, h); px += 356
    if (i + 1) % 5 == 0:
        px = X0; py += rowh + 12; rowh = 0
y = py + rowh + 40

text(X0, y, "Apps & roles", size=22, bold=True); text(X0 + 1000, y, "Scope", size=22, bold=True); y += 40
apps = ("Front Desk   receptionist · owner\n  room map · tape chart · new booking · booking page · stay page\n  folio (print) · arrivals / departures · search\n\nBack Office  owner · receptionist (receivables, expenses - assumed)\n  dashboard · receivables · expenses · reports (owner)\n\nSetup        owner\n  CRUD per Setup item · users + roles\n\nroles v1: receptionist, owner (fixed capability bundles; custom later)\nowner-only by default: void · refund · write-off · transfer · reports · setup · users")
card(X0, y, "sys", "Three apps, two roles", apps, size=11, minw=900, kind="note")
scope = ("v1     Setup · individual + group booking w/ inline availability · assign now or later · tape chart + room map\n       check-in/out · guests per stay · one charge flow · folio own/master + routing · cash / transfer / card-method\n       payments, deposits, refunds · receivables by company · hk state + OOO · dashboard + reports · expenses\n       history tabs · folio print · search\n\nlater  OTA support (commission, gross/net, sync) · discount approvals · VAT / red invoice · receivable due dates\n       group label + color · registration card print · PA18 export · breakfast / pickup lists · thank-you email\n       merge stay into group · inspected hk state · custom roles · per-staff activity · multi-currency\n\nnever  card data · restaurant POS · hk scheduling · key cards · hourly / day-use")
card(X0 + 1000, y, "sys", "v1 / later / never", scope, size=11, minw=820, kind="note")

doc = {"type": "excalidraw", "version": 2, "source": "solex-product", "elements": els,
       "appState": {"gridSize": None, "viewBackgroundColor": "#ffffff"}, "files": {}}
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "solex-domain.excalidraw")
json.dump(doc, open(out, "w"), indent=1)
print(out, len(els))
