import { connect, url, log, SHOTS } from './lib.mjs';
import path from 'path';
const { b, p } = await connect();
await p.goto(await url('page=reservation&cmd=check_availability&arrival_time=21/09/2026&departure_time=28/09/2026&night=7'), { waitUntil:'domcontentloaded' });
await p.waitForTimeout(3000);
await p.screenshot({ path: path.join(SHOTS,'fd-group-availability.png'), fullPage:true });
const d = await p.evaluate(() => {
  const txt = e => (e.innerText||'').replace(/\s+/g,' ').trim();
  const opts = n => [...(document.querySelector(`[name="${n}"]`)?.options||[])].map(o=>`${o.value}=${o.text}`.slice(0,40));
  // availability cell markup (is the paren a tooltip?)
  const cells = [...document.querySelectorAll('.check-availability-day')].slice(0,14)
    .map(e=>({t:txt(e), title:e.title||e.getAttribute('data-original-title')||'', cls:e.className, style:(e.getAttribute('style')||'').slice(0,60)}));
  // room-type rows: label + the per-type input group
  const types = [...document.querySelectorAll('input[name^=room_quantity_]')].map(e=>{
    const suffix = e.name.replace('room_quantity_','');
    const row = e.closest('tr');
    return { key:suffix, rowLabel: row? txt(row).slice(0,60):'' };
  });
  return {
    book: (()=>{const el=document.querySelector('#book,[name=book]'); return el?{tag:el.tagName,type:el.type,name:el.name,value:el.value}:null;})(),
    formAction: document.forms.CheckAvailabilityForm?.action,
    hidden: [...document.querySelectorAll('input[type=hidden]')].map(e=>`${e.name}=${(e.value||'').slice(0,30)}`).slice(0,40),
    block_id: opts('block_id'), source: opts('reservation_type_id'), pttt: opts('pttt'), saler: opts('list_saler_id').slice(0,12),
    cells, types,
  };
});
log(JSON.stringify(d,null,1));
await b.close().catch(()=>{});
