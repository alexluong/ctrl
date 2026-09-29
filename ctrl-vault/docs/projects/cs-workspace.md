# Project: Collie Studio workspace (`~/workspaces/cs`)

Alex's personal agent workspace for Collie Studio work: Collie Demo, Collie UI and the Collie Studio idea. Fourth workspace after Enable, hookdeck and SoLex, built from the playbook (`../workspace-setup.md`). It is also a Collie Studio dogfood: friction goes to `cs-vault/notes/studio/friction.md`. Project notes live in the vault: `~/workspaces/cs/cs-vault/notes/{studio,demo,ui}/` (index `README.md`); `collie-studio.md`, `collie-demo/README.md` and `collie-ui/README.md` here are pointers.

**Status (2026-09-28): set up, no code yet.** Repo `alexluong/cs-workspace` (GitHub, private). Waiting on the code repos (below).

## Decisions (2026-09-28, with Alex)

- **Name:** dir `~/workspaces/cs`, repo `alexluong/cs-workspace` (personal config, not company-branded, so `alexluong` over `colliestudio`).
- **Projects:** Collie Demo, Collie UI, Collie Studio. Not collielab infra.
- **Notes moved into the vault** (not linked): ctrl keeps pointer READMEs. History before the move is in ctrl's git log.
- **Several own repos, no systems, no submodules:** one bare clone per repo, `wt/<repo>/<name>` (hookdeck's shape). Own repos, so task IDs in branch names (`task-N-<slug>`, SoLex's rule).
- **No infra:** no `ops/`, env wrappers, gcloud or prod guard. Publishing (npm `@colliestudio`), hosting and secrets are Alex's.

## As built (2026-09-28)

- **Layout:** as SoLex (AGENTS.md + CLAUDE.md symlink, `.agents/{skills,roles,references}`, `.claude/` wiring, `cs-vault/`, `bin/`, `local/`). Board labels `demo`, `ui`, `studio`.
- **Repos:** `collie-ui` (`alexluong/collie-ui`) and `collie-demo` (`colliestudio/collie-demo`). Neither cloned yet: collie-ui's first slice is uncommitted and the remote is empty; collie-demo isn't created. `~/code/replay-lab` (lab prototype, local-only) stays outside the workspace and is frozen once the demo repo exists.
- **`bin/wt`** (`.agents/skills/worktree/wt`): `init [repo...] | add <task-N> <repo...> [--slug s] [--from ref] [--no-setup] | rm <task-N> [repo...] | sync | ls`. `init` skips repos missing or empty on GitHub (`git ls-remote --exit-code`), so it can run before the repos exist. `add` runs `mise run setup` when the repo defines it (collie-ui: free port range via `scripts/setup-env.mjs` + `pnpm install`); `ls` shows the worktree's `PORT_*`. Tested end to end on a throwaway repo only.
- **Tools:** root `mise.toml` = node 22.22.0, pnpm 11.20.0, jq, gh, ripgrep, backlog.md 1.53.0. Worktrees use each repo's own `mise.toml`.
- **Skills and roles:** lead, workspace, worktree, recall, done, tidy and the four roles, adapted from SoLex (SoLex domain rules swapped for public API / file format / publish risks). `tidy/check` walks `wt/*/task-*` and every `repos/*.git`.
- **Claude:** `settings.json` (memory → `cs-vault/memory`, SessionStart env hook with the mise PATH fix, deny `.env` reads, edits under `repos/` and `wt/*/main/`), role wrappers. No plugins, no MCP.
- **Verified:** fresh `claude -p` at the root: AGENTS.md via the CLAUDE.md symlink, 6 skills, 4 agent types, memory dir, `backlog`/`wt`/`node` from mise, no MCP.

## Alex to do

- Commit and push collie-ui's first slice, then `bin/wt init collie-ui`.
- Create `colliestudio/collie-demo` (private), then `bin/wt init collie-demo`.
- Obsidian: open `~/workspaces/cs/cs-vault`.
- Tell the collie-lab session (owns `demo/engineering.md`) that the notes moved, if it's restarted.
