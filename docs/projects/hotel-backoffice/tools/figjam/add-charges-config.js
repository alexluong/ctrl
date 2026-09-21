
const setText = async (n, chars) => {
  const t = 'characters' in n ? n : n.text;
  for (const s of t.getStyledTextSegments(['fontName'])) await figma.loadFontAsync(s.fontName);
  t.characters = chars;
};
await figma.loadFontAsync({ family: 'Inter', style: 'Semi Bold' });
await figma.loadFontAsync({ family: 'Inter', style: 'Regular' });
const mkText = (chars, size, style) => {
  const t = figma.createText();
  t.fontName = { family: 'Inter', style }; t.fontSize = size; t.characters = chars;
  t.name = chars.slice(0, 60); return t;
};

const W = 520, GAP = 80, PAD = 60, TOP = 96;
const created = [];

// build a section: frames [{name,h,cap}], optional trailing text panel {chars,w}
function build(title, frames, panel) {
  const sec = figma.createSection(); sec.name = title;
  figma.currentPage.appendChild(sec);
  const t = mkText(title, 26, 'Semi Bold'); sec.appendChild(t); t.x = PAD; t.y = 30;
  let x = PAD, rowMax = 0; const ids = {};
  for (const f of frames) {
    const fr = figma.createFrame(); fr.name = f.name; sec.appendChild(fr);
    fr.resizeWithoutConstraints(W, f.h); fr.x = x; fr.y = TOP;
    const c = mkText(f.cap, 15, 'Regular'); sec.appendChild(c);
    c.resizeWithoutConstraints(W, c.height); c.x = x; c.y = TOP + f.h + 16;
    ids[f.name] = fr.id; created.push(fr.id, c.id);
    rowMax = Math.max(rowMax, f.h + 16 + c.height);
    x += W + GAP;
  }
  if (panel) {
    const p = mkText(panel, 15, 'Regular'); sec.appendChild(p);
    p.resizeWithoutConstraints(panel.w || 600, p.height); p.x = x; p.y = TOP;
    created.push(p.id);
    rowMax = Math.max(rowMax, p.height); x += (panel.w || 600) + GAP;
  }
  sec.resizeWithoutConstraints(x - GAP + PAD, TOP + rowMax + 40);
  created.push(sec.id, t.id);
  return { sec, ids };
}

// ---- CHARGES ---------------------------------------------------------
const charges = build(
  'RECEPTIONIST · 3b · CHARGES — posted from the room tile, landing in one of eight fixed buckets',
  [
    { name: 'fd-room-detail-panel', h: 515, cap: 'a · Room tile modal — THE posting entry point. Footer: DIRTY · MINIBAR · LAUNDRY · COMPENSATION · EXTRA SERVICE. The invoice pages are registers; their “add” route is closed to reception.' },
    { name: 'fd-laundry-invoice',   h: 515, cap: 'b · Laundry register — itemised per garment (Quần Tây, Áo Sơ Mi, Vớ…) with quantities. Minibar works the same way, except each room has its OWN minibar (58 stock locations, not one product list).' },
    { name: 'rpt-fd-revenue',       h: 521, cap: 'c · Where every charge lands — eight fixed buckets: room · surcharge · minibar · laundry · damages · extended service · phone · restaurant, settled by cash / card / transfer / comp / debt.' },
  ],
  Object.assign(new String(
    'EXTENDED-SERVICE CATALOGUE, as it stands (19 items, 2 groups)\n\n' +
    'Duplicates:\n' +
    '• Card Fee  ↔  Phí thẻ\n' +
    '• Check out lately  ↔  Checkout Later\n' +
    '• Taxi  ↔  Transportation  ↔  Ô tô sân bay/Taxi airport\n\n' +
    'Meaningless names:\n' +
    '• “dịch vụ”  (= “service”)\n' +
    '• “Cái Mới”  (= “new thing”)\n\n' +
    'The rest: Check in early · Ăn Sáng · Business center · Air ticket · Restaurant · Refund · Room Charge · Cafe · phone deduction · Other\n\n' +
    'Early check-in / late check-out are charged from THIS list in practice — not via the multipliers on the booking form.\n\n' +
    '→ The argument for a curated catalogue.'), { w: 560 })
);

// ---- CONFIG ----------------------------------------------------------
const config = build(
  'ADMIN · CONFIG — split in two: item masters (locked) and charge behaviour (in Settings)',
  [
    { name: 'sys-charge-config', h: 327, cap: 'Settings › Thuế - Dịch vụ — per charge type: service charge %, tax %, net/gross. Every value is 0 and everything is net: they charge gross, no VAT line.' },
    { name: 'sys-booking-rules', h: 327, cap: 'Settings › Cấu hình đặt phòng — day boundary 23:59 · overbooking ON · under 6 = child · auto-count adults/children · auto-assign soonest room.' },
  ],
  Object.assign(new String(
    'ITEM MASTERS — exist, all permission-blocked for reception\n\n' +
    '• room\n• room_type\n• product\n• minibar · minibar_product\n• laundry\n• service · extra_service\n• category\n• package\n• currency\n• restaurant_product\n\n' +
    'This is where rooms, room prices, minibar items, laundry items and service items are maintained. ' +
    'Nobody doing the daily work can see it. Documenting the fields needs an admin login.\n\n' +
    'Settings has 26 tabs in total. Hourly/day-use pricing is configured there (1h 400k, 2h 500k) but NOT used — SoLex is daily only.'), { w: 560 })
);

// ---- restack: hub, 1, 2, 3, 3b charges, 4, 5, config -----------------
const order = ['12:77','1:38','1:39','1:40', charges.sec.id, '1:41','1:42', config.sec.id];
let y = 100, widest = 0;
for (const id of order) {
  const s = await figma.getNodeByIdAsync(id);
  s.x = 40; s.y = y; y += s.height + 60; widest = Math.max(widest, s.width);
}

// findings column clears the widest section
const colX = 40 + widest + 120;
(await figma.getNodeByIdAsync('2:74')).x = colX;
let sy = 100;
for (const st of figma.currentPage.findAll(n => n.type === 'STICKY').sort((a, b) => a.y - b.y)) {
  st.x = colX; st.y = sy; sy += 300;
}

// early/late sticky: reflect how it's actually charged
await setText(await figma.getNodeByIdAsync('11:75'),
  'Early check-in / late check-out are charged as catalogue items (extra services). The booking form also offers +0.3 / +0.5 / +1 rate multipliers — unused. Rebuild: one mechanism, the catalogue.');

return { created, frames: { ...charges.ids, ...config.ids }, bottomY: y, colX };
