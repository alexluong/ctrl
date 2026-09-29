---
name: workspace-setup
description: Set up, audit, or update personal agent workspaces (~/workspaces/<name>) — new workspace from the playbook, drift check across all workspaces, or propagate a shared change (e.g. the done skill) to every workspace. Use for "set up a workspace for X", "check the workspaces", "sync done/skill across workspaces".
---

# Workspace setup

Source of truth: `docs/workspace-setup.md` (playbook: principles, steps 0–9, gotchas). This skill drives it; don't duplicate its content here. Per-workspace history: `docs/projects/<name>-workspace.md`. Related: `docs/claude-config.md`, `docs/infra-access.md`.

Pick the mode from the request; ask if unclear.

## new `<name>`

1. Read `docs/workspace-setup.md` in full, plus the reference workspace's project doc closest to the shape (playbook intro lists them: enable = super-repo + systems + prod; hookdeck = independent team repos + prod; solex = one own repo; cs = several own repos, no prod).
2. Step 0 decisions 👤: ask Alex everything in one `AskUserQuestion` round; propose defaults from the closest reference.
3. Run steps 1–9 in order. Copy from the closest reference workspace and adapt, never write from scratch. Stop at each ✅ checkpoint: commit + push in the workspace, summarize, wait for Alex. Hand 👤 steps to Alex with exact commands.
4. Skip infra steps (7, prod parts of 8) for workspaces with no prod.
5. End: run `check <name>`; must be clean.

## audit

1. Run `.claude/skills/workspace-setup/check` (all workspaces) or `check <name>`. It checks the structural invariants: CLAUDE.md→AGENTS.md symlink, `.claude/skills` symlink, standard skills + scripts, roles + agent wrappers, identical `done`, vault dirs + digest, memory settings, hooks, deny rules, gitignore essentials, prod guard when `ops/` exists, favicon tracked, dirty/unpushed.
2. Beyond the script (judgment): `AGENTS.md` layout section matches the tree; `recall`/`tidy` adapted to this workspace (vault name, branch naming, stack commands); gotchas in the playbook newer than the workspace's setup applied (e.g. PATH line in `session-env.sh`).
3. Report per workspace, concise. Uncommitted work in a vault may belong to a live session: report it, don't commit it. Fix setup drift only after Alex agrees.

## sync `<file>`

For files meant to be identical across workspaces (today: `.agents/skills/done/SKILL.md`):

1. Edit in one workspace, then `for w in ~/workspaces/*/; do cp <src> "$w<path>"; done`.
2. Commit + push each workspace (`skills: <what>`); run `check`.
3. Changing what counts as shared → update the playbook step 5 and `std_skills`/checks in `check`.

## After any mode

- New lesson → add to the playbook's Gotchas (and the step it affects); new invariant → add it to `check`.
- Update `docs/projects/<name>-workspace.md` "as built"; commit ctrl (`docs(workspace-setup): …`).
