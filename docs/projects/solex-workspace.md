# Project: SoLex workspace (`~/workspaces/solex`)

Alex's personal agent workspace for SoLex (the hotel back office). Third workspace after Enable (`enable-workspace.md`) and hookdeck (`hookdeck-workspace.md`), built from the playbook (`../workspace-setup.md`). SoLex itself: `~/workspaces/solex/solex-vault/notes/` (entry point `mvp.md`); `hotel-backoffice/README.md` here is only a pointer.

**Status (2026-09-28): set up.** Repo `alexluong/solex-workspace` (GitHub, private). Next: first real `/lead` run on an `mvp.md` follow-up.

## As built (2026-09-28)

- **Single repo, no systems:** `repos/solex.git` (bare clone of `alexluong/solex`), `wt/main` read-only (detached at `origin/main`), `wt/task-N` on branch `task-N-<slug>`. SoLex is Alex's own repo, so task IDs are fine in branch names (no "workspace stays invisible" rule like Enable/hookdeck).
- **`bin/wt`** (`.agents/skills/worktree/wt`, ~120 lines): `init | add <task-N> [slug] [--from <ref>] [--no-setup] | rm | sync | ls`. `add` reuses solex's own per-worktree setup (`scripts/setup-env.mjs`: free 10-port range from 7000, `.env`, `BETTER_AUTH_SECRET`; then `mise run setup`: deps + local SQLite), then renames `COMPOSE_PROJECT_NAME` to `solex-task-N`. ≈15s per worktree; `pnpm check` green in a fresh one. No slots.
- **Tools:** root `mise.toml` = node 22.22.0, pnpm 11.20.0 (same as solex), jq, gh, ripgrep, backlog.md 1.53.0. Worktrees use solex's own `mise.toml`.
- **Cloudflare:** Alex's global wrangler login (decided 2026-09-28: a scoped token in an `ops/stg` env dir looked tricky; revisit later). No `ops/`, no prod (doesn't exist yet), no guard hook. Deploy = `pnpm deploy` from a worktree on `main`, only when Alex asks.
- **Secrets:** stay in `ctrl/secrets/hotel-backoffice.md` (staging sign-in, ezFolio access); `tools/ezfolio/lib.mjs` reads them from there.
- **Protocol:** `lead`, `recall`, `done`, `tidy`, `workspace`, `worktree` skills adapted from Enable; roles product/dev/reviewer/qa rewritten for SoLex (decisions D-n, spec §10–12, `pnpm check`, e2e + rrweb journeys, the old QA checklist). No ClickUp/ticket CLI: work comes from Alex and `mvp.md` follow-ups.
- **Claude wiring:** `.claude/skills` symlink, role wrappers, `settings.json` (memory → `solex-vault/memory`, deny edits in `repos/` + `wt/main`, deny reading the root `.env`), SessionStart env hook that also puts mise tool dirs first on PATH. No plugins.
- **Context move (Alex: option A, move all):** `ctrl/docs/projects/hotel-backoffice/` → `solex-vault/notes/`. Live docs at the top level (`mvp`, `project` = the old README, `product`, `ux`, `decisions`, `questions`, `stack`, `existing-system`, `requirements`, `discovery`, `client/`, `qa/`, `review/`, `diagrams/`); the old multi-agent setup (agent profiles + journals, team log/progress/qa) frozen in `solex-vault/notes/history/`. Paths inside live notes rewritten; history left as written. ezFolio scripts → `tools/ezfolio/` (tracked; `node_modules` and the Chrome `.profile` gitignored); screenshots, flow board and exports (guest data) → `local/ezfolio/` (gitignored). ctrl history stays in ctrl's git log.
- **Vault:** `solex-vault/` (renamed from `vault/` 2026-09-28, workspace 07249d7, so Obsidian shows it as "solex-vault").
- **Memory:** none migrated (SoLex never used auto-memory; everything was in the ctrl docs).
- **Old checkouts** `~/git/hub/alexluong/solex{,-architect,-lab,-qa}` untouched; `solex/CLAUDE.md` (machine-local) now points at the workspace. Retire them when convenient.
- **Verified:** fresh `claude -p` at the root: AGENTS.md via the CLAUDE.md symlink, 6 workspace skills, 4 agents, memory dir = `solex-vault/memory`, no MCP, `wt`/`backlog`/node/pnpm from mise, Write in `wt/main` denied. `wt add` + `pnpm check` green; the app itself (`mise run dev`) not booted from `wt/`.

## Open

- Evaluate an `ops/stg` env dir with a scoped Cloudflare token (Worker + D1) so the root has no Cloudflare access.
- First real `/lead` run; boot the app from a `wt/task-N` (`mise run dev` + `mise run user`).
- Retire the old `solex-*` checkouts.
