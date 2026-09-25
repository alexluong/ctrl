# Collie Demo: engineering notes

Build-side notes from the replay-demo session (2026-09-25). Product and positioning: [README.md](README.md). Market: [market.md](market.md).
Code is still named "replay" until the CLI name, npm scope and extension are locked.

## Lab: `~/code/replay-lab` (local git, no remote)

| File | What |
|---|---|
| `app/server.js` + `index.html` | Demo app. Todos (SQLite via `node:sqlite`), login cookie, localStorage, a broken `/api/report` (500 + an outbound call to a 503 "report worker"), **webhooks** (HMAC-signed, backoff 300/600/1200 ms, dead after 4 attempts). Optional OTel: `db.*` spans + a `trace=<id>` log prefix (no-ops without the SDK). `--record` injects the in-page recorder. |
| `src/recorder.js` | Playwright recorder. `record(browser, {name, url, stage})` → `{page, say, go, click, type, pause, http.*, until, onStep, stream, finish}`. |
| `src/inpage.js` | No-Playwright recorder: a plain `<script>` + a Record/Step/Stop widget; survives full page loads through sessionStorage. |
| `src/backend.js` | `catcher()` (programmable webhook receiver) and `dbWatch()` (SQLite row diffs). |
| `src/bundle.js` | Writes the bundle dir + the zip. Shared by every recorder. |
| `src/player.js` | Bundle dir → one self-contained `index.html`. |
| `run.js` | Runner: starts the app as a child, `--journey <name>`, `--logs`, `--otel` (local OTLP receiver). |
| `journeys/todo.js`, `journeys/webhooks.js` | UI journey; backend-only journey (`export const stage = "http"`). |
| `demo.js`, `native-demo.js`, `serve.js` | In-process demo; Playwright-native video + trace comparison; static server with Range support for `out/`. |

Run: `node run.js --journey webhooks --otel` · `node demo.js` · `node app/server.js --record` (:7103) · `node serve.js 7101` → `http://localhost:7101/<name>/index.html`.

## Format v0 (as built; the future spec)

A zip (`<name>.replay` today) of JSON files. Every entry carries `t` = epoch ms on one clock (the recording machine).

| File | Always? | Shape |
|---|---|---|
| `manifest.json` | ✓ | `{format:"replay/0", name, url, recorder:"playwright"\|"inpage", stage:"ui"\|"http", startedAt, durationMs, viewport, colorScheme, counts, files}` |
| `rrweb.json` | ✓ (empty for `http`) | rrweb events (standard rrweb format) |
| `steps.json` | ✓ | `{t, text}` |
| `console.json` | ✓ | `{t, level, text, source?, stack?}` |
| `network.json` | ✓ | `{id, t, end, duration, method, url, type:"document"\|"fetch"\|"xhr"\|"api"\|…, status, error?, requestHeaders, requestBody, responseHeaders, responseBody (≤64 KB), traceId?, spanId?}` |
| `storage.json` | ✓ | an event log: cookie `snapshot`; local/session `snapshot`, `set`, `remove`, `clear` |
| `server.json` | opt-in | `{t, stream:"stdout"\|"stderr", text, traceId?}` |
| `spans.json` | opt-in | flattened OTLP: `{traceId, spanId, parentSpanId, name, kind, service, scope, start, end, status, attributes}` |
| `inbound.json` | if used | catcher hits: `{t, method, path, headers, body, status, traceId, parentSpanId}` |
| `db.json` | if used | `{t, table, op:"snapshot"\|"insert"\|"update"\|"delete", key, rows?\|after?\|before?, changed?}` |
| `trace.zip` | optional | Playwright trace (90%+ of the zip size) |

The bundle writer sorts every stream by `t`, and writes optional files only when they're non-empty.

To add: `format` versioning rules, `view` (default player view), `redactions` applied, `expect` results, compare/collection manifests.

## Sizes measured (zipped, without trace.zip)

| Demo | Size |
|---|---|
| UI, 23 s (Playwright) | 7.5 KB (38 KB raw) |
| UI, 36 s (in-page, recorded by hand) | 4.4 KB |
| UI + `--otel` (17 spans, 9 log lines) | 9.9 KB |
| Backend webhooks demo, 13 s (25 spans, 8 inbound, 16 DB events) | 6.8 KB |
| Playwright trace.zip alone | 380 KB–3.9 MB |
| Native video (webm) + trace for the same journey | 1.2 MB + 3.9 MB |

## How capture works

- **Clock:** `Date.now()` everywhere on one machine. Remote or containerized backends will need clock-offset handling.
- **UI (Playwright):**
  - The init script injects rrweb (every keystroke; don't use `sampling.input:"last"`) plus a `Storage.prototype` patch plus a fetch patch that adds a W3C `traceparent` to same-origin requests.
  - `exposeBinding` sends events to Node, so they survive navigations.
  - Network comes from `context.on('request'/'requestfinished'/'requestfailed')`; cookies from `context.cookies()` after each response (HttpOnly included).
- **UI (in-page):** the same data from inside the page (patched console/fetch/XHR, navigation timing entry, `document.cookie` polling). No HttpOnly cookies, no static-asset requests, no browser-level errors.
- **API (`r.http.*`):** Playwright's `context.request` (shares cookies with the browser context) emits **no** request events and is **absent from library-mode traces** (verified), so we record each call ourselves and add a `traceparent`.
- **Backend logs:** the runner starts the app as a child process and timestamps each stdout/stderr line.
- **Backend spans:**
  - The runner hosts an OTLP/HTTP JSON receiver (~40 lines).
  - The app runs under Node zero-code instrumentation with `OTEL_EXPORTER_OTLP_ENDPOINT` pointing at the runner.
  - The browser/client request is the root span. Async work (setTimeout retries) keeps the originating trace through AsyncLocalStorage, so webhook retries land in the same trace.
- **Catcher:** records inbound requests. Their `traceparent` parent = the app's outbound span, so the player joins them into the waterfall.
- **DB watch:** polls SQLite read-only every 120 ms and diffs by rowid. Can miss short-lived states; triggers/CDC would be exact. Postgres is not done.

## Gotchas

1. rrweb/rrweb-player packages don't export `umd/*` paths → read the files by path, not `require.resolve`.
2. The rrweb-player UMD global is a namespace: `new (rrwebPlayer.default ?? rrwebPlayer)(…)`.
3. Attach console listeners once (`context.on('page')` only), or every line is duplicated.
4. The player must not re-render rows on every time tick (it breaks clicks); render once, toggle classes.
5. `page.screencast.start()` recorded an 800×500 page inside a 1280×800 frame; the context-level `recordVideo` is full size.
6. Python's `http.server` has no Range support → `<video>` can't seek; hence `serve.js`.
7. The trace viewer needs a service worker; the Claude desktop browser pane blocks it (fine in a normal browser or `show-trace`).
8. **ESM apps + OTel:** `--import …/register` alone doesn't instrument `import { createServer } from "node:http"`; add `--experimental-loader @opentelemetry/instrumentation/hook.mjs`.
9. The OTLP receiver's keep-alive sockets hold the runner open → explicit `process.exit`.
10. Cookies are per host, not per port: another localhost app's cookie leaks into in-page recordings. Filter it.
11. The in-page navigation entry is back-dated → streams must be sorted when saving.
12. Generated player HTML is built from a JS template string: escaping bugs are easy (`\"`, `\n`) → `node --check` on the extracted script caught both.

## Lab rough edges and half-done work (as of lab 8b254df)

- **No redaction at all:** bodies, headers, cookies and the webhook `secret` are recorded verbatim.
- **The in-page recorder has no `traceparent` patch** (only the Playwright init script does), so in-page recordings can't correlate with backend spans.
- **Custom capture instead of rrweb's official network/console plugins** (not adopted yet).
- **Player:**
  - always shows the "deep debug: trace.zip" hint, even without a trace
  - fixed 16:10 box, so tall in-page recordings letterbox
  - the waterfall has no collapse/zoom (fine for ~15 spans)
  - the http-stage cards repeat payloads (only retries are trimmed)
- **Runner:**
  - always *starts* the app (no "attach to an already running app" mode)
  - `--logs` only works when it owns the process
  - hacky `--journey` argument parsing
  - `node:sqlite` prints an ExperimentalWarning (silenced for the child via `NODE_NO_WARNINGS`)
- **One unexplained flake:** the first `--journey webhooks` run died with an `AggregateError` on the first `context.request.post` (connection refused?); the re-run passed. Possibly the app not fully ready although `GET /` answered.
- **Background processes during the lab session** (not needed to resume): `serve.js` :7101, the record-mode app :7103 (started before the webhook/SQLite change, so it runs old code), `show-trace` :7102.
- **Demo names are fixed per journey/mode** (`todo-otel`, …), so re-runs overwrite; there are no ids yet.

## Field report: a real work demo (2026-09-25)

Another Claude session recorded an 83 s walkthrough of a real permissions change in Alex's work app with plain Playwright video. Presentation ideas worth borrowing:

- **Slides between steps:** full-screen cards via `page.setContent()`: a title card, a **code-diff card** (+/− lines in green/red), transition cards. A natural shape for PR demos: "here's the change → here's the effect". Demo: slide/card steps (title, diff from git, before/after) on the timeline.
- **Highlights:** `boundingBox()` + an orange overlay a few px outside the element, removed afterwards, with `.catch(() => null)` so a missing element never kills the run. Demo: showcase highlights that can't fail the run.
- **Captions:** a fixed caption bar updated per step (= our `say()`).
- **Frame checks before sharing:** screenshots at key steps caught a loading spinner. Demo: `frame --step N` / `summarize` self-check.
- **mp4 export** (ffmpeg `libx264`, `yuv420p`, `+faststart`) for places that want a plain video. Demo: optional video export.

Out of scope for Demo: signing in, seeding, state changes and network stubs. The journey/app handles those (plain Playwright/scripts); Demo just records whatever the journey does.

## Design points decided or leaning (this session)

### Where each piece runs (language split, leaning)
The format is language-agnostic. What pins a language is where each piece runs:
- **Spec:** JSON Schema + docs, the real "core".
- **Browser bundle (recorder + player):** JS, required.
- **Playwright adapter:** the test suite's language (TS first; a Python adapter later is ~200 lines around the same JS bundle).
- **CLI / runner / server:** any language. **Leaning Go**: one binary with the web bundle embedded; does serve/publish/login/open/summarize plus the backend capture (logs, OTLP, catcher, DB watch). `demo run journey.ts` starts Node for the adapter. `frame` (PNG) needs a browser.
- Open: Go vs all-TS (simpler npm shipping, shared types). The analyst tracks this in README "Open questions".

### Browser: don't bundle Chromium
`demo run` picks the first available and says which one it used:
1. `--cdp <url>` (your Chrome, an agent's browser, a cloud browser)
2. an existing Playwright browser cache
3. system Chrome/Edge (`channel: "chrome"`)
4. offer to download (ask first)

The in-page recorder, API-only demos, viewing, publishing and the server need no extra browser.

### Private team sharing (the paid add-on, but private-first by design)
- Workspace → members (email invites / GitHub or Google org) → demos.
- Visibility per demo: **`team` (default)** / `link` (unguessable, optional expiry, admin can disable) / `public` (optional; off on private plans).
- Workspace API tokens (`DEMO_TOKEN`, publish-only) for agents and CI; `demo login` uses a device-code flow like `gh`.
- **Redaction on by default at record time, before upload:** `authorization`, `cookie`, `set-cookie`, `*token*`, `*secret*` headers/fields, password inputs, plus configurable rules. (The lab's webhook `secret` would leak today.)
- The player loads data through the authenticated API (short-lived signed URLs), never from a public bucket. Encryption at rest, a view access log, retention per workspace.
- Self-host gets all of it; paid = hosting (seats, retention, storage), per market.md.
- Server MVP order: auth (OAuth + magic link) + workspaces + invites → upload + team-only demo page → list/search → link sharing with expiry → recorder redaction.
- Open: sign-in methods (GitHub only first, or GitHub + Google + email); Go vs TS.

### Demo vs suite, per feature
Rule: **Demo owns recording, understanding and sharing demos; the suite owns *why* a demo exists.** For borderline ideas, build the manual version in Demo and park the context-aware version.

| Idea | Demo | Suite (parked) |
|---|---|---|
| Collections | a manual page of demos + text | auto-built collections (e.g. merged PRs this week) |
| Diagrams | **auto sequence diagram from a demo's trace**; Mermaid in collection text | standalone diagram docs |
| Release | none (a collection named "v1.4" by hand) | versions, changelog from PRs |
| Test cases | `r.expect` ✓/✗ saved in the demo | test-case entities, history |
| Before/after | ✓ | linking to the bug ticket |
| Agent workflow | CLI commands + a skill | orchestration across tasks/agents |

## Next build steps (proposed; Alex to pick)
1. Package shape: spec/ + web/ (recorder + player) + adapters/playwright-node + CLI; rrweb's official network plugin.
2. Playwright fixture `off|on|retain-on-failure|showcase` + `run` for throwaway journeys + browser resolution (system Chrome, `--cdp`).
3. Server with private workspaces + `login`/`publish` + recorder redaction.
4. `summarize` / `frame` + an agent skill.
5. Player views (reviewer, storyboard), before/after compare, collections + auto diagrams.
6. Presentation features (from the field report), mostly part of showcase mode:
   - **Slides/cards** as timeline steps: `r.slide.title(text)`, `r.slide.diff({ base: "main", paths })` (renders the git diff), `r.slide.compare(before, after)`, custom HTML. In the ui stage, a full-screen overlay recorded by rrweb; in the http stage, a card. Listed in the step list, so a viewer can jump to "the change".
   - **Highlights:** `r.highlight(selector, { label })` draws an overlay around the element (and an optional callout), captured by rrweb; automatic before each `click`/`type` in showcase mode. Never fails the run if the element is missing.
   - **Video export:** `demo export x.replay --mp4` renders the replay (with captions/slides) to mp4 for places that want plain video.
