"""Generates diagrams/solex-ux.excalidraw from ux.md (IA map + screen wireframes + two journeys).
Run: python3 gen-solex-ux.py   (from this directory). Edit DATA, re-run, commit both files. Never hand-edit the output.
Sibling of gen-solex-domain.py; same drawing helpers, different data.
"""
import json, random, time, textwrap
random.seed(11)
els = []
NOW = int(time.time() * 1000)
CW, LH = 0.62, 1.25

def base(t, x, y, w, h, **k):
    d = dict(id=f"{t}{len(els)}_{random.randint(1000, 99999)}", type=t, x=x, y=y, width=w, height=h, angle=0,
             strokeColor="#1e1e1e", backgroundColor="transparent", fillStyle="solid", strokeWidth=1,
             strokeStyle="solid", roughness=0, opacity=100, groupIds=[], frameId=None, roundness=None,
             seed=random.randint(1, 2**31), version=1, versionNonce=random.randint(1, 2**31), isDeleted=False,
             boundElements=None, updated=NOW, link=None, locked=False)
    d.update(k); els.append(d); return d

def rect(x, y, w, h, bg="transparent", stroke="#1e1e1e", dash=False, sw=1, opacity=100):
    return base("rectangle", x, y, w, h, backgroundColor=bg, strokeColor=stroke, roundness={"type": 3},
                strokeStyle="dashed" if dash else "solid", strokeWidth=sw, opacity=opacity)

def tsize(s, size):
    lines = s.split("\n")
    return max(len(l) for l in lines) * size * CW, len(lines) * size * LH

def text(x, y, s, size=12, color="#1e1e1e", bold=False):
    w, h = tsize(s, size)
    return base("text", x, y, w, h, text=s, fontSize=size, fontFamily=1 if bold else 3, textAlign="left",
                verticalAlign="top", containerId=None, originalText=s, lineHeight=LH, strokeColor=color, autoResize=True)

def arrow(x1, y1, x2, y2, color="#868e96", dash=False, label=None):
    a = base("arrow", x1, y1, abs(x2 - x1) or 1, abs(y2 - y1) or 1, points=[[0, 0], [x2 - x1, y2 - y1]],
             startBinding=None, endBinding=None, startArrowhead=None, endArrowhead="arrow",
             strokeColor=color, strokeStyle="dashed" if dash else "solid", roundness={"type": 2}, lastCommittedPoint=None)
    if label:
        text((x1 + x2) / 2 - tsize(label, 10)[0] / 2, (y1 + y2) / 2 - 14, label, size=10, color=color)
    return a

# ---------------------------------------------------------------- palette
APP = {"fd": ("#1971c2", "#e7f5ff", "Front Desk"), "bo": ("#2f9e44", "#ebfbee", "Back Office"),
       "su": ("#e8590c", "#fff4e6", "Setup"), "sys": ("#495057", "#f1f3f5", "System (operator)")}
PERSONA = {"R": ("#1971c2", "receptionist"), "O": ("#e8590c", "owner / manager"), "S": ("#862e9c", "setup admin (owner hat)")}
GAP_C = "#c92a2a"     # not built yet
OWN_C = "#e8590c"     # owner-only control

def chip(x, y, label, color):
    w, h = tsize(label, 9)
    rect(x, y, w + 8, h + 4, bg=color, stroke=color)
    text(x + 4, y + 2, label, size=9, color="#ffffff", bold=True)
    return w + 8

# ---------------------------------------------------------------- DATA
# screens: key -> (app, title, route, personas, regions)   region = (label, kind) kind: "" built, "gap" target-only, "own" owner-only
SCREENS = {
    "map": ("fd", "Room map · Sơ đồ phòng", "/", "RO", [
        ("today strip: arrivals · departures · occupancy", "gap"),
        ("floors → tiles: number · hk state · [tonight's guest]", ""),
        ("tile → /rooms/:id  ·  quick panel: mark clean/dirty → SetHousekeeping", "gap"),
        ("quick panel: open stay · check out → CheckOut · OOO → TakeOutOfOrder", "gap"),
        ("[+ New booking] → /bookings", ""),
        ("define room → DefineRoom  (move to Setup)", ""),
    ]),
    "room": ("fd", "Room · Phòng", "/rooms/:id", "RO", [
        ("header: number · type · floor · state", ""),
        ("[Mark clean] [Mark dirty] → SetHousekeeping", ""),
        ("reason [__] [Take out of order] → TakeOutOfOrder  |  [Return] → ReturnToService", ""),
        ("note [__] [Save] → SetRoomNote", ""),
        ("who is in it tonight / next arrival", "gap"),
        ("History", ""),
    ]),
    "cal": ("fd", "Calendar · Lịch phòng", "/calendar", "RO", [
        ("← earlier · today · later →  (14 nights)", ""),
        ("grid rooms × nights: booked / in / out-held / free / OOO; cell → /stays/:id", ""),
        ("availability per type row (quoting)", "gap"),
        ("click empty cell → new booking prefilled", "gap"),
        ("unassigned nights: [Assign a room] → /stays/:id", ""),
        ("drag bar → MoveStay / ChangeNights", "gap"),
    ]),
    "bookings": ("fd", "Bookings · Đặt phòng", "/bookings", "RO", [
        ("kind: one guest | group · billed to (company)", ""),
        ("guest · phone · arrive · depart · adults · room type · rate (quote)", ""),
        ("room (decide later) | group: rooms qty", ""),
        ("[Take the booking] → CreateBooking → /stays/:id | /bookings/:id", ""),
        ("list: guest · dates · nights · status · [Open stay]", ""),
        ("search name / phone / company · filters", "gap"),
    ]),
    "booking": ("fd", "Booking · Đặt phòng (đoàn)", "/bookings/:id", "RO", [
        ("header: contact · status · dates · nights", ""),
        ("[Finish] → CloseBooking  (group)", ""),
        ("group's bill: lines · void → VoidCharge · [Record payment] → TakePayment · [Move to company] → TransferToReceivable", "own"),
        ("stays: dates · room · status · [Open stay] → /stays/:id", ""),
        ("[Cancel booking] → CancelBooking · edit notes · add/remove stays", "gap"),
        ("History", ""),
    ]),
    "stay": ("fd", "Stay · Lượt lưu trú", "/stays/:id", "RO", [
        ("header: guest · status · dates · room · phone   ⚠ room OOO", ""),
        ("room (select) [Assign] → AssignRoom / [Move] → MoveStay", ""),
        ("guests [+] → AddGuest · [Check in] → CheckIn · reason [Cancel] → CancelStay", ""),
        ("[Check out] → CheckOut", ""),
        ("routing (group): category → own | master → SetRouting", ""),
        ("bill: lines · [Add to bill] → PostCharge · [Record payment] → TakePayment · refund → Refund · void → VoidCharge", "own"),
        ("bill: company (select) [Move to the company] → TransferToReceivable", ""),
        ("move line → MoveCharge · print · change nights → ChangeNights · no-show → MarkNoShow", "gap"),
        ("nights held: night · room · rate", ""),
        ("History", ""),
    ]),
    "people": ("bo", "People · Khách & liên hệ", "/guests", "RO", [
        ("search [name / phone] (POST) → read", ""),
        ("guests: name → /guests/:id · phone · ID · erase → EraseGuest", "own"),
        ("[Add guest] → CreateGuest", ""),
        ("contacts: name · phone · erase → EraseContact", "own"),
        ("[Add contact] → CreateContact", ""),
        ("edit details → UpdateGuest / UpdateContact · guest's stays", "gap"),
    ]),
    "recv": ("bo", "Receivables · Công nợ", "/receivables", "RO", [
        ("by company: contacts · outstanding · since · [Open]", ""),
        ("statement: night · what · amount", ""),
        ("method · amount · ref [Record payment] → RecordReceivablePayment", ""),
        ("reason [Write off] → WriteOffReceivable", "own"),
        ("lines link to stay / booking · settled toggle", "gap"),
    ]),
    "exp": ("bo", "Expenses · Chi phí", "/expenses", "RO", [
        ("from · to [Show] · total", ""),
        ("list: date · category · what · method · amount · void → VoidExpense", "own"),
        ("category · what · amount · method · date · ref [Record it] → RecordExpense", ""),
        ("by category totals", ""),
        ("cash handover / day close (parked §8)", "gap"),
    ]),
    "dash": ("bo", "Dashboard · Hôm nay", "(none)", "RO", [
        ("in house · arrivals · departures · dirty · OOO", "gap"),
        ("cash in today by method · revenue posted", "gap"),
        ("companies owing · expenses today", "gap"),
        ("forward book 7 days", "gap"),
        ("reports: revenue by category / method · occupancy over time", "gap"),
    ]),
    "setup": ("su", "Setup · Thiết lập", "/setup", "S", [
        ("room types: name · id · sleeps · [Retire] → RetireRoomType · [Add] → DefineRoomType", ""),
        ("rates: type · from · until · price · [Retire] · [Add rate] → DefineRate", ""),
        ("charge categories · [Add the standard list] → DefineChargeCategory×N", ""),
        ("companies: name · tax code · phone · [Retire] → RetireCompany · [Add] → DefineCompany", ""),
        ("company default routing", "gap"),
        ("rooms (read) → /rooms/:id", ""),
        ("hotel profile · booking rules · floors · charge items · sources", "gap"),
    ]),
    "accounts": ("su", "Accounts · Tài khoản", "/accounts", "S", [
        ("person → /accounts/:id · username · role (select) → AddStaff / ChangeStaffRole · sessions", ""),
        ("[Reset password] → ResetPassword · [Former staff] → DeactivateStaff · [Bring back] → ReactivateStaff", ""),
        ("name · username · password · email · role [Create] → CreateUser", ""),
        ("/accounts/:id: name · email [Save] → UpdateUser · History (user.* + staff.*)", ""),
    ]),
    "signin": ("sys", "Sign in · Đăng nhập", "/sign-in", "ROS", [
        ("username · password [Sign in]", ""),
    ]),
    "system": ("sys", "System console", "/system…", "", [
        ("overview: event count · [Rebuild projections] · event types · streams · tables", ""),
        ("events log (filters) · tables browser", ""),
    ]),
}

# navigation arrows between screens: (from, to, label)
NAV = [
    ("map", "room", "tile"), ("map", "bookings", "+ new booking"), ("cal", "stay", "cell"), ("cal", "room", "row"),
    ("bookings", "stay", "individual / open stay"), ("bookings", "booking", "group"), ("booking", "stay", "open stay"),
    ("stay", "recv", "transfer → company owes"), ("people", "stay", "(gap) guest's stays"), ("setup", "accounts", "staff"),
    ("stay", "cal", "back"), ("recv", "exp", "write-off = expense"),
]

# journeys drawn as chains: (label, persona, [(screen, action)])
JOURNEYS = [
    ("J1 walk-in → pay → leave", "R", [("map", "free clean room"), ("bookings", "CreateBooking"), ("stay", "CheckIn"),
                                       ("stay", "PostCharge"), ("stay", "TakePayment"), ("stay", "CheckOut"), ("map", "SetHousekeeping clean")]),
    ("J2 group: book → assign → route → finish", "R", [("bookings", "CreateBooking group"), ("cal", "AssignRoom ×6"), ("stay", "CheckIn ×6"),
                                                       ("stay", "SetRouting"), ("booking", "TakePayment deposit"), ("stay", "CheckOut ×6"), ("booking", "CloseBooking")]),
    ("O2 month-end receivables", "O", [("recv", "open company"), ("recv", "RecordReceivablePayment"), ("recv", "WriteOffReceivable 👑")]),
    ("S1 go-live", "S", [("setup", "DefineRoomType"), ("map", "DefineRoom"), ("setup", "DefineRate"), ("setup", "seed categories"),
                         ("setup", "DefineCompany"), ("accounts", "CreateUser"), ("accounts", "AddStaff")]),
]

# ---------------------------------------------------------------- drawing
X0, Y = 0, 0
text(X0, Y, "SoLex — UX map by persona", size=28, bold=True); Y += 40
text(X0, Y, "generated from ux.md · IA map (top) → screen wireframes (middle) → journeys (bottom). Red = not built yet (ux.md §6). Orange = owner-only control.", size=12, color="#495057"); Y += 26
# legend
lx = X0
for k, (c, name) in PERSONA.items():
    lx += chip(lx, Y, k, c) + 4; text(lx, Y, name, size=11, color=c); lx += tsize(name, 11)[0] + 24
lx += chip(lx, Y, "gap", GAP_C) + 4; text(lx, Y, "target, not built", size=11, color=GAP_C); lx += tsize("target, not built", 11)[0] + 24
lx += chip(lx, Y, "👑", OWN_C) + 4; text(lx, Y, "owner-only", size=11, color=OWN_C)
Y += 40

# ---- IA map
text(X0, Y, "1 · Information architecture — apps → screens (who sees what)", size=18, bold=True); Y += 34
ia_pos = {}
cx = X0
IA_COLS = [("fd", ["map", "room", "cal", "bookings", "booking", "stay"]), ("bo", ["people", "recv", "exp", "dash"]),
           ("su", ["setup", "accounts"]), ("sys", ["signin", "system"])]
col_w = 300
for app, keys in IA_COLS:
    c, bg, name = APP[app]
    h = 44 + len(keys) * 38 + 12
    rect(cx, Y, col_w, h, bg=bg, stroke=c, sw=2)
    text(cx + 12, Y + 10, name, size=15, color=c, bold=True)
    who = {"fd": "receptionist + owner", "bo": "receptionist (partly) + owner", "su": "owner only", "sys": "everyone / operator"}[app]
    text(cx + 12, Y + 30, who, size=10, color=c)
    yy = Y + 52
    for k in keys:
        _, title, route, personas, regions = SCREENS[k]
        gap = all(r[1] == "gap" for r in regions)
        rect(cx + 12, yy, col_w - 24, 30, bg="#ffffff", stroke=GAP_C if gap else c, dash=gap)
        text(cx + 20, yy + 4, title.split(" · ")[0], size=12, bold=True, color=GAP_C if gap else "#1e1e1e")
        text(cx + 20, yy + 18, route, size=9, color="#868e96")
        px = cx + col_w - 24
        for p in reversed(personas):
            px -= 18; chip(px, yy + 8, p, PERSONA[p][0])
        ia_pos[k] = (cx + 12, yy, col_w - 24, 30)
        yy += 38
    cx += col_w + 30
Y += max(44 + len(k) * 38 + 12 for _, k in IA_COLS) + 50

# ---- wireframes
text(X0, Y, "2 · Screens — regions and the command each control fires (ux.md §4)", size=18, bold=True); Y += 34
WF_COLS = 4
wf_w = 420
order = ["map", "room", "cal", "bookings", "booking", "stay", "people", "recv", "exp", "dash", "setup", "accounts", "signin", "system"]
pos = {}
col_y = [Y] * WF_COLS
for i, k in enumerate(order):
    app, title, route, personas, regions = SCREENS[k]
    c, bg, _ = APP[app]
    col = i % WF_COLS
    x = X0 + col * (wf_w + 30); y = col_y[col]
    # measure
    body_h = 0
    lines = []
    for label, kind in regions:
        wrapped = textwrap.wrap(label, 62) or [""]
        lines.append((wrapped, kind)); body_h += len(wrapped) * 14 + 12
    h = 48 + body_h + 10
    rect(x, y, wf_w, h, bg="#ffffff", stroke=c, sw=2)
    rect(x, y, wf_w, 40, bg=bg, stroke=c, sw=2)
    text(x + 12, y + 8, title, size=14, bold=True, color=c)
    text(x + 12, y + 25, route, size=10, color="#868e96")
    px = x + wf_w - 12
    for p in reversed(personas):
        px -= 18; chip(px, y + 12, p, PERSONA[p][0])
    yy = y + 48
    for wrapped, kind in lines:
        rh = len(wrapped) * 14 + 8
        stroke = {"gap": GAP_C, "own": OWN_C}.get(kind, "#adb5bd")
        rect(x + 10, yy, wf_w - 20, rh, bg="#fff5f5" if kind == "gap" else ("#fff4e6" if kind == "own" else "#f8f9fa"), stroke=stroke, dash=(kind == "gap"))
        text(x + 16, yy + 4, "\n".join(wrapped), size=10, color=GAP_C if kind == "gap" else "#1e1e1e")
        yy += rh + 4
    pos[k] = (x, y, wf_w, h)
    col_y[col] = y + h + 30
Y = max(col_y) + 20

# nav arrows between wireframes (side-to-side, best effort straight lines)
for a, b, label in NAV:
    ax, ay, aw, ah = pos[a]; bx, by, bw, bh = pos[b]
    gap = label.startswith("(gap)")
    arrow(ax + aw, ay + 20, bx, by + 20, color=GAP_C if gap else "#868e96", dash=gap, label=label)

# ---- journeys
text(X0, Y, "3 · Journeys — screen → command chains (ux.md §2)", size=18, bold=True); Y += 34
for name, p, steps in JOURNEYS:
    c = PERSONA[p][0]
    chip(X0, Y + 6, p, c); text(X0 + 26, Y + 4, name, size=13, bold=True, color=c)
    Y += 30
    x = X0
    for i, (k, action) in enumerate(steps):
        title = SCREENS[k][1].split(" · ")[0]
        label = f"{title}\n{action}"
        w, h = tsize(label, 11); w += 20; h += 12
        rect(x, Y, w, h, bg="#ffffff", stroke=c)
        text(x + 10, Y + 6, label, size=11)
        if i < len(steps) - 1:
            arrow(x + w, Y + h / 2, x + w + 30, Y + h / 2, color=c)
        x += w + 30
    Y += 60

text(X0, Y + 10, "not built yet: dashboard · reports · search · quick panel · availability row · cancel booking · change nights · move line · print · company routing · profile/rules — see ux.md §6", size=11, color=GAP_C)

out = {"type": "excalidraw", "version": 2, "source": "gen-solex-ux.py", "elements": els,
       "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None}, "files": {}}
with open("solex-ux.excalidraw", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print(len(els), "elements")
