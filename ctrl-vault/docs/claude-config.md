# Claude config audit (global vs workspace)

**Goal:** zero global tools. Each workspace declares what it uses, so context stays intentional. This doc is the inventory and the target state. See `projects/enable-workspace.md` and `projects/collie-studio.md` for the workspace model.

Audited 2026-09-27, Claude Code 2.1.283, desktop app.

## Global today

### `~/.claude/settings.json`

- `model: opus[1m]`, `effortLevel: medium`, `tui: fullscreen`, `skipDangerousModePermissionPrompt: true`, cross-session inbound on, push notifications on.
- `permissions.allow`: **239 entries**. Covers every file tool plus a very broad Bash set (`rm`, `curl`, `ssh`, `kubectl`, `gcloud`, `aws`, `docker`, `terraform`, `brew`, `kill`, `systemctl`, …).
- `permissions.deny`: 31 catastrophic patterns (rm -rf /, sudo, mkfs, shutdown, …).
- `enabledPlugins` (user scope): `gopls-lsp`, `coderabbit`, `frontend-design`, `discord`.

### `~/.claude/CLAUDE.md`

One line: "be extremely concise…". Keep it; it's a personal preference, not a tool.

### User MCP (`~/.claude.json` → `mcpServers`), loaded in every session

| server | transport | tools | used by |
|---|---|---|---|
| `railway` | stdio (`railway` CLI) | 65 | hookdeck (outpost-railway, outpost-fleet-cleanup, …); **also** in hookdeck `.mcp.json` as `Railway` (npx), so it's **duplicated** there |
| `notion` | http | 45 | hookdeck (notion-publish-spec, investigate); **also** in hookdeck `.mcp.json`, so it's **duplicated** |

### Per-project MCP in `~/.claude.json` (machine-local, not in any repo)

- `ebutler-qa/enable-backend` → `clickup` (http). Stale: that repo is now a submodule of the workspace.

### claude.ai connectors (account-level; on in every desktop session unless toggled per session)

| connector | tools | used by |
|---|---|---|
| ClickUp | 61 | enable only |
| Claude Docs | 8 | artifacts/docs; general |
| visualize | 2 | inline widgets; general |

### Plugins (`anthropics/claude-plugins-official`)

| plugin | scope | status | used by |
|---|---|---|---|
| gopls-lsp | user | on | Go repos only (outpost, enable-connectors, eldobot is Python) |
| coderabbit | user | on | unclear; needs the CodeRabbit CLI |
| frontend-design | user | on | FE work only |
| discord | user | on, **MCP failing** | unclear (eldobot?) |
| figma | local → ctrl | on, **needs auth** | wrong place; design work happens in hookdeck/enable/collie |

### User skills

- `~/.claude/skills/use-railway`: Railway-only, installed globally.
- `~/.claude/skills/synced/…`: 13 claude.ai account skills synced by the desktop app:
  - `docx` `pdf` `pptx` `xlsx`
  - `deep-research` `morning` `skill-creator`
  - `built-in-browser` `chrome-browser` `computer-use`
  - `docs` `import-memory`
  - Managed from the claude.ai skills settings, not this folder.

### Desktop-app built-ins (not configurable per project)

Browser pane, Chrome, terminal, iOS simulator, `ccd_*` (sessions, sidebar, PR, settings), `scheduled-tasks`, `mcp-registry`. These are part of the app, and most are deferred (loaded on demand), so the context cost is small.

## Workspaces today

### ctrl (`~/workspaces/ctrl`; `hub/alexluong/ctrl` symlinks to it)

- Hub workspace (2026-09-29): `AGENTS.md` (`CLAUDE.md` → symlink); `.claude/settings.json` → auto-memory in `ctrl-vault/memory`, SessionStart env hook, deny rules, `additionalDirectories: ~/git/hub/alexluong`
- `.claude/settings.local.json` → figma plugin
- skills (`.agents/skills`): bookkeeping-import, bookkeeping-report, dev-setup, disk-audit, implement, new-project, workspace-setup + standard done, recall, tidy, worktree, workspace
- **Needs:** none of railway, notion or ClickUp. Everything MCP-related loaded here is noise.

### hookdeck (`hub/alexluong/hookdeck` = `alexluong/hookdeck-workspace`; `hub/alexluong/hookdeck-workspace/` = its worktrees)

- `CLAUDE.md` ("Read AGENTS.md" + communication rules), `AGENTS.md`, `AGENTS_core.md`, `AGENTS_outpost.md`
- `.mcp.json`: `notion`, `figma-desktop` (local :3845), `Railway` (npx)
- 30 skills; the ones that use MCP: notion-publish-spec, investigate, outpost-railway, outpost-fleet-cleanup, outpost-cloud, outpost-healthcheck, outpost-loadtest, clickhouse, gcp
- No `settings.json`; permissions come from global.

### enable (`ebutler-qa/workspace/<wt>`)

- `CLAUDE.md` + `AGENTS.md` (team repo)
- `.claude/` = personal `workspace-claude` repo:
  - `settings.json` with a PreToolUse write-DB guard hook, plus a `mcpServers.clickup` block. **Probably ignored:** `settings.json` isn't where Claude Code reads MCP servers from (`.mcp.json` / `~/.claude.json` are), which fits AGENTS.md's note that it curls the ClickUp API instead. Unverified.
  - 13 skills; ClickUp users: investigate, ops-delete-branches, spec, ticket
- In practice, ClickUp comes from the claude.ai connector.

## Findings

1. **Every session loads about 170 MCP tools it mostly doesn't need:** railway 65, ClickUp 61, notion 45. In ctrl, all three are unused.
2. **Duplicates in hookdeck:** railway and notion are each loaded twice (user + `.mcp.json`).
3. **Broken or unauthenticated:**
   - discord MCP failing
   - figma needs auth, and is enabled in the wrong workspace
   - enable's `settings.json` MCP block likely does nothing
4. **Stale:** the `enable-backend` project MCP entry in `~/.claude.json`.
5. **Global permissions are huge:** 239 allows, including `rm`, `ssh`, `curl`, cloud CLIs. Combined with bypass mode, workspaces can't tighten anything. This is the other half of "control".
6. **Global plugins that belong to a stack:** gopls-lsp (Go), frontend-design (FE). The use-railway skill likewise.

## Target: zero global tools

**Global keeps only preferences, no tools:**
- `CLAUDE.md` (concise style)
- `model` / `effortLevel` / UI prefs
- the **deny** list (safety floor)
- the `agents-md` `instructionFiles` setting (needed for `~/workspaces/*`; see enable-workspace.md)
- a small read-only allow list (`ls`, `cat`, `git status` …)

**Each workspace declares its own:**

| | MCP (`.mcp.json`) | plugins (`enabledPlugins` in project settings) | skills | permissions |
|---|---|---|---|---|
| ctrl | none | none (figma out) | its 6 | project allow list |
| hookdeck | notion, Railway, figma-desktop | gopls-lsp | its 30 + use-railway | project allow list |
| enable | clickup (`.mcp.json`, replaces the connector) | gopls-lsp? frontend-design? | its 13 | project allow list + write guard |

**Moves:**
1. Remove user MCP `railway` and `notion` from `~/.claude.json`. hookdeck already has both in `.mcp.json`.
2. Remove the stale `enable-backend` clickup entry.
3. Plugins: switch gopls-lsp, coderabbit and frontend-design from user scope to project scope where they're used. Figma: ctrl local → the workspaces that do design. Discord: fix it or remove it.
4. Move `use-railway` from `~/.claude/skills` into hookdeck (or a plugin later).
5. **claude.ai connectors (ClickUp):** they come from the account, not a file. Plan: use ClickUp via a project `.mcp.json` in enable (`https://mcp.clickup.com/mcp`, OAuth via `/mcp`) or the REST API plus a token, and disable the connectors in Claude Code. Switches (MCP docs, 2026-09-27):
   - `"disableClaudeAiConnectors": true` in any settings file. If any source says `true`, that wins; a project `false` can't turn them back on.
   - `ENABLE_CLAUDEAI_MCP_SERVERS=false claude`: for that shell only.
   - `deniedMcpServers: ["claude.ai ClickUp"]`: blocks one connector by name or URL pattern.
   - `/mcp` panel toggle: per project.
   - **Catch:** these only cover connectors the CLI fetches itself. **Desktop-app sessions (local/SSH) get connectors from claude.ai**, so there the only options are a per-session toggle in the app or disconnecting on claude.ai. Cloud sessions follow org settings.
6. **Synced account skills:**
   - document skills (docx/pdf/pptx/xlsx) and `skill-creator`: fine as general-purpose, or turn off on claude.ai
   - `morning`, `import-memory`: check whether they're used
7. **Permissions:** shrink global allow to read-only; move the stack-specific commands to each workspace's `.claude/settings.json`. Decide whether bypass mode stays the default.

**Open:**
- Does a project `.mcp.json` server cost context when unused? (Tool search defers them, so mostly names only; still noise and processes.)
- Can claude.ai connectors be scoped per project at all?
- coderabbit: used?

## Applied (2026-09-27)

Backups: `~/.claude.json.bak-2026-09-27`, `~/.claude/settings.json.bak-2026-09-27`.

- `claude mcp remove railway -s user`, `claude mcp remove notion -s user`. Nothing else in `hub/alexluong` uses Railway (no railway.json/toml). **hookdeck now has no notion/Railway either.** Its `settings.local.json` had all three `.mcp.json` servers in `disabledMcpjsonServers` (it relied on the user-level ones). Left off on purpose: new workspaces will declare their own.
- `claude mcp remove clickup -s local` in `ebutler-qa/enable-backend` (the stale entry).
- claude.ai ClickUp connector: disconnected by Alex on claude.ai.
- Plugins: all disabled at user scope (`gopls-lsp`, `coderabbit`, `frontend-design`, `discord`); `figma` disabled in ctrl local. Enabled per project (local scope): hookdeck → gopls-lsp; `ebutler-qa/workspace/main` → gopls-lsp, frontend-design. Still installed (cache); re-enable with `claude plugin enable X --scope project|local`.
- `use-railway` skill removed from `~/.claude/skills` (moved to `~/.claude/backups/2026-09-27/`).
- Artifacts off: `"enableArtifact": false` in user settings. That's the official switch (also `CLAUDE_CODE_DISABLE_ARTIFACT=1`, `/config` → Artifacts), and it removes `Artifact`/`ArtifactComments`/`ArtifactData` plus the `artifact-*` skills. `DesignSync` survives it, so it's in `permissions.deny`. Verified with a fresh `claude -p`. Projects can also set `enableArtifact: false`; `true` can't turn it back on.
- Per-project setup: to be discussed when the new workspaces are set up.
- Desktop app and T3 Code both read user + project + local settings (T3: Agent SDK `settingSources: [user, project, local]`), so per-project enables work in both.
- Still global:
  - connectors Claude Docs + visualize (account-level; disconnect on claude.ai)
  - the synced claude.ai skills
  - desktop-app built-ins
- **Disable mechanisms:**
  - a bare tool name, or `mcp__<server>__*`, in `permissions.deny` removes it from context
  - `skillOverrides: {"<skill>": "off"}`
  - `syncClaudeAiSkills: false`
  - `disableBundledSkills: true`
  - `disableClaudeAiConnectors: true` (CLI only)
- **visualize** renders only in hosts with an HTML widget renderer (Claude desktop/web/mobile). T3 Code and the terminal CLI can't render it (T3 source: no MCP UI rendering), so it's noise there.
- Global `~/.claude/CLAUDE.md` = the concision line + the communication style guide moved from hookdeck's `CLAUDE.md` (Alex's general preference for all agents). hookdeck's `CLAUDE.md` deleted; `AGENTS.md` now loads natively there. The "sacrifice grammar" line and "plain language" pull different ways; revisit if replies get too clipped.

## Reproducing on another machine (dotfiles)

- `dotfiles/dot/.claude/{settings.json,CLAUDE.md}` are symlinked into `~/.claude/` (by stow via `setup-dotfiles.sh`, which keeps `~/.claude` a real dir). Claude's own writes (`claude plugin …`, `/config`) go through the symlink, tested 2026-09-27, so changes show as dotfiles diffs to commit.
- `dotfiles/scripts/setup-claude.sh`: adds the official marketplace, installs plugins (gopls-lsp, frontend-design) and keeps them disabled at user level. Prints the manual account-level checklist.
- Not tracked: `~/.claude.json` (auth, per-project state), history/sessions/cache, `skills/synced`, `settings.local.json`.
- Account/app-level (manual): `/login`; claude.ai connectors (Claude Docs + visualize on, ClickUp off); synced skills; desktop app + T3 settings. Secrets in Vaultwarden.
- This MBP: `stow` isn't installed and the other dotfiles (`.zshrc`, `.gitconfig`) aren't stowed here (plain files). The Claude files were linked by hand with `ln -s`.
