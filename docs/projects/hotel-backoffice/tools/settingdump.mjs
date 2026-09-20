import { connect, url, redact } from './lib.mjs';
const { b, p } = await connect();
await p.goto(await url('page=setting'), { waitUntil: 'domcontentloaded' });
await p.waitForTimeout(3000);
const d = await p.evaluate(() => {
  const secs = [...document.querySelectorAll('legend,h1,h2,h3,fieldset')].map(e => (e.innerText||'').replace(/\s+/g,' ').trim()).filter(Boolean);
  const labeled = [...document.querySelectorAll('input,select,textarea')].map(e => {
    const row = e.closest('tr,div');
    const lbl = row ? (row.innerText||'').replace(/\s+/g,' ').trim().slice(0,70) : '';
    return [e.name||e.id||'', (e.type||e.tagName), (e.value||'').slice(0,40), lbl].join(' :: ');
  });
  return { secs: secs.slice(0,20), labeled: labeled.slice(0, 140) };
});
console.log(redact(d.labeled.filter(l=>/ezcms|vat|invoice|policy|gia|price|commission|hoa hong|mail|api|url|port|token|key/i.test(l)).join('\n')));
console.log('--- SECTIONS ---'); console.log(redact(d.secs.join(' | ').slice(0,1500)));
await b.close().catch(()=>{});
