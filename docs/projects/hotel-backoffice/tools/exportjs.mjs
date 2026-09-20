import { connect, url, redact } from './lib.mjs';
const { b, p } = await connect();
await p.goto(await url('page=reservation&status=INHOUSE'), { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(2500);
const d = await p.evaluate(() => {
  const btn = document.querySelector('[id=btnExport],[name=btnExport]');
  const fn = window.ExportToExcel || window.exportToExcel || window.export_excel;
  const ids = [...document.querySelectorAll('table[id]')].map(t => t.id + ':' + t.querySelectorAll('tr').length);
  return { onclick: btn ? btn.getAttribute('onclick') : null, fnsrc: fn ? String(fn).slice(0, 900) : null, ids };
});
console.log(redact(JSON.stringify(d, null, 1)).slice(0, 2000));
await b.close().catch(()=>{});
