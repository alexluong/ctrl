import json, random, time
random.seed(7)
els = []
NOW = int(time.time()*1000)

def base(t, x, y, w, h, **k):
    d = dict(id=f"{t}{len(els)}_{random.randint(1000,99999)}", type=t, x=x, y=y, width=w, height=h, angle=0,
             strokeColor="#1e1e1e", backgroundColor="transparent", fillStyle="solid", strokeWidth=1,
             strokeStyle="solid", roughness=0, opacity=100, groupIds=[], frameId=None, roundness=None,
             seed=random.randint(1, 2**31), version=1, versionNonce=random.randint(1, 2**31), isDeleted=False,
             boundElements=None, updated=NOW, link=None, locked=False)
    d.update(k); els.append(d); return d

def rect(x, y, w, h, bg="transparent", stroke="#1e1e1e", dash=False, sw=1):
    return base("rectangle", x, y, w, h, backgroundColor=bg, strokeColor=stroke,
                roundness={"type": 3}, strokeStyle="dashed" if dash else "solid", strokeWidth=sw)

def text(x, y, s, size=14, color="#1e1e1e", w=None, align="left", bold=False):
    lines = s.split("\n")
    lh = 1.25
    h = len(lines) * size * lh
    if w is None:
        w = max(len(l) for l in lines) * size * 0.6
    return base("text", x, y, w, h, text=s, fontSize=size, fontFamily=3 if not bold else 1, textAlign=align,
                verticalAlign="top", containerId=None, originalText=s, lineHeight=lh, strokeColor=color, autoResize=True)

def arrow(x1, y1, x2, y2, color="#1e1e1e", label=None, dash=False):
    a = base("arrow", x1, y1, abs(x2-x1) or 1, abs(y2-y1) or 1, points=[[0, 0], [x2-x1, y2-y1]],
             startBinding=None, endBinding=None, startArrowhead=None, endArrowhead="arrow",
             strokeColor=color, strokeStyle="dashed" if dash else "solid", roundness={"type": 2}, lastCommittedPoint=None)
    if label:
        text((x1+x2)/2 - 30, (y1+y2)/2 - 18, label, size=11, color=color)
    return a

# ---------- palette per context
C = dict(setup="#6b4fbb", res="#0e7c86", rooms="#2f7d32", bill="#b3541e", ledger="#7a4a10", guest="#8a3b6b", exp="#4a5d8a")
BG = dict(setup="#efeafc", res="#e0f3f4", rooms="#e6f3e6", bill="#fcece0", ledger="#f6ecd9", guest="#f7e6f0", exp="#e6ebf7")

def context(x, y, w, h, key, title, sub):
    rect(x, y, w, h, bg=BG[key], stroke=C[key], sw=2)
    text(x+14, y+10, title, size=20, color=C[key], bold=True)
    text(x+14, y+38, sub, size=12, color="#555555")

def box(x, y, w, key, title, body, extra_h=0):
    lines = body.count("\n") + 1
    h = 36 + lines * 14 * 1.25 + 12 + extra_h
    rect(x, y, w, h, bg="#ffffff", stroke=C[key])
    text(x+10, y+8, title, size=15, color=C[key], bold=True)
    text(x+10, y+34, body, size=11, color="#1e1e1e")
    return h

# ---------- title
text(40, 20, "SoLex — domain model v1 (2026-09-23)", size=28, bold=True)
text(40, 58, "CQRS + event sourcing. Command → checks capability + rules → events appended → projections rebuilt (same batch) → screens read projections.\nSolid arrows = depends on / references. Dashed = event reaction. Source: product.md v1.", size=12, color="#555555")

# ---------- Setup (top band)
context(40, 120, 1560, 250, "setup", "Setup", "reference data · upstream of everything, depends on nothing · retire never delete · seeded by admin SDK (D-9)")
sx = 60; sy = 170
items = [
 ("HotelProfile", "name, address, timeZone\ncheckInTime 14:00, checkOutTime 12:00\nbusinessDayStart 02:00 (D-7)"),
 ("Floor · RoomType · Room def", "type: name, capacity\nroom: number, floor, type, bedType\nretire versions availability"),
 ("RateTable", "roomTypeId, bedType\ndateRange | dayOfWeek\nratePerNight · no overlaps"),
 ("ChargeCategory · ChargeItem", "seeded: room* roomSurcharge minibar\nlaundry compensation extraService restaurant\nitem: category, VN+EN name, unitPrice"),
 ("BookingSource · ExpenseCategory", "walk-in, phone, Agoda… (lookup only)\ngroceries, incidental, hkOvertime, advance"),
 ("Company", "name, contact, kind\ndefault group routing {category → own|master}\ncommission / terms → later"),
 ("BookingRules", "childAgeThreshold 6\noverbooking warn+override\nautoDirtyOnCheckout · idEnforcement"),
 ("User · Role", "user: username, email?, roleId, status\nrole: capabilities[] — checked per command\nidentity (password) NOT in the log (D-11)"),
]
w = 185
for i, (t, b) in enumerate(items):
    box(sx + i*(w+8), sy, w, "setup", t, b)

# ---------- Reservations
context(40, 420, 760, 430, "res", "Reservations", "Booking = the envelope · Stay = one guest visit, night by night · availability rule lives here")
box(60, 480, 340, "res", "Booking", "id, hotelId, kind: individual | group\nparty { companyId?, contactId }   ← PII by id (D-20)\nsourceId?  (Setup BookingSource)\narrive, depart (exclusive)\nrequests[]: { roomTypeId, bedType, qty,\n              adults, children, ratePerNight }\nnotes?, status: open | cancelled | closed\n\nevents: booking.created · requests_changed ·\nparty_changed · notes_changed · cancelled · closed")
box(430, 480, 350, "res", "Stay", "id, hotelId, bookingId, roomTypeId, bedType\nnights: Night[]   ← THE UNIT (D-15)\n  Night { date, roomId?, rate, posted }\n  arrive/depart derived · move never splits\nadults, children, guests: GuestId[]\nrouting? {category → own | master}  (group)\nstatus: booked | checkedIn | checkedOut |\n        cancelled | noShow\ncheckedInAt?, checkedOutAt?\n\nevents: stay.created · room_assigned · room_changed ·\nnights_changed · rate_set · guest_added/removed ·\nrouting_set · checked_in · checked_out · cancelled ·\nmarked_no_show · overbooking_overridden")
arrow(400, 520, 430, 520, color=C["res"], label="1 → N")
rect(60, 730, 720, 100, bg="#ffffff", stroke=C["res"], dash=True)
text(72, 738, "Availability rule (one availability:<hotel> stream, D-8)", size=13, color=C["res"], bold=True)
text(72, 760, "• per room: no two stays share (roomId, date)   • per type per night: booked ≤ rooms in service, warn + override\n• every command touching supply or demand versions the stream: assign / move / nights / check-in / OOO / room retire / override", size=11)

# ---------- Rooms
context(830, 420, 360, 200, "rooms", "Rooms", "physical + housekeeping state")
box(850, 480, 320, "rooms", "Room", "id, hotelId, number, floor, roomTypeId, bedType\nhousekeeping: clean | dirty   (inspected → later)\noutOfOrder? { reason, since }, note?\noccupied / arriving / departing = DERIVED\n\nevents: room.marked_clean/dirty ·\ntaken_out_of_order · returned_to_service · note_set")

# ---------- Guests
context(1220, 420, 380, 200, "guest", "Guests", "thin profile · PII in mutable table, never in events")
box(1240, 480, 340, "guest", "Guest", "id, hotelId, name, phone?, email?, nationality?\nidDoc? { type: cccd | passport | other, number }\nnotes?\nerasure = overwrite row + guest.erased tombstone\n\nevents: guest.created · updated · erased")

# ---------- Billing
context(40, 900, 760, 400, "bill", "Billing", "hotel vocabulary over the Ledger · Folio + Receivable are PROJECTIONS + commands, not aggregates")
box(60, 960, 350, "bill", "Folio (projection)", "id, hotelId\nowner: stay (own) | booking (master)\nstatus: open | closed\nbalance = Σcharges − Σvoided − Σpayments + Σrefunds\n\nCharge { stayId, businessDate, categoryId,\n  itemId?, description, qty, unitPrice, voided? }\nPayment { businessDate, method: cash | bankTransfer\n  | card (word only), kind: deposit | settlement\n  | refund, amount, ref? }\n\nevents: folio.opened · charge_posted · charge_voided ·\ncharge_moved · payment_received · payment_refunded ·\ndeposit_forfeited · transferred_to_receivable · closed")
box(440, 960, 340, "bill", "Receivable (projection)", "id, hotelId, debtorCompanyId, folioId\namount, status: open | partial | settled |\n        writtenOff\nno due date in v1 · overdue = age\n\nevents: receivable.opened · payment_received ·\nsettled · written_off")
arrow(410, 1000, 440, 1000, color=C["bill"], label="transfer\nremainder")

# ---------- Ledger
context(830, 900, 470, 400, "ledger", "Ledger", "generic double-entry · knows nothing about hotels · one balance rule, one money log (D-17)")
box(850, 960, 430, "ledger", "Account · Entry", "Account { id, hotelId, kind: folio | receivable | cash |\n  bank | revenue | expense, ref?, status }\nEntry { id, hotelId, businessDate, kind: charge |\n  payment | refund | transfer | expense | reversal,\n  lines[]: { accountId, amount }  Σ = 0,\n  ref?, memo? }\nentries immutable · undo = reversal · close at 0\n\ncharge     debit folio / credit revenue:category\npayment    debit cash|bank / credit folio\ntransfer   debit receivable:company / credit folio\nexpense    debit expense:category / credit cash|bank\n\nevents: ledger.account_opened · entry_posted ·\nentry_reversed · account_closed")

# ---------- Expenses
context(1330, 900, 270, 200, "exp", "Expenses", "owner's cash-out")
box(1350, 960, 230, "exp", "ExpenseCommand", "businessDate, categoryId\namount, method: cash | bankTransfer\npayee?, note?\n\nevents: expense.recorded · voided")

# ---------- dependency arrows
arrow(420, 370, 420, 420, color=C["setup"])          # setup -> reservations
arrow(1010, 370, 1010, 420, color=C["setup"])        # setup -> rooms
arrow(1410, 370, 1410, 420, color=C["setup"])        # setup -> guests
arrow(800, 640, 800, 900, color=C["setup"], dash=False)  # placeholder (setup -> billing via left edge)
arrow(600, 850, 600, 900, color=C["res"], label="charges posted\nagainst a stay")
arrow(800, 1100, 830, 1100, color=C["bill"], label="posts entries")
arrow(1330, 1050, 1300, 1050, color=C["exp"], label="posts entries")
arrow(1010, 620, 1010, 900, color=C["rooms"], dash=True, label="stay.checked_out →\nroom.marked_dirty (reaction, via Rooms)")
arrow(1240, 620, 700, 700, color=C["guest"], dash=True, label="guestId refs only")

# ---------- flow strip + apps + projections
y0 = 1360
text(40, y0, "Write side → read side", size=20, bold=True)
steps = ["Command\n(~40, §11)\ne.g. CheckIn {stayId}", "Capability check\nrole = capability bundle\n(D-18)", "Rules / invariants\naggregate decides", "Events appended\nenvelope: id, hotelId, stream,\nversion, businessDate, actor… (D-12)", "Projections rebuilt\nsame batch (D-8)", "Screens read\nprojections"]
x = 40
for i, s in enumerate(steps):
    rect(x, y0+40, 230, 80, bg="#ffffff")
    text(x+10, y0+48, s, size=11)
    if i < len(steps)-1:
        arrow(x+230, y0+80, x+260, y0+80)
    x += 260

y1 = y0 + 160
text(40, y1, "Apps & roles", size=20, bold=True)
rect(40, y1+40, 500, 150, bg="#ffffff")
text(52, y1+48, "Front Desk  — receptionist · owner\n  room map · tape chart · new booking · booking page · stay page · folio (print) · arrivals/departures · search\nBack Office — owner · receptionist (receivables, expenses)\n  dashboard · receivables · expenses · reports (owner)\nSetup       — owner\n  CRUD per Setup item · users + roles\n\nroles v1: receptionist, owner · capability-based per command · void/refund/write-off/transfer/setup/users = owner", size=11)

text(580, y1, "Projections (read models)", size=20, bold=True)
rect(580, y1+40, 1020, 150, bg="#ffffff")
text(592, y1+48, "RoomMap (per room now) · StayNights (roomId, date → stay, rate, posted) · Availability (type × night) · ArrivalsDepartures · BookingList (search)\nFolioView (lines, balance, print) · Receivables (by company, age) · DashboardToday · ForwardBook · Revenue (date × category × source × method)\nExpenses · GuestHistory · History (events w/ actor per room / stay / folio = audit)\n\nlater: WaitingList · Breakfast list · PA18 export · CommissionByChannel · Deposits · per-staff activity", size=11)

y2 = y1 + 230
text(40, y2, "Later / never", size=20, bold=True)
rect(40, y2+40, 1560, 90, bg="#fff8e6", stroke="#9a6700")
text(52, y2+48, "LATER: OTA support (commission, gross/net, sync) · discount approvals · VAT / red invoice · receivable due dates · group label + color · registration card print · PA18 · breakfast / pickup lists · thank-you email · merge stay into group · inspected hk state · custom roles · per-staff activity · multi-currency\nNEVER: card data · restaurant POS · hk scheduling · key cards · hourly / day-use", size=11, color="#5a4000")

doc = {"type": "excalidraw", "version": 2, "source": "solex-product", "elements": els,
       "appState": {"gridSize": None, "viewBackgroundColor": "#ffffff"}, "files": {}}
out = "/Users/alexluong/git/hub/alexluong/ctrl/docs/projects/hotel-backoffice/diagrams/solex-domain.excalidraw"
import os; os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(doc, open(out, "w"), indent=1)
print(out, len(els))
