---
name: workspace
description: How ctrl is organized and maintained - where notes, skills, settings and code go; memory vs notes; vault and git conventions; adding tools. Use when changing ctrl itself, deciding where something should be written down, or when unsure where a file belongs.
---

# Workspace

`~/workspaces/ctrl` is Alex's hub workspace (repo `alexluong/ctrl`, private): notes for every personal domain, workspace playbook, and explorations/POCs before they graduate. Same shape as the other workspaces (`ctrl-vault/docs/workspace-setup.md`, "hub" profile): a board but no roles, no prod access. **The vault is `ctrl-vault/`** (Obsidian names a vault after its folder); "the vault" in skills means this folder. The old path `~/git/hub/alexluong/ctrl` is a symlink here.

## Where things go

| what | where | notes |
|---|---|---|
| always-on rules, context map | `AGENTS.md` (`CLAUDE.md` → symlink) | keep it short; details go in skills |
| how-to procedures | `.agents/skills/<name>/SKILL.md` | scripts next to the skill |
| Claude wiring | `.claude/` | `skills` → `../.agents/skills`; `hooks/`; `settings.json` |
| tools, env vars | `mise.toml` (root) | worktrees use each repo's own `mise.toml` |
| secrets | Vaultwarden / `secrets/` (gitignored), root `.env` | never in the vault or any tracked file |
| ideas | `ctrl-vault/docs/ideas.md` | one entry each; graduates to a project doc |
| project living docs | `ctrl-vault/docs/projects/<name>.md` or `<name>/README.md` | status, decisions, plan; left as a pointer README when the project graduates |
| machines, workflow, Claude config, infra | `ctrl-vault/docs/*.md` | |
| real estate | `ctrl-vault/re/` | conventions in `re/notes.md`; binaries on iCloud |
| bookkeeping | `ctrl-vault/biz/`, `ctrl-vault/re/bookkeeping/` | system in `biz/BOOKKEEPING.md` |
| task board | `ctrl-vault/backlog/` via the `backlog` CLI | never hand-edit task files; labels in `backlog.config.yml` |
| per-task notes | `ctrl-vault/work/task-N/` | only when comments aren't enough; `summary.md` at close (`done`) |
| memory (short facts) | `ctrl-vault/memory/` | auto-memory; see below |
| exploration/POC code | `repos/` + `wt/` (`worktree` skill) | gitignored |
| scratch, exports | `local/` | gitignored, never committed |

**Edit sources, not wiring:** change skills in `.agents/skills/`, not through `.claude/skills`.

## Memory vs notes

- **Memory** (`ctrl-vault/memory/`, one fact per file; `MEMORY.md` index loads every session): cheap capture and cross-cutting traps. Keep the index under ~150 lines. `tidy` sorts captures into notes/skills or deletes them.
- **Notes** (the rest of the vault): everything longer, in the domain it belongs to. Date anything that can go stale.
- **Preferences/conventions** of Alex's: the skill or AGENTS.md where they apply.
- Adding happens in `done`; organizing in `tidy`. Never: credentials in the vault.

## Git

- Conventional prefixes with a scope (`docs(<area>):`, `re:`, `biz:`, `memory:`, `feat(skills):`, `chore:`). Commit when a piece of work is done; push freely (private).
- POC code commits happen in `wt/<repo>/<name>`.

## Adding things

- **Skill:** `.agents/skills/<name>/SKILL.md` with `name` + `description` frontmatter. Shared with other workspaces? `done` is identical everywhere (`workspace-setup` sync mode).
- **Tool:** root `mise.toml` `[tools]` (mise backends), `mise install`. No global installs.
- **Hook or setting:** `.claude/settings.json` / `.claude/hooks/`; verify with a fresh session.

## Surfaces

Start sessions at `~/workspaces/ctrl` (desktop app, T3, or `claude`). Obsidian opens `ctrl-vault/`. Board UI: `backlog browser`.
