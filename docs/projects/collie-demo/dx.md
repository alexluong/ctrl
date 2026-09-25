# Collie Demo: DX and agent skill

**DRAFT, pending Alex's review (2026-09-25).** A hypothetical reference: what an author (agent or human) touches, and the skill that teaches an agent when and how to demo. It's the thing we hand to agents in the walkthroughs. Scenario: [end-state.md](end-state.md). Feasibility: [engineering.md](engineering.md). Names (`demo`, `@collie/demo`, `.demo`) are placeholders.

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
- Setup and sign-in happen off camera (seed/config), not in the journey.
- Prefer visible text for targets (`r.click("Move room")`); fall back to `r.page` for anything unusual.
- At least one `r.expect` per claim a caption makes.
- Throwaway by default (`.demo/`, gitignored); keep it in `demos/` only when asked.

**The loop**
1. `demo run <journey>`
2. `demo summarize <out>`: read it. Any console error, a failed request, a failed ✗ expect, or a caption that doesn't match what happened? Then `demo frame --step N`, fix, re-run.
3. At most 3 attempts; after that, report to the human instead of shipping a bad demo.
4. `demo publish <out>` → paste the **PR Demo section** it prints; mention the local GIF path so the human can drag it in.

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
