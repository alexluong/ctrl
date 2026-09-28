# Collie Demo: learnings from the exploration (2026-09-25 → 27)

What we tried, what we learned, and why we landed where we did. Round 2 of exploration: after the lab spikes (README) and the market scan (market.md), we tested the idea against real agents, real PRs and real runs. Detail lives in [end-state.md](end-state.md), [dx.md](dx.md), [backend.md](backend.md), [walkthroughs/](walkthroughs/) and [engineering.md](engineering.md).

## Where we landed

- **UI demos are the product.** Proven on a real SoLex PR (N64): cheap to record, and the self-check caught a real bug that tests missed.
- **Value = seeing it.** The narrated visual, the step list and "what to notice". Devtools panels, backend capture and slides are secondary; nobody asked for them.
- **Backend demos: parked.** Most backend PRs are served by tests and a good description. A real graph-stage prototype (outpost#1087) worked but was hard to follow; its value only shows on rare, complex multi-component flows, and those are closer to documentation than PR review.
- **Not every task needs a demo.** Demo when a reviewer would otherwise have to run the branch to believe it.
- **Environment setup is not ours.** It's per project. We offer escape hatches only (`start`/`reset` commands, `r.offstage()`).

## The path, step by step

1. **Sample end state** ([end-state.md](end-state.md)): one concrete scenario (agent finishes a PR → demo → team link → reviewer). The lab (collie-lab) flagged two traps early: a GIF preview in a PR leaks private demos (GitHub fetches images anonymously), and `--logs` only works if the runner owns the app process. **Alex decided:** the GIF is a local teaser file; the demo itself is team-only (demo.collie.studio).
2. **DX + skill draft** ([dx.md](dx.md)): skill, journey API, CLI, config. Deliverables settled: format + capture tooling + player + CLI + (maybe) server + agent skill/AGENTS.md; MCP later, only for agents without a shell.
3. **Paper walkthroughs**: agents with finished PRs judged the drafts, opinion only.
   - **outpost#1093** (backend, RabbitMQ/Redis): "as written I'd skip it". It wanted a scenario table, state probes and fault injection, not a replay. Setup was the blocker. → **Alex:** fine, not every task needs a demo.
   - **solex-qa** (UI, built the original film/player): would use it. The big lessons were **self-check by looking** (contact sheets; `summarize` would have caught none of its ~20 findings) and **seed/state is the real work**. Reviewers used the visuals + step list + "what to notice", never the panels.
4. **Clarifying with Alex:**
   - self-check = the agent looks at its own demo (`demo sheet`)
   - a bug found while demoing → ask the user, don't script around it
   - environment setup stays out of scope
   - skill file + AGENTS.md rather than MCP, because agents with a shell can already call a CLI
5. **Real UI run (N64)**: collie-lab recorded solex-qa's paper journey for real (with solex-architect's setup advice).
   - Setup ~3 min, recording 21 s, worked first time; 82 KB.
   - **The sheet caught what the passing expects missed:** erased rows stay on screen until reload. Filed by solex-qa as **N65**, and solex-qa realised its own film had shown the same stale rows unnoticed.
   - What broke in the API:
     - text-only targets cover ~60% of clicks → locators should be first-class
     - the seed (40 lines) dwarfs the demo (15 lines) → a `reset` key is needed
     - full-frame sheets are unreadable → 1:1 zoom on what each step touched
     - Vite dev traffic bloats the network data → filter static assets
6. **Backend research** ([backend.md](backend.md)): a subagent proposed backend demos as evidence reports (case × outcome tables). Alex pushed back: a replay could still work in another form. We explored a "system view".
7. **Reality check against hookdeck/outpost PRs**: ~15 recent PRs already have strong descriptions (behaviour, scope, config, tests, benchmarks). A time-based demo adds little. The only gaps: flows written as prose (a sequence diagram reads faster) and "show the real output" snippets.
8. **Alex:** the request chain from the lab's TODO case was still valuable. → An idea for a player where the stage is a graph of actions (nodes = services, edges = requests), stepped, no autoplay.
9. **Built it for real: outpost#1087** (RabbitMQ resubscribe). Outpost was built from source before and after the fix, with throwaway RabbitMQ/Redis/Postgres, a webhook receiver, a management-API probe and fault injection. Result:
   - before the fix: 16× "channel/connection is not open"; orders #2/#3 stuck in the queue
   - after: all delivered in 5 s
   - Artifact: https://claude.ai/artifact/6NEDyB41hMeFEQhR1GwZv5
   - **Alex's verdict:** interesting, but hard to follow. The change is clear, but the graph didn't make it clearer. The before/after verdict and the text tree carried the message.
10. **Search for a complex enough PR** (#771–#1087):
    - Races (#1063, #987) can't be reproduced on demand; a diagram explains them better.
    - The best fit, "what happens when an endpoint goes down" (retries → alert suppression → auto-disable → operator events), spans 5+ PRs. It's a *behaviour demo* for docs/onboarding/QA, not per-PR review.
    - → **Backend parked.**

## Lessons worth keeping

- **Test ideas on real work early.** Paper walkthroughs and one real run changed more than the whole market scan: the contact sheet, the seed cost, text targets, the backend verdict.
- **Agents are good critics when asked for opinions, not usage.** Frame it as "opinion only, don't install/run anything". Blunt beats polite.
- **Expects check what you ask; a viewer sees everything else.** Visual self-check is a core feature, not polish.
- **Reviewers read summaries.** Step list, "what to notice", before/after verdicts. Rich panels are drill-down at best.
- **A visualization has to beat one sentence.** If the change fits in "before X, after Y", show a verdict, not a graph.
- **Setup cost decides adoption.** Anything that needs services, seeds, personas or a clock is where agents give up. Keep it out of scope, but make the escape hatches good.
- **Real-run evidence has its own traps:** stats lag (RabbitMQ management API), repeated warnings need collapsing (×N), and the runner must always kill its child process (orphans hold ports).

## Open ideas (not decided)

- **Agents with a browser, not Playwright** (e.g. Claude Code's browser pane, Claude in Chrome): `demo proxy http://localhost:5173` injects the in-page recorder into every HTML page, sees all HTTP traffic (static assets, HttpOnly cookies too), and takes `demo say "…"` narration from the shell. Suggested flow: explore live, then record a clean take. The agent can open the player itself to self-check. A candidate spike for collie-lab.
- **Behaviour demos** (docs/onboarding): e.g. Outpost's endpoint-down lifecycle. A possible later use of the backend capture + graph stage.
- **Backend evidence snippets**: captured real requests/logs, and a sequence diagram from spans, as opt-in extras in a PR.

## Next (pending Alex)

Decide v1: the scope cut (UI demos + self-check + publish), Go vs TS, the server in v1 or not, naming leftovers (CLI, extension, scope). Decided 2026-09-28: repo `colliestudio/collie-demo` (private → public at v1), Apache-2.0. v1 candidates for collie-lab: `r.highlight`, a `reset` config key, static-asset filtering, the proxy spike.

## Artifacts from this round

- Docs: end-state.md, dx.md, backend.md, walkthroughs/outpost-1093.md, walkthroughs/solex-qa.md, engineering.md § "First real demo: SoLex N64".
- N64 demo: `~/code/replay-lab/out/n64-erase/` (player + sheet.png); journey `~/code/replay-lab/targets/solex/n64-erase.demo.ts`.
- #1087 prototype: artifact above; code + recordings saved in the lab at `~/code/replay-lab/targets/outpost-1087/` (lab 174bedd; README marks it parked).
