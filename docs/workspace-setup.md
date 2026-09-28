# Workspace setup playbook

How to set up a personal agent workspace (`~/workspaces/<name>`) for a project: agent config, board, notes, memory, isolated tools and infra access, code in worktrees. Reference implementations: Enable (`~/workspaces/enable`, repo `alexluong/enable-workspace`; history in `projects/enable-workspace.md`) = one team super-repo with submodules; hookdeck (`~/workspaces/hookdeck`, `projects/hookdeck-workspace.md`) = independent repos, no systems. SoLex (`~/workspaces/solex`, `projects/solex-workspace.md`) = one own repo, no team, no prod: the smallest shape. Collie Studio (`~/workspaces/cs`, `projects/cs-workspace.md`) = several own repos, no prod: hookdeck's `wt/<repo>/<name>` with SoLex's skills. Related: `claude-config.md` (zero-global Claude config), `infra-access.md` (the env-dir pattern in depth).

Written for whoever runs the setup (Claude or a human). Steps marked **👤** need the person: browser logins, tokens, decisions.

## Principles

- **One personal repo per workspace** holds agent config, board, notes and memory. Code is never in it: `repos/` (bare clones) and `wt/` (worktrees) are gitignored.
- **Harness-neutral content, thin Claude wiring:** `AGENTS.md` + `.agents/skills` + `.agents/roles` are the content; `.claude/` only symlinks and settings. No `CLAUDE.md`.
- **Nothing global:** tools via the workspace `mise.toml`, no global MCP/plugins (`claude-config.md`), tokens in the workspace `.env`, gcloud in a workspace config dir.
- **No access by default:** the root and worktrees carry no prod credentials; each env is a directory (`ops/stg`, `ops/prd` read-only, `ops/prd-rw`) reached through wrappers.
- **Pristine sources:** `repos/` fetch-only, `wt/main` read-only reference; every change in `wt/task-N`.
- **Sessions start at the workspace root.**
- **Stop at each checkpoint** (✅) for review; commit and push there.

## Prerequisites (machine, once)

- mise (activated in the interactive shell), git, gh, jq, Docker Desktop.
- dotfiles applied (`~/.claude/settings.json` + `CLAUDE.md` symlinked from the dotfiles repo). User-level settings that matter here:
  - `autoMemoryEnabled: false` (workspaces turn it on and point it at their vault)
  - `pluginConfigs."agents-md@builtin".options.instructionFiles: "claude-md-and-agents-md"` (AGENTS.md loads even next to a team CLAUDE.md)
  - `disableClaudeAiConnectors: true`, `enableArtifact: false`, plugins disabled at user level
- Obsidian installed.

## Steps

### 0. Decide 👤

- Name + repo (`alexluong/<name>-workspace`, **private**: notes will hold client data).
- Which code repos, and whether you need "systems" (sets of submodules/services worked on together). One super-repo → systems (Enable). Independent repos → skip them: one bare clone per repo, `wt/<repo>/<name>`, a task picks its repos (hookdeck).
- Branch naming in team repos: task IDs (`task-N-slug`, Enable) or team style (`feat/<slug>`, hookdeck: the workspace must not surface to the team).
- An existing repo to reuse? `git switch --orphan workspace` keeps the old layout on `main` as a reference.
- Environments and credentials: which systems have prod/staging access; which have read-only credentials (a system without one gets nothing in `prd`).
- Where tickets come from (ClickUp, GitHub, Linear) and which CLI reads them.

### 1. Skeleton ✅

- `git init ~/workspaces/<name>`, add the remote.
- `.gitignore`: `/repos/`, `/wt/`, `.env`, `.env.*`, `!.env.example`, `**/.obsidian/workspace*.json`, `**/.obsidian/cache`, `/.gcloud/`, `/local/`, `/ops/*/*` + `!/ops/*/mise.toml`.
- `AGENTS.md` (layout, how work flows, where commands run, work items, infra access, what to remember, git prefixes). Start from Enable's and replace the specifics.
- `.agents/roles/{product,dev,reviewer,qa}.md` (copy Enable's; adjust the repo specifics in dev/qa).
- Dirs: `<name>-vault/{backlog,work,notes,memory}` (the vault folder is named `<name>-vault`, e.g. `enable-vault`: Obsidian names a vault after its folder, and the bare workspace name clashes with repo/system names), `ops/{stg,prd,prd-rw}`, `bin/`, `local/`.
- Root `favicon.svg` (or `.ico`/`.png`): T3 Code auto-detects it as the sidebar project icon. Use the product's brand favicon if one exists in its repos; else a rounded monogram tile in a color not used by other workspaces. Current: enable = brand swirl (`.ico`), hookdeck = brand tile, solex = Fluent Emoji "Hotel" 3D, `favicon.png` (MIT, microsoft/fluentui-emoji; the SoLex hotel, HCM, has no usable logo online: website dead, Facebook only), cs = green tile + solid white border collie head silhouette (line art is unreadable at 16px) (SVG Repo #21797, CC0; collie = herding dog, fits Studio's "you direct many small agents"). A T3 per-project override hides the favicon; clear it to show the file. Fallback without a file: T3 per-project override (Lucide icon + color + 2-char monogram, or emoji), stored only in T3's local DB. T3 caches icon lookups, including "no icon found", so reload T3 after adding or changing a favicon.

### 2. Tools (mise) ✅

Root `mise.toml`:

```toml
[tools]
# language runtimes + CLIs the project needs, pinned
"npm:backlog.md" = "<ver>"
# ticket CLI, e.g. "github:nicholasbester/clickup-cli" = { version = "<ver>", bin = "clickup" }

[env]
_.file = ".env"                      # root: non-prod values only (ticket-tool token)
_.path = "{{config_root}}/bin"
CLOUDSDK_CONFIG = "{{config_root}}/.gcloud"
CLOUDSDK_ACTIVE_CONFIG_NAME = "none"
# Go/Terraform ignore CLOUDSDK_CONFIG and fall back to ~/.config/gcloud ADC: fail closed
GOOGLE_APPLICATION_CREDENTIALS = "{{config_root}}/.gcloud/NO-ACCESS-use-stg-prd-prd-rw.json"
```

- `mise trust && mise install`. Check `mise env` at the root shows no prod values.
- Prefer mise backends (`npm:`, `github:`, core) over global installs; mise's github backend verifies release attestations.

### 3. Vault + board ✅

- `backlog init <name> --backlog-dir <name>-vault/backlog --config-location root --integration-mode none --check-branches false --include-remote false --auto-open-browser false --defaults` (a custom backlog dir needs root config). Keep the stock statuses (To Do, In Progress, Done).
- Check the CLI from the root and `<name>-vault/`: create a task, comment (`--comment-author @dev`), read with `--plain`, delete.
- 👤 Obsidian: open `<name>-vault/` as a vault (shows as "<name>-vault"). Don't rename it in the app: that renames the folder and breaks every path. Optional: `~/Obsidian/<name>` symlinks for quick access (the name still comes from the real folder).
- `<name>-vault/digest.md` stub (Needs Alex / In flight / Done recently).

### 4. Code: repos + worktrees ✅

- Bare clone into `repos/<repo>.git` (`--reference <old clone> --dissociate` speeds it up), set `remote.origin.fetch`, fetch. Add `.claude` to `repos/<repo>.git/info/exclude` (a symlink isn't matched by a team `.claude/` ignore).
- Worktree script as a skill: `.agents/skills/worktree/{SKILL.md,wt}` + `bin/wt` symlink. Copy Enable's and adapt:
  - systems → submodules + services
  - slots/ports (`PORT = base + slot*step`; skip ports the team's compose hardcodes)
  - env files copied into each worktree (**never** a team root `.env` with prod creds)
  - submodules as partial clones (`--filter=blob:none`) started from their latest `origin/main` on a task-named branch (pinned pointers are usually stale)
  - `mise trust` each new worktree
- `bin/wt init` → `wt/main` (all submodules), then copy its dev env files from the old setup/Vaultwarden. Give `wt/main` a `STACK_NAME` that doesn't collide with old worktrees (compose project names are shared machine-wide).
- Try one stack end to end (`bin/wt up main`); expect environment issues (Enable hit mongo 8.0 vs Docker kernel ≥ 6.19).

### 5. Skills ✅

- Copy the useful project skills from wherever they lived (e.g. a team `.claude` repo); rename `skill.md` → `SKILL.md`; move references to `.agents/references/`.
- Rewrite anything using an MCP/connector to the CLI (ticket tool). Add a ticket-tool skill: a cheat sheet of the ~10 commands used + IDs/conventions; `<cli> --help` for the rest.
- Replace copies of team docs that drift with thin pointers to the source (Enable: `local-env` points at the team's `dev/README.md` and `cli.ts --help`).
- Add "where to run" notes: repo paths are relative to a worktree.
- Workspace skills: `lead` (orchestration), `workspace` (where things go, memory vs notes, how to add things), `worktree`, `done` (session/task wrap-up).
- `done` is workspace-agnostic: byte-identical in every workspace (`<vault>` placeholder; specifics come from the `workspace`/`worktree` skills). Copy it verbatim from any workspace; when changing it, copy the new version to all (`for w in ~/workspaces/*/; do cp … "$w.agents/skills/done/SKILL.md"; done`) and commit each.

### 6. Claude wiring ✅

- `.claude/skills` → `../.agents/skills`.
- `.claude/agents/<role>.md`: thin wrappers (name, description, "read `.agents/roles/<role>.md` and follow it").
- `.claude/settings.json`: `autoMemoryEnabled: true`, `autoMemoryDirectory: ~/workspaces/<name>/<name>-vault/memory`, `enabledPlugins` for the project (e.g. an LSP), hooks (SessionStart env, PreToolUse guard), `permissions.deny`: `Read`/`Edit` of `.env`, `ops/**/.env`, `.gcloud/**`; `Edit` of `repos/**` and `wt/main/**`.
- Ticket CLI token 👤: create it in the tool, put it in the workspace `.env` (not the CLI's global config; if a `setup` command wrote one, move the token and delete the global file). Disable branch-name ID detection if task branches use Backlog.md IDs.

### 7. Infra access ✅

Full pattern: `infra-access.md`. Per env dir:

```toml
# ops/prd/mise.toml
[env]
_.file = ".env"                      # read-only credentials only
DEPLOY_ENV = "prd"
CLOUDSDK_ACTIVE_CONFIG_NAME = "prd"
GOOGLE_APPLICATION_CREDENTIALS = "{{config_root}}/../../.gcloud/adc-<name>.json"
TF_VAR_project_id = "<prod project>"
```

- Split the old `.env` values into `ops/{stg,prd,prd-rw}/.env` (read-only in `prd`, write in `prd-rw`), `chmod 600`, without printing them. `mise trust` each dir.
- `bin/env-run` + symlinks `stg`, `prd`, `prd-rw`: `cd ops/<env>`, `eval "$(mise env -s bash)"`, then run the command there; a single quoted argument runs via `bash -c` so `$VARS` expand inside the env; shortcuts like `prd mongo`.
- gcloud: `CLOUDSDK_CONFIG=.gcloud`; configs `none` (no account), `stg`, `prd`, `prd-rw` with account + project.
  - 👤 `cd ~/workspaces/<name>` (check `echo $CLOUDSDK_CONFIG`), `gcloud auth login <account>`, `gcloud auth application-default login`.
  - Then: unset the account on `none` (login writes it into the active config); move `.gcloud/application_default_credentials.json` → `.gcloud/adc-<name>.json`.
  - Delete stale global ADC files in `~/.config/gcloud/` that belong to this project (Go tools read them from anywhere).
- Hooks: `session-env.sh` (SessionStart: `mise env -s bash >> "$CLAUDE_ENV_FILE"`; Claude's shell never runs mise's cd hook) and `guard-prod.sh` (PreToolUse Bash: ask on `prd-rw` and write creds; deny prod identifiers without a `prd`/`prd-rw` prefix, incl. `--account`/`--impersonate-service-account`; deny reading secrets files).
- Rewrite skills/references to the wrappers; team scripts run as `prd bun ../../wt/main/scripts/…`.

### 8. Verify ✅

From the workspace root:

- `mise env` at root: no prod values; `gcloud projects describe <prod>` fails; Terraform at root fails (missing ADC file).
- `prd …` reads work (DB count, logs, `terraform plan -lock=false`); `prd` has no write credentials; `stg` works.
- Guard unit tests: pipe `{"tool_input":{"command":"…"}}` into the hook for allow/ask/deny cases.
- Fresh session (`claude -p` and the app/T3) audit prompt: instruction files, skills, MCP/tools, memory dir, hooks, `which prd wt <cli> backlog`, a `prd` read, an unprefixed prod command (blocked), a ticket read, `bin/wt ls`.
- Write in `wt/main` denied, in `wt/` allowed.

### 9. Document ✅

- Project doc in ctrl (`docs/projects/<name>-workspace.md`): why, layout, decisions, as built.
- `infra-access.md`: add the workspace's "as built" section.

## Gotchas (learned on Enable, hookdeck, SoLex and cs)

- **AGENTS.md loads natively only without a CLAUDE.md** in the dir or above; the user-level `instructionFiles` setting fixes worktrees of team repos.
- **Project settings load from the session start dir**, not parents: `.claude` symlink in worktrees if sessions ever start there.
- **mise `[env]` doesn't reach Claude's shell** except through shims → SessionStart env hook.
- **`gcloud auth login` writes the account into the active config**, even the deliberately empty one.
- **Go/Terraform ignore `CLOUDSDK_CONFIG`** for ADC → fail-closed `GOOGLE_APPLICATION_CREDENTIALS` at the root; delete global ADC files.
- **Without any credentials, Terraform hangs** probing the GCE metadata server instead of failing; the fail-closed path makes it error at once.
- **`$VAR` in `prd <cmd> "$VAR"` expands in the caller** (empty) → one quoted arg / `bash -c` inside the env.
- **`--allowedTools` in `claude -p` is variadic**: put the prompt first.
- **Permission rules:** `Edit(path)` covers all file-editing tools; `Write(...)`/`NotebookEdit(...)` path rules are rejected.
- **Obsidian vault name = folder name**; symlinks don't change it. Hence `<name>-vault/`. Deleting a symlink a vault was opened through makes Obsidian drop the vault from its list.
- **Team compose files share project names machine-wide** (`name: <x>-${STACK_NAME}`): pick unique `STACK_NAME`s.
- **Pinned submodule pointers go stale** (Enable: 40–274 commits): branch from `origin/main`.
- **A symlinked `.claude` isn't matched by a team `.claude/` gitignore** → `info/exclude`.
- **New worktrees' `mise.toml` is untrusted** → `mise trust` in the worktree script.
- **mise shims set the workspace env even with a prefix env var:** `KUBECONFIG=… kubectl …` inside the workspace is overridden by the root `[env]`; run such one-offs outside the workspace (or call the brew binary from `/tmp`).
- **macOS `/usr/bin/env bash` is 3.2:** `"${arr[@]}"` on an empty array fails under `set -u`; use `${arr[@]+"${arr[@]}"}`.
- **Team repos may track their own `.claude/`** (hookdeck core, hookdeck-cli): don't symlink over it.
- **Old auto-memory lives in `~/.claude/projects/<old-path-slug>/memory/`** (one dir per old session root): copy it into `<name>-vault/memory/`; scan it and the notes for credentials first (hookdeck: a QA API key → root `.env`).
- **Bruno keys secret env values by collection path:** moving collections means re-entering them.
- **`gcloud` from mise has no `gke-gcloud-auth-plugin`:** `gcloud components install gke-gcloud-auth-plugin` (again after a version bump).
- **Blobs copied from an old branch are free:** `git archive main notes | tar -x` into the orphan branch reuses the same objects.
- **A repo's own per-worktree setup beats slots:** if it already assigns ports/DB per checkout (SoLex `scripts/setup-env.mjs`), `wt add` just runs it. But check what it names things after: SoLex names the compose project after the directory, so every workspace's `task-3` collides → `wt` rewrites it to `<project>-task-N`.
- **`mise env` keeps the login PATH order:** global installs earlier in PATH (`~/Library/pnpm`, pnpm 10) shadow mise tools (pnpm 11) in Claude's shell. The SessionStart hook also appends `export PATH="$(mise bin-paths | paste -sd: -):$PATH"`. Check `which pnpm node` in the audit. (Enable/hookdeck have the same PATH, unfixed.)
- **Moving a ctrl project dir into a vault:** copy tracked files, rewrite paths in the live docs only, freeze the old agent/team history under `notes/history/`, move gitignored data (screenshots, exports) to `local/` and scripts to `tools/` (repoint their paths), and leave a pointer `README.md` in ctrl so existing links keep working. Check first that no session is mid-work on those files.
- **The Bash tool runs zsh:** unquoted `$files` isn't word-split; use `xargs -0` for file lists.
- **A workspace can come before its repos** (cs: one repo uncommitted, one not created): `wt init` checks `git ls-remote --exit-code <url> HEAD` and skips missing/empty repos; rerun `wt init <repo>` later.
- **`mise tasks ls` prints a bare name for a task without a description** (no trailing space): detect a task with `mise tasks ls --no-header | awk '{print $1}' | grep -qx setup`.
- **No `timeout` on macOS:** run the `claude -p` audit without it (Bash tool timeout is enough).
- **Cross-session messages can be held:** a peer session in another permission mode holds your message for its user's approval, and it can expire undelivered. When coordinating a notes move, ask Alex directly instead of waiting on the peer.
