import { connect, url, log, SHOTS } from './lib.mjs';
import path from 'path';
const [q, slug] = process.argv.slice(2);
const { b, p } = await connect();
await p.goto(await url(q), { waitUntil:'domcontentloaded' });
await p.waitForTimeout(3500);
if (slug) await p.screenshot({ path: path.join(SHOTS, slug + '.png'), fullPage:true });
const d = await p.evaluate(() => {
  const txt = e => (e.innerText||'').replace(/\s+/g,' ').trim();
  const skip = e => e.closest('script,style,#ribbon,.ribbon,#menu,.menu');
  const lab = e => {
    const l = e.closest('label') || document.querySelector(`label[for="${e.id}"]`);
    if (l) return txt(l).slice(0,30);
    const td = e.closest('td'); const prev = td && td.previousElementSibling;
    return prev ? txt(prev).slice(0,30) : '';
  };
  const fields = [...document.querySelectorAll('input,select,textarea')].filter(e=>!skip(e) && e.type!=='hidden')
    .map(e=>({ n: e.name||e.id, t: e.type||e.tagName.toLowerCase(), v: String(e.value||'').slice(0,26),
               lab: lab(e), opts: e.tagName==='SELECT' ? [...e.options].map(o=>o.text.trim()).filter(Boolean).slice(0,8) : undefined }))
    .filter(f=>f.n);
  const tabs = [...document.querySelectorAll('a[data-toggle=tab],.nav-tabs a,li.tab a')].map(txt).filter(Boolean);
  const btns = [...document.querySelectorAll('button,input[type=button],a.btn')].filter(e=>!skip(e))
    .map(e=>({l:txt(e).slice(0,28), id:e.id, o:(e.getAttribute('onclick')||'').slice(0,90)})).filter(x=>x.l||x.id).slice(0,30);
  return { loc: location.search, tabs, btns, fieldCount: fields.length, fields: fields.slice(0,80),
           panels: [...document.querySelectorAll('legend,.panel-title,.box-title,fieldset>div:first-child')].filter(e=>!skip(e)).map(txt).filter(Boolean).slice(0,20) };
});
log(JSON.stringify(d,null,1));
await b.close().catch(()=>{});
