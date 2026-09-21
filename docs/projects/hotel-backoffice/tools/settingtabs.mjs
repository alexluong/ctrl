import { connect, url, log, SHOTS } from './lib.mjs';
import path from 'path';
const { b, p } = await connect();
await p.goto(await url('page=setting'), { waitUntil:'domcontentloaded' });
await p.waitForTimeout(2500);
const tabs = await p.evaluate(() => [...document.querySelectorAll('.nav-tabs a,[data-toggle=tab],ul.tabs a')].map((a,i)=>({i, t:a.innerText.trim(), href:a.getAttribute('href')})).filter(x=>x.t));
log('TABS ' + JSON.stringify(tabs.map(t=>t.t)));
for (const tb of tabs) {
  if (!/thuế|dịch vụ|lễ tân|phần mềm/i.test(tb.t)) continue;
  await p.evaluate(sel => { const a=[...document.querySelectorAll('.nav-tabs a,[data-toggle=tab]')].find(x=>x.getAttribute('href')===sel); if(a) a.click(); }, tb.href);
  await p.waitForTimeout(900);
  const d = await p.evaluate(sel => {
    const pane = document.querySelector(sel);
    if (!pane) return null;
    const txt = e => (e.innerText||'').replace(/\s+/g,' ').trim();
    return { label: txt(pane).slice(0,900),
             fields: [...pane.querySelectorAll('input,select')].filter(e=>e.type!=='hidden')
               .map(e=>`${e.name||e.id}=${String(e.value||'').slice(0,18)}`).slice(0,30) };
  }, tb.href);
  log('\n--- ' + tb.t + ' ---\n' + JSON.stringify(d, null, 1).slice(0,1600));
}
await p.screenshot({ path: path.join(SHOTS,'sys-settings.png'), fullPage:true });
await b.close().catch(()=>{});
