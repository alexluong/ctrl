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
- **Placement**: schedule workloads onto machines (MBP, Mac Mini, cloud VM/sandbox) by resource class and env needs; heavy dev work off the laptop.
- **Declarative**: a project declares its env ("app + SQLite, seed script, ports from a range, preview deploy optional"); personas declare their class; the runtime reconciles (restart the dead, reap the idle, respect budgets).
- Existing pieces to study: devcontainers, Nix/devbox, mise (already used), Coder / Gitpod / Daytona (remote dev envs), e2b / Modal sandboxes, Cloudflare/Vercel preview deploys, herdr (agent sessions across machines).

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

Kandev (kanban + worktree per task + approval gates + agent CLIs via ACP; no proof/tests), herdr (the runtime/multiplexer layer), Vibe Kanban, Claude Squad, Crystal/Nimbalyst, Sculptor, Conductor, Copilot agent, Devin. Crowded: orchestration and boards. Less crowded: **evidence** (demos, before/after, QA tied to acceptance criteria) and the **attention inbox**.

## Stance

- Collie Demo stays the first real piece. A core, if ever, emerges once 2–3 apps need the same objects.
- Parking lot for thoughts, not a roadmap.
