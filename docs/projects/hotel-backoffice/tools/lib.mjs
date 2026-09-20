import { chromium } from 'playwright-core';
import fs from 'fs';
import path from 'path';

const raw = fs.readFileSync(process.env.HOME + '/git/hub/alexluong/ctrl/secrets/hotel-backoffice.md', 'utf8');
const get = k => (raw.match(new RegExp('^- ' + k + ':\\s*(.+)$', 'm'))?.[1] || '').replace(/[`<>]/g, '').trim();
export const sec = { pub: get('Public'), lan: get('LAN'), user: get('User'), pass: get('Pass') };
export const SHOTS = path.join(import.meta.dirname, '..', 'screens');

const hosts = [sec.pub, sec.lan].filter(Boolean).map(u => { try { return new URL(u).host; } catch { return u; } });
export const redact = s => [sec.pass, sec.user, sec.pub, sec.lan, ...hosts]
  .filter(Boolean).sort((a, b) => b.length - a.length)
  .reduce((a, v) => a.split(v).join('<redacted>'), String(s));
export const log = (...a) => console.log(redact(a.join(' ')));

// read-only guard: nothing but GET/HEAD ever leaves the browser
export async function connect() {
  const b = await chromium.connectOverCDP('http://localhost:9334');
  const ctx = b.contexts()[0];
  await ctx.route('**/*', r => {
    const m = r.request().method();
    if (m === 'GET' || m === 'HEAD') return r.continue();
    if (process.env.ALLOW_POST === '1') return r.continue();
    // some read-only screens fetch their data via POST (json=1). Allow those,
    // but never anything that looks like a write.
    const u = r.request().url(), body = r.request().postData() || '';
    const writeish = /(cmd=(add|save|edit|update|delete|del|cancel|insert|remove|checkin|checkout|post|confirm|merge|audit)|action=(save|delete|update))/i;
    const readish = /[?&](json=1|(list|get|load|view|search|check)_[a-z_]+=)/i;
    if (readish.test(u) && !writeish.test(u) && !writeish.test(body)) {
      console.error('[allowed read-POST]', redact(u), redact(body).slice(0, 200));
      return r.continue();
    }
    console.error('[BLOCKED non-GET]', m, redact(r.request().url()));
    return r.abort();
  });
  const p = ctx.pages()[0] || await ctx.newPage();
  return { b, p };
}

export async function url(q) { return sec.pub.replace(/\/$/, '') + '/' + (q.startsWith('?') ? q : '?' + q); }

export async function describe(p, slug) {
  if (slug) { fs.mkdirSync(SHOTS, { recursive: true }); await p.screenshot({ path: path.join(SHOTS, slug + '.png'), fullPage: true }); }
  const d = await p.evaluate(() => {
    const t = e => (e.innerText || '').replace(/\s+/g, ' ').trim();
    return {
      title: document.title,
      path: location.pathname + location.search,
      headings: [...document.querySelectorAll('h1,h2,h3,legend,caption,.title,.panel-title')].map(t).filter(Boolean).slice(0, 25),
      tables: [...document.querySelectorAll('table')].slice(0, 8).map(tb => ({
        headers: [...tb.querySelectorAll('tr')].slice(0, 3).map(r => [...r.children].map(c => t(c)).filter(Boolean).join(' | ')).filter(Boolean).slice(0, 3),
        rows: tb.querySelectorAll('tr').length,
      })).filter(x => x.headers.length),
      controls: [...document.querySelectorAll('input,select,textarea,button')].slice(0, 80)
        .map(e => [e.tagName.toLowerCase(), e.type || '', e.name || e.id || '', (e.placeholder || e.value || t(e) || '').slice(0, 28)].join('|')),
      text: (document.body.innerText || '').replace(/\n{3,}/g, '\n\n').slice(0, 4000),
    };
  });
  log(JSON.stringify(d, null, 1));
  return d;
}
