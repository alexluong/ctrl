---
name: workspace-setup
description: Set up, audit, or update personal agent workspaces (~/workspaces/<name>) — new workspace from the playbook, drift check across all workspaces, propagate an identical file (the done skill), or port an improvement from one workspace's adapted skill or role into the others. Use for "set up a workspace for X", "check the workspaces", "sync done/skill across workspaces", "port this to the other workspaces".
---

# Workspace setup

Source of truth: `ctrl-vault/docs/workspace-setup.md` (playbook: principles, steps 0–9, gotchas). This skill drives it; don't duplicate its content here. Per-workspace history: `ctrl-vault/docs/projects/<name>-workspace.md`. Related: `ctrl-vault/docs/claude-config.md`, `ctrl-vault/docs/infra-access.md`.

Pick the mode from the request; ask if unclear.

## new `<name>`

1. Read `ctrl-vault/docs/workspace-setup.md` in full, plus the reference workspace's project doc closest to the shape (playbook intro lists them: enable = super-repo + systems + prod; hookdeck = independent team repos + prod; solex = one own repo; cs = several own repos, no prod).
2. Step 0 decisions 👤: ask Alex everything in one `AskUserQuestion` round; propose defaults from the closest reference.
3. Run steps 1–9 in order. Copy from the closest reference workspace and adapt, never write from scratch. Stop at each ✅ checkpoint: commit + push in the workspace, summarize, wait for Alex. Hand 👤 steps to Alex with exact commands.
4. Skip infra steps (7, prod parts of 8) for workspaces with no prod.
5. End: run `check <name>`; must be clean.

## audit

1. Run `.agents/skills/workspace-setup/check` (all workspaces) or `check <name>`. It checks the structural invariants: CLAUDE.md→AGENTS.md symlink, `.claude/skills` symlink, standard skills + scripts, roles + agent wrappers, identical `done`, vault dirs + digest, memory settings, hooks, deny rules, gitignore essentials, prod guard when `ops/` exists, favicon tracked, dirty/unpushed.
2. Beyond the script (judgment): `AGENTS.md` layout section matches the tree; `recall`/`tidy` adapted to this workspace (vault name, branch naming, stack commands); gotchas in the playbook newer than the workspace's setup applied (e.g. PATH line in `session-env.sh`).
3. Report per workspace, concise. Uncommitted work in a vault may belong to a live session: report it, don't commit it. Fix setup drift only after Alex agrees.

## sync `<file>`

For files meant to be identical across workspaces (today: `.agents/skills/done/SKILL.md`):

1. Edit in one workspace, then `for w in ~/workspaces/*/; do cp <src> "$w<path>"; done`.
2. Commit + push each workspace (`skills: <what>`); run `check`.
3. Changing what counts as shared → update the playbook step 5 and `std_skills`/checks in `check`.

## port `<improvement>`

For files each workspace adapts (`lead`, `.agents/roles/*`, `recall`, `tidy`, `workspace`, `worktree`, and skills two workspaces share such as `qa`, `seed`, `investigate`, `gh-respond`). ctrl does the syncing; workspaces don't pull. Background: `ctrl-vault/docs/workspace-sync.md`.

1. Diff the file across workspaces (`diff ~/workspaces/{a,b}/.agents/…`). Sort each difference: substitution (vault, paths, `wt` form), workspace rule (keep where it is), or general improvement (port it).
2. Show Alex the list of improvements and which workspaces lack each. Port only what Alex agrees to.
3. Edit each workspace's own copy, in its own wording and paths. Never overwrite a variant with another workspace's file.
4. Don't write a workspace repo that has live sessions, a dirty tree, or its home on another machine (hookdeck = the `hookdeck-ws` VM): put the ask in a ctrl task and hand it to that workspace's lead (memory `shared-checkouts-parallel-sessions`).
5. Commit + push each workspace (`skills: <what>`); run `check`.

## After any mode

- New lesson → add to the playbook's Gotchas (and the step it affects); new invariant → add it to `check`.
- Update `ctrl-vault/docs/projects/<name>-workspace.md` "as built"; commit ctrl (`docs(workspace-setup): …`).
