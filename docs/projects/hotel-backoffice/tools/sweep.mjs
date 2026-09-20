import { connect, url, redact, SHOTS } from './lib.mjs';
import path from 'path';
const targets = JSON.parse(process.argv[2]);
const { b, p } = await connect();
for (const [slug, q] of targets) {
  try {
    await p.goto(await url(q), { waitUntil: 'domcontentloaded' });
    await p.waitForTimeout(2500);
    await p.screenshot({ path: path.join(SHOTS, slug + '.png'), fullPage: true });
    const d = await p.evaluate(() => {
      const t = e => (e.innerText || '').replace(/\s+/g, ' ').trim();
      const heads = [...document.querySelectorAll('h1,h2,h3,legend,caption')].map(t).filter(Boolean).slice(0, 6);
      const tabs = [...document.querySelectorAll('table')].map(tb => {
        const r = [...tb.querySelectorAll('tr')];
        const hdr = r.slice(0, 2).map(x => [...x.children].map(t).filter(Boolean).join(' | ')).filter(h => h.length > 25)[0];
        return hdr ? hdr.slice(0, 260) + `  [${r.length} rows]` : null;
      }).filter(Boolean).slice(0, 4);
      const ctl = [...document.querySelectorAll('input,select,button')]
        .filter(e => !/sub_menu/.test(e.name || ''))
        .map(e => (e.name || e.id || '') + ':' + (e.type || '') + (e.value && e.type !== 'text' ? '=' + String(e.value).slice(0, 18) : ''))
        .filter(x => x !== ':').slice(0, 26);
      return { heads, tabs, ctl };
    });
    console.log(redact(`\n### ${slug}\nH: ${d.heads.join(' / ')}\nT: ${d.tabs.join('\n   ')}\nC: ${d.ctl.join(' ')}`));
  } catch (e) { console.log(`\n### ${slug}\nERR ${redact(String(e).slice(0, 120))}`); }
}
await b.close().catch(() => {});
