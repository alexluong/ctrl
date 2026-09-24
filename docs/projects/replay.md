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

## Direction (Alex, 2026-09-25)

- **A cool project for Alex's own use**, not a money idea. No need to validate a market.
- Shape: an **agent MCP** that generates a narrated, seekable demo during development, locally (a single-file player) or pushed to a hosted player to share (in a PR, with the team, from cloud dev). A hosted, team-private version is a possible later extra, not the goal.
- Not PR/CI-centric, and not "demos for marketing".
- How it differs from Playwright trace viewer (dev debugging, snapshots per action, MB-sized zip): continuous watchable playback, captions written by the agent, a UI built for review, ~150 KB.
- Nearest threats if it were ever a product: cloud browsers (Browserbase session replay is rrweb-based) adding sharing; agent platforms building it in (Codex/Copilot attach screenshots today).
- Design lean: **script, then render** (agent writes a short journey, the tool runs it cleanly) as the core; recording the agent's live browser session is a stretch goal (needs trimming of retries and dead time).

## Minimal first version

1. Extract `support.ts` + `rrweb.ts` from SoLex into its own repo; rrweb as an npm dependency.
2. An MCP wrapper: `record → step(caption) → finish` → `player.html`.
3. Publish via Claude artifacts first; a self-hosted player on collielab only if needed.
4. Dogfood on SoLex feature work.

## Lab prototype (2026-09-25): `~/code/replay-lab`

A working scratch prototype, local git only (no remote). Alex: "extremely similar to what I'm looking for"; the remaining gaps are UX (guided demo, like SoLex's player).

- `node demo.js` films a tiny todo app (~23 s) → `out/todo-demo/` + `out/todo-demo.replay`.
- **Recorder** captures five streams on one clock: rrweb DOM (every keystroke), console + uncaught errors, network (timing, headers, fetch/xhr bodies ≤64 KB), storage (cookie snapshots on change; local/session writes via an in-page `Storage.prototype` patch), steps (`say()`). Plus the Playwright trace.
- **Player**: a single HTML file. Replay + caption on the left; Steps / Console / Network / Storage tabs on the right, following playback; clicking a row seeks; storage shows the state at the current time, rebuilt from its change log.
- **`.replay` zip**: `manifest.json`, `rrweb.json`, `steps.json`, `console.json`, `network.json`, `storage.json`, `trace.zip`. Ours: manifest / steps / console / network / storage. rrweb's standard format: `rrweb.json`. Playwright's: `trace.zip`. For 23 s: ~37 KB of data; the trace is 377 KB of the 384 KB zip.
- vs Playwright trace viewer: trace = snapshots around each action, a debugger UI, MB-sized. Here: continuous watchable replay, captions, synced devtools-like panels, trace optional.

## Proposed SDK / DX (not built yet)

- Packages: `@replay/core` (format, recorder, zip), `@replay/playwright` (capture adapter), `@replay/player`, `replay` CLI.
- Ways in:
  1. **Playwright fixture**: `use: { replay: 'on' | 'retain-on-failure' }`; `test.step` titles become markers automatically; optional `replay.say()`.
  2. **`replay.attach(context)`** for scripts and agents.
  3. **CLI**: `run`, `open`, `summarize`, `frame`, `publish`.
- Don't wrap `click`/`type`. A **showcase mode** (slowMo + highlight injected on pointer-down + pause after `say()`) gives demo pacing without learning a new API.
- LLM usage: writing = a library + a skill/instructions (LLMs write Playwright well). Reading needs tools: `summarize` (text timeline of steps + network errors + console + storage changes) and `frame --step N` (PNG), so an agent can check its own demo. MCP later, thin: `publish` / `list` for agents without a shell.
- Hosted: upload the `.replay` zip → a link; a static player loads it; link-only by default, team-private later.

## Open questions

- Name / repo.
- Does an "agent demo recorder" MCP already exist? Quick prior-art check before extracting.
