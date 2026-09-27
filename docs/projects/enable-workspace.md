# Project: Enable workspace (`~/workspaces/enable`)

Alex's personal agent workspace for Enable (EButler-QA) work. The first concrete run of the Collie Studio ideas (context folder, team-mode protocol, Backlog.md + Obsidian). See `collie-studio.md` for the thinking behind it.

**Status (2026-09-27): plan confirmed, about to scaffold.** Local only: no remotes, nothing pushed, the team repos stay as they are.

## Why Enable first (over hookdeck)

- There's a real stream of incoming work (ClickUp tickets, bug reports), so the protocol gets tested on real input right away.
- Much of it exists already: the super-repo dev harness (`dev/cli.ts`), per-worktree stacks (`STACK_NAME` + `PORT`), Playwright `e2e/`, `qa/suites`, and skills like `/worktree`, `/qa`, `/investigate`, `/ticket`, `/spec`, `/session`.
- Teammates open PRs there too (Taha, Hieu, Sherif), so review and "done" get tested against a real team.
- hookdeck is round 2. It needs a restructure first (notes to Obsidian, submodules to a context folder).

## Current state (`~/git/hub/ebutler-qa/`)

- `workspace.git`: bare clone of `EButler-QA/workspace`, the team super-repo. `workspace/` is a plain folder (not a git repo) holding its worktrees (`main/`, `qa/`, `dev/`, 15 total).
- Super-repo submodules: enable-backend, enable-frontend, enable-connectors, ebchat-saas-backend, ebchat-saas-dashboard, ebchat-sdk, enable-internal-app. The repo itself also holds `dev/`, `e2e/`, `qa/`, `terraform/`, `scripts/`, the website.
- **Submodules:** they aren't there for version pinning, just convenience. The long-term goal is one monorepo with the other repos deprecated, but not now. Don't do an in-between step (gitignored clones); go straight to the monorepo when it happens.
- `.claude/` in each worktree is gitignored and cloned from `EButler-QA/workspace-claude.git` (per-dev branch, Alex's = `alexluong`). Contents: skills (investigate, local-env, qa, seed, session, spec, ticket, worktree, ops-*), the `guard-write-access.sh` hook (asks before running a command with write-DB credentials), and the ClickUp MCP.
- Repos outside the super-repo but still Enable work: `enable_loyalty_app`, `al-batteel`, others.

### Parallel stacks

- `dev/compose/docker-compose.yml`: `name: enable-${STACK_NAME}` keeps containers, networks and volumes separate per worktree. Caddy publishes `${PORT}:80`, and `dev/cli.ts syncEnvFiles` rewrites the env URLs to match. Both are set in each worktree's `dev/env/.env`.
- Existing convention: `PORT` steps by 100 (main=4500, qa=4600, dev=4400). There are already clashes (dev and core both use 4400; qa and zones both use 4600).
- **Clash:** three hardcoded host ports: `6001` (soketi), `9099` and `4400` (firebase emulator). A second stack that starts these fails to bind. Fix (team repo, Alex's call): `${SOKETI_PORT:-6001}` and similar, or drop host bindings that aren't needed.
- Note `4400` is both the firebase emulator port and a stack `PORT`.

## Layout

```
~/workspaces/enable/                 ← git repo, local only (no remote yet)
  .gitignore                         ← repos/, wt/, .env*, vault/.obsidian/workspace*.json
  AGENTS.md                          ← context map: repos, stacks/slots, protocol, conventions (no CLAUDE.md)

  .agents/                           ← harness-neutral source of truth
    skills/                          ← Agent Skills (SKILL.md)
      local-env/ seed/ worktree/ qa/ investigate/ spec/ ticket/ ops-*/   ← copied from workspace-claude
      lead/                          ← new
    roles/                           ← new: role prompts, harness-neutral
      dev.md  reviewer.md  qa.md

  .claude/                           ← Claude adapter, no content of its own
    skills → ../.agents/skills       ← symlink
    agents/dev.md reviewer.md qa.md  ← thin wrappers: frontmatter + "follow .agents/roles/<x>.md"
    hooks/guard-write-access.sh      ← copied
    settings.json                    ← hooks, permissions, plugins, memory (see § Claude config)

  vault/                             ← Obsidian vault (a subfolder so Obsidian doesn't index repos/ and wt/)
    backlog/                         ← Backlog.md
    work/<task-id>/                  ← dev.md, review.md, qa.md, evidence/
    notes/                           ← knowledge
    memory/                          ← Claude auto-memory (autoMemoryDirectory), in git + visible in Obsidian
    digest.md                        ← lead's digest / needs-alex queue

  repos/                             ← gitignored
    workspace.git                    ← fresh bare clone of EButler-QA/workspace
    (others as needed: enable_loyalty_app, al-batteel, …)

  wt/                                ← gitignored worktrees of workspace.git
    main/                            ← .claude → ../../.claude (symlink; the team repo gitignores .claude)
    task-12/                         ← same, + STACK_NAME=t12, PORT from its slot
```

### Decisions

- **Personal, outside `ebutler-qa/`:** it's Alex's setup, not the team's.
- **One git repo for everything personal:** agent config, skills, notes and backlog. One clone, one history. Commit prefixes separate the busy parts from the quiet ones (`notes:`, `task-12:`, `skills:`).
- **Harness-neutral first:** `AGENTS.md` + `.agents/skills` + `.agents/roles` are the content; `.claude/` is only wiring. See how Claude fits before adding anything Claude-only.
- **`roles/`, not `agents/`:** `.agents/agents/` reads badly, and a *role* (neutral content) differs from an *agent* (harness-specific definition that runs it). A role can also be loaded into an interactive session (`/work task-12`) instead of spawned as a subagent.
- **Backlog.md + Obsidian, in one vault:**
  - agents change tasks only through the `backlog` CLI
  - Alex uses `backlog browser` as the board, and Obsidian to read, link and keep notes
  - small hand edits in Obsidian are fine
- **Existing things stay put:** skills are *copied* from workspace-claude, and the `ebutler-qa/` worktrees keep working. New work goes through `wt/`, and the old worktrees retire gradually.

### AGENTS.md in Claude Code (docs, 2026-09-27; local is v2.1.283)

- Claude reads `AGENTS.md` natively (v2.1.277+), but by default **only when there's no `CLAUDE.md`/`CLAUDE.local.md` in the working dir or above it**. Files under `.agents/` are never read as instructions.
- **Catch:** the team repo has its own `CLAUDE.md`. So a session started *inside* `wt/task-12/` sees that `CLAUDE.md` and skips `~/workspaces/enable/AGENTS.md`.
- Fix: user-level setting `pluginConfigs."agents-md@builtin".options.instructionFiles = "claude-md-and-agents-md"` in `~/.claude/settings.json`. It's ignored in project settings, so it has to go there. Alternatively, start sessions at the workspace root.
- Sessions started at `~/workspaces/enable/` (the lead) have no `CLAUDE.md` above them, so `AGENTS.md` loads.

## Claude config

Zero global tools; the workspace declares everything (see `../claude-config.md`).

**User level** (`dotfiles/dot/.claude/settings.json`, applied at setup time):
- `autoMemoryEnabled: false`, so nothing gets saved machine-local by accident.
- `pluginConfigs."agents-md@builtin".options.instructionFiles: "claude-md-and-agents-md"`, so sessions inside `wt/*` (team `CLAUDE.md`) also load the workspace `AGENTS.md`.
- Open: `disableClaudeAiConnectors: true`. It removes Claude Docs / Gmail / Calendar / Drive / ClickUp from CLI + T3 sessions (desktop is controlled on claude.ai).

**Workspace** (`~/workspaces/enable/.claude/settings.json`):
- `autoMemoryEnabled: true` + `autoMemoryDirectory: ~/workspaces/enable/vault/memory`. Check that project `true` beats user `false`; the directory needs the folder trusted.
- `enabledPlugins`: `gopls-lsp` (enable-connectors is Go), `frontend-design`. Moves from `ebutler-qa/workspace/main/.claude/settings.local.json`.
- Hooks: `guard-write-access.sh`. Permissions: a workspace allow list (docker, bun, make, mongosh, …).
- MCP: none at first; ClickUp through the CLI (§ ClickUp access).
- `AGENTS.md` gets a "What to remember" section: client/tenant facts, environment quirks, decisions → memory; task status → Backlog.md; long-form knowledge → `vault/notes`; never credentials.

**Skills that need rewriting:** `ticket`, `investigate`, `spec` and `ops-delete-branches` call the claude.ai ClickUp connector tools (`mcp__claude_ai_ClickUp__*`), which are now disconnected. Point them at clickup-cli when copying. (`ticket` has `disable-model-invocation: true`, so only Alex can trigger it, and it isn't in Claude's skill list.)

**Audit of the current setup, T3 in `ebutler-qa/workspace/main` (2026-09-27):**
- The team `CLAUDE.md` loaded, `AGENTS.md` did **not** (the CLAUDE.md links it but doesn't `@import` it), which confirms the catch in § AGENTS.md.
- The 131-note memory index loaded.
- 12 of 13 skills, plus the plugins (frontend-design, LSP via gopls) and the Artifact tools off, all as expected.
- The `mcpServers.clickup` block in `.claude/settings.json` is ignored (no server).

**Memory migration:** copy the existing machine-local notes into `vault/memory/` once and review them:
- `~/.claude/projects/-Users-alexluong-git-hub-ebutler-qa-workspace-git/memory/` (131 notes)
- `…-ebutler-qa-workspace-dev/memory/` (3)
- The originals stay until the move is verified.

**Surfaces:** open the workspace root in the desktop app / T3 (not `ebutler-qa/workspace`, which is a plain folder and loads nothing). Per-task sessions open `wt/task-N`, which gets config through the `.claude` symlink.

## Work items

- Backlog.md task IDs (`task-N`), statuses: `todo`, `in-progress`, `review`, `qa`, `needs-alex`, `done`.
- **The source is just a field.** A task can come from a ClickUp ticket, a freeform ask, a bug found mid-work, a `/spec`, or a pasted report. The lead only works with the queue. The source gets an update when the task finishes, if it has one (e.g. a ClickUp comment, which is outward-facing and needs Alex's OK).
- **One ID for everything:**
  - agents `dev:task-12` / `review:task-12` / `qa:task-12`
  - worktree `wt/task-12`, branch `task-12-<slug>`
  - `STACK_NAME=t12`
  - PR title `… (task-12)`
  - notes `vault/work/task-12/`
- **History:**
  - short attributed events go in Backlog.md comments (`backlog task edit task-12 --comment "…" --comment-author @review`)
  - long notes go in `work/task-12/*.md`
  - the git log of this repo is the timeline, with a commit per state change

## ClickUp access (plan)

- **Primary: a CLI**, [clickup-cli](https://clickup-cli.com/) (`nicholasbester/clickup-cli`; community project by D3 Vitamin, Rust, Apache-2.0, ~50★, started 2026-03).
  - Token-based (`pk_…`).
  - Flattens ClickUp's verbose JSON (claims ~150 tokens vs ~12k per task query).
  - Covers ~130 endpoints.
  - Costs no context until called.
- **Use its CLI mode only.** Skip its MCP mode (143 tools) and `agent-config`, which writes into CLAUDE.md; we write the instructions.
- **How agents know the commands:**
  - a small `clickup` skill whose description is always visible and whose body is a cheat sheet of the ~10 commands we use (get task, comments, post comment, set status, search), loaded on demand
  - `clickup-cli <group> --help` for anything else
  - the same pattern as `gh`
- **Token** in the workspace's gitignored `.env`, not global config (check that the CLI supports this). Pin a version and skim the source, since it holds a full-account token.
- **Alternative:** `triptechtravel/clickup-cli` (Go, MIT, ~39★). It takes the task ID from the branch name and links GitHub, which fits branch-per-task.
- **Fallback:** the official remote MCP in the workspace `.mcp.json` (`https://mcp.clickup.com/mcp`, OAuth, 61 tools).
- **Evaluate** on a real ticket: tokens used, reliability, CLI vs MCP.
- The claude.ai ClickUp connector is disconnected (2026-09-27), so ClickUp is no longer global.

## Protocol (team-mode)

- **Lead:** the `/lead` skill, in a session started at `~/workspaces/enable/`.
  - takes in work
  - triages into go / needs-alex / skip
  - creates a worktree and assigns a slot
  - spawns workers
  - gathers results into `digest.md`
  - Alex talks to the lead only.
- **Dev worker:** subagent, one task, one worktree, one slot, one PR.
  - investigate → plan → fix → boot its own stack → checks → PR
  - escalates instead of guessing on money, data, prod, or off-task work
- **Reviewer:** subagent with fresh context. Reads the PR diff against the submodule's `AGENTS.md`; returns a verdict plus findings.
- **QA:** subagent that runs the existing `/qa` against the worker's slot: the task's criteria, plus the relevant suite or e2e, plus evidence.
- **Slots:** `PORT = 4400 + slot*100`, following the existing step. The lead tracks which slots are in use. Start with at most 2 parallel workers because of machine load (see SoLex overload in `collie-studio.md`).
- **Merge:** Alex merges.

### Build order (smallest thing that proves it)

1. Scaffold:
   - `git init` the workspace; write `.gitignore`, `AGENTS.md`, `.agents/`, `.claude/` (symlinks, settings)
   - `vault/` with `backlog init` (statuses above); test that the CLI works in `vault/backlog`, else root + symlink
   - bare-clone `EButler-QA/workspace` into `repos/`; add `wt/main` with the `.claude` symlink
   - copy skills + hook from workspace-claude
   - migrate memory
   - apply the user-level settings in dotfiles
   - install clickup-cli; token into `.env`
   - verify with the T3 audit prompt at the root and in `wt/main`: AGENTS.md loaded, skills present, memory dir = vault, no stray MCP
2. Dev worker, then reviewer, on one real task, driven by hand (no lead). Check worker and review quality.
3. Add QA.
4. Add `/lead` and slots; run 2 tasks in parallel.
5. Record friction (submodule pointer bumps, worktree setup time, port clashes, interruptions to Alex) as input for the monorepo pitch and Collie Studio.

## Later

- **Plugins:**
  - Personal marketplace repo (the Collie framework seed): `team-mode` plugin (lead + roles + hooks), generic analysis/review skills.
  - Team marketplace: `workspace-claude` turned into `enable-dev` (local-env, seed, worktree, qa) + `enable-ops` (ops-* runbooks + write guard). Team `settings.json` declares `extraKnownMarketplaces` + `enabledPlugins`.
  - The workspace then keeps only config + data.
  - Open: do teammates actually use workspace-claude branches?
- **Sharing skills:** personal until a teammate would use it, then promoted by PR to the team side (repo `.agents/skills` or the team marketplace).
- **Remote** for `~/workspaces/enable` (private; notes will contain client data, so pick the account carefully).
- **Monorepo** migration (import each repo with history).
- Fix the hardcoded compose ports.
