#!/usr/bin/env python3
"""ezFolio look-alike flow for SoLex — demo mockups (no build). Run from this dir: python3 gen.py
Writes ezfolio.css + index.html + one page per screen. Sample data is invented; no guest PII.
D-29: English labels; ezFolio Vietnamese term in brackets only where it aids recognition.
Reference: ../../screens/fd-*.png (gitignored, PII) + ../../existing-system.md. Rules: ../../product.md, ../../ux.md.
"""
from pathlib import Path

OUT = Path(__file__).parent

CSS = r"""
:root{
  --bg:#f4f5f7; --paper:#fff; --ink:#222; --muted:#666; --line:#d5d8dd;
  --bar:#eceef1; --tab-on:#fff; --icon:#2e6fb7; --logo:#2b5fb3; --logo2:#f28c1e;
  --st-all:#f0f0f0; --st-all-ink:#555;
  --st-ready:#34d24a; --st-arr:#c65bd6; --st-in:#e2241f; --st-dep:#a6d1f5; --st-dep-ink:#5f8fb5;
  --st-occdirty:#8cc63e; --st-vacdirty:#3d1f66; --st-ooo:#111;
  --key1:#f7923e; --key2:#9d9d9d; --modal:#4a6ed0; --tab-line:#e2241f;
  --note:#c8501f; --mono:ui-monospace,Menlo,monospace; --sans:"Helvetica Neue",Arial,system-ui,sans-serif;
  --drop:#b3261e; --dropbg:#fdecea; --ok:#2f7d4f; --okbg:#e9f5ee; --later:#8a5a00; --laterbg:#fff4dc;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --bg:#1b1d21; --paper:#24272c; --ink:#e8e6e1; --muted:#a2a6ad; --line:#3a3e45; --bar:#2b2f36; --tab-on:#24272c;
  --st-all:#3a3e45; --st-all-ink:#ccc; --dropbg:#3d201c; --okbg:#1f3328; --laterbg:#3a2f14; color-scheme:dark;}}
:root[data-theme="dark"]{
  --bg:#1b1d21; --paper:#24272c; --ink:#e8e6e1; --muted:#a2a6ad; --line:#3a3e45; --bar:#2b2f36; --tab-on:#24272c;
  --st-all:#3a3e45; --st-all-ink:#ccc; --dropbg:#3d201c; --okbg:#1f3328; --laterbg:#3a2f14; color-scheme:dark;}
/* the ezFolio frame + modal always render light: they mimic ezFolio's own colours */
.ez,.modal{--paper:#fff;--ink:#222;--muted:#666;--line:#d5d8dd;--bar:#eceef1;--tab-on:#fff;--st-all:#f0f0f0;--st-all-ink:#555;color:var(--ink)}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 var(--sans);padding:20px 16px 48px}
.wrap{max-width:1200px;margin:0 auto}
h1{font-size:20px;margin:0 0 2px}
.sub{color:var(--muted);margin:0 0 14px}
.sub code,code{font-family:var(--mono);font-size:12px}
.crumb{font-size:13px;margin-bottom:10px}.crumb a{color:var(--icon);text-decoration:none}.crumb a:hover{text-decoration:underline}
/* ---- ezFolio frame ---- */
.ez{background:var(--paper);border:1px solid var(--line);border-radius:4px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08);position:relative}
.topbar{display:flex;align-items:center;gap:0;background:var(--bar);border-bottom:1px solid var(--line);font-size:14px;height:30px;padding-left:8px}
.topbar .hotel{font-weight:600;padding:0 14px 0 6px}
.topbar a{color:var(--ink);text-decoration:none;padding:0 12px;line-height:28px;height:28px;display:inline-block;margin-top:2px}
.topbar a.on{background:var(--tab-on);border:1px solid var(--line);border-bottom:0;border-radius:3px 3px 0 0}
.topbar .right{margin-left:auto;display:flex;gap:12px;color:var(--muted);font-size:12px;padding-right:12px}
.ribbon{display:flex;align-items:flex-start;gap:0;padding:6px 8px 0;border-bottom:1px solid var(--line);background:var(--paper);overflow-x:auto}
.ribbon .big{display:flex;flex-direction:column;align-items:center;gap:2px;padding:4px 10px 8px;color:var(--ink);text-decoration:none;font-size:13px;white-space:nowrap}
.ribbon .big i{font-style:normal;font-size:24px;line-height:26px;color:var(--icon)}
.ribbon .grp{border-left:1px solid var(--line);padding:0 10px 4px;display:flex;flex-direction:column;font-size:13px;min-width:150px}
.ribbon .grp a{color:var(--ink);text-decoration:none;line-height:20px;white-space:nowrap}
.ribbon .grp a::before{content:"▪ ";color:var(--icon);font-size:10px}
.ribbon .grp .cap{color:var(--muted);font-size:11px;border-top:1px solid var(--line);margin-top:2px;padding-top:1px}
.ribbon a.x{color:var(--muted);text-decoration:line-through}
.logo{padding:6px 10px;font-weight:700;font-size:15px;color:var(--logo);letter-spacing:-.3px}.logo b{color:var(--logo2)}
.page{padding:10px 12px 16px}
/* status buttons */
.stbar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:12px}
.stbar .date{border-bottom:1px dotted var(--muted);font-size:13px;padding:2px 4px;margin-right:6px;color:var(--muted)}
.st{font-size:12px;font-weight:600;padding:5px 10px;border-radius:3px;color:#fff;text-decoration:none;text-transform:uppercase;white-space:nowrap}
.st.all{background:var(--st-all);color:var(--st-all-ink);border:1px solid var(--line)}
.st.ready{background:var(--st-ready)}.st.arr{background:var(--st-arr)}.st.in{background:var(--st-in)}
.st.dep{background:var(--st-dep);color:var(--st-dep-ink)}.st.occdirty{background:var(--st-occdirty)}
.st.vacdirty{background:var(--st-vacdirty)}.st.ooo{background:var(--st-ooo)}
.st.key1{background:var(--key1)}.st.key2{background:var(--key2)}
.stbar .tools{margin-left:auto;color:var(--muted);font-size:12px;display:flex;gap:10px;align-items:center}
/* tiles */
.tiles{display:grid;grid-template-columns:repeat(auto-fill,58px);gap:14px 17px;padding:4px 0 8px}
.tile{width:58px;height:70px;border-radius:2px;color:#fff;text-decoration:none;display:flex;flex-direction:column;justify-content:space-between;padding:5px 4px 4px;position:relative;box-shadow:0 1px 2px rgba(0,0,0,.25)}
.tile small{font-size:8px;line-height:9px;font-weight:600;text-transform:uppercase;opacity:.95}
.tile b{font-size:18px;line-height:18px;text-align:right;font-weight:600}
.tile.ready{background:var(--st-ready)}.tile.arr{background:var(--st-arr)}.tile.in{background:var(--st-in)}
.tile.dep{background:var(--st-dep);color:var(--st-dep-ink)}.tile.occdirty{background:var(--st-occdirty)}
.tile.vacdirty{background:var(--st-vacdirty)}.tile.ooo{background:var(--st-ooo)}
.tile.sel{outline:3px solid var(--modal);outline-offset:2px}
.floor{font-size:11px;color:var(--muted);margin:14px 0 -2px;text-transform:uppercase;letter-spacing:.04em}
/* modal (drawn in place) */
.modal{width:548px;max-width:100%;background:var(--paper);border:1px solid var(--line);border-radius:4px;box-shadow:0 8px 30px rgba(0,0,0,.25);font-size:13px;margin:0 auto}
.modal .mh{background:var(--modal);color:#fff;display:flex;align-items:center;padding:12px 16px;font-size:19px}
.modal .mh .act{margin-left:auto;font-size:12px;font-weight:600;letter-spacing:.02em}
.modal .mh .x{margin-left:22px;font-size:18px}
.modal .mtabs{display:flex;border-bottom:1px solid var(--line)}
.modal .mtabs span{padding:12px 20px;font-size:12px;letter-spacing:.02em}
.modal .mtabs .on{border-bottom:2px solid var(--tab-line)}
.modal .mbody{display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:14px 16px 6px}
.card{border:1px solid var(--line);border-radius:3px;padding:8px 14px}
.card .lk{color:var(--icon);font-size:11px;font-weight:600;letter-spacing:.02em;display:block;margin-bottom:12px}
.kv{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--line);font-size:13px}.kv:last-child{border:0}
.kv span:last-child{text-align:right;font-variant-numeric:tabular-nums}
.card .lab{padding:8px 0;border-bottom:1px solid var(--line)}
.card .val{padding:8px 0;text-align:right;border-bottom:1px solid var(--line)}
.card textarea{width:100%;height:50px;border:1px solid var(--icon);border-radius:2px;font:11px var(--sans);padding:3px;resize:none;background:var(--paper);color:var(--ink)}
.modal .bal{text-align:right;font-size:18px;font-weight:700;padding:8px 24px 6px}
.modal .mfoot{display:flex;gap:8px;padding:6px 16px 16px;justify-content:flex-end}
.modal .mfoot span{border:1px solid var(--line);border-radius:2px;padding:9px 12px;font-size:12px;box-shadow:0 1px 1px rgba(0,0,0,.08)}
.fade{background:rgba(0,0,0,.18);padding:36px 12px 44px;margin-top:-4px;border-top:1px solid var(--line)}
.arrowline{text-align:center;color:var(--muted);font-size:13px;padding:8px 0 0}
/* callouts */
.n{display:inline-block;width:20px;height:20px;border-radius:50%;background:var(--note);color:#fff;font:600 11px/20px var(--mono);text-align:center;vertical-align:middle;margin-right:6px}
[data-n]{position:relative}
[data-n]::after{content:attr(data-n);position:absolute;left:-10px;top:-10px;width:20px;height:20px;border-radius:50%;background:var(--note);color:#fff;font:600 11px/20px var(--mono);text-align:center;box-shadow:0 0 0 2px var(--paper);z-index:2}
/* notes below */
.notes{margin-top:18px;display:grid;grid-template-columns:1fr 1fr;gap:18px 28px}
@media (max-width:860px){.notes{grid-template-columns:1fr}}
.notes h3{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);margin:0 0 6px}
.notes p{margin:0 0 8px;font-size:13px}
table.map{border-collapse:collapse;width:100%;font-size:12.5px}
table.map th{text-align:left;color:var(--muted);font-weight:500;padding:3px 6px;border-bottom:1px solid var(--line);font-size:11.5px}
table.map td{padding:4px 6px;border-bottom:1px solid var(--line);vertical-align:top}
table.map tr:last-child td{border:0}
.tag{font-size:10.5px;padding:1px 6px;border-radius:3px;font-weight:600;white-space:nowrap}
.tag.same{background:var(--okbg);color:var(--ok)}.tag.drop{background:var(--dropbg);color:var(--drop)}.tag.later{background:var(--laterbg);color:var(--later)}
.cant{margin-top:14px;padding:8px 12px;background:var(--dropbg);color:var(--drop);border-radius:4px;font-size:13px}
.cant b{margin-right:6px}
.foot{margin-top:22px;font-size:13px;display:flex;gap:16px;flex-wrap:wrap}
.foot a{color:var(--icon);text-decoration:none}.foot a:hover{text-decoration:underline}
.legend{margin-top:16px;font-size:12px;color:var(--muted);display:flex;gap:14px;flex-wrap:wrap;align-items:center}
/* index */
.idx{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;margin-top:14px}
.idx a{display:block;border:1px solid var(--line);border-radius:4px;padding:12px 14px;background:var(--paper);color:var(--ink);text-decoration:none}
.idx a:hover{border-color:var(--icon)}
.idx a.todo{opacity:.55}
.idx b{display:block;font-size:15px;margin-bottom:4px}
.idx small{color:var(--muted);display:block}
"""

# ---------------------------------------------------------------- shared shell
TABS = [("Front desk (Lễ tân)", "shell.html", True), ("Housekeeping (Buồng)", "room-map.html#housekeeping", False),
        ("Reports (Báo cáo)", "index.html#later", False), ("System (Hệ thống)", "index.html#later", False)]

def topbar(active="Front desk (Lễ tân)"):
    t = ''.join(f'<a href="{h}" class="{"on" if n == active else ""}">{n}</a>' for n, h, _ in TABS)
    return (f'<div class="topbar"><span class="hotel">⌂ SOLEX HOTEL</span>{t}'
            f'<span class="right"><span>Print</span><span>Linh · desk</span><span>⏻</span></span></div>')

RIBBON_BIG = [("▦", "Room map", "room-map.html"), ("▤", "Tape chart", "index.html#todo"),
              ("👤", "Walk-in", "index.html#todo"), ("👥", "Group", "index.html#todo"),
              ("⇲", "Arriving", "index.html#todo"), ("⇱", "Departing", "index.html#todo"),
              ("⇄", "Move room", "index.html#todo"), ("🔍", "Search", "index.html#todo")]
RIBBON_GRPS = [
    ("Services", [("Laundry", "", False), ("Minibar", "", False), ("Restaurant", "", True)]),
    ("Today", [("Arrivals today", "index.html#todo", False), ("Departures today", "index.html#todo", False), ("Booking summary", "", True)]),
    ("Lists", [("In house", "index.html#todo", False), ("Cancelled", "index.html#todo", False), ("Unassigned", "index.html#todo", False)]),
    ("PA18", [("Export PA18", "", True), ("Guest registry", "", True)]),
]

def ribbon(mark=False):
    big = ''.join(f'<a class="big" href="{h}"><i>{ic}</i>{n}</a>' for ic, n, h in RIBBON_BIG)
    grps = ''
    for cap, items in RIBBON_GRPS:
        rows = ''.join(f'<a href="{h or "#"}" class="{"x" if x else ""}">{n}</a>' for n, h, x in items)
        grps += f'<div class="grp">{rows}<span class="cap">{cap}</span></div>'
    return f'<div class="ribbon">{big}{grps}</div><div class="logo">ez<b>FOLIO</b></div>'

def page(title, sub, body, notes, cant, links, crumb="index.html"):
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><link rel="stylesheet" href="ezfolio.css">
<div class="wrap">
<div class="crumb"><a href="{crumb}">← Index</a></div>
<h1>{title}</h1><p class="sub">{sub}</p>
{body}
<div class="notes">{notes}</div>
<div class="cant"><b>Not replicated:</b>{cant}</div>
<div class="foot">{links}</div>
</div></html>"""

# ---------------------------------------------------------------- 1. shell
SHELL_BODY = f"""
<div class="ez">
  <div data-n="1">{topbar()}</div>
  <div data-n="2">{ribbon()}</div>
  <div class="page" style="min-height:120px;color:var(--muted);font-size:13px">
    Screen content (room map, tape chart, lists …) renders here. Tabs and ribbon are the same on every screen.
  </div>
</div>
<div class="legend"><span class="n">n</span>note below · <span class="tag same">keep</span> as ezFolio, over a SoLex command/read · <span class="tag later">later</span> exists in SoLex, not in the demo · <span class="tag drop">drop</span> not available (struck through on the ribbon)</div>
"""

SHELL_NOTES = """
<div><h3><span class="n">1</span>Top tabs</h3>
<p>Keep 4 ezFolio tabs: <b>Front desk · Housekeeping · Reports · System</b>. Drop <b>Sales (Kinh doanh)</b> (only Companies → lives under Front desk › Lists), <b>Restaurant (Nhà hàng)</b> (POS unused; the folio keeps a restaurant line), <b>Audit (Kiểm toán)</b> (no night audit: the hotel day rolls itself at the hour set in Setup).</p>
<table class="map"><tr><th>tab</th><th>maps to</th><th></th></tr>
<tr><td>Front desk (Lễ tân)</td><td>ribbon below: room map · tape chart · new booking · lists</td><td><span class="tag same">keep</span></td></tr>
<tr><td>Housekeeping (Buồng)</td><td>same room map, DIRTY filter preselected; Clean/Dirty → <code>SetHousekeeping</code>; Out of order → <code>TakeOutOfOrder</code>/<code>ReturnToService</code></td><td><span class="tag same">keep</span></td></tr>
<tr><td>Reports (Báo cáo)</td><td>owner dashboard (revenue, occupancy, receivables) — projections, owner-only</td><td><span class="tag later">later</span></td></tr>
<tr><td>System (Hệ thống)</td><td>Setup (rooms, room types, charge categories, day-roll hour) + Accounts</td><td><span class="tag later">later</span></td></tr>
</table></div>
<div><h3><span class="n">2</span>Front desk ribbon</h3>
<table class="map"><tr><th>button</th><th>maps to</th><th></th></tr>
<tr><td>Room map (Sơ đồ)</td><td>read <code>RoomBoard</code> → screen 2</td><td><span class="tag same">keep</span></td></tr>
<tr><td>Tape chart (Tình hình)</td><td>read <code>Calendar</code> → screen 5</td><td><span class="tag same">keep</span></td></tr>
<tr><td>Walk-in (Khách lẻ)</td><td><code>CreateBooking{kind:'individual'}</code> then <code>CheckIn</code> — ezFolio lands in a folio already CHECKIN; SoLex is two steps on one form (book → check in) because check-in is a ruled event (tonight's room must be in service)</td><td><span class="tag same">keep</span></td></tr>
<tr><td>Group (Khách đoàn)</td><td><code>CreateBooking{kind:'group', requests[]}</code> — same form: company · source · dates · rooms per type; rooms assigned later</td><td><span class="tag same">keep</span></td></tr>
<tr><td>Arriving / Departing · Arrivals / Departures today · In house · Cancelled · Unassigned</td><td>one list screen, <code>status=</code> tabs → screen 4 (read <code>StayList</code>)</td><td><span class="tag same">keep</span></td></tr>
<tr><td>Move room (Đổi phòng)</td><td><code>MoveStay</code> — from the folio / stay (screen 3), no separate screen</td><td><span class="tag same">keep</span></td></tr>
<tr><td>Search (Tìm kiếm)</td><td>by name · phone · booking code → screen 4</td><td><span class="tag same">keep</span></td></tr>
<tr><td>Laundry · Minibar (registers)</td><td>read folio lines by category; posting still happens from the room tile (screen 2)</td><td><span class="tag later">later</span></td></tr>
<tr><td>Booking summary</td><td>Reports (owner)</td><td><span class="tag later">later</span></td></tr>
<tr><td>Restaurant · PA18 · Guest registry</td><td>out of v1 scope (PA18: product.md §8)</td><td><span class="tag drop">drop</span></td></tr>
</table></div>
"""
SHELL_CANT = " Sales, Restaurant, Audit tabs and key cards (ĐỌC/XÓA THẺ): out of scope. Tabs and ribbon are a shell; every button inside runs on an existing command or read — the UI holds no rule."
SHELL_LINKS = '<a href="room-map.html">Next: 2 · Room map →</a>'

# ---------------------------------------------------------------- 2. room map
# rooms: (number, type/bed code, status) — invented layout, 40 rooms
ROOMS = [
 ("101","VIP / DBL","ooo"),("103","SUPT / TWN","in"),("104","SUPD / DBL","in"),("105","DLX5 / DBL","in"),("106","DLX6 / DBL","dep"),
 ("107","DLX5 / DBL","in"),("108","DLX5 / DBL","vacdirty"),("109","DLX5 / DBL","in"),("110","DLXT / TWN","in"),
 ("201","VIP / DBL","in"),("203","SUPT / TWN","in"),("204","SUPD / DBL","occdirty"),("205","DLX5 / DBL","in"),("206","DLX6 / DBL","in"),
 ("207","DLX5 / DBL","in"),("208","DLX5 / DBL","in"),("209","DLX5 / DBL","dep"),("210","DLXT / TWN","in"),
 ("301","SUPD / DBL","in"),("302","STD2 / DBL","ready"),("303","SUPT / TWN","in"),("304","SUPT / TWN","in"),("305","DLX5 / DBL","ready"),
 ("306","DLX6 / DBL","in"),("307","DLX5 / DBL","ready"),("308","DLX5 / DBL","vacdirty"),("309","DLX5 / DBL","in"),("310","DLXT / TWN","in"),
 ("401","SUPD / DBL","in"),("402","STD2 / DBL","in"),("403","SUPT / TWN","arr"),("404","SUPT / TWN","in"),("405","DLX5 / DBL","in"),
 ("406","DLX6 / DBL","in"),("407","DLX5 / DBL","in"),("408","DLX5 / DBL","arr"),("409","DLX5 / DBL","in"),("410","DLXT / TWN","in"),
 ("501","SUPD / DBL","arr"),("502","STD2 / DBL","in"),
]
ST = [("all","ALL"),("ready","READY"),("arr","ARRIVING"),("in","IN HOUSE"),("dep","DEPARTING"),
      ("occdirty","OCCUPIED DIRTY"),("vacdirty","VACANT DIRTY"),("ooo","OUT OF ORDER")]
cnt = {k: sum(1 for r in ROOMS if r[2] == k) for k, _ in ST}
cnt["all"] = len(ROOMS)
# ezFolio's ĐANG Ở count includes departing/occupied-dirty rooms (all in-house); keep that reading
cnt_in_display = cnt["in"] + cnt["dep"] + cnt["occdirty"]

def stbar():
    b = ''.join(f'<a class="st {k}" href="#">{n}({cnt_in_display if k=="in" else cnt[k]})</a>' for k, n in ST)
    return (f'<div class="stbar" data-n="1"><span class="date">24/09/2026</span>{b}'
            f'<span class="tools">FILTER · ▦ · 🖶 <span class="st key1" style="text-decoration:line-through">READ CARD</span>'
            f'<span class="st key2" style="text-decoration:line-through">ERASE CARD</span></span></div>')

def tiles():
    out, floor = '', None
    for num, code, st in ROOMS:
        f = num[0]
        if f != floor:
            if floor is not None: out += '</div>'
            out += f'<div class="floor">Floor {f}</div><div class="tiles">'
            floor = f
        sel = ' sel' if num == "110" else ''
        out += f'<a class="tile {st}{sel}" href="#detail" title="{code}"><small>{code}</small><b>{num}</b></a>'
    return out + '</div>'

MODAL = """
<div class="modal" id="detail">
  <div class="mh">Detail (Chi tiết) <span class="act">⎘ BOOK (ĐẶT PHÒNG)</span><span class="x">✕</span></div>
  <div class="mtabs" data-n="3"><span class="on">CHECKIN ROOM</span><span style="text-decoration:line-through;color:var(--muted)">ADVANCE POST ROOM CHARGE</span></div>
  <div class="mbody">
    <div class="card" data-n="4"><a class="lk" href="index.html#todo">🔍 VIEW DETAIL (XEM CHI TIẾT)</a>
      <div class="kv"><span>Room</span><span>110</span></div>
      <div class="kv"><span>Rate</span><span>1,100,000</span></div>
      <div class="kv"><span>Arrival</span><span>18/09/2026 20:11</span></div>
      <div class="kv"><span>Departure</span><span>28/09/2026 12:00</span></div>
      <div class="kv"><span>Nights</span><span>10</span></div>
      <div class="kv"><span>Status</span><span>CHECKIN</span></div>
    </div>
    <div class="card">
      <div class="lab">Guest</div><div class="val">NGUYEN VAN A 0903 xxx xxx</div>
      <div class="lab">Company</div><div class="val">—</div>
      <div class="lab">Note <span style="float:right;color:#c00">🖫</span></div>
      <textarea>20h in</textarea>
    </div>
  </div>
  <div class="bal">Balance (Còn lại): 350,000 ⎆</div>
  <div class="mfoot" data-n="5"><span>DIRTY</span><span>MINIBAR</span><span>LAUNDRY</span><span>COMPENSATION</span><span>EXTRA SERVICE</span></div>
</div>
"""

MAP_BODY = f"""
<div class="ez">
  {topbar()}{ribbon()}
  <div class="page" id="housekeeping">
    {stbar()}
    <div data-n="2">{tiles()}</div>
  </div>
  <div class="arrowline">▼ click tile <b>110</b> → "Detail" box (opens over the map; drawn apart here for reading)</div>
  <div class="fade">{MODAL}</div>
</div>
<div class="legend"><span class="n">n</span>note below · struck through = dropped · tile colour = status, ezFolio's palette · sample data, no real guests</div>
"""

MAP_NOTES = f"""
<div><h3><span class="n">1</span>Status buttons with live counts</h3>
<p>Same 8 buttons, colours and order (ezFolio: TẤT CẢ · SẴN SÀNG · DỰ KIẾN ĐẾN · ĐANG Ở · DỰ KIẾN ĐI · CÓ KHÁCH BẨN · TRỐNG BẨN · PHÒNG SỬA). Counts and tile colours are <b>derived</b> from the room (clean/dirty, out of order) + the stays' nights — no stored status (product.md §6 Room: "derived, never stored"). Click = filter tiles.</p>
<table class="map"><tr><th>button</th><th>maps to (read <code>RoomBoard</code>)</th></tr>
<tr><td>ALL</td><td>every defined room</td></tr>
<tr><td>READY</td><td>vacant · clean · nobody arriving today</td></tr>
<tr><td>ARRIVING</td><td>stay <i>booked</i> with tonight in its nights, room assigned</td></tr>
<tr><td>IN HOUSE</td><td>stay <i>checkedIn</i> tonight (includes departing / occupied dirty, as ezFolio counts)</td></tr>
<tr><td>DEPARTING</td><td>checkedIn, last night was yesterday</td></tr>
<tr><td>OCCUPIED DIRTY / VACANT DIRTY</td><td>housekeeping = dirty, with / without a guest</td></tr>
<tr><td>OUT OF ORDER</td><td><code>room.outOfOrder</code></td></tr>
<tr><td>Date 24/09</td><td>display only; cannot be changed (see "not replicated")</td></tr>
</table></div>
<div><h3><span class="n">2</span>Room tiles</h3>
<p>Type / bed code on top, room number below, colour = status. Grouped by floor. Click → <b>Detail</b> box. ezFolio's corner triangles (key card / note flags) are not drawn.</p>
<h3><span class="n">3</span>Detail box header</h3>
<table class="map"><tr><th>button</th><th>maps to</th><th></th></tr>
<tr><td>BOOK (ĐẶT PHÒNG)</td><td><code>CreateBooking{{kind:'individual', room:110}}</code> — booking form with the room prefilled</td><td><span class="tag same">keep</span></td></tr>
<tr><td>CHECKIN ROOM</td><td><code>CheckIn{{stayId}}</code> (tonight's room must be in service; early arrival → adds tonight, warns)</td><td><span class="tag same">keep</span></td></tr>
<tr><td>ADVANCE POST ROOM CHARGE</td><td>none: the room charge is posted by the system at check-in and at the day roll; the <i>room</i> category is locked for everyone</td><td><span class="tag drop">drop</span></td></tr>
</table>
<h3><span class="n">4</span>Detail box body</h3>
<table class="map"><tr><th>field</th><th>maps to</th></tr>
<tr><td>Room · Rate · Arrival / Departure · Nights · Status · Guest · Company</td><td>read the room's stay tonight (<code>Stay</code> + <code>Booking.party</code>); Rate = tonight's night rate</td></tr>
<tr><td>Note + 🖫</td><td><code>SetRoomNote</code> (the room's note; the booking note lives on screen 3)</td></tr>
<tr><td>Balance (Còn lại)</td><td>read folio balance (total − deposit − paid); ⎆ → screen 3 (folio)</td></tr>
<tr><td>VIEW DETAIL</td><td>→ screen 3 (booking editor / stay)</td></tr>
</table>
<h3><span class="n">5</span>Quick buttons</h3>
<table class="map"><tr><th>button</th><th>maps to</th></tr>
<tr><td>DIRTY</td><td><code>SetHousekeeping{{dirty}}</code> (Housekeeping tab: same button plus CLEAN)</td></tr>
<tr><td>MINIBAR · LAUNDRY · COMPENSATION · EXTRA SERVICE</td><td><code>PostCharge</code> with the category preselected; the button list = the charge categories in Setup (the hotel's own names and prices). Each opens one line: item · qty · unit price → posted to the folio per routing (group: guest folio or master folio)</td></tr>
</table></div>
"""
MAP_CANT = " READ / ERASE CARD (key cards out of scope, permanently) · date picker on the map (the map is now; over time is the tape chart, product.md §4) · ADVANCE POST ROOM CHARGE (room charge is a system category, §6) · Rate not editable in place (a night's price change = <code>SetNightRate</code> with a reason, screen 3)."
MAP_LINKS = '<a href="shell.html">← 1 · Shell</a><a href="index.html#todo">Next: 3 · Booking editor (not drawn yet) →</a>'

# ---------------------------------------------------------------- index
INDEX = f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SoLex ezFolio Flow</title><link rel="stylesheet" href="ezfolio.css">
<div class="wrap">
<h1>SoLex — the "same as ezFolio" flow</h1>
<p class="sub">Demo mockups for the client: the desk's daily screens in <b>ezFolio's shapes</b>, running on SoLex's existing commands and reads (the UI holds no rule). To compare "same as before" with the SoLex flow (<code>ux.md</code>). Not a build. Sample data; no real guests. Labels in English (D-29); ezFolio's Vietnamese term in brackets where it helps recognise the original.</p>
<div class="idx">
  <a href="shell.html"><b>1 · Shell</b><small>top tabs + Front desk ribbon; which buttons keep / later / drop</small></a>
  <a href="room-map.html"><b>2 · Room map + Detail</b><small>status buttons with live counts, room tiles, Detail box with Balance + quick buttons</small></a>
  <a class="todo" id="todo" href="#todo"><b>3 · Booking editor</b><small>three panels guest · booking · money; tabs; actions; show log; fast checkout → quickout — after review of 1+2</small></a>
  <a class="todo" href="#todo"><b>4 · Status lists</b><small>status= tabs, individual / group, ezFolio column order — pending</small></a>
  <a class="todo" href="#todo"><b>5 · Tape chart</b><small>rooms by type, used / free / % rows — pending</small></a>
</div>
<div class="legend" id="later"><span class="tag same">keep</span> as ezFolio, over SoLex commands/reads · <span class="tag later">later</span> in SoLex, not in the demo · <span class="tag drop">drop</span> out of scope (key cards, card fields, discount/FOC/tax, restaurant, night audit)</div>
<p class="sub" style="margin-top:16px">Each screen: mockup first, notes below (≤5), one "maps to" line per control, one "not replicated" line with the reason. Drawn from <code>screens/fd-*.png</code> (not committed) + <code>existing-system.md</code>; rules per <code>product.md</code>. Generated by <code>gen.py</code> — do not hand-edit the HTML.</p>
</div></html>"""

(OUT / "ezfolio.css").write_text(CSS.strip() + "\n")
(OUT / "index.html").write_text(INDEX)
(OUT / "shell.html").write_text(page("1 · Shell — tabs + Front desk ribbon",
    "Common shell of every screen. Rendered as: Linh (desk). Reference: header of <code>fd-room-map.png</code>.",
    SHELL_BODY, SHELL_NOTES, SHELL_CANT, SHELL_LINKS))
(OUT / "room-map.html").write_text(page("2 · Room map (Sơ đồ) + Detail box",
    "The desk's default screen. Rendered as: Linh. Reference: <code>fd-room-map.png</code>, <code>fd-room-detail-panel.png</code>.",
    MAP_BODY, MAP_NOTES, MAP_CANT, MAP_LINKS))
print("ok", cnt, "in-display", cnt_in_display)
