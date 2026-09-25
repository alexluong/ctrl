# Collie Demo (`collie-demo`): narrated, seekable demos of features, recorded by agents

Formerly the working name **replay** (renamed 2026-09-25). Older sections below still say "replay", `.replay`, `@replay/*`: read those as working names.

Status: **going ahead as a personal tool** (2026-09-25). Lab prototype at `~/code/replay-lab`; no public repo yet. Market scan: [market.md](market.md).

## Positioning (Alex, 2026-09-25): decided

- A **simple tool Alex wants to use and share with his team**. Making money is not the goal; a subscription only covers the cost of private/team hosting.
- **Local runner / self-hostable** first: record → `.replay` → open or serve it yourself.
- **Public sharing** option: upload to a hosted player → a link.
- **Paid, optional**: private, team-based sharing (workspaces, access control).
- **The core is embeddable**: built so it can later be part of Alex's own IDE/agent-harness feature.
- Market check (market.md): a real but narrow gap; others are converging on video (Playwright screencast chapters, ProofShot, Cursor/Devin). Our niche: one synced view (replay + console + network + storage + captions), a small file, and agent self-check.
Origin: built inside SoLex ([hotel-backoffice](../hotel-backoffice/README.md)) by solex-qa in ~1h, because Alex wanted a seekable HTML "session replay as demo" instead of screen recordings.
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

Full scan (2026-09-25): [market.md](market.md). Closest: Playwright screencast chapters + trace viewer, tracelane, ProofShot. Verdict: real but narrow gap; build on rrweb 2.x.


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
- Nearest threats if it were ever a product: cloud browsers adding sharing (note: Browserbase and Steel dropped rrweb for video, 2025–26; see [market.md](market.md)); agent platforms building it in (Codex/Copilot attach screenshots today).
- Design lean: **script, then render** (agent writes a short journey, the tool runs it cleanly) as the core; recording the agent's live browser session is a stretch goal (needs trimming of retries and dead time).

## Context: Alex's workspace vision (background only, not a suite plan)

Alex has a longer-term idea for an agent workspace: agent management, ticketing, PR review, test-case management, with proof/replay as one component. This is not a plan to build a suite. It explains why the core should be embeddable. Reference points (checked 2026-09-25):
- **[Kandev](https://github.com/kdlbs/kandev):**
  - AGPL-3.0; one Go binary with an embedded TS web UI; 837★, v0.95.1 (2026-09-22).
  - Kanban board with tickets imported from GitHub, Jira, Linear and others; a worktree per task; multi-step workflows with approval gates; a review workspace (editor, terminal, changes, live browser preview, PR links); a task MCP; a plugin system.
  - Runs 20+ agent CLIs via ACP.
  - **No test cases or proof/recording.** Natural fit: a replay artifact tab next to Changes, uploaded through its MCP or a plugin.
- **[herdr](https://github.com/herdrdev/herdr):**
  - Apache-2.0 Rust TUI, "the runtime your coding agents live on"; ~40.6k★, v0.9.1.
  - A tmux-like multiplexer for agents: sessions that persist in the background, several SSH machines, agent state per pane, a socket API.
  - It's the layer that runs the agents, not a task/PR surface. Proof would plug in only as a plugin pane or a link.
- Similar tools: Vibe Kanban (Apache-2.0, ~28k★), Claude Squad, Crystal (now Nimbalyst), Sculptor, Conductor (closed source).

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

## Native Playwright comparison (lab 4e69660)

`native-demo.js` → `out/native/`. The same journey, using only Playwright 1.63: `recordVideo` + `showActions`, `page.screencast.showChapter()` title cards, `tracing.group()` per step, and a `<video>` page with WebVTT chapters.
- Gotcha: `page.screencast.start()` recorded an 800×500 page inside a 1280×800 frame. Context-level `recordVideo` is full size.
- Chapter cards blur or cover the page for ~2 s. Our caption bar leaves the page visible.
- Size: 1.2 MB video + 3.9 MB trace, vs ~40 KB of rrweb data.
- The video and the trace are separate views and don't play in sync. There's no storage timeline.
- The trace viewer won't render in the Claude desktop browser pane (service worker registration fails). It works in a normal browser or with `show-trace`.
- **Takeaway:** native gives ~70% for free. What's missing is **one synced view + a small shareable file**. Fallback where rrweb is fragile: play the real video in our player with synced panels (hybrid).

## No-Playwright recorder (lab caf9d31, `src/inpage.js`)

A plain `<script>` (rrweb UMD + `inpage.js`) that the app injects in record mode (`node app/server.js --record`, :7103).
- Widget: ● Record / caption + Step / ■ Stop & save. Saving POSTs to the server and produces the same `.replay` + player. `window.replay.say()` works for agents or from the console.
- In-page capture:
  - console: patched methods + `error` / `unhandledrejection`
  - fetch/XHR: patched, with bodies
  - the document request: from the navigation timing entry
  - local/session storage: `Storage.prototype` patch
  - cookies: `document.cookie` polling
- Survives full page loads: on `pagehide` the buffer is parked in sessionStorage and resumed on the next page. Tested with a reload mid-recording.
- Hand-recorded in the browser pane: 36 s, 4 steps, 4.4 KB zip.
- Limits vs Playwright:
  - no HttpOnly cookies
  - no static-asset requests or browser-level "Failed to load resource" errors
  - cookies shared per host across ports (a SoLex cookie leaked in)
  - viewport = the user's window size
- **Architecture this implies:**
  - **core** = in-page recorder + `.replay` format + player, with **no Playwright dependency**
  - **adapters:**
    - Playwright fixture: most complete, reproducible
    - browser extension: `chrome.debugger` for full network + HttpOnly cookies
    - in-app dev script: lets humans record too
    - CDP/agent browsers (Chrome DevTools MCP, Claude in Chrome) injecting the script

## CLI + server (proposed; Alex likes it)

Alex: "a CLI that allows a server people can log in/sign up to and upload".
- **CLI** (run via npx):
  - `replay login`: device-code flow like `gh auth login`
  - `publish x.replay [--private]` → link
  - `ls` / `rm` / `open`
  - `serve`: self-host
  - `summarize` / `frame`: agent self-check
- **One server codebase, three modes:**
  - local `replay serve`: no auth
  - self-hosted for a team: accounts, API tokens
  - Alex's hosted instance: adds billing for private/team
- **Server:** accounts, teams, upload, list, visibility (public/unlisted/team), expiry, player page. SQLite + disk for self-host; S3 for hosted.
- **Agents:** `REPLAY_TOKEN` env → `replay publish` from any harness. The widget's Stop & save uploads the same way.
- Candidate for Alex's "bigger Go project" goal: one Go binary with server + CLI + embedded player.
- Open-core precedents (license split, what to gate): [market.md § Open-core models](market.md#open-core-models).

## Ideas: backend capture + test cases (Alex, 2026-09-25)

**Backend capture** (inspired by ProofShot's synced server logs). Options, cheapest first:
1. **Server logs:** the runner spawns the dev server (`replay run -- npm run dev`) and timestamps stdout/stderr on the replay clock. This adds a Server tab.
2. **Correlation:** our fetch patch (or Playwright `extraHTTPHeaders`) adds a W3C `traceparent` to each request, and the app logs the trace ID. Clicking a network row then shows that request's server logs.
3. **OTel spans:** the runner hosts a local OTLP receiver and the app exports spans (handler, SQL, outbound calls). This gives a per-request waterfall inside the replay. It's the most "BE replay", but needs app instrumentation.
4. **DB diff:** a snapshot per step (easy with SQLite, e.g. SoLex), shown like the storage panel: "what rows changed at this step".
5. **Backend-only replay:** API steps (fetch/curl) as the script, with captions. Same player without the DOM pane, showing req/res + logs + spans + DB diff.

**Test-case tie-in:** test case = spec (steps + expected). The agent writes the journey from it, the steps map 1:1 to `test.step`/`say()`, and each run's `.replay` is attached as evidence next to the case.
- Link via a Playwright annotation (`{type:'case', description:'N29'}`).
- Prior art: TestRail/Qase/Xray (screenshot/video attachments), Allure (per-step attachments, OSS).
- Dogfood: SoLex's `qa/cases.md` already has case IDs.

## Backend capture spike (lab 710b194): works end to end

Run with `node run.js [--logs | --otel]`. The app runs as a **child process** on :7105 and the journey lives in `journeys/todo.js`.
- **`--logs`**: the child's stdout/stderr, line by line, stamped on the replay clock → `server.json` `{t, stream, text, traceId}`.
- **`--otel`** (implies `--logs`):
  - The runner hosts an OTLP/HTTP JSON receiver on :7104.
  - The app starts with Node's **zero-code auto-instrumentation** (`--experimental-loader @opentelemetry/instrumentation/hook.mjs --import @opentelemetry/auto-instrumentations-node/register`, OTEL_* env, http + undici only).
  - Output → `spans.json` `{traceId, spanId, parentSpanId, name, kind, service, start, end, status, attributes}`.
- **Correlation:**
  - The in-page fetch patch adds a W3C `traceparent` to same-origin requests.
  - Playwright copies it onto the network row.
  - **The browser request is the root span.** Verified.
- **Demo extras in the app:**
  - a custom `db.*` span via `@opentelemetry/api` (a no-op without the SDK)
  - a trace-id log prefix
  - an outbound call to a "report worker" that returns 503
- **Example** (`/api/report`): browser GET 117 ms → server GET 66 ms (error) → db select 10 ms + POST report-worker 46 ms (error) → worker POST /render 41 ms. All 6 API requests are correlated and the logs carry the trace id.
- **Size:**
  - browser only: 38.4 KB raw / 7.5 KB zipped
  - with logs + otel: 51.7 KB / 9.9 KB zipped (+~30%); `spans.json` is 2.8 KB for 17 spans
  - Real apps with ORM/SQL instrumentation will produce far more spans, so cap or sample per request. Still tiny next to trace.zip (390 KB).
- **Player:**
  - **Server** tab: logs on the timeline, stderr in red, the trace id links to that request's network row.
  - Network rows show "⧉ trace". Clicking one shows a **waterfall**: browser root, then the server span, db (green), outbound (grey), errors in red, indented by parent; then that request's logs.
  - "Click the 500 → see why" takes one click.
  - Deeper traces will need collapse/zoom.
- **Opt-in:** `server.json`/`spans.json` are written only when enabled and listed in the manifest. The player hides the Server tab and trace links when they're absent. When off, it costs nothing.
- **Gotchas:**
  1. For ESM apps, `--import …/register` alone doesn't instrument `import { createServer } from "node:http"`. The **loader hook is required**. Without it, spans become separate roots and logs have no trace id.
  2. The receiver's keep-alive sockets hold the runner open, so it needs an explicit `process.exit`.
  3. Clocks: `Date.now()` works when everything is on one machine. Remote or containerized backends need clock-offset estimation.
  4. Document and static requests carry no `traceparent` (only fetch is patched). They're filtered out of the waterfall.
- **Not done:** per-step SQLite DB diff.
- **Fits** the opt-in shape: `replay run --logs|--otel` or the fixture option `backend: 'logs'|'otel'`.

## Backend-feature demos (lab 4f680ea)

Alex: "what about backend features, not UI?"

**Framing:** a backend demo = **stimulus → effects**, narrated.
- Stimuli: API calls, CLI, messages, time.
- Effects: responses, spans, logs, DB changes, outbound calls (webhooks/3rd-party), queue messages.
- The recording's **stage is pluggable**: `ui` (rrweb) | `http` (cards) | `terminal` (future, asciinema-like). The side panels are shared across stages.

**Built:**
- **Demo feature:** the todo app now uses `node:sqlite`.
  - `POST /api/webhooks` registers an endpoint; every created todo is delivered as a signed webhook (HMAC sha256, `x-webhook-attempt` header).
  - Backoff 300/600/1200 ms, dead-lettered after 4 attempts; `GET /api/deliveries`.
- **`r.http.get/post/…`:** HTTP goes through Playwright's `context.request` (cookies shared with the browser). That path emits **no** context request events and **doesn't appear in library-mode traces** (verified: `trace.network` is empty), so we record the call ourselves and add a `traceparent`.
- **`r.catcher`** (`src/backend.js`): a local webhook receiver.
  - Programmable, e.g. `respond([500, 500])`.
  - Records `{t, method, path, headers, body, status, traceId, parentSpanId}` → `inbound.json`.
- **`dbWatch`:** polls the app's SQLite file read-only every 120 ms → row-level insert/update (changed cols before→after)/delete → `db.json`.
  - Caveat: polling can miss short-lived states (`pending`/`sending`). A trigger/CDC hook would be exact.
- **`r.until(fn)`** waits for async effects. `export const stage = "http"` in a journey means no page at all.
- **Player `http` stage:** a card timeline (step banners, API request→response, "Received" webhook cards with signature/attempt/answered status, DB diff cards) on its own play/scrub clock (1/2/4×). Clicking an API card opens its waterfall.

**Result** (`journeys/webhooks.js`, `node run.js --journey webhooks --otel`, 13 s):
- 3 scenarios:
  - delivered on the first try
  - flaky receiver (500, 500, then 200 on attempt 3)
  - receiver down → dead after 4 attempts
- **Retries keep the originating request's trace** (Node AsyncLocalStorage context survives `setTimeout`). One waterfall for `POST /api/todos` shows: app span → db insert → 4× `webhook.deliver` → outbound POST → "receiver answered 503", spaced out by the backoff.
- The catcher's hits join the tree via their `traceparent` parent span id. The trace's server logs sit underneath (a warn per retry, an error when dead).
- **Size:** 6.8 KB zipped without trace.zip (raw: db 4 KB, inbound 7 KB, spans 15 KB).

**Gaps / next:**
- queue taps (OTel messaging spans or a broker tap)
- Postgres watch (logical replication/triggers vs polling)
- `terminal` stage for CLI features
- assertions shown as ✓/✗ cards (`r.expect`)
- collapsing repeated payloads (done for retry attempts)

**Prior art to check:**
- Hurl / Bruno / Postman runs: scripted API calls, no narration or backend view
- Runme / notebooks
- **Tracetest**: trace-based assertions
- Keploy: API capture/replay

## Scope: tool now, suite parked (Alex, 2026-09-25)

**We build only the tool (capture + sharing).** The suite is an idea: not finalized, not being built.

**Boundary:** the tool is about **recordings**; the suite is about **work**. Test: does the feature make sense without any project/task/team context? Yes → tool. No → suite.
- **Tool:**
  - recording
  - player views
  - before/after compare
  - publish/share
  - collections (several replays + text + diagrams on one page)
  - Mermaid diagram blocks + an **auto sequence diagram generated from trace spans**
- **Suite (parked):**
  - releases (version / changelog / "demos in this release", rendered as a collection)
  - test cases (requirement → journeys → pass/fail history)
  - agent orchestration (bug → repro → fix → compare → attach to PR)
- **Seams to keep clean** so a suite can sit on top later:
  1. the `.replay` format + collection/compare manifests
  2. the player as an embeddable component with a plugin API (stages/panels/views)
  3. the CLI with `--json` output

### Usage levels
- **Throwaway** (default for agents): the script lives in a gitignored `.replay/`; the replay itself is the artifact.
- **Showcase:** kept `demos/*.demo.ts`, re-run to regenerate.
- **Suite:** a Playwright fixture, `use: { replay: 'off'|'on'|'retain-on-failure'|'showcase' }`.
  - `off` = no-op (`test.step` works as normal)
  - `on` = a replay per test
  - `showcase` = demo pacing
- Users don't set up Playwright themselves; the tool ships it.
- Our verbs: `go/click/type/say/http/until`, plus raw `r.page`.
- **Not a test framework:** a reporter layer, like the trace viewer / HTML report.

### Player views (same file, different views)
- The views:
  - **dev** (today)
  - **backend** (`http` stage)
  - **reviewer / non-technical:** big captions, pause at each step + Next, outcome summary, no dev panels
  - **storyboard:** a frame per step → PDF/GIF/MP4
  - **test report:** ✓/✗ per step
  - **compare**
  - **embed**
- Picked via `?view=` or `manifest.view`.
- Custom panels via a plugin API (e.g. a SoLex domain panel).
- Pricing caution (see [market.md § Open-core models](market.md#open-core-models)): keep views and the plugin API free everywhere. Charge only for hosted conveniences: branded share pages / custom domain, private viewer links, viewer analytics, retention.

### Before/after compare + bug demos
- `replay run x.demo.ts --compare main`: creates a git worktree at the base and at HEAD, runs the same journey on each (fresh DB each time), and writes `compare.json`.
- Steps are aligned by caption.
- A soft `r.expect` records ✗ instead of throwing, so the "before" run completes.
- The compare view shows a per-step diff summary (status / console / DB / trace shape / visual) plus the two runs side by side.
- **Bug workflow:** reproduce first (before, ✗) → fix → after (✓). The journey then becomes a regression test.
- For features, "before" is optional.

**Lab next** (Alex to pick): the before/after compare spike, or the auto sequence diagram from spans.

## Naming

**Decided (Alex, 2026-09-25): project = Collie Demo / `collie-demo`.** Still open: the CLI command (`demo` vs `collie demo`), npm scope (`@collie/*` vs a standalone scoped package first), file extension (`.demo`? `.take`?), and whether "journey" is the script term. The history below explains how we got here.

### History (2026-09-25)

"Replay" is a working name only: Alex says it doesn't fit, and it collides with Replay.io.

**Umbrella candidate: Collie.**
- Alex's personal brand since 2021 ("Collie Studio"; later collielab and collie-ui). Named after his border collie.
- The "herding agents" reading is a coincidence and a bonus, not the origin.
- Convention under discussion: Collie umbrella + plainly named modules (Collie Replay, later Board/Review/Cases); npm `@collie/*`; one `collie` CLI with subcommands. "Collie Studio" could be the eventual workspace app. No suite is planned now.
- Collisions:
  - [AltanS/collie](https://github.com/AltanS/collie) (~1.1k★): a mobile terminal for coding agents on herdr, i.e. the same space.
  - [meshcloud/collie-cli](https://github.com/meshcloud/collie-cli): a `collie` command.
  - The bare `collie` npm package is taken (unrelated).
  - Fine for personal/team use; recheck before any public launch.

**Standalone name pass** (checked npm, GitHub, brew, local commands, fileinfo, DNS; domains and trademarks not registrar-verified):
- **Free on npm:** rushes, outtake, playthru, cutroom, foley.
- **Most dictionary names are taken on npm:** take, reel, slate, exhibit, witness, receipt, rewind, retrace, tape.
- **Eliminated:**
  - `take`: oh-my-zsh `take` = mkdir+cd, installed on Alex's machine. Only a problem as a *bare CLI*; `.take` as a file extension is clean.
  - `tape`: charmbracelet VHS uses `.tape`.
  - `witness`: the in-toto `witness` attestation CLI.
  - `dailies`: an active npm package "release decisions for AI changes", adjacent space.
  - rewind/retrace: screen-memory apps.
- **Top picks:**
  - **rushes** (film: raw footage reviewed daily, before anything is final): npm free, clean CLI, `.rush` ext; only collision is rushes.co, a small filmmaker video platform.
  - **outtake**
  - **exhibit** (needs an npm scope)
- **Suite names (film theme), if ever:** Editbay, Cutroom, Picturelock (all free on npm); Backlot is risky (brekkylab/backlot = local SaaS emulator for agents).

**Later discussion (same day):**
- **"Proof"**: liked the angle, but too strong. Alex: in a PR "I want to share a demo", not proof.
- **Shared noun = "demo".** The dev/backend panels are extras inside a demo.
- CLI candidates:
  - **`demo`** (plain, later "Collie Demo"; bare npm taken by a dead package → scoped package with a `demo` bin; no local command clash)
  - **runthru** (npm free)
  - `qed` (clever; npm dead)
- **"Journey"**:
  - Already SoLex's term (`e2e/journeys`).
  - Fits the *script* (a path of steps; also a request's journey through the backend).
  - As a product name it has marketing/analytics baggage (Journey Builder, journey analytics). Bare `journey` npm is dead; `journeys` npm is dead (2022, "test user journeys through a REST API").
  - Lean: journey = the script term, demo = the output/noun.
- **Standalone first:** ship a standalone CLI; formalize under Collie later (scope `@collie/*`; the command and file extension don't mention Collie, so nothing needs renaming).

**File format:** a plain zip (magic `PK`) with `manifest.json` (format name + version) and NDJSON streams; a custom extension for "open with"; a `--zip` export. Extension candidates: `.take`, `.rush`, `.reel` (none has a fileinfo entry).

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

- Name: **Collie Demo** (decided). Open: repo location, CLI command, file extension, npm scope. See § Naming.
- License split: MIT for core/adapters/player/CLI; server MIT vs AGPL. Lean: MIT everywhere, AGPL server as fallback; skip FSL/BSL ([market.md](market.md#open-core-models)).
- Go (single binary: server + CLI + embedded player) vs TS monorepo. The recorder/player stay JS either way.
- ~~Does an "agent demo recorder" MCP already exist?~~ Answered in [market.md](market.md): several are video-only; none are DOM replays.
