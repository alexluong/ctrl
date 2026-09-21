import { connect, url, log } from './lib.mjs';
const { b, p } = await connect();
for (const q of ['extra_service_invoice','minibar_invoice','laundry_invoice','equipment_invoice']) {
  await p.goto(await url('page=' + q), { waitUntil:'domcontentloaded' });
  await p.waitForTimeout(2200);
  const d = await p.evaluate(() => {
    const skip = e => e.closest('script,style,#ribbon,.ribbon,#menu,.menu');
    const sels = [...document.querySelectorAll('select')].filter(e=>!skip(e)).map(e=>({
      n: e.name||e.id, count: e.options.length,
      opts: [...e.options].map(o=>o.text.replace(/\s+/g,' ').trim()).filter(Boolean).slice(0,40)
    })).filter(s=>s.count>1);
    const heads = [...document.querySelectorAll('h1,h2,h3,.title')].filter(e=>!skip(e)).map(e=>e.innerText.trim()).filter(Boolean).slice(0,3);
    const cols = [...document.querySelectorAll('table thead tr, table tr:first-child')].slice(0,2)
      .map(r=>[...r.children].map(c=>c.innerText.replace(/\s+/g,' ').trim()).filter(Boolean).join(' | ')).filter(Boolean);
    return { heads, cols, sels };
  });
  log('\n===== ' + q + ' =====\n' + JSON.stringify(d, null, 1));
}
await b.close().catch(()=>{});
