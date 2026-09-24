#!/usr/bin/env python3
"""ezFolio look-alike flow for SoLex — demo mockups (no build). Run from this dir: python3 gen.py
Writes ezfolio.css + index.html + one page per screen. Sample data is invented; no guest PII.
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
TABS = [("Lễ tân", "shell.html", True), ("Buồng", "room-map.html#buong", False),
        ("Báo cáo", "index.html#later", False), ("Hệ thống", "index.html#later", False)]

def topbar(active="Lễ tân"):
    t = ''.join(f'<a href="{h}" class="{"on" if n == active else ""}">{n}</a>' for n, h, _ in TABS)
    return (f'<div class="topbar"><span class="hotel">⌂ SOLEX HOTEL</span>{t}'
            f'<span class="right"><span>In</span><span>Linh · lễ tân</span><span>⏻</span></span></div>')

RIBBON_BIG = [("▦", "Sơ đồ", "room-map.html"), ("▤", "Tình hình", "index.html#todo"),
              ("👤", "Khách lẻ", "index.html#todo"), ("👥", "Khách đoàn", "index.html#todo"),
              ("⇲", "Khách sẽ đến", "index.html#todo"), ("⇱", "Khách sẽ đi", "index.html#todo"),
              ("⇄", "Đổi phòng", "index.html#todo"), ("🔍", "Tìm kiếm", "index.html#todo")]
RIBBON_GRPS = [
    ("Dịch vụ", [("Giặt là", "", False), ("Minibar", "", False), ("Nhà hàng", "", True)]),
    ("Thống kê", [("Đến trong ngày", "index.html#todo", False), ("Đi trong ngày", "index.html#todo", False), ("Tổng hợp đặt phòng", "", True)]),
    ("Danh sách", [("Khách đang lưu trú", "index.html#todo", False), ("Hủy đặt phòng", "index.html#todo", False), ("Đ.phòng chưa gán", "index.html#todo", False)]),
    ("PA18", [("Kết xuất PA18", "", True), ("Quản lý khách ở", "", True)]),
]

def ribbon(mark=False):
    big = ''.join(f'<a class="big" href="{h}"><i>{ic}</i>{n}</a>' for ic, n, h in RIBBON_BIG)
    grps = ''
    for cap, items in RIBBON_GRPS:
        rows = ''.join(f'<a href="{h or "#"}" class="{"x" if x else ""}">{n}</a>' for n, h, x in items)
        grps += f'<div class="grp">{rows}<span class="cap">{cap}</span></div>'
    return f'<div class="ribbon">{big}{grps}</div><div class="logo">ez<b>FOLIO</b></div>'

def page(title, sub, body, notes, cant, links, crumb="index.html"):
    return f"""<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><link rel="stylesheet" href="ezfolio.css">
<div class="wrap">
<div class="crumb"><a href="{crumb}">← Mục lục</a></div>
<h1>{title}</h1><p class="sub">{sub}</p>
{body}
<div class="notes">{notes}</div>
<div class="cant"><b>Không sao chép được:</b>{cant}</div>
<div class="foot">{links}</div>
</div></html>"""

# ---------------------------------------------------------------- 1. shell
SHELL_BODY = f"""
<div class="ez">
  <div data-n="1">{topbar()}</div>
  <div data-n="2">{ribbon()}</div>
  <div class="page" style="min-height:120px;color:var(--muted);font-size:13px">
    Nội dung màn hình (Sơ đồ, Tình hình, danh sách …) hiện ở đây. Tab và ribbon giữ nguyên ở mọi màn hình.
  </div>
</div>
<div class="legend"><span class="n">n</span>ghi chú bên dưới · <span class="tag same">giữ</span> như ezFolio, chạy trên lệnh/đọc của SoLex · <span class="tag later">sau</span> có trong SoLex nhưng chưa ở bản demo · <span class="tag drop">bỏ</span> không có (gạch ngang trên ribbon)</div>
"""

SHELL_NOTES = """
<div><h3><span class="n">1</span>Thanh tab trên cùng</h3>
<p>Giữ 4 tab ezFolio: <b>Lễ tân · Buồng · Báo cáo · Hệ thống</b>. Bỏ <b>Kinh doanh</b> (chỉ có Công ty → nằm ở Lễ tân › Danh sách), <b>Nhà hàng</b> (POS không dùng; vẫn có dòng "nhà hàng" trên hoá đơn), <b>Kiểm toán</b> (không có night audit: ngày khách sạn tự lật lúc giờ đã đặt trong Thiết lập).</p>
<table class="map"><tr><th>tab</th><th>maps to</th><th></th></tr>
<tr><td>Lễ tân</td><td>ribbon dưới: Sơ đồ · Tình hình · đặt phòng · danh sách</td><td><span class="tag same">giữ</span></td></tr>
<tr><td>Buồng</td><td>cùng Sơ đồ, lọc sẵn BẨN; nút Sạch/Bẩn → <code>SetHousekeeping</code>; Phòng sửa → <code>TakeOutOfOrder</code>/<code>ReturnToService</code></td><td><span class="tag same">giữ</span></td></tr>
<tr><td>Báo cáo</td><td>bảng chủ (doanh thu, công suất, công nợ) — đọc từ projection, chỉ chủ thấy</td><td><span class="tag later">sau</span></td></tr>
<tr><td>Hệ thống</td><td>Thiết lập (phòng, loại phòng, khoản mục, giờ lật ngày) + Tài khoản</td><td><span class="tag later">sau</span></td></tr>
</table></div>
<div><h3><span class="n">2</span>Ribbon Lễ tân</h3>
<table class="map"><tr><th>nút</th><th>maps to</th><th></th></tr>
<tr><td>Sơ đồ</td><td>đọc <code>RoomBoard</code> → màn 2</td><td><span class="tag same">giữ</span></td></tr>
<tr><td>Tình hình</td><td>đọc <code>Calendar</code> (tape chart) → màn 5</td><td><span class="tag same">giữ</span></td></tr>
<tr><td>Khách lẻ</td><td><code>CreateBooking{kind:'individual'}</code> rồi <code>CheckIn</code> — ezFolio vào thẳng folio đã CHECKIN; SoLex 2 bước trên cùng một form (đặt → nhận phòng), vì nhận phòng là sự kiện có quy tắc (phòng tối nay phải sẵn sàng)</td><td><span class="tag same">giữ</span></td></tr>
<tr><td>Khách đoàn</td><td><code>CreateBooking{kind:'group', requests[]}</code> — cùng form: công ty · nguồn · ngày · số phòng theo loại; phòng gán sau</td><td><span class="tag same">giữ</span></td></tr>
<tr><td>Khách sẽ đến / sẽ đi · Đến/Đi trong ngày · Khách đang lưu trú · Hủy đặt phòng · Đ.phòng chưa gán</td><td>một màn danh sách, tab <code>status=</code> → màn 4 (đọc <code>StayList</code>)</td><td><span class="tag same">giữ</span></td></tr>
<tr><td>Đổi phòng</td><td><code>MoveStay</code> — từ hoá đơn/lượt ở (màn 3), không có màn riêng</td><td><span class="tag same">giữ</span></td></tr>
<tr><td>Tìm kiếm</td><td>tìm theo tên · SĐT · mã đặt phòng → màn 4</td><td><span class="tag same">giữ</span></td></tr>
<tr><td>Giặt là · Minibar (sổ đăng ký)</td><td>đọc các dòng hoá đơn theo khoản mục; ghi nhận vẫn từ ô phòng (màn 2)</td><td><span class="tag later">sau</span></td></tr>
<tr><td>Tổng hợp đặt phòng</td><td>Báo cáo (chủ)</td><td><span class="tag later">sau</span></td></tr>
<tr><td>Nhà hàng · PA18 · Quản lý khách ở</td><td>ngoài phạm vi v1 (PA18: product.md §8)</td><td><span class="tag drop">bỏ</span></td></tr>
</table></div>
"""
SHELL_CANT = " Kinh doanh, Nhà hàng, Kiểm toán, thẻ từ (ĐỌC/XÓA THẺ): ngoài phạm vi. Tab ribbon là vỏ; mọi nút bên trong chạy trên lệnh/đọc đã có, giao diện không giữ quy tắc nào."
SHELL_LINKS = '<a href="room-map.html">Tiếp: 2 · Sơ đồ →</a>'

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
ST = [("all","TẤT CẢ"),("ready","SẴN SÀNG"),("arr","DỰ KIẾN ĐẾN"),("in","ĐANG Ở"),("dep","DỰ KIẾN ĐI"),
      ("occdirty","CÓ KHÁCH BẨN"),("vacdirty","TRỐNG BẨN"),("ooo","PHÒNG SỬA")]
cnt = {k: sum(1 for r in ROOMS if r[2] == k) for k, _ in ST}
cnt["all"] = len(ROOMS)
# ezFolio's ĐANG Ở count includes departing/occupied-dirty rooms (all in-house); keep that reading
cnt_in_display = cnt["in"] + cnt["dep"] + cnt["occdirty"]

def stbar():
    b = ''.join(f'<a class="st {k}" href="#">{n}({cnt_in_display if k=="in" else cnt[k]})</a>' for k, n in ST)
    return (f'<div class="stbar" data-n="1"><span class="date">24/09/2026</span>{b}'
            f'<span class="tools">FILTER · ▦ · 🖶 <span class="st key1" style="text-decoration:line-through">ĐỌC THẺ</span>'
            f'<span class="st key2" style="text-decoration:line-through">XÓA THẺ</span></span></div>')

def tiles():
    out, floor = '', None
    for num, code, st in ROOMS:
        f = num[0]
        if f != floor:
            if floor is not None: out += '</div>'
            out += f'<div class="floor">Tầng {f}</div><div class="tiles">'
            floor = f
        sel = ' sel' if num == "110" else ''
        out += f'<a class="tile {st}{sel}" href="#chi-tiet" title="{code}"><small>{code}</small><b>{num}</b></a>'
    return out + '</div>'

MODAL = """
<div class="modal" id="chi-tiet">
  <div class="mh">Chi tiết <span class="act">⎘ ĐẶT PHÒNG</span><span class="x">✕</span></div>
  <div class="mtabs" data-n="3"><span class="on">CHECKIN ROOM</span><span style="text-decoration:line-through;color:var(--muted)">ADVANCE POST ROOM CHARGE</span></div>
  <div class="mbody">
    <div class="card" data-n="4"><a class="lk" href="index.html#todo">🔍 XEM CHI TIẾT</a>
      <div class="kv"><span>Phòng</span><span>110</span></div>
      <div class="kv"><span>Giá</span><span>1,100,000</span></div>
      <div class="kv"><span>Ngày đến</span><span>18/09/2026 20:11</span></div>
      <div class="kv"><span>Ngày đi</span><span>28/09/2026 12:00</span></div>
      <div class="kv"><span>Đêm</span><span>10</span></div>
      <div class="kv"><span>Trạng thái</span><span>CHECKIN</span></div>
    </div>
    <div class="card">
      <div class="lab">Tên khách</div><div class="val">NGUYỄN VĂN A 0903 xxx xxx</div>
      <div class="lab">Công ty</div><div class="val">—</div>
      <div class="lab">Ghi chú <span style="float:right;color:#c00">🖫</span></div>
      <textarea>20h in</textarea>
    </div>
  </div>
  <div class="bal">Còn lại: 350,000 ⎆</div>
  <div class="mfoot" data-n="5"><span>DIRTY</span><span>MINIBAR</span><span>LAUNDRY</span><span>COMPENSATION</span><span>EXTRA SERVICE</span></div>
</div>
"""

MAP_BODY = f"""
<div class="ez">
  {topbar()}{ribbon()}
  <div class="page" id="buong">
    {stbar()}
    <div data-n="2">{tiles()}</div>
  </div>
  <div class="arrowline">▼ bấm ô <b>110</b> → hộp "Chi tiết" (mở đè lên sơ đồ, vẽ tách ra đây để đọc)</div>
  <div class="fade">{MODAL}</div>
</div>
<div class="legend"><span class="n">n</span>ghi chú bên dưới · gạch ngang = bỏ · màu ô = trạng thái, đúng bảng màu ezFolio · số liệu mẫu, không phải khách thật</div>
"""

MAP_NOTES = f"""
<div><h3><span class="n">1</span>Nút trạng thái có số đếm</h3>
<p>Cùng 8 nút, cùng màu, cùng thứ tự. Số đếm và màu ô đều <b>suy ra</b> từ phòng (sạch/bẩn, ngừng SD) + các đêm của lượt ở — không lưu trạng thái riêng (product.md §6 Room: "derived, never stored"). Bấm nút = lọc ô.</p>
<table class="map"><tr><th>nút</th><th>maps to (đọc <code>RoomBoard</code>)</th></tr>
<tr><td>TẤT CẢ</td><td>mọi phòng đang định nghĩa</td></tr>
<tr><td>SẴN SÀNG</td><td>trống · sạch · không ai đến hôm nay</td></tr>
<tr><td>DỰ KIẾN ĐẾN</td><td>lượt ở <i>booked</i> có đêm nay, phòng đã gán</td></tr>
<tr><td>ĐANG Ở</td><td>lượt ở <i>checkedIn</i> tối nay (gồm cả sắp đi / có khách bẩn, như ezFolio đếm)</td></tr>
<tr><td>DỰ KIẾN ĐI</td><td>checkedIn, đêm cuối là hôm qua</td></tr>
<tr><td>CÓ KHÁCH BẨN / TRỐNG BẨN</td><td>housekeeping = dirty, có / không có khách</td></tr>
<tr><td>PHÒNG SỬA</td><td><code>room.outOfOrder</code></td></tr>
<tr><td>Ngày 24/09</td><td>chỉ hiển thị; không đổi được (xem "không sao chép")</td></tr>
</table></div>
<div><h3><span class="n">2</span>Ô phòng</h3>
<p>Mã loại / giường trên, số phòng dưới, màu = trạng thái. Xếp theo tầng. Bấm ô → hộp <b>Chi tiết</b>. Tam giác góc ô của ezFolio (thẻ từ / ghi chú) không vẽ.</p>
<h3><span class="n">3</span>Đầu hộp Chi tiết</h3>
<table class="map"><tr><th>nút</th><th>maps to</th><th></th></tr>
<tr><td>ĐẶT PHÒNG</td><td><code>CreateBooking{{kind:'individual', room:110}}</code> — form đặt phòng, phòng điền sẵn</td><td><span class="tag same">giữ</span></td></tr>
<tr><td>CHECKIN ROOM</td><td><code>CheckIn{{stayId}}</code> (phòng tối nay phải sẵn sàng; đến sớm → cộng đêm nay, cảnh báo)</td><td><span class="tag same">giữ</span></td></tr>
<tr><td>ADVANCE POST ROOM CHARGE</td><td>không có: tiền phòng do hệ thống ghi lúc nhận phòng và lúc lật ngày; khoản mục <i>room</i> bị khoá với mọi người</td><td><span class="tag drop">bỏ</span></td></tr>
</table>
<h3><span class="n">4</span>Thân hộp</h3>
<table class="map"><tr><th>ô</th><th>maps to</th></tr>
<tr><td>Phòng · Giá · Ngày đến/đi · Đêm · Trạng thái · Tên khách · Công ty</td><td>đọc lượt ở tối nay của phòng (<code>Stay</code> + <code>Booking.party</code>); Giá = giá đêm nay</td></tr>
<tr><td>Ghi chú + 🖫</td><td><code>SetRoomNote</code> (ghi chú của phòng; ghi chú đặt phòng ở màn 3)</td></tr>
<tr><td>Còn lại</td><td>đọc số dư folio (tổng − cọc − đã trả); ⎆ → màn 3 (hoá đơn)</td></tr>
<tr><td>XEM CHI TIẾT</td><td>→ màn 3 (booking editor / lượt ở)</td></tr>
</table>
<h3><span class="n">5</span>Nút nhanh</h3>
<table class="map"><tr><th>nút</th><th>maps to</th></tr>
<tr><td>DIRTY</td><td><code>SetHousekeeping{{dirty}}</code> (Buồng: cùng nút, thêm CLEAN)</td></tr>
<tr><td>MINIBAR · LAUNDRY · COMPENSATION · EXTRA SERVICE</td><td><code>PostCharge</code> với khoản mục chọn sẵn; danh sách nút = các khoản mục trong Thiết lập (tên/giá của khách sạn), nên COMPENSATION = "Đền bù" nếu họ đặt vậy. Mỗi nút mở một dòng: món · SL · đơn giá → ghi vào hoá đơn theo định tuyến (đoàn: HĐ khách hay HĐ đoàn)</td></tr>
</table></div>
"""
MAP_CANT = " ĐỌC/XÓA THẺ (thẻ từ ngoài phạm vi, vĩnh viễn) · chọn ngày trên sơ đồ (sơ đồ = bây giờ; theo ngày là Tình hình, product.md §4) · ADVANCE POST ROOM CHARGE (tiền phòng là khoản mục hệ thống, §6) · Giá không sửa tại chỗ (đổi giá đêm = <code>SetNightRate</code> có lý do, màn 3)."
MAP_LINKS = '<a href="shell.html">← 1 · Khung</a><a href="index.html#todo">Tiếp: 3 · Booking editor (chưa vẽ) →</a>'

# ---------------------------------------------------------------- index
INDEX = f"""<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SoLex ezFolio Flow</title><link rel="stylesheet" href="ezfolio.css">
<div class="wrap">
<h1>SoLex — luồng "giống ezFolio"</h1>
<p class="sub">Mockup cho buổi demo: màn hình lễ tân hằng ngày, <b>đúng hình dạng ezFolio</b>, chạy trên lệnh/đọc đã có của SoLex (giao diện không giữ quy tắc nào). Để so "như cũ" với luồng SoLex (<code>ux.md</code>). Không phải bản dựng. Số liệu mẫu, không có khách thật.</p>
<div class="idx">
  <a href="shell.html"><b>1 · Khung</b><small>tab trên + ribbon Lễ tân; nút nào giữ / sau / bỏ</small></a>
  <a href="room-map.html"><b>2 · Sơ đồ + Chi tiết</b><small>nút trạng thái có số đếm, ô phòng, hộp Chi tiết với Còn lại + nút nhanh</small></a>
  <a class="todo" id="todo" href="#todo"><b>3 · Booking editor</b><small>3 khung khách · đặt phòng · tiền; tab; Thao tác; Show log; Fast checkout → quickout — chờ duyệt 1+2</small></a>
  <a class="todo" href="#todo"><b>4 · Danh sách theo trạng thái</b><small>tab status=, lẻ/đoàn, thứ tự cột ezFolio — chờ</small></a>
  <a class="todo" href="#todo"><b>5 · Tình hình (tape chart)</b><small>phòng theo loại, dòng dùng/trống/% — chờ</small></a>
</div>
<div class="legend" id="later"><span class="tag same">giữ</span> như ezFolio, trên lệnh/đọc SoLex · <span class="tag later">sau</span> có trong SoLex, không ở demo · <span class="tag drop">bỏ</span> ngoài phạm vi (thẻ từ, thẻ tín dụng, giảm giá/FOC/thuế, nhà hàng, night audit)</div>
<p class="sub" style="margin-top:16px">Mỗi màn: mockup trước, ghi chú dưới (≤5), mỗi nút một dòng "maps to", một dòng "không sao chép được" và vì sao. Vẽ theo <code>screens/fd-*.png</code> (không commit) + <code>existing-system.md</code>; quy tắc theo <code>product.md</code>. Sinh bởi <code>gen.py</code> — không sửa tay HTML.</p>
</div></html>"""

(OUT / "ezfolio.css").write_text(CSS.strip() + "\n")
(OUT / "index.html").write_text(INDEX)
(OUT / "shell.html").write_text(page("1 · Khung — tab + ribbon Lễ tân",
    "Vỏ chung của mọi màn. Rendered as: Linh (lễ tân). Tham chiếu: đầu trang <code>fd-room-map.png</code>.",
    SHELL_BODY, SHELL_NOTES, SHELL_CANT, SHELL_LINKS))
(OUT / "room-map.html").write_text(page("2 · Sơ đồ + hộp Chi tiết",
    "Màn hình mặc định của lễ tân. Rendered as: Linh. Tham chiếu: <code>fd-room-map.png</code>, <code>fd-room-detail-panel.png</code>.",
    MAP_BODY, MAP_NOTES, MAP_CANT, MAP_LINKS))
print("ok", cnt, "in-display", cnt_in_display)
