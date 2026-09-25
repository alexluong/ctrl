# Collie Demo: DX and agent skill

**DRAFT, pending Alex's review (2026-09-25).** A hypothetical reference: what an author (agent or human) touches, and the skill that teaches an agent when and how to demo. It's the thing we hand to agents in the walkthroughs. Scenario: [end-state.md](end-state.md). Feasibility: [engineering.md](engineering.md). Names (`demo`, `@collie/demo`, `.demo`) are placeholders.

## Deliverables (Alex, 2026-09-25)

1. **Format:** the `.demo` file (a zip of JSON streams on one clock).
2. **Capture tooling:** the in-page browser recorder, the Playwright adapter, optional backend capture (server logs, OTLP receiver, webhook catcher, DB watch).
3. **Player:** one HTML file (step list, captions, replay; panels and views optional).
4. **CLI:** `run` / `summarize` / `sheet` / `open` / `publish`. What agents call.
5. **Server (maybe):** upload → team link; self-hostable.
6. **Agent instructions:** a skill + an `AGENTS.md` block. An MCP only later, as a thin wrapper for agents without a shell.

**Not ours:** environment setup (services, seed, auth, clock, personas); it differs per project. We give escape hatches only: a `start` and an optional `reset` command, plus `r.offstage()` / raw `r.page`. Not a test framework. Not the suite. Not every task needs a demo.

## Calls from the walkthroughs (2026-09-25)

From [walkthroughs/](walkthroughs/) (outpost#1093, solex-qa):
- **Self-check = look at it.** `demo sheet` (a grid of frames the agent views) is the default check; `summarize` covers technical errors, `frame --step` zooms in. All of solex-qa's ~20 findings were visible on screen, not in logs.
- **Bugs found while demoing → ask the user** how to proceed; don't script around them silently.
- **Value = narrated visual + step list + "what to notice".** Devtools panels are secondary: nobody asked for them.
- **The PR gets the link + the step list;** the GIF is optional garnish; `slide.diff` is optional.
- **Full Playwright** as the authoring surface (a DSL dies at the first native dialog/date/select).
- **Backend:** open; worth exploring separately (see README / backend exploration).

## Surfaces

| Surface | Who touches it | Goal |
|---|---|---|
| **Skill** | the agent, every PR | knows *when* to demo and *how* without being told |
| **Journey** (`*.demo.ts`) | the agent writes it | ~20 lines, plain Playwright + a few verbs |
| **CLI** | the agent runs it | run → check → publish, readable output, `--json` |
| **`demo.config`** | set up once per repo (agent or human) | how to start and seed the app |
| **Player** | reviewers | not DX; see end-state § 7–8 |

## 1. The skill (agent-facing)

Shipped with the package. `demo init` writes it where the harness looks (`.claude/skills/demo/SKILL.md`, or a block in `AGENTS.md` for other agents). The contents, in short:

**When to demo**
- After a **user-visible** change (UI, API behaviour, a webhook, a CLI), before opening or updating the PR.
- For bug fixes: a repro first (`--compare main`: before ✗ → after ✓).
- Skip: refactors, deps, docs, test-only changes. When unsure, ask the human.

**How to write the journey**
- Story first: 3–6 steps, one `say()` per step, written for a reviewer ("what changed and why it matters"), not a click log.
- Open with `slide.title`; add `slide.diff` only when the change is small enough to read.
- Setup and sign-in happen off camera (the project's own scripts, or `r.offstage(async page => …)` mid-journey), not on camera.
- Prefer visible text for targets (`r.click("Move room")`); fall back to `r.page` for anything unusual.
- At least one `r.expect` per claim a caption makes.
- Throwaway by default (`.demo/`, gitignored); keep it in `demos/` only when asked.

**The loop**
1. `demo run <journey>`
2. `demo sheet <out>`: **look at every frame.** Wrong text/language, spinners, stale values, a caption the screen doesn't back up? Then `demo summarize <out>` for errors/failed requests, `demo frame --step N` to zoom, fix, re-run.
3. If the demo exposes a **real bug**: stop and ask the human how to proceed. Never script around it silently.
4. At most 3 attempts; after that, report to the human instead of shipping a bad demo.
5. `demo publish <out>` → paste the **PR Demo section** it prints; mention the local GIF path so the human can drag it in.

**Never**
- Put secrets or real personal data in captions or seed data.
- Demo against production.
- Publish if `summarize` shows unexplained errors.

## 2. Journey API

```ts
import { demo } from "@collie/demo";
export default demo("Title", async (r) => { … });
```

| Verb | What |
|---|---|
| `r.say(text)` | a step marker + caption |
| `r.go(path)` | navigate (relative to the config `url`) |
| `r.click(text \| locator)`, `r.type(label, text)`, `r.pick(label, option)` | actions that pace themselves and get highlighted in showcase mode |
| `r.expect(locator)…` | Playwright `expect`, recorded as ✓/✗ on the timeline; soft in `--compare` |
| `r.slide.title(t, sub?)`, `r.slide.diff({base, paths})`, `r.slide.html(html)` | cards drawn by the player |
| `r.highlight(target, {label})` | an outline plus a callout; never fails the run |
| `r.http.get/post/…` | API calls for backend demos (`export const stage = "http"`) |
| `r.until(fn, {timeout})` | wait for async effects (webhooks, jobs) |
| `r.page`, `r.context` | the raw Playwright escape hatch |

Also: a Playwright fixture for existing suites: `use: { demo: 'off' | 'on' | 'retain-on-failure' | 'showcase' }`, where `test.step` titles become steps.

## 3. CLI

| Command | What |
|---|---|
| `demo init` | writes `demo.config.ts`, the skill, and the `.demo/` gitignore entry; detects the start command |
| `demo run <journey> [--logs\|--otel] [--compare <ref>] [--cdp <url>]` | records → `out/<name>.demo`; prints the browser, the app, a step count and the size |
| `demo summarize <file> [--json]` | a text timeline: steps, requests, errors, expects, storage |
| `demo sheet <file>` | a contact sheet: one image with a frame every few seconds + captions; the agent's default self-check |
| `demo frame <file> --step N` | a PNG of that moment |
| `demo open <file>` | the local player, no account |
| `demo publish <file> [--link\|--public]` | uploads after redaction → team-only link + the PR section + a local GIF |
| `demo login` / `ls` / `rm` | device-code login (like `gh`); `DEMO_TOKEN` for agents/CI |
| `demo export <file> --mp4\|--gif` | video/teaser for places without the player |
| `demo serve` | self-hosted server |

## 4. `demo.config.ts`

```ts
export default {
  start: "pnpm dev",            // runner owns the process → --logs works
  url: "http://localhost:5173",
  seed: "pnpm db:seed:demo",    // before each run, off camera
  auth: { storageState: ".demo/auth.json" }, // or a setup journey
  redact: { headers: ["x-api-key"], fields: ["secret"] },
};
```

## Open DX questions (for the walkthroughs)

1. **Authoring:** TS + Playwright (above) vs a smaller DSL/YAML. Do agents want fewer choices or full Playwright?
2. **Trigger:** should the skill demo by default after user-visible changes, or only when asked?
3. **Setup cost:** is `demo.config` + seed + auth a one-time chore agents can do, or the main reason they'd skip?
4. **Self-check:** is `summarize` enough, or do they need `frame` every time?
5. **PR output:** link + steps enough, or is the GIF essential? Who attaches it?
6. **Skill form:** a Claude skill vs an `AGENTS.md` block vs an MCP. What would each harness actually load?
7. **Backend changes:** does the `http` stage fit webhook/API PRs, or would they rather show tests + logs?
