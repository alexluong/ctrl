import { connect, url, redact } from './lib.mjs';
const { b, p } = await connect();
await p.goto(await url('page=reservation&status=INHOUSE'), { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(2500);
const d = await p.evaluate(() => {
  const btn = document.querySelector('[id=btnExport],[name=btnExport]');
  const out = { attrs: {}, listeners: null };
  for (const a of btn.attributes) out.attrs[a.name] = a.value.slice(0, 120);
  // find jQuery-bound handlers if jQuery present
  try {
    const $ = window.jQuery;
    if ($) { const ev = $._data ? $._data(btn, 'events') : null;
      out.listeners = ev ? Object.keys(ev).map(k => ev[k].map(h => String(h.handler).slice(0, 700)).join('\n')).join('\n') : 'none'; }
  } catch (e) { out.listeners = 'err ' + e.message; }
  return out;
});
console.log(redact(JSON.stringify(d, null, 1)).slice(0, 2500));
await b.close().catch(()=>{});
