# replay (candidate) — Playwright journeys → seekable HTML replay

Status: **evaluating** (2026-09-25) as a possible product or OSS project. No repo yet.
Origin: built inside SoLex ([hotel-backoffice](hotel-backoffice/README.md)) by solex-qa in ~1h, because Alex wanted a seekable HTML "session replay as demo" instead of screen recordings.
Source: `alexluong/solex` @ a204175 (commits 84bd446, d290e53), `e2e/journeys/`. Briefed by solex-architect + solex-qa.

## What exists (SoLex prototype)

- `pnpm journeys` = `playwright test -c journeys.config.ts`: its own port (PORT_BASE+2) and its own DB (`data/journeys.db`, rebuilt every run). Projects: `seed` → `journeys`. 1 worker, 180 s timeout, 1280×800.
- `seed.setup.ts` builds the data off camera through the real UI. It then makes the stub user a real owner with a direct SQL update.
- `support.ts` `film(browser, name)` → `{page, say, go, click, type, pick, look, done}`.
  - Records video.
  - Draws a caption bar on `<html>` (not `<body>`, to stay clear of React hydration). It is re-inserted every 150 ms from sessionStorage, so it survives navigations.
  - Pacing: ~1.4 s to read, ~1 s to look, 55 ms per key. Click targets get an amber outline for 900 ms.
  - `actAs(name)` renames the dev-bypass user so the persona's name shows.
- Journeys are ~60 lines each, one `say()` per step. R1 = desk walk-in, R2 = owner morning. ~54 s each.
- **Recorder** (`rrweb.ts`):
  - rrweb 2.1.6 UMD from jsDelivr, cached and injected via `addInitScript`. cdnjs doesn't carry rrweb.
  - Guarded to http(s) only, because on about:blank the page crashed.
  - `exposeBinding("__rrwebEmit")` sends events to a Node-side array, so they survive full page loads.
  - `say()` → `addCustomEvent("step", {text})`, which becomes a timeline marker.
- **Player**: a single self-contained `player.html`.
  - rrweb-player JS/CSS inlined; all journeys embedded as one JSON literal, with `</` escaped.
  - Journey picker, amber step markers on the progress bar, clickable step list (`player.goto`), caption follows the current time.
  - Why inline everything: `file://` can't fetch a sibling JSON, and jsDelivr serves `.cjs` as `application/node` with nosniff.
  - Works as a Claude artifact (CSP-safe).
- Sizes: JSON ~140–165 KB per 50 s journey; the player itself ~230 KB; `player.html` with 2 journeys = 540 KB; webm ~3 MB each (the replay is ~20× smaller).
- Cost: ~55 min total, about half of it tracking same-day UI changes. ~12 min per new journey. Ongoing cost = script upkeep when the UI moves.
- Side benefit: it surfaced a real app bug (silent drop on a shared command id, fixed in 8716fc2). Journeys double as a flake detector.
- SoLex next step (D-30): suite-wide capture behind an env flag, with `test.step` names as markers, plus hand-narrated showcase journeys.

## Gotchas hit

- The rrweb-player UMD global is a namespace: `new (rrwebPlayer.default ?? rrwebPlayer)(...)`.
- Strip the `sourceMappingURL` line from the injected UMD.
- Playwright forbids a test file importing another test file, so shared constants live in `hotel.ts`.
- The replay follows the viewer's `prefers-color-scheme`, so it can render dark while the app/webm is light.

## Rough edges

- Color scheme mismatch (above).
- Embedded JSON grows linearly with journeys; no lazy load.
- No sharing beyond the file.
- Step markers are rrweb custom events, not a standard format.

## If productized: QA's design notes

1. **Fixture/plugin**, not `film()`. A `use: { rrweb: 'off' | 'on' | 'retain-on-failure' }` option like `trace`, on the stock `page` fixture. `test.step` titles become markers automatically; `say()` stays optional for narrated showcases.
2. Vendor rrweb as an npm dependency; no runtime CDN fetch.
3. **Reporter output** like html-report: an index filtered by project/file/status, linked from the Playwright HTML report and trace entries. Lazy-load per-test JSON over http; inline for `file://`. Optional gzip + DecompressionStream.
4. Batch events in the page and flush on an interval, on pagehide, and at context close. Support multiple pages/popups (pageId per event; tabbed player).
5. Privacy: mask password inputs by default, `blockClass`/`blockSelector`, a redact hook. A replay is text, so it's greppable and exfiltratable.
6. Record the emulated color scheme; the player forces it on the iframe.
7. Optionally show the webm side by side, synced, or drop the video entirely.
8. Caption overlay and pacing only in "showcase" mode, so ordinary tests stay fast.
9. Document the limits: canvas/WebGL needs rrweb's canvas plugin; cross-origin iframes aren't captured; cross-origin CSS may not inline.

Other ideas (architect): TTS narration from captions; diff two replays of the same journey across builds; publish to a static host.

## Prior art to check

- Playwright trace viewer: per-action DOM snapshots, dev-oriented, not a single shareable file.
- rrweb / rrweb-player: the raw pieces.
- Storybook interaction stories.
- Meticulous, Replay.io: proprietary.
- Cypress/Checkly session-replay add-ons.

## Open questions

- OSS package (`playwright-rrweb`-style) vs product (hosted share/diff)?
- Does something close to QA's #1–3 already exist? Needs a prior-art search before building.
