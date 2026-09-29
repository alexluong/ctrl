# ctrl workspace

ctrl turned into a hub workspace on 2026-09-29: moved from `~/git/hub/alexluong/ctrl` to `~/workspaces/ctrl` (old path = symlink), notes into an Obsidian vault, standard workspace skills. Playbook: `ctrl-vault/docs/workspace-setup.md` § Hub profile.

## Why

- ctrl already acted as a workspace (notes, skills, cockpit sessions) but didn't share the other workspaces' shape: no repo-backed memory, no recall/done/tidy, notes not browsable in Obsidian.
- Incubator: explorations/POCs (any domain, RE included) start here and graduate to `~/workspaces/<name>` when they outgrow it (`workflow.md` § Project lifecycle).

## Decisions

- **Vault = `ctrl-vault/`** holding `docs/`, `re/`, `biz/`, `memory/` (folder names unchanged, paths rewritten to `ctrl-vault/…`). Repo root isn't the vault: Obsidian would index `wt/` code and `.claude/`.
- **Memory:** auto-memory on, into `ctrl-vault/memory` (in git). Replaces the old "never use memory" rule, whose reason (`~/.claude` doesn't follow Alex across machines) no longer applies.
- **Board (added 2026-09-29, same day):** Backlog.md in `ctrl-vault/backlog`, labels `re`, `biz`, `project`, `infra`, `machine`, `workspace`; UI on port 6421 (6420 = other workspaces). No roles, lead or digest.
- **POC code:** `repos/` + `wt/<repo>/<name>` via a generic `wt` (no repo list, no task IDs). Existing repos in `~/git/hub/alexluong` stay put; pointer `CLAUDE.md`s updated to the new path.
- **Links:** plain backticked paths, no wikilinks (searchable by Claude, harness-neutral).
- **Secrets:** `secrets/` stays at the root, gitignored, outside the vault.
- **Favicon:** indigo tile + white sliders.

## As built (2026-09-29)

- `AGENTS.md` (`CLAUDE.md` → symlink), `.agents/skills` (+ `.claude/skills` symlink): bookkeeping-import/report, dev-setup, disk-audit, implement, new-project, workspace-setup, done (identical to other workspaces), recall, tidy, worktree, workspace.
- `.claude/settings.json`: memory dir, SessionStart env hook (`session-env.sh` from cs), deny `.env` read/edit and edits in `repos/`, `wt/*/main`; `additionalDirectories: ~/git/hub/alexluong`.
- `mise.toml` (was `.mise.toml`): bun, jq, ripgrep, backlog.md; `bin/` on PATH.
- Other workspaces' references to `~/git/hub/alexluong/ctrl` / `ctrl/docs/` updated in live files (skills, AGENTS.md, notes); frozen history notes left alone (the symlink keeps old absolute paths resolving).

## Open

- 👤 Open `ctrl-vault/` in Obsidian; re-add ctrl in T3 / the desktop app at the new path.
- `media`, `finance`, `career` domains still planned (no folders yet).
