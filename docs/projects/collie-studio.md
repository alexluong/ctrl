# Collie Studio — idea notes

**Status: idea only (2026-09-25).** Not a plan, not a direction, nothing to build. Notes from a brainstorm that started as a review of how the SoLex agents work (hotel-backoffice), then widened. Related: [collie-demo](collie-demo/README.md) (its § "Alex's workspace vision" is the seed of this), [hotel-backoffice](hotel-backoffice/README.md) (where the friction below comes from).

## One-liner

A personal, local-first workspace for working with agents: **a board where columns are agents, cards carry evidence, and humans have an inbox.** Personal first; team use possible.

## Similes (each covers a layer)

| simile | layer | what it contributes |
|---|---|---|
| **Obsidian** | data | local-first, your files, works offline with zero setup; team features added on top |
| **Odoo** | apps | install apps and configure them; apps share one data model, so a ticket links its doc, PR, demo, and agent runs without glue |
| **k8s for agents** | runtime + dev env (§ Runtime) | resource classes per persona, env per project; declarative desired state ("keep 2 devs on the Ready column"), reconcile (restart a dead/idle/compacted agent from its resume state), scheduling across machines (MBP / Mac Mini / cloud), resource limits (token budgets), health probes ("no progress for hours"). Borrow the ideas, not the YAML |
| **game IDE** (Unity/Godot editor) | workspace surface | one place to run, inspect, test, deploy, demo; per-project actions become buttons for you and verbs for agents (§ Workspace actions) |
| **Gru / minions** | UX, feel | you direct; many small eager, slightly chaotic workers; the inbox is the lab they report back to. The chaos is why review + evidence exist |
| **ClickUp alternative** | horizon | a team runs entirely on Studio's built-ins. A far vision, not a direction |

## Personal vs team

Personal-first; the team sees the outputs, like git (you work locally, the team sees what you push).

- **Personal:** your agents/personas/sessions, your inbox + digest, drafts and experiments.
- **Team-shared:** tickets + status, review (diff + demo + agent findings + QA evidence), decisions (who or what decided, who approved), playbooks.
- New team-level problems: routing "needs a human" to the right person, not just the owner; **delegated authority with an audit trail**. SoLex's D-21 ("the architect decides on Alex's behalf, breaking calls escalate") is the single-user version.

## Capabilities and providers

Each capability is a slot with a local default and optional external providers. Agents use the same verbs whatever sits behind them (`ticket.create`, `publish`, `request_review`, `attach`).

| capability | built-in (local) | bring your own |
|---|---|---|
| tickets / board | local board | Linear, GitHub Issues, ClickUp |
| docs / notes | local markdown | Notion, Confluence, Claude Docs |
| review | local branch review (before any PR exists) | GitHub PRs |
| evidence | Collie Demo files | hosted demo server |

An external tool can play two roles; keep them distinct:
1. **Sync/publish target.** Local is the source of truth; part of it goes out for the team (RFC → Notion, demo → PR). Only relevant when sharing.
2. **Primary provider.** Someone who lives in Linear uses Linear *as* their ticketing; the local board steps aside.

One source of truth per capability; no two-way sync (the markdown ↔ Notion-blocks trap).

**Core** = the object model (ticket, doc, evidence, decision, run, inbox item) as interfaces + local defaults + the inbox + persona runtime + app host. Everything else is an app: Collie Demo, providers, sync targets, persona packs, playbooks.

## Git

Integrate, don't host. Hosting (permissions, CI, backups) is its own product, and teams won't leave GitHub. What Studio could own is the **review experience**, plus reviewing local agent branches before they are pushed. Forgejo on collielab could be a backend for Alex; it's not a Studio feature.

## Knowledge (docs, RFCs, wiki, playbooks)

Docs have a lifecycle with different audiences:

| stage | where | who |
|---|---|---|
| draft | local markdown | you + your agent |
| out for review | the team's tool (Notion / Linear doc / PR / …) | team + reviewer personas |
| accepted | frozen decision record, linked to the tickets it spawned | everyone; agents as constraints |
| living | wiki / playbook | team; agents as skills/context |

RFC flow: draft with your agent → publish to the team's tool → comments come back to your agent, which drafts replies/revisions for you to approve → accept → the decision is recorded and spawns tickets. Ownership is **handed off** per stage (draft = your markdown; after publishing = the published copy; accepted = frozen back), not synced.

Two audiences: humans browse and search; agents fetch as context (playbooks = skills, decisions = constraints). ctrl today is organized for Claude only.

## Personas and orchestration

- A persona = **profile** (role prompt, tools, permissions, owned paths) + **memory** (files, ticket history — never the session) + **triggers**. The **session is disposable**: boot, work, write back, exit; you can attach to chat when it's useful.
- **Kanban columns = personas.** A card moving Ready → Dev → Review → QA → Done *is* the handoff; each column's automation boots its persona; "Needs human" is a column = your inbox. The card is the message, so there's no relaying and no messages lost to idle sessions.
- Runtime swappable: Claude Agent SDK / headless `claude -p` / ACP to run other agent CLIs; a worktree per card.
- Roles that worked in SoLex: builder, an independent reviewer with fresh context (is the code right), QA (does it behave to the acceptance criteria), architect only for design-changing work, product/explore on demand.
- Phases: figuring out *what to build* = conversational (one lead, or a few independent threads, with parallel research/spikes underneath); *building* = parallel once there's a cutline, a contract, and acceptance criteria. Cycles back and forth; it's not a waterfall. "Work that needs you = few threads; work that doesn't = parallel." Independent threads that do need you (product vs stack) are fine as long as decisions merge in one place.

## Runtime and environments (the k8s layer)

The k8s simile is about **managing agents as workloads**: where they run, with what resources, in which dev environment. A full runtime + dev env layer, not just orchestration.

- **Resource classes per persona**, like pod requests/limits:
  - product / explore: light — reads docs, talks, no build; cheaper model or effort OK
  - QA: medium — needs a browser + a running app, not a compiler
  - dev: heavy — build, tests, DB, dev server; strongest model, most CPU and tokens
  - "resources" = model tier + effort, token budget, CPU/mem, and capabilities (browser, DB, network, secrets)
- **Environment spec per project**, since projects differ:
  - simple: each agent gets its own env (worktree + own port + own SQLite), fully parallel
  - heavy: can't be replicated per agent (big stack, external deps, can't deploy) → a shared env with **leases/locks**, or agents queue for it
  - QA's target varies: a local env, a per-branch preview, or a shared staging/deployed env
- **Env lifecycle**: provision → seed → run → teardown; health checks; nothing left behind (SoLex: stale dev servers holding ports, stuck shims pushing load avg to 260).
- **Registered hosts** (Alex's idea): register machines agents can run on — MBP, Mac Mini, collielab VM, a cloud box, a teammate's machine — each advertising what it offers (CPU/mem, OS, browser, Docker, GPU, network reach, which repos/secrets it may hold). Like k8s nodes or CI self-hosted runners. Work is scheduled onto a host that matches the persona's class + the project's env.
- **Agents instead of CI** (Alex's idea): with registered hosts, CI-shaped work (build, test, e2e, deploy checks) can be done by agents that also *act* on results — rerun a flake, bisect, draft the fix, attach a demo. Needs guaranteed resources and deterministic parts (the test run itself stays a script; the agent wraps it).
- **Process / system visibility** (Alex's idea): track what agents are *running* — dev servers, Docker containers/compose stacks, DBs, tunnels, background jobs — as first-class objects: owner (which agent / card / worktree), host, ports, logs, CPU/mem, started-at, health. A "`ps` for agents" in the UI, plus an API/MCP so an agent checks before starting ("a dev server for this worktree is already up on :7531") and can read another's logs. Lifecycle tied to the card: done/abandoned card → its processes reaped. Directly targets SoLex's stale dev servers holding ports, orphan postgres container, stuck shims at load avg 260. Pieces to study: Docker labels, process-compose / overmind, mise tasks, Tilt, Portainer.
- **Built-in agent browser** (Alex, 2026-09-25): a browser pane inside the workspace that human and agent share, like the Claude Code desktop app's browser pane or T3 Code's. The "viewport" of the game-IDE surface.
  - Same page for both: the agent drives it (read the page as text, click, screenshot, console/network), the human watches and can take over (sign-in, CAPTCHA, judgment calls).
  - **Tab per card / worktree**, pointed at that worktree's dev server port or a remote/demo env; tabs are processes in the registry, closed with the card.
  - **Recording built in**: the pane can run the Collie Demo recorder on whatever the agent does → evidence without writing a journey (the "record the agent's live session" stretch goal, native).
  - Previews start from project actions ("start dev server" → tab opens on it), like the desktop app's `launch.json` + preview.
  - Parallel headless workers still need isolated browsers (own profile, own port; CLI tools like `agent-browser` fit); the pane is for work the human wants to see. Never an agent on your real browser profile.
- **Placement**: schedule workloads onto machines (MBP, Mac Mini, cloud VM/sandbox) by resource class and env needs; heavy dev work off the laptop.
- **Declarative**: a project declares its env ("app + SQLite, seed script, ports from a range, preview deploy optional"); personas declare their class; the runtime reconciles (restart the dead, reap the idle, respect budgets).
- Existing pieces to study: devcontainers, Nix/devbox, mise (already used), Coder / Gitpod / Daytona (remote dev envs), e2b / Modal sandboxes, Cloudflare/Vercel preview deploys, herdr (agent sessions across machines).

## Workspace actions ("game IDE")

Alex (2026-09-25): a workspace where you can *do* a lot, like a game engine editor (Unity/Godot: play button, inspectors, consoles, everything in one surface), configured per project the Odoo way.

- **Actions, declared per project:** "how to run tests", "how to seed", "how to deploy", "how to start a demo env", "how to tail prod logs". Each is config (command + target host/env + inputs + what it produces), like mise tasks / VS Code tasks / `launch.json`, but surfaced three ways at once:
  - a **button/panel** for the human (test runner with results, deploy with status)
  - a **verb/tool** for agents (same definition, so what you teach the workspace, agents can use)
  - a **tracked run** (process registry: owner, logs, result, evidence), attachable to a card
- **Targets beyond local:** an agent can drive a **remote env** — a preview deploy, a demo environment, staging — not just a dev server. Provision → seed → run the demo → record it (Collie Demo) → tear down.
- **Panels are apps (Odoo):** a test-runner panel, a deploy panel, a DB inspector, a log viewer, a demo player. Install the ones a project needs; a project that never deploys never sees a deploy panel. Teach it to deploy → you get a deploy interface.
- Ties to § Teaching agents: actions are the concrete form of "agents learn verbs, teams write mappings".

## App delivery (open)

Web-hosted is out (Studio manages local dirs, processes, git). But "web UI" ≠ cloud:
- **Local daemon + web UI** (Jupyter / Kandev / Vibe Kanban shape): a daemon owns dirs, git, processes, envs; the UI is served on localhost, reachable from a phone through a tunnel. Registered hosts imply a daemon per host anyway (a k8s node agent), so the architecture is client/server by nature. Daemon = a fit for Go.
- **Electron shell** (Claude desktop, T3, VS Code, Cursor): cross-platform, embeds Chromium → the built-in agent browser can be driven over CDP and recorded. Heavy.
- **Tauri**: light, but uses the system webview (WebKit on macOS) → no CDP for the agent browser; would need a separate Chromium.
- **Native macOS (Swift)**: best feel, Mac-only, slowest for panel-heavy UI; WKWebView browser, same CDP problem.
- Lean: daemon + web UI as the core; an Electron shell when the browser pane needs it.

## Cross-agent portability

- **Skills:** Agent Skills (`SKILL.md` folders, spec at agentskills.io) started at Anthropic and is now an open standard read by Claude Code, Codex, Copilot, Cursor, Gemini CLI, OpenCode, Antigravity, Kiro. Discovery paths differ per tool (`.claude/skills`, `.cursor/skills`, …) → Studio would install one copy and link it where each harness looks.
- **Instructions:** `AGENTS.md` is the cross-tool file; Claude Code reads `CLAUDE.md` (which can import `AGENTS.md`).
- **Tools:** MCP is cross-agent.
- **Harness-specific** (Studio would compile to each): subagent definitions, hooks, slash commands, permissions/settings, plugin packaging. **ACP** covers the client ↔ agent link (a UI driving different agent CLIs).

## Workspace MCP (idea)

MCP servers can already be scoped: `.mcp.json` in a project (shared), per-project local scope, or user-wide. **stdio** servers are processes the harness spawns per session and kills with it; **HTTP** servers are long-running (local or remote) and shared across sessions. `.mcp.json` does not load from parent dirs, so a context folder can't rely on it for repos below it.

Idea: **one workspace MCP** exposing the context to any agent in any harness: its repos, notes/vault search, the context's tracker and docs (ClickUp for enable, Notion for hookdeck), actions (test, seed, deploy, demo), the process registry, hosts, cards. Run as the daemon's HTTP endpoint, registered once at user level; it resolves the workspace from the session's cwd / MCP roots. This is probably **Studio's agent-facing API**: the UI is for the human, the workspace MCP is for agents, same daemon behind both.

**Transports (2026-09-27):** same capabilities either way (tools, resources, prompts, notifications). stdio = spawned per session in the session's cwd/env, no auth, state dies with the session (observed: 5 `railway mcp` processes for 5 open sessions; subagents reuse the parent's). HTTP = one long-running server, shared state, needs to be told the workspace (MCP roots / header), auth if not localhost, can live on another host. Best of both: a tiny **stdio shim per session** (knows cwd for free) forwarding to the **shared daemon** (holds registry, cards, locks).

**Skills over MCP (checked 2026-09-27):** the official MCP Skills extension (`io.modelcontextprotocol/skills`, SEP-2640, Final 2026-09-13) lets a server publish Agent Skills: `skills/list` (frontmatter + file manifest with digests), `skills/get`, and `resources/read` for `SKILL.md` + supporting files. Purpose: "ship the manual with the product". Client support still rolling out; check each harness. For Studio: the workspace MCP could **serve the context's skills** next to its tools, one source for every harness, sidestepping per-tool skill folders and parent-dir loading. Before this: MCP *prompts* (user-invoked templates, slash commands), resources, server instructions, or tools that return "how to drive me" text (T3's `device_open`).

**Config, not code:** one generic workspace MCP reads a per-workspace file; each action becomes a tool; `confirm: true` = the agent must ask first. New workspace = new config, not a new server.

```yaml
# workspace.yaml (context folder)
actions:
  test:   { run: "pnpm test", cwd: "be" }
  seed:   { run: "pnpm db:seed", cwd: "be" }
  deploy: { run: "gh workflow run deploy.yml", confirm: true }
docs: clickup
```

Building one is small: official SDKs (TS / Python / Go); a stdio server with a couple of tools is ~30 lines; register with `claude mcp add <name> --scope project -- <cmd>` or `claude mcp add --transport http <name> <url>`. Natural first target: SoLex (mise tasks, dev server, seed already exist).

## Teaching agents

Every user has to teach agents how to work locally and with their team. Keep it small, and make it config rather than prose:

| layer | holds | written by |
|---|---|---|
| Studio defaults | local protocol: personas, columns, doc lifecycle, evidence | shipped |
| team playbook | where things live: tracker + status mapping, doc space, review rules, bug intake | one teammate, once; shared file (like `CODEOWNERS`) |
| personal | style, what needs your approval, autonomy level | you |

- **Agents learn verbs; teams write mappings; corrections become rules.**
- The agent proposes the setup from the connected tools ("Linear has Todo/In Progress/In Review/Done — map to Ready/Dev/Review/Done?").
- A correction ("RFCs need 2 approvals") is offered as a playbook rule, durable and shared, unlike chat memory.
- Evidence: Alex's `CLAUDE.md` + `docs/workflow.md` + the SoLex roster/checklist are this teaching, done by hand in prose. The QA checklist growing to 25+ prose items shows why it should be structured.

## Team hooks

Events run the same pipeline:
- bug report (issue / Sentry / Discord / email) → triage persona reproduces it with a Collie Demo "before ✗" → fix → PR with before/after demo → human review
- a person opens a PR → reviewer persona + a demo of the change
- CI red on main → fixer drafts a PR
- a decision is needed → routed to its owner's inbox

Guardrails: opt-in per label/repo, a budget per event, dedup, humans merge. Could be tried today with GitHub Actions + Claude Code's GitHub action / scheduled routines + Collie Demo.

## Friction observed in SoLex (2026-09-19 → 25)

The manual version's pain = candidate requirements. Setup: 5 long-lived persona sessions (architect hub; dev, explore, product, QA), ctrl files as shared memory, `SendMessage` pings, a worktree per role.

- **Worked:** an independent verifier (N1–N45 real defects, a recurring concurrency class invisible to unit tests); findings → checklist rules; state in files survives compaction; delegated decisions unblocked throughput; dev + QA shipped slices 5.7–5.8 alone overnight while architect/product were unreachable.
- **The hub became relay + scribe:** ~120 architect commits, mostly "accepted / relayed / re-briefed"; the loop didn't slow when it vanished.
- **Liveness:** idle sessions unreachable by name; "unchanged for hours — is it receiving messages?"; messages relayed twice.
- **Context ceremony:** 200k clean stops, an hourly usage cron, pre-compaction checkpoints — built, then retired.
- **Write amplification:** one landing → 6–8 file writes across profiles/notes/log/progress/qa; bookkeeping commits about bookkeeping; rebase contention.
- **Shared machine:** load avg 190–260 from stuck shims, port squatting, "environmental" e2e reds.
- **No scope brake:** gap list grew G1–G35, slices 5.1–5.8; nobody owned "not v1".
- **Human attention unbudgeted:** staging passes requested repeatedly and not done; mockups unreviewed. rrweb journeys (watch, don't read) were the right instinct → Collie Demo.
- **Serial build, parallel discovery** — the wrong way round: discovery depended on Alex anyway; the build had one dev.
- **Rules in prose accrete:** 25+ checklist items, 30 decisions, a growing boot cost per session.

## Landscape (see collie-demo § workspace vision for detail)

**T3 Code** (t3.codes, pingdotgg/t3code; checked 2026-09-25: MIT, ~22k★, free, BYO subscription): one GUI over many harnesses (Claude Code, Codex, Cursor, OpenCode, Antigravity, Grok), switch harness/model mid-thread, a git worktree per thread, diff review, one-click PR, custom actions; desktop + web + iOS/Android remote control of agents on your machine. Sits at the harness-front/runtime layer, not board/personas/env/evidence. Kandev (kanban + worktree per task + approval gates + agent CLIs via ACP; no proof/tests), herdr (the runtime/multiplexer layer), Vibe Kanban, Claude Squad, Crystal/Nimbalyst, Sculptor, Conductor, Copilot agent, Devin. Crowded: orchestration and boards. Less crowded: **evidence** (demos, before/after, QA tied to acceptance criteria) and the **attention inbox**.

## Studio as a distro (packaging of tools)

Alex (2026-09-25): Studio is a **packaging** of multiple tools, not one app — fine with it being an **opinionated distro / workspace with git management tooling built in** (worktrees, branches, review, local → Forgejo/Gitea/GitHub). Closer to a Linux distro than to a product: pick good existing pieces, configure them to work together, add glue where nothing exists.

| need | candidate piece |
|---|---|
| review, local → hosted | a review tool + Gitea/Forgejo (or GitHub) |
| tickets | a self-hosted tracker (or Linear/GitHub for teams) |
| wiki / notes | an Obsidian vault (plain markdown, local-first, synced) |
| agent sessions | herdr-like runtime over Claude Code / Codex |
| skills, personas, hooks | harness plugins (see below) |
| evidence | Collie Demo |

Glue Studio would own: the card ↔ session ↔ evidence links, the inbox, persona/env/host config, install + wiring.

## The workspace-repo problem

The workspace in question is **`hub/alexluong/hookdeck`** (remote `hookdeck-workspace`): a personal repo wrapping the company repos as submodules (core, outpost, hookdeck-cli, terraform-provider-hookdeck, http-ingestion, website, fde/amp-labs/*). It holds what the team never sees: `notes/` (~76 investigations, specs, RFC drafts), `qa/` suites, `.bruno/`, `mise.toml` + env, `.mcp.json`, ~30 skills in `.claude/skills` (worktree, notes, qa, investigate, orchestrate, outpost-*, notion-publish-spec, …), plus `AGENTS_core.md` / `AGENTS_outpost.md` and submodule worktrees as flat siblings (`core-wt-*`, `outpost-wt-*`). Rule: never surface the workspace in team output. Some submodules also carry their own `.claude/` / `CLAUDE.md` / `AGENTS.md` (team-shared).

ctrl plays the same role for personal projects. Both work, but using Claude consistently requires wrapping your repos in a personal super-repo. Alex doesn't want that as the precondition.

Wanted: start Claude in any repo and get the same personal setup, the repo's own (team) skills, generic skills (analysis), and access to notes, with no wrapper repo.

### Context folder layout (2026-09-27)

```
~/workspaces/hookdeck/          ← small git repo: tracks only its own files
  .gitignore                    ← ignore every repo + worktree dir
  workspace.yaml                ← repos (name, url, base branch), actions, docs provider
  CLAUDE.md / AGENTS.md         ← context rules (loaded from parent by any repo below)
  .claude/skills/               ← context skills (same)
  notes/                        ← personal notes (or an Obsidian vault)
  core/ outpost/ cli/ …         ← independent clones, gitignored (not submodules)
  core-wt-<slug>/ …             ← worktrees, gitignored
```
- `workspace.yaml` replaces `.gitmodules` as the manifest; a bootstrap script (or a workspace action) clones whatever's missing on a new machine. No pins: each repo follows its own branch.
- Start in a repo for single-repo work; start at the root for cross-repo work.
- Migrating hookdeck: `git submodule deinit` + remove from the index, keep the dirs as ignored clones, write the manifest.
- Open: `~/workspaces/<context>/` vs keeping them under `~/git/…`.

Split by what each thing is:

| thing | lives in | reaches every session via |
|---|---|---|
| personal skills / agents / hooks | a personal **plugin** (a git repo as a marketplace), or `~/.claude` managed by dotfiles | installed once per machine; user-level, so present in every repo |
| team skills | each repo's `.claude/` (checked in) + a team plugin marketplace for cross-repo ones | the repo itself / team install |
| notes, wiki, project docs | an **Obsidian vault** (markdown), synced (iCloud / Obsidian Sync / git) | added as a directory the session can read/write (additional directory, or an MCP over the vault) |
| work / tickets | tracker | MCP |
| domain data (bookkeeping, RE) | its own repo; it's a domain, not a workspace | normal repo |

Result: no wrapper repo; the vault takes the `notes/` role, a personal plugin takes the `.claude/skills` role, env/QA tooling stays per project. Worktrees then live wherever the runtime puts them, not as siblings inside a wrapper. Open: how a session knows *which* vault notes belong to the repo it's in (a convention like `vault/projects/<repo>/`, or a frontmatter tag the plugin resolves).

## Retrieval / RAG for personas (idea, later)

Alex: would a RAG system for personas make sense later?

- **Now: no.** Agentic search (grep + read) over structured markdown works at hundreds of files, and exact ids (N29, D-21, function names, ticket numbers) are better found by grep than embeddings.
- **When it would:** the corpus outgrows grep: years of notes across projects, tickets, PR reviews, Notion, Slack; or fuzzy recall ("seen this bug before?", "what did we decide about retries?") where the words aren't known.
- **Per persona = a retrieval policy, not a separate store:** one index, scoped per persona. QA: cases + past findings. Dev: decisions + conventions + similar past PRs. Reviewer: checklist + past review findings. Product: specs + client inputs.
- **Main risk is staleness:** retrieving a superseded decision as truth (SoLex's README kept stale Go/Hookdeck sections). Needs metadata: type, status (accepted/superseded), project, date, supersedes, plus citations back to the source.
- **Order:** structure first (frontmatter + a decision registry), then hybrid search (keyword + embeddings) exposed via MCP over the vault, then per-persona scopes. A Studio capability ("retrieve") with swappable providers.

## T3 Code, closer look (2026-09-27)

Alex is trying T3 Code (desktop 0.0.42) as the daily driver to see how far it goes. Read from source (pingdotgg/t3code @ main, 2026-09-27). It already covers much of Studio's runtime + "game IDE" layer.

**Architecture:** the same shape we landed on. A local **server owns everything** (provider processes, PTYs, git, files); web / desktop / mobile are thin clients over authenticated RPC. State = an event log (commands → decider → events + projections; checkpoints as hidden git refs). **Multiple environments**: one client connects to many servers (SSH-installed onto a remote host, Tailscale, LAN pairing, T3 Connect relay for mobile/push); new threads can be **load-balanced across machines by CPU/mem** (Prefer / Less often / Manual only per machine). Devcontainers only for developing T3 itself.

**Objects:** environment · project (one directory) · worktree · thread (durable conversation, outlives processes) · turn / activity · provider instance (one account/config) · device (simulator/emulator).

**Agent visualization:** an **Agents** panel = fleet view (fixed-height rows: status, current activity, model/effort, tokens, elapsed, tool uses); in chat, one expandable row per spawn batch. T3 doesn't orchestrate; it **parses each harness's native events** (Claude Agent SDK `task_started/progress/notification` + `parent_tool_use_id`; Codex `collabAgent/*`; others) into one normalized `task.* / tool.*` model, folded client-side into agents (subagent / batch / workflow / workflow agent, with phases and parent). Patterns: all in-flight states read "Working", only settled states differ; "Idle · resumable" is distinct; Claude Code workflows render as phased groups.

**Panels:** diff, files, **browser preview**, device (iOS sim / Android emu), terminal, PRs, agents.
- **Agent-driven shared browser**: Electron webview over CDP + Playwright's injected runtime; agent tools `preview_open/navigate/snapshot/click/type/evaluate/wait_for/resize` and **`preview_recording_start/stop` → a webm "evidence file"** the agent can cite. Human can pick/annotate elements into the composer; cookie import into a browser profile. Only while a desktop client is connected (no headless browser on a bare server). Per-project toggle.
- **Port discovery**: `lsof` listening ports, HTTP-probed, tied to each thread's terminal PIDs.
- Terminals are server-owned, shareable, reattachable, but not an agent tool (agents use their harness's shell).

**Project config (`t3.json`):** `scripts[]` (name, command, icon, `runOnWorktreeCreate`, `async` = hold the agent until setup finishes, `previewUrl` + `autoOpenPreview`), `defaultThreadEnvMode` (worktree/local), `worktreeSubmodules`. Settings layer project override → environment → t3.json → built-in, with the UI showing the source. Scripts are **human buttons, not agent tools**. No plugin system.

**Git:** worktree per thread (or local); fan one prompt out to several models = several threads/worktrees; commit/push/PR with generated text following AGENTS.md/CLAUDE.md conventions; GitHub, GitLab, **Forgejo/Gitea**, Bitbucket, Azure DevOps; multiple PRs per thread, stack merge/rebase; threads **auto-settle on merge or after 3 days idle**; worktree auto-cleanup.

**Skills / MCP:** pass-through (native CLAUDE.md, `.claude/skills`, MCP config apply). T3 adds a short runtime note and **its own HTTP MCP with a per-thread credential and capability gating** (preview, device, pull requests) — a thread-scoped cousin of the workspace-MCP idea.

**Attention:** desktop notifications; mobile push + iOS Live Activities (done / failed / needs approval / question) via T3 Connect; threads pinned / snoozed / settled; permission modes Supervised → Full access; multiple accounts per provider.

**Resources:** Rust sidecar samples CPU/mem/IO per process (only while watched), diagnostics UI with signal/kill. Not a registry: no owner/card, no agent API.

### Against Studio
- **Covered:** harness front-end, worktree per thread + setup scripts, shared agent browser + recording, device viewport, review/PR incl. Forgejo, remote hosts + mobile, subagent visibility, cleanup, much of the attention loop.
- **Partial:** hosts (load balancing, no capability advertising / resource classes / leases); actions (human-only buttons, no tracked runs); process registry (telemetry + port discovery, no ownership / agent API); evidence (webm, not tied to acceptance criteria; not a seekable DOM replay with synced panels → Collie Demo still distinct); inbox (per-thread, no cross-project digest).
- **Missing:** board / tickets, personas + triggers + budgets, config-driven workspace MCP, env specs / seeding / leases, multi-repo workspaces (a project is one dir), docs/decisions lifecycle, team routing.
- **Plug-in points:** outside T3 — a Studio daemon's workspace MCP registered at user level reaches every T3 session; Studio can write `t3.json` scripts. In a fork (MIT) — scripts as agent tools, new MCP toolkits beside `apps/server/src/mcp/toolkits/*`, a board panel, cards in the event log. T3's RPC is versioned but internal.

### T3 evidence, in detail
- Agent calls `preview_recording_start` on the shared browser tab, acts, then `preview_recording_stop` → a compressed **webm** (≤50 MiB) is written as an **evidence file** in the agent's environment and its path returned. The compositor draws **click rings and key-press labels** on the video (`apps/web/src/browser/recordingCompositor.ts`).
- The runtime note tells every agent it can **embed images and videos in its reply** via Markdown with absolute paths → evidence lives in the thread.
- Screenshots / page state come from `preview_snapshot` / `preview_evaluate`. **SnapShots** is the other direction: the human captures any window (with its accessibility data) as *input* to the agent.
- Not there: steps/captions, console/network/server timeline, a small shareable file, rerun as a script, linking to a PR or acceptance criteria.
- **Integration path without a fork:** the Collie Demo in-page recorder (lab `src/inpage.js`) is a plain script → an agent can inject it with `preview_evaluate`, drive the tab, then collect the `.replay` — Collie Demo evidence inside T3's browser.

### Multi-repo in T3
A T3 project = one directory; a worktree is per repo. Options for a context folder: add each repo as its own T3 project (worktree per thread works), and add the context root as a project in `local` mode for cross-repo threads. Gap: a change spanning FE + BE wants a **worktree set** (matching branches in both repos, created and cleaned together) — T3 doesn't have it; a Studio idea (the card owns a worktree set). `t3.json` has a `worktreeSubmodules` flag, so T3 has some submodule awareness.

### Patterns worth borrowing
Capability negotiation via an environment descriptor (clients/servers upgrade independently) · per-thread MCP credentials with capability gating · tools that return "how to drive me" instructions on open instead of an always-loaded prompt · recording tool returns an evidence path the agent cites · one agent model normalized across harnesses · settings layering with visible provenance · hidden-ref checkpoints for per-turn diff/revert · auto-settle driven by PR state · native helpers as supervised children.

## Studio as a framework (2026-09-27)

Alex: Studio could also be a **framework** — actions and patterns for how to do things. Like Rails (convention over configuration), Shape Up, or the 12-factor app: a way of working, packaged so it runs.

Three layers, each useful without the next:
1. **Framework** — conventions + patterns, portable across harnesses via the open standards (Agent Skills, AGENTS.md, MCP):
   - schemas: `workspace.yaml` (repos, actions, docs/tracker providers), cutline, card/issue template, PR template, decision record
   - patterns: lead / worker / reviewer / QA; cutline as scope brake; explore conversationally, build in parallel; context folder; worktree set per card; evidence per PR; escalation rules; corrections → rules; doc lifecycle (draft → review → accepted → living)
   - delivered as a plugin (skills + templates) + docs
2. **Tools** — Collie Demo, the config-driven workspace MCP, bootstrap/worktree-set scripts.
3. **App** — optional: T3 (or any harness UI) may be enough as the surface; build Studio's own UI only for what's left (board, inbox).

Framework-first is cheap, starts now, and is what `docs/workflow.md` + the SoLex protocol already are, in prose. Codifying it = turning that prose into skills, schemas and actions.

## Tool picks: tasks (2026-09-27)

Want: "Obsidian for tasks" — local-first, plain files, git-versioned, agents read/write directly. Plane: AGPL but its licensing/pricing moves put Alex off.

| option | shape | notes |
|---|---|---|
| **Backlog.md** (MrLesk/Backlog.md) | a task = a markdown file in the repo; CLI + terminal kanban + local web UI | built for humans + agents; acceptance criteria / definition of done, dependencies, milestones, docs + decisions; no server/account/telemetry. Lives in any git repo → fits a context folder |
| **Obsidian itself** | tasks as notes with frontmatter; Bases + a kanban view plugin (Kanban Bases View, Base Board…) | one tool for notes + tasks; the board depends on community plugins; deps / AC only by convention |
| Vikunja | self-hosted web app, AGPL, Go | light; agents go through its API, not files |
| Huly | self-hosted all-in-one, EPL | heavy |
| Plane | self-hosted, AGPL community edition | commercial pressure |
| ~~Planka~~ | now "Fair Use" source-available | avoid |
| GitHub Issues / Projects | hosted | best PR linking (`Closes #n`); not local-first |

Lean: **Backlog.md in the context folder** (tasks next to notes and the manifest; the card id goes in branch names and PR text), with Obsidian for notes. Team contexts keep their tracker (ClickUp for enable, Hookdeck's own) as the provider.

## Notes + git (open, 2026-09-27)

Something to think about, not decided. History for notes matters less than for code, but Alex wants meaningful commits over "vault backup" snapshots.

- Obsidian is git-unaware; the Obsidian Git plugin gives timed/debounced auto-commit ("backup" messages), manual commit, branch create/switch, diff + history views. No worktrees, no PRs; switching branches swaps files under Obsidian (index churn, unresolved links). Parallel branches = a worktree per branch opened as its own vault (commit `.obsidian/`).
- Idea: a **commit cron** (workspace action) — dirty tree under `notes/`, `backlog/` → `claude -p` reads the diff + the in-progress task → task-sized commits with real messages; auto-commit when confident, otherwise propose in the inbox. Never touches other paths.
- Idea: **two lanes** — trunk for journal/investigations/task progress (progress can live in the Backlog.md task file); branch + PR only for docs that need review (RFC/spec), with the agent doing the git side and review on GitHub/Forgejo. Branch-per-task for all notes rejected-ish: unmerged notes are hidden from other agents, and Obsidian handles branches poorly.
- Gap for Studio: review UI for notes branches.

## Value check: Studio vs plain Claude Code (2026-09-25)

Question (Alex): with all this, is a tool warranted, or is Claude Code + skills enough?

**Claude Code already covers a lot, natively or with light config:** subagents with worktree isolation, workflows (scripted multi-agent), skills, hooks, scheduled/cloud routines, desktop sessions + messaging between them, remote control, the GitHub action (bug/PR triggers), MCP connectors (Linear, Notion, ClickUp, GitHub), artifacts/docs with comments routed back to Claude. And it improves fast; the vendor is building toward this space (as are GitHub, Cursor, Devin).

**What it doesn't do today** (the candidate Studio-only list):
- a durable **board as the orchestration substrate** (cards drive personas; state outside any session)
- a cross-project **attention inbox / digest**
- **evidence in review** (demos, before/after, QA tied to acceptance criteria) → Collie Demo
- **hosts + environments**: registered machines, resource classes, env specs, leases, cleanup
- **declarative personas** with budgets and health/reconcile
- **vendor neutrality**: mixing agent CLIs (only matters for teams, not Alex)

**Honest read:**
- For Alex personally, a lot is reachable with Claude Code + skills + GitHub Projects + Collie Demo + a few scripts. Studio earns its place as the **organizing layer** (below), not by replacing the harness.
- As a product for others, the orchestration/board part has little moat (crowded, platform-adjacent). The differentiated parts are evidence, the inbox, and possibly env/hosts.

**How to tell:** run the manual protocol on plain Claude Code for a while and sort each friction into *can't / can with config / can with a skill*. Only the "can't" pile is Studio. Collie Demo is already in that pile.

## Shape: an organizing layer over existing harnesses

Studio does **not** run the agent loop. Harnesses (Claude Code, Codex, …) do: tools, context, skills, MCP, models. A multiplexer/runtime (herdr or similar) keeps sessions alive on hosts and attachable. Studio organizes them.

```
Studio      — organize: board/cards, personas, inbox, evidence, env specs, host registry
  ↓ launches / attaches / reads back
runtime     — herdr-like: sessions on hosts, alive, attachable, across machines
  ↓ runs
harness     — Claude Code, Codex, …: the agent loop, tools, skills, hooks, MCP
  ↓ on
hosts       — MBP, Mac Mini, collielab, cloud
```

"Thin" means: little code of its own; it pushes config *into* the harness instead of inventing parallel systems — a persona compiles to a harness session prompt + skills + permissions + model/effort; a playbook compiles to skills/`CLAUDE.md`; a card's context is what the session boots with; the harness's hooks report back to the card. The harness gets better for free; Studio stays about **how work is organized** (Alex, 2026-09-25: "mostly around how to organize them").

## Stance

- **A personal tool that could become a product**; product is not important. Not a learning project.

- Collie Demo stays the first real piece. A core, if ever, emerges once 2–3 apps need the same objects.
- Parking lot for thoughts, not a roadmap.
