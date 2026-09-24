#!/usr/bin/env python3
"""SoLex, ezFolio-shaped — demo mockups (no build). Run from this dir: python3 gen.py
Alex 2026-09-24: keep ezFolio's nav, screen shapes, placement and daily flow; style, logic and feature set are SoLex's.
English labels (D-29); ezFolio's Vietnamese term bracketed only where it aids recognition.
Labels follow solex main (5.6) where built; otherwise product.md / ux.md. Sample data invented; no guest PII.
Reference: ../../screens/fd-*.png (gitignored) + ../../existing-system.md. Style: solex.css (hand-kept).
"""
from pathlib import Path
OUT = Path(__file__).parent

# ---------------------------------------------------------------- shell
TABS = [("Front desk", "shell.html"), ("Housekeeping", "room-map.html#hk"), ("Back office", "index.html#later"), ("Setup", "index.html#later")]
RIBBON = [  # (label, href, group) — Front desk ribbon entries, ezFolio order
    ("Room map", "room-map.html", None), ("Tape chart", "tape-chart.html", None),
    ("Walk-in", "booking-editor.html#new", "New booking"), ("Group", "status-lists.html#new", None),
    ("Due to arrive", "status-lists.html", "Lists"), ("In house", "status-lists.html", None), ("Due to leave", "status-lists.html", None),
    ("All bookings", "status-lists.html", None), ("People", "index.html#later", None),
]

def shell(active_tab="Front desk", active_rib=None, owner=False):
    tabs = ''.join(f'<a href="{h}" class="{"on" if n == active_tab else ""}">{n}</a>' for n, h in TABS)
    right = ('<span>Needs attention <span class="badge">3</span></span><span>Anh Tuấn · owner</span>' if owner
             else '<span>Linh · desk</span>') + '<span>Sign out</span>'
    rib, last = '', None
    for n, h, g in RIBBON:
        if g:
            rib += ('<span class="sep"></span>' if last else '') + f'<span class="grp">{g}</span>'
        rib += f'<a href="{h}" class="{"on" if n == active_rib else ""}">{n}</a>'
        last = n
    return (f'<div class="top"><span class="brand">SoLex</span>{tabs}<span class="right">{right}</span></div>'
            f'<div class="ribbon">{rib}</div>')

def page(title, sub, body, notes, cant, links):
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><link rel="stylesheet" href="solex.css">
<div class="wrap">
<div class="crumb"><a href="index.html">← Index</a></div>
<h1>{title}</h1><p class="sub">{sub}</p>
{body}
<div class="notes">{notes}</div>
<div class="cant"><b>Not carried over from ezFolio:</b>{cant}</div>
<div class="foot">{links}</div>
</div></html>"""

LEGEND = ('<div class="legend"><span class="n">n</span>note below · <span class="btn pri">Primary</span> the one action this state is for · '
          '<span class="btn">Button</span> fires a command · <span class="btn own">Owner</span> owner-only; the desk sees "Ask approval" (5.8) · '
          '<span class="in sel">select</span> <span class="in">input</span> · <span class="tag same">shape</span> ezFolio shape kept · <span class="tag ours">ours</span> SoLex addition</div>')

# ================================================================ 1. shell
SHELL_BODY = f"""
<div class="app">
  <div data-n="1">{shell()}</div>
  <div class="page" style="min-height:110px;color:var(--muted);font-size:13px">Screen content renders here. Tabs and the ribbon are the same on every screen; the ribbon changes with the tab.</div>
</div>
<div class="arrowline">▼ same shell, signed in as the owner</div>
<div class="app" data-n="2">{shell(owner=True)}</div>
{LEGEND}
"""
SHELL_NOTES = """
<div><h3><span class="n">1</span>Tabs + ribbon, ezFolio's structure</h3>
<p>Four tabs like ezFolio (Lễ tân · Buồng · Báo cáo · Hệ thống), a ribbon of entries under the tab in ezFolio's order: map · chart · new booking · lists. Every entry is a SoLex route; nothing on the ribbon is a feature we do not have.</p>
<table class="map"><tr><th>tab</th><th>ribbon entries → maps to</th><th></th></tr>
<tr><td>Front desk</td><td>Room map (<code>RoomBoard</code>) · Tape chart (<code>Calendar</code>) · Walk-in / Group (<code>CreateBooking</code>) · Due to arrive · In house · Due to leave · All bookings (one list, <code>StayList</code>, screen 4) · People (guests + companies)</td><td><span class="tag same">shape</span></td></tr>
<tr><td>Housekeeping</td><td>the same room map with <b>Vacant, dirty</b> + <b>Occupied, dirty</b> preselected; Mark clean / dirty → <code>SetHousekeeping</code>; Out of order → <code>TakeOutOfOrder</code> / <code>ReturnToService</code></td><td><span class="tag same">shape</span></td></tr>
<tr><td>Back office</td><td>Owed (receivables) · Spending (expenses) · Reports (owner)</td><td><span class="tag ours">ours</span></td></tr>
<tr><td>Setup</td><td>Setup (hotel, room types, rates, charge categories, companies, rooms, staff) · Accounts · System (operator)</td><td><span class="tag same">shape</span></td></tr>
</table></div>
<div><h3><span class="n">2</span>Owner sees one more thing</h3>
<p><b>Needs attention</b> with a count, top right: aged receivables, long out-of-order rooms, tomorrow's arrivals without a room, overstays with a balance, pending approvals (product.md §3 Home & inbox). The desk never sees it; the map is the desk's to-do list. Reports and Setup entries appear for the owner only.</p>
<table class="map"><tr><th>ezFolio entry</th><th>where it went</th></tr>
<tr><td>Sales › Companies (Kinh doanh)</td><td>Front desk › People, and Setup › Companies</td></tr>
<tr><td>Laundry / Minibar registers (Dịch vụ)</td><td>posting is from the room tile (screen 2); a per-category register is a report, later</td></tr>
<tr><td>Change room (Đổi phòng)</td><td>an action on the stay (screen 3), not a screen</td></tr>
<tr><td>Unassigned bookings (Đ.phòng chưa gán)</td><td>"Nights without a room" under the tape chart (screen 5)</td></tr>
<tr><td>Audit › Night audit (Kiểm toán)</td><td>none: the hotel day rolls itself at the hour set in Setup</td></tr>
</table></div>
"""
SHELL_CANT = " Restaurant POS, PA18 export, key cards, print icon in the tab bar (print lives on the bill and the lists, 5.5)."
SHELL_LINKS = '<a href="room-map.html">Next: 2 · Room map →</a>'

# ================================================================ 2. room map
ROOMS = [  # number, type code, state, guest surname shown on tile
 ("101","VIP","ooo",""),("103","SUPT","in","Trần"),("104","SUPD","in","Lê"),("105","DLX5","in","Phạm"),("106","DLX6","dep","Hoàng"),
 ("107","DLX5","in","Vũ"),("108","DLX5","dirty",""),("109","DLX5","in","Đặng"),("110","DLXT","in","Nguyễn"),
 ("201","VIP","in","Bùi"),("203","SUPT","in","Đỗ"),("204","SUPD","in dirty","Hồ"),("205","DLX5","in","Ngô"),("206","DLX6","in","Dương"),
 ("207","DLX5","in","Lý"),("208","DLX5","in","Mai"),("209","DLX5","dep","Trịnh"),("210","DLXT","in","Đinh"),
 ("301","SUPD","in","Lâm"),("302","STD2","ready",""),("303","SUPT","in","Phan"),("304","SUPT","in","Võ"),("305","DLX5","ready",""),
 ("306","DLX6","in","Tạ"),("307","DLX5","ready",""),("308","DLX5","dirty",""),("309","DLX5","in","Cao"),("310","DLXT","in","Hà"),
 ("401","SUPD","in","Kim"),("402","STD2","in","Lưu"),("403","SUPT","arr","Chu"),("404","SUPT","in","Tô"),("405","DLX5","in","Quách"),
 ("406","DLX6","in","Thái"),("407","DLX5","in","Ông"),("408","DLX5","arr","Diệp"),("409","DLX5","in","Hứa"),("410","DLXT","in","Từ"),
]
def count(pred): return sum(1 for r in ROOMS if pred(r[2].split()))
ST = [("all","All", lambda s: True), ("ready","Ready", lambda s: s==["ready"]), ("arr","Due to arrive", lambda s: "arr" in s),
      ("in","In house", lambda s: "in" in s or "dep" in s), ("dep","Due to leave", lambda s: "dep" in s),
      ("dirty","Occupied, dirty", lambda s: "dirty" in s and ("in" in s or "dep" in s)), ("dirty","Vacant, dirty", lambda s: s==["dirty"]),
      ("ooo","Out of order", lambda s: "ooo" in s)]

def stbar(on="All"):
    return '<div class="stbar" data-n="1">' + ''.join(
        f'<a class="st {"on" if n==on else ""}" href="#"><i class="i-{k}"></i>{n}<b>{count(p)}</b></a>' for k, n, p in ST) + '</div>'

def tiles():
    out, floor = '', None
    for num, code, st, guest in ROOMS:
        if num[0] != floor:
            if floor: out += '</div>'
            out += f'<div class="floor">Floor {num[0]}</div><div class="tiles">'; floor = num[0]
        sel = ' sel' if num == "110" else ''
        out += f'<a class="tile {st}{sel}" href="#panel"><small>{code}</small><b>{num}</b><em>{guest}</em></a>'
    return out + '</div>'

PANEL = """
<div class="dlg" id="panel">
  <div class="dh">Room 110 · Deluxe twin <span class="status">Checked in</span><span class="x">✕ Close</span></div>
  <div class="db">
    <div class="two">
      <div class="kv" data-n="3"><span>State</span><span>occupied · clean</span><span>Guest</span><span>Nguyễn Văn A · 0903 xxx xxx</span><span>Company</span><span>—</span>
        <span>Stay</span><span>24/09 → 26/09 · 2 nights</span><span>Tonight</span><span>800,000</span></div>
      <div><div class="dim" style="font-size:12px">Note</div><div class="in" style="width:100%;min-height:48px;margin:4px 0">arrives ~20:00</div><span class="btn">Save note</span></div>
    </div>
    <div class="row" style="justify-content:flex-end;font-size:16px"><span class="dim">Left to pay</span> <b>350,000</b> <a href="booking-editor.html" class="btn">Open the stay →</a></div>
  </div>
  <div class="df" data-n="4"><span class="dim" style="margin-right:auto">Add to bill:</span><span class="btn">Minibar</span><span class="btn">Laundry</span><span class="btn">Compensation</span><span class="btn">Extra service</span><span class="btn">Restaurant</span></div>
  <div class="df" data-n="5"><span class="btn">Mark dirty</span><span class="btn">Room history</span><span class="btn pri">Check out</span></div>
</div>
"""
MAP_BODY = f"""
<div class="app">{shell(active_rib="Room map")}
  <div class="page" id="hk">{stbar()}<div data-n="2">{tiles()}</div></div>
  <div class="arrowline">▼ click tile <b>110</b> → quick panel (opens over the map; drawn apart here)</div>
  <div class="fade">{PANEL}</div>
</div>{LEGEND}
"""
MAP_NOTES = """
<div><h3><span class="n">1</span>Status buttons with live counts <span class="tag same">shape</span></h3>
<p>ezFolio's eight buttons (TẤT CẢ · SẴN SÀNG · DỰ KIẾN ĐẾN · ĐANG Ở · DỰ KIẾN ĐI · CÓ KHÁCH BẨN · TRỐNG BẨN · PHÒNG SỬA), same order, click = filter. Counts and colours are <b>derived</b> from the room's housekeeping / out-of-order flags plus the stays' nights; nothing is stored (product.md §6 Room). In house counts every checked-in room, as ezFolio does. Built in 5.6.</p>
<table class="map"><tr><th>button</th><th>reads (<code>RoomBoard</code>)</th></tr>
<tr><td>Ready</td><td>vacant · clean · nobody due today</td></tr><tr><td>Due to arrive</td><td>a <i>booked</i> stay holds tonight, room assigned</td></tr>
<tr><td>In house / Due to leave</td><td>checked in tonight / checked in and last night was yesterday</td></tr>
<tr><td>Occupied, dirty / Vacant, dirty</td><td>housekeeping = dirty with / without a guest</td></tr><tr><td>Out of order</td><td><code>room.outOfOrder</code></td></tr></table>
<h3 style="margin-top:12px"><span class="n">2</span>Tiles by floor <span class="tag same">shape</span></h3>
<p>Type code · number · guest surname (ours: ezFolio shows the type only). Colour = state; a split tile = in house and dirty. No date picker: the map is <i>now</i>; over time is the tape chart.</p></div>
<div><h3><span class="n">3</span>Quick panel = ezFolio's "Chi tiết" <span class="tag same">shape</span></h3>
<p>Same facts in the same places: room · rate · dates · nights · status on the left, guest · company · note on the right, <b>Left to pay (Còn lại)</b> prominent, quick-charge buttons in the footer, "Open the stay" = XEM CHI TIẾT. Note → <code>SetRoomNote</code>. Built in 5.6 as a dialog.</p>
<h3><span class="n">4</span>Add to bill <span class="tag same">shape</span></h3>
<p>One button per charge category from Setup (the hotel's own names: Minibar · Laundry · Compensation · Extra service · Restaurant). Each opens What · Qty · Unit price → <code>PostCharge</code> with the category preselected; the room category is never offered. Group stay: posts to the guest's or the group's bill per routing.</p>
<h3><span class="n">5</span>State actions <span class="tag ours">ours</span></h3>
<table class="map"><tr><th>state</th><th>primary</th><th>maps to</th></tr>
<tr><td>booked, due today</td><td>Check in</td><td><code>CheckIn</code> (tonight's room must be in service)</td></tr>
<tr><td>checked in</td><td>Check out</td><td>settle dialog (screen 3) → <code>TakePayment</code> or <code>TransferToReceivable</code>, then <code>CheckOut</code></td></tr>
<tr><td>vacant</td><td>New booking for this room</td><td><code>CreateBooking</code> with the room prefilled (ezFolio's ĐẶT PHÒNG)</td></tr>
<tr><td>any</td><td>Mark dirty / clean · Out of order</td><td><code>SetHousekeeping</code> · <code>TakeOutOfOrder</code></td></tr></table></div>
"""
MAP_CANT = " key-card buttons; date picker on the map; ADVANCE POST ROOM CHARGE (the room charge is posted by the system at check-in and at the day roll); editing the rate in the panel (a night's price is <code>SetNightRate</code> with a reason, screen 3)."
MAP_LINKS = '<a href="shell.html">← 1 · Shell</a><a href="booking-editor.html">Next: 3 · Booking editor →</a>'

# ================================================================ 3. booking editor (stay)
EDITOR = f"""
<div class="app">{shell(active_rib="In house")}
<div class="page">
  <div class="head"><h2>Nguyễn Văn A</h2><span class="status">Checked in</span><span class="dim">booking #5533 · walk-in</span><span class="back">← In house</span></div>
  <div class="three" data-n="1">
    <div class="box"><div class="t">Guest</div><div class="b">
      <div class="kv"><span>Name</span><span>Nguyễn Văn A</span><span>Phone</span><span>0903 xxx xxx</span><span>ID</span><span>0790xxxxxxxx</span><span>Nationality</span><span>VN</span><span>Company</span><span>—</span></div></div></div>
    <div class="box"><div class="t">Booking</div><div class="b">
      <div class="kv"><span>Arrive</span><span>24/09/2026</span><span>Depart</span><span>26/09/2026 · 2 nights</span><span>Room</span><span>110 · Deluxe twin</span><span>Adults / children</span><span>2 / 0</span><span>Source</span><span>Walk-in</span><span>Notes</span><span>arrives ~20:00</span></div></div></div>
    <div class="box"><div class="t">Money</div><div class="money" style="grid-template-columns:1fr 1fr;border:0">
      <div><small>Total</small><b>830,000</b></div><div><small>Deposit</small><b>480,000</b></div><div><small>Paid</small><b>0</b></div><div><small>Due</small><b>350,000</b></div></div>
      <div class="hint" style="padding:6px 12px">as of today; tomorrow's night not yet posted</div></div>
  </div>
  <div class="box" data-n="2"><div class="t">Actions</div><div class="b"><div class="row">
    <span class="btn pri">Check out</span><span class="btn">Move room <span class="in sel" style="min-width:48px">110</span></span><span class="btn">Extend / shorten</span><span class="btn">Add a guest</span><span class="btn">Print the bill</span>
    <span class="hint">when booked: Assign room · Check in · Cancel the stay · Nobody came</span></div></div></div>
  <div class="tabs" data-n="3"><span>Guests</span><span class="on">Bill</span><span>Nights</span></div>
  <div class="box"><div class="b">
    <table><tr><th>Night</th><th>What</th><th class="num">Qty</th><th class="num">Unit price</th><th class="num">Amount</th><th></th></tr>
      <tr><td>24/09</td><td>Room</td><td class="num">1</td><td class="num">800,000</td><td class="num">800,000</td><td><span class="btn own">Void</span> <span class="btn own">Reprice</span></td></tr>
      <tr><td>24/09</td><td>Minibar · water <span class="chip">approval pending</span></td><td class="num">2</td><td class="num">15,000</td><td class="num">30,000</td><td></td></tr>
      <tr><td>24/09</td><td>Deposit · cash</td><td class="num"></td><td class="num"></td><td class="num neg">−480,000</td><td></td></tr></table>
    <div class="row">Add: <span class="in sel">Kind</span> <span class="in">What</span> Qty <span class="in" style="min-width:32px">1</span> Unit price <span class="in">0</span> <span class="btn">Add to bill</span></div>
    <div class="row">Payment: <span class="in sel">Payment</span> <span class="in sel">Cash</span> Amount <span class="in">350,000</span> Reference <span class="in"></span> <span class="btn">Record payment</span> <span class="btn own">Refund</span><span class="hint">refund at most 480,000</span></div>
    <div class="row">Move to the company: <span class="in sel">Company</span> <span class="btn">Move</span><span class="hint">the company owes it instead of the guest</span></div>
  </div></div>
  <div class="box" data-n="4"><div class="t">History <span class="r dim">ezFolio's Show log</span></div><div class="b"><table>
    <tr><th>v</th><th>Event</th><th>Detail</th><th>When</th><th>Who</th></tr>
    <tr><td>3</td><td>Checked in</td><td>room 110, 2 guests</td><td>24/09 14:02</td><td>Linh</td></tr>
    <tr><td>4</td><td>Deposit recorded</td><td>cash 480,000</td><td>24/09 14:05</td><td>Linh</td></tr></table></div></div>
</div>
<div class="arrowline">▼ <b>Check out</b> → settle dialog (ezFolio's quickout shape)</div>
<div class="fade"><div class="dlg" data-n="5">
  <div class="dh">Check out · room 110 <span class="x">✕</span></div>
  <div class="db">
    <div class="row" style="font-size:15px"><span class="dim">Owes</span> <b>350,000</b></div>
    <div class="row">How <span class="in sel">Cash</span> <span class="dim">Cash · Bank transfer · Card · On account — the company pays</span></div>
    <div class="row">Amount <span class="in">350,000</span> Reference <span class="in"></span></div>
    <div class="hint">On account: pick the company; the balance moves to its receivable, then the stay checks out. Nights after today go back on sale; the room becomes dirty.</div>
  </div>
  <div class="df"><span class="btn">Cancel</span><span class="btn pri">Check out</span></div>
</div></div>
</div>{LEGEND}
"""
EDITOR_NOTES = """
<div><h3><span class="n">1</span>Three panels across the top <span class="tag same">shape</span></h3>
<p>ezFolio's editor opens with guest · booking · money side by side; we keep that. Money = the four-number strip (Tổng · Đặt cọc · Trả trước · Còn lại → Total · Deposit · Paid · Due), built in 5.6. Guest fields stay minimal (name · phone · ID · nationality); PA18 fields come with PA18.</p>
<table class="map"><tr><th>field</th><th>maps to</th></tr><tr><td>Guest / party</td><td><code>UpdateParty</code> (5.7)</td></tr><tr><td>Room</td><td><code>AssignRoom</code> / <code>MoveStay</code></td></tr><tr><td>Source</td><td><code>BookingSource</code> from Setup, default walk-in (5.7)</td></tr><tr><td>Notes</td><td>booking notes</td></tr></table>
<h3 style="margin-top:12px"><span class="n">2</span>Actions row = ezFolio's Thao tác <span class="tag same">shape</span></h3>
<table class="map"><tr><th>button</th><th>maps to</th></tr>
<tr><td>Check in</td><td><code>CheckIn</code> — early arrival adds tonight and warns</td></tr><tr><td>Check out</td><td>settle dialog, then <code>CheckOut</code> (refused while the bill owes; the payment stands)</td></tr>
<tr><td>Move room</td><td><code>MoveStay</code> (unposted nights only)</td></tr><tr><td>Extend / shorten</td><td><code>ChangeNights</code>; a night's price → <code>SetNightRate</code> (5.7)</td></tr>
<tr><td>Add a guest</td><td><code>AddGuest</code></td></tr><tr><td>Cancel the stay / Nobody came</td><td><code>CancelStay {reason}</code> / <code>MarkNoShow</code>; owner may then <code>ForfeitDeposit</code></td></tr><tr><td>Print the bill</td><td>read (5.5)</td></tr></table></div>
<div><h3><span class="n">3</span>Tabs = Bản khai báo · Hóa đơn chi tiết · Đặt phòng <span class="tag same">shape</span></h3>
<p><b>Guests</b>: who checked in with (registration names). <b>Bill</b>: lines, add, pay, move to the company — every money act on one tab. <b>Nights</b>: night · room · rate, read-only. Group booking: a fourth tab <b>Rooms</b> lists the room stays, and the money panel shows the group's bill (master folio) with the routing table (rooms × categories → guest's bill / group's bill, <code>SetRouting</code>).</p>
<table class="map"><tr><th>control</th><th>maps to</th></tr>
<tr><td>Add to bill</td><td><code>PostCharge</code> (room category never offered; unit price ≥ 0)</td></tr><tr><td>Record payment (Payment / Deposit)</td><td><code>TakePayment</code></td></tr>
<tr><td>Refund 👑</td><td><code>Refund</code> ≤ money received</td></tr><tr><td>Void 👑 / Reprice 👑</td><td><code>VoidCharge</code> / <code>RepriceCharge</code> = the only discount; the desk's button says <b>Ask approval</b> → <code>RequestApproval</code>, the line shows the badge until the owner decides (5.8)</td></tr>
<tr><td>Move to the company</td><td><code>TransferToReceivable</code></td></tr></table>
<h3 style="margin-top:12px"><span class="n">4</span>History = Show log <span class="tag same">shape</span></h3><p>Same block at the bottom of every entity page: one line per event, who and when.</p>
<h3><span class="n">5</span>Settle dialog = quickout <span class="tag same">shape</span></h3>
<p>Balance · How · Amount · Reference, <b>On account — the company pays</b> last (ezFolio's Công nợ). Two commands in order, never one batch: <code>TakePayment</code> or <code>TransferToReceivable</code>, then <code>CheckOut</code>. The dialog never decides whether check-out is allowed. Built in 5.6.</p></div>
"""
EDITOR_CANT = " card number / expiry / CVV tab (no card data, ever); FOC, discount %, tax and service-fee fields (discount = owner reprice with a reason); editable per-night price grid; commission, saler, display colour; gender / DOB / address / visa until PA18."
EDITOR_LINKS = '<a href="room-map.html">← 2 · Room map</a><a href="status-lists.html">Next: 4 · Status lists →</a>'

# ================================================================ 4. status lists
LIST_ROWS = [  # section, #, guest, room, type, rate, nights, arrive, depart, source, company, notes, due
 ("Individuals · 3", None),
 ("", ("5533","Nguyễn Văn A","110","DLXT","800,000","2","24/09 14:00","26/09","Walk-in","—","arrives ~20:00","350,000")),
 ("", ("5860","Trần Thị B","106","DLX6","950,000","1","24/09 14:00","25/09","Agoda","—","14h out, luggage","0")),
 ("", ("5950","Lê Văn C","403","SUPT","850,000","3","24/09 15:00","27/09","Phone","—","",  "2,550,000")),
 ("Groups · 1 booking · 2 rooms", None),
 ("", ("5916","Phạm D (Metro Travel)","408","DLX5","850,000","4","24/09 14:00","28/09","Agent","Metro Travel","group's bill","—")),
 ("", ("5916","Phạm D (Metro Travel)","—","DLX5","850,000","4","24/09 14:00","28/09","Agent","Metro Travel","no room yet","—")),
]
def list_table():
    out = '<table><tr><th>#</th><th>Guest</th><th>Room</th><th>Type</th><th class="num">Rate</th><th class="num">Nights</th><th>Arrive</th><th>Depart</th><th>Source</th><th>Company</th><th>Notes</th><th class="num">Due</th></tr>'
    for sec, r in LIST_ROWS:
        if r is None: out += f'<tr class="grp"><td colspan="12">{sec}</td></tr>'; continue
        n, g, room, t, rate, ni, a, d, s, c, note, due = r
        room = room if room != "—" else '<span class="chip">assign</span>'
        out += f'<tr><td>{n}</td><td><a href="booking-editor.html" style="color:var(--accent);text-decoration:none">{g}</a></td><td>{room}</td><td>{t}</td><td class="num">{rate}</td><td class="num">{ni}</td><td>{a}</td><td>{d}</td><td>{s}</td><td>{c}</td><td class="dim">{note}</td><td class="num">{due}</td></tr>'
    return out + '</table>'

LISTS = f"""
<div class="app">{shell(active_rib="Due to arrive")}
<div class="page">
  <div class="head"><h2>Bookings</h2><span class="dim">arriving 24/09/2026</span><span class="back"><span class="btn">Print list</span> <a href="#new" class="btn pri">New booking</a></span></div>
  <div class="tabs" data-n="1"><span>All<b>40</b></span><span class="on">Due to arrive<b>5</b></span><span>Arriving today<b>3</b></span><span>In house<b>30</b></span><span>Leaving today<b>2</b></span><span>Cancelled<b>4</b></span></div>
  <div class="row" data-n="2">From <span class="in">24/09/2026</span> to <span class="in">24/09/2026</span> Type <span class="in sel">All</span> Room <span class="in" style="min-width:48px"></span> Company <span class="in sel">All</span> <span class="in" style="min-width:200px">Find: name, phone or booking #</span> <span class="btn">Search</span></div>
  <div class="box" data-n="3"><div class="b">{list_table()}</div></div>
  <div class="row dim" style="font-size:12px">5 stays · 5 rooms · 13 nights</div>
</div>
<div class="arrowline" id="new">▼ <b>New booking</b> (ezFolio's Khách lẻ / Khách đoàn on one form)</div>
<div class="fade"><div class="dlg" data-n="4" style="width:640px">
  <div class="dh">New booking <span class="x">✕</span></div>
  <div class="db">
    <div class="row">Booking for <span class="in sel">One guest</span> <span class="dim">One guest · A group</span> Source <span class="in sel">Walk-in</span></div>
    <div class="row">Guest <span class="in" style="min-width:160px"></span> Phone <span class="in"></span> Adults <span class="in" style="min-width:36px">2</span> Children <span class="in" style="min-width:36px">0</span></div>
    <div class="row">Arrive <span class="in">24/09/2026</span> Depart <span class="in">26/09/2026</span> <span class="hint">2 nights · 1,600,000 from the rate table</span></div>
    <div class="row">Room type <span class="in sel">Deluxe twin</span> Room <span class="in sel">110</span> <span class="dim">or decide later</span> Rate per night <span class="in">800,000</span></div>
    <div class="row">Billed to <span class="in sel">Nobody — the guests pay</span> Notes <span class="in" style="min-width:200px"></span></div>
    <div class="hint">A group: company + rooms per type (qty · adults · children · rate), rooms assigned later from the tape chart. Live availability per type shows next to the qty.</div>
  </div>
  <div class="df"><span class="btn">Take the booking</span><span class="btn pri">Take and check in now</span></div>
</div></div>
</div>{LEGEND}
"""
LISTS_NOTES = """
<div><h3><span class="n">1</span>One list, status tabs <span class="tag same">shape</span></h3>
<p>ezFolio has one list screen switched by <code>status=</code> (WILL_CHECKIN · CHECKIN · INHOUSE · CHECKOUT · CANCEL · NOSHOW). Same here: tabs with counts over one list, built in 5.6. Cancelled includes no-shows.</p>
<table class="map"><tr><th>tab</th><th>reads (<code>StayList</code>)</th></tr><tr><td>Due to arrive</td><td>booked, arrive in the window</td></tr><tr><td>Arriving today / Leaving today</td><td>arrive = today · depart = today</td></tr><tr><td>In house</td><td>checked in</td></tr><tr><td>Cancelled</td><td>cancelled + no-show</td></tr></table>
<h3 style="margin-top:12px"><span class="n">2</span>Filters <span class="tag same">shape</span></h3><p>ezFolio's bar: date range · type · room · company · name. Ours adds one Find box (name, phone, booking #). Print list = the printed list with its header (5.5).</p>
<h3><span class="n">3</span>Rows grouped Individuals / Groups, ezFolio's columns <span class="tag same">shape</span></h3>
<p># · Guest · Room · Type · Rate · Nights · Arrive · Depart · Source · Company · Notes, then <b>Due</b> (ours). Source is a real field (Walk-in · Phone · Agoda · Agent …), not a tag in the guest's name. A group row without a room shows <b>assign</b> → tape chart. Guest → the editor (screen 3).</p></div>
<div><h3><span class="n">4</span>New booking = Khách lẻ + Khách đoàn on one form <span class="tag same">shape</span></h3>
<table class="map"><tr><th>control</th><th>maps to</th></tr>
<tr><td>Take the booking</td><td><code>CreateBooking {kind, party, sourceId, arrive, depart, requests[]}</code> → individual opens the stay, group opens the booking</td></tr>
<tr><td>Take and check in now</td><td>ezFolio's walk-in lands in a CHECKIN folio; here it is <code>CreateBooking</code> then <code>CheckIn</code>, two commands, one click (room must be in service)</td></tr>
<tr><td>Rate per night</td><td>defaults from the rate table (<code>getQuote</code>); override is allowed and recorded</td></tr>
<tr><td>Availability per type</td><td>read <code>Availability</code> — ezFolio's availability grid inside the group form (G20)</td></tr>
<tr><td>Billed to</td><td>company → its receivable; deposit is a payment on the bill, not a form field</td></tr></table>
<p>Dropped columns: nationality code (on the guest), account / saler (who took the booking is in History), display code / colour (later, tape chart label).</p></div>
"""
LISTS_CANT = " Mã QT / Mã hiển thị columns; commission and saler fields; Export to Excel (a report, later); two separate entry points for walk-in and group."
LISTS_LINKS = '<a href="booking-editor.html">← 3 · Booking editor</a><a href="tape-chart.html">Next: 5 · Tape chart →</a>'

# ================================================================ 5. tape chart
DAYS = ["24/09 Wed","25/09 Thu","26/09 Fri","27/09 Sat","28/09 Sun","29/09 Mon","30/09 Tue"]
TYPES = [  # type, rooms: (number, state dot, bars: (start_idx, len, cls, label))
 ("VIP · 2", [("101","ooo",[(0,7,"ooo","Out of order — AC")]), ("201","in",[(0,3,"in","Bùi")])], [1,1,1,2,2,2,2]),
 ("Deluxe twin · 4", [("110","in",[(0,2,"in","Nguyễn Văn A")]), ("210","in",[(0,5,"in","Đinh")]), ("310","in",[(0,1,"in","Hà"),(2,3,"arr","Chu — Metro Travel")]), ("410","in",[(0,4,"in","Từ")])], [0,0,1,1,2,3,4]),
 ("Deluxe double · 6", [("105","in",[(0,2,"in","Phạm")]), ("107","in",[(0,1,"in","Vũ"),(3,4,"arr","Diệp")]), ("108","dirty",[(1,3,"arr","Lê Văn C")]), ("109","in",[(0,6,"in","Đặng")]), ("305","ready",[(2,2,"arr","Walk-in hold")]), ("307","ready",[])], [1,1,2,2,3,4,5]),
]
def tape():
    out = f'<table><tr><th>Room</th>' + ''.join(f'<th class="day{" today" if i==0 else ""}">{d}</th>' for i, d in enumerate(DAYS)) + '</tr>'
    for t, rooms, free in TYPES:
        out += f'<tr class="type"><td>{t}</td>' + ''.join(f'<td>{f} free</td>' for f in free) + '</tr>'
        for num, dot, bars in rooms:
            cells, i = '', 0
            while i < len(DAYS):
                b = next((x for x in bars if x[0] == i), None)
                if b:
                    s, l, cls, lab = b; l = min(l, len(DAYS)-i)
                    cells += f'<td colspan="{l}"><a class="bar {cls}" href="booking-editor.html">{lab}</a></td>'; i += l
                else:
                    cells += f'<td class="{"today" if i==0 else ""}"></td>'; i += 1
            out += f'<tr><td class="room"><i class="i-{dot}"></i>{num}</td>{cells}</tr>'
    used = [30,29,27,24,20,18,16]; total = 40
    out += '<tr class="sum"><td>Rooms used</td>' + ''.join(f'<td>{u}</td>' for u in used) + '</tr>'
    out += '<tr class="sum"><td>Rooms free</td>' + ''.join(f'<td>{total-1-u}</td>' for u in used) + '</tr>'
    out += '<tr class="sum"><td>Occupancy</td>' + ''.join(f'<td>{round(u/(total-1)*100)}%</td>' for u in used) + '</tr>'
    return out + '</table>'

TAPE = f"""
<div class="app">{shell(active_rib="Tape chart")}
<div class="page">
  <div class="row" data-n="1"><span class="btn">← Earlier</span><span class="btn">Today</span><span class="btn">Later →</span> <span class="dim">·</span> Window <span class="in sel">7 days</span> <span class="dim">7 · 14 · 30</span> Floor <span class="in sel">All</span>
    <span class="dim" style="margin-left:auto;font-size:12px"><i class="i-in" style="display:inline-block;width:9px;height:9px;border-radius:2px"></i> checked in &nbsp; <i class="i-arr" style="display:inline-block;width:9px;height:9px;border-radius:2px"></i> booked &nbsp; <i class="i-ooo" style="display:inline-block;width:9px;height:9px;border-radius:2px"></i> out of order &nbsp; ● dot = room state now</span></div>
  <div class="tape box" data-n="2">{tape()}</div>
  <div class="box" data-n="4"><div class="t">Nights without a room <span class="r dim">ezFolio's Đ.phòng chưa gán</span></div><div class="b"><table>
    <tr><th>Guest</th><th>Booking</th><th>Nights</th><th></th></tr>
    <tr><td>Phạm D — Metro Travel</td><td>#5916 · Deluxe double</td><td>24/09 → 28/09</td><td><span class="btn pri">Assign a room</span></td></tr></table></div></div>
</div></div>{LEGEND}
"""
TAPE_NOTES = """
<div><h3><span class="n">1</span>Window and filters <span class="tag same">shape</span></h3>
<p>ezFolio's Hôm nay · 1 · 7 · 15 · 30 ngày + floor multi-select. Ours: Earlier / Today / Later, window 7 · 14 · 30, floor filter. Built in 5.6 (floor filter: 5.7).</p>
<h3><span class="n">2</span>Rows grouped by room type, free count per type per day <span class="tag same">shape</span></h3>
<p>ezFolio puts the free count in the type's sub-header row; so do we (read <code>Availability</code>). That is the number the desk quotes on the phone. Bars = stays (read <code>Night</code> rows): a moved stay shows as two bars. The dot before the room number is the room's state <i>now</i> (ezFolio's legend: Sẵn sàng · Phòng bẩn · Có khách bẩn · Có khách sạch · Sửa chữa).</p>
<table class="map"><tr><th>gesture</th><th>maps to</th><th></th></tr>
<tr><td>click a bar</td><td>open the stay (screen 3)</td><td><span class="tag same">shape</span></td></tr>
<tr><td>click an empty cell</td><td>New booking with room + date prefilled</td><td><span class="tag later">later</span></td></tr>
<tr><td>drag a bar sideways / stretch it</td><td><code>MoveStay</code> / <code>ChangeNights</code> (unposted nights only; refused otherwise)</td><td><span class="tag later">later</span></td></tr></table></div>
<div><h3><span class="n">3</span>Bottom rows: used · free · occupancy <span class="tag same">shape</span></h3>
<p>Exactly ezFolio's #Phòng sử dụng · #Phòng trống · %Công suất, per day. Out-of-order rooms are out of supply (free excludes them; here 39 of 40). This is the owner's forward book at a glance.</p>
<h3><span class="n">4</span>Nights without a room <span class="tag ours">ours</span></h3>
<p>ezFolio keeps unassigned bookings on a separate list; ours sits under the chart, one click fewer. <b>Assign a room</b> → <code>AssignRoom</code> (type mismatch or out of order: warn, allow; hard stop is check-in only).</p>
<p class="dim">Colour by booking (ezFolio's Theo màu đặt phòng: a group's display colour) is later, with the group label on the bar.</p></div>
"""
TAPE_CANT = " colour-by-booking toggle and group display colour (later); 1-day and 15-day windows (7 · 14 · 30); the booking-list scroll arrows; radio buttons per room row."
TAPE_LINKS = '<a href="status-lists.html">← 4 · Status lists</a><a href="index.html">Index</a>'

# ================================================================ index
INDEX = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SoLex Flow Mockups</title><link rel="stylesheet" href="solex.css">
<div class="wrap">
<h1>SoLex, ezFolio-shaped — the desk's daily screens</h1>
<p class="sub">Mockups for the client demo. ezFolio's navigation, screen shapes, placement and daily flow, kept; SoLex's style, rules and feature set. Not a build: every control maps to an existing command or read, and the UI holds no rule. Labels in English (D-29), ezFolio's Vietnamese term bracketed where it helps recognise the original. Sample data invented.</p>
<div class="idx">
  <a href="shell.html"><b>1 · Shell</b><small>four tabs + Front desk ribbon; desk vs owner</small></a>
  <a href="room-map.html"><b>2 · Room map</b><small>status buttons with live counts, tiles by floor, tile → quick panel with Left to pay + Add to bill</small></a>
  <a href="booking-editor.html"><b>3 · Booking editor</b><small>guest · booking · money panels, Actions, Guests / Bill / Nights tabs, History, Check out → settle dialog</small></a>
  <a href="status-lists.html"><b>4 · Status lists</b><small>one list, status tabs with counts, Individuals / Groups, ezFolio's columns, New booking form</small></a>
  <a href="tape-chart.html"><b>5 · Tape chart</b><small>rooms by type with free-per-type rows, bars, used / free / occupancy, nights without a room</small></a>
</div>
<div class="legend" id="later"><span class="tag same">shape</span> ezFolio shape kept · <span class="tag ours">ours</span> SoLex addition · <span class="tag later">later</span> in SoLex, not in this demo · <span class="btn own">Owner</span> owner-only; the desk sees "Ask approval" (5.8)</div>
<p class="sub" style="margin-top:16px">Each screen: mockup first, notes below (≤5), one "maps to" line per control, one line on what was not carried over and why. Labels follow what dev built in 5.6 where it exists; the drawing shows what should be, not what is. Sources: <code>screens/fd-*.png</code> (not committed), <code>existing-system.md</code>, <code>product.md</code>, <code>ux.md</code>. Generated by <code>gen.py</code>; style in <code>solex.css</code>. Do not hand-edit the HTML.</p>
</div></html>"""

(OUT / "index.html").write_text(INDEX)
(OUT / "shell.html").write_text(page("1 · Shell — tabs and ribbon", "Common to every screen. Rendered as Linh (desk), then as the owner.", SHELL_BODY, SHELL_NOTES, SHELL_CANT, SHELL_LINKS))
(OUT / "room-map.html").write_text(page("2 · Room map (Sơ đồ)", "The desk's default screen. Rendered as Linh. Shape: <code>fd-room-map.png</code> + <code>fd-room-detail-panel.png</code>.", MAP_BODY, MAP_NOTES, MAP_CANT, MAP_LINKS))
(OUT / "booking-editor.html").write_text(page("3 · Booking editor (the stay)", "Where the desk works a guest: <code>/stays/:id</code>. Rendered as the owner so the amber buttons show; the desk sees \"Ask approval\" there. Shape: <code>fd-booking-detail.png</code> + quickout.", EDITOR, EDITOR_NOTES, EDITOR_CANT, EDITOR_LINKS))
(OUT / "status-lists.html").write_text(page("4 · Status lists + new booking", "One list for every status: <code>/bookings</code>. Rendered as Linh. Shape: <code>fd-arrivals-today.png</code> + walk-in / group forms.", LISTS, LISTS_NOTES, LISTS_CANT, LISTS_LINKS))
(OUT / "tape-chart.html").write_text(page("5 · Tape chart (Tình hình)", "The hotel over time: <code>/calendar</code>. Rendered as Linh. Shape: <code>fd-room-situation.png</code>.", TAPE, TAPE_NOTES, TAPE_CANT, TAPE_LINKS))
print("ok", {n: count(p) for _, n, p in ST})
