# Workspace sync: keeping the dev loop the same across workspaces

Status: **proposal (2026-10-02), nothing applied.** Alex's ask: ctrl manages the workspaces' shared skills, keeps them in sync, allows per-workspace customization, and carries an improvement made in one to the others. Related: `workspace-setup.md` (playbook), the `workspace-setup` skill (`check`, `sync`), `dev-workflow-research.md` (ideas to land once sync exists), `~/workspaces/cs/cs-vault/notes/studio/README.md` § Studio as a framework (the same idea, stated as a product).

## What exists (surveyed 2026-10-02)

| workspace | shape | dev loop specifics |
|---|---|---|
| solex | one own repo, no prod | `mise run setup/dev`, `pnpm check`, Playwright e2e, rrweb journeys, D-n decisions |
| cs | several own repos, no prod | solex's skills; Collie Demo (the evidence tool) is built here |
| enable | team super-repo + submodules, prod | slots/ports, up to 5 stacks, seed archetypes, markdown QA suites, filmed PR demo by default for UI changes, `ship`, ClickUp, nothing may leak `task-N` to the team |
| hookdeck | independent team repos, prod | QA suites in the vault + browser runner, `seed`, per-system local-dev skills, `pr-description`, `rebase`, same leak rule |
| ctrl | hub | no lead/roles; `implement` for older `hub/alexluong` repos |

All four full workspaces already run the same loop: lead → acceptance criteria → dev → independent reviewer (criteria table first) → qa on the running app with evidence → Alex merges.

Shared files today:

| file | cs | enable | hookdeck | solex | state |
|---|---|---|---|---|---|
| `skills/done` | = | = | = | = | byte-identical, enforced by `check` |
| `skills/lead` | 87 | 92 | 88 | 87 | four variants |
| `roles/{product,dev,reviewer,qa}` | 109 | 124 | 105 | 117 | four variants each (total lines) |
| `skills/{recall,tidy,workspace,worktree}` | | | | | five variants each (hashes differ; not diffed yet) |
| `skills/{qa,seed,investigate,gh-respond}` | | ✓ | ✓ | | same lineage, diverged |

Read from the `lead` and role diffs: each variant is the same skeleton with three kinds of difference.

1. **Substitutions:** vault name, `bin/wt add` argument shape, repo paths, checks command.
2. **Workspace rules:** SoLex money/D-n checklist; Enable and hookdeck team-leak rule, stack limits, tracker.
3. **Stranded improvements:** general advice that landed in one workspace only. Examples: Enable's reviewer comment checks ("workspace leak?", "too task-specific?") and "report in one or two lines, add a headline only if urgent"; hookdeck's "findings must be real: state the input or state that breaks it" and "a PR-ready review covers the full diff, not the latest delta"; Enable's "UI-visible changes get a demo by default".

Kind 3 is the problem: copy-and-adapt has no path back.

## Proposed model: identical core + local overlay

Generalize what already works for `done`.

- **Core file:** byte-identical in every workspace. Refers to specifics by indirection (`<vault>`, "the `worktree` skill", "the workspace profile"), never by name. Ends with "then read `<name>.local.md` if it exists; it wins on conflict".
- **Local overlay** (`<name>.local.md`, optional): workspace rules only. Never synced.
- **Workspace profile:** one small facts file per workspace for kind-1 substitutions (vault, repos, wt command form, branch naming, whether task IDs may appear outside, checks command, stack limit, tracker). Same keys everywhere, different values. Candidate home: a section of the `workspace` skill, or the `workspace.yaml` from the Studio notes.
- **Canonical source:** ctrl holds the core files (`ctrl/workspace-kit/`). ctrl is also a consumer for the ones it uses.

Tiers:

| tier | what | sync |
|---|---|---|
| core | `done`, `lead`, four roles, later `recall` / `tidy` SKILL.md, plus new shared pieces (verify protocol, PR body template, design standard) | byte-identical; `check` compares hashes with ctrl |
| profile | workspace facts | same keys, `check` verifies presence |
| local | overlays; `outpost-*`, `ops-*`, tracker skills | never synced |
| candidates | `qa`, `seed`, `investigate`, `gh-respond` (enable + hookdeck) | promote to core + overlay once a third workspace needs them |

## How an improvement travels

1. **Edit lands in a core file inside workspace X** (a session there fixed something): `check` reports the hash mismatch. In ctrl, read the diff and choose: accept into canonical and push to all, or move it into X's overlay because it was X-specific.
2. **Overlay rule that would help everyone:** ctrl's audit reads all overlays side by side and proposes promotions to core. Judgment, run with `tidy` or monthly.
3. **Idea from outside** (pstack, Pocock, Collie tools): edit canonical once, push, commit each workspace.
4. `done` in any workspace notes "touched a core file" so step 1 is not left to chance.

`sync` stays a plain copy + per-workspace commit. No template rendering, no generated files, no plugin.

## Rejected

- **Templates rendered per workspace:** files read naturally, but outputs are generated, so an edit made in a workspace is overwritten unless someone remembers to edit the template.
- **Agent-ported sync** (keep variants, have an agent re-apply each improvement four times): no refactor needed, but drift continues and `check` cannot verify it.
- **Personal Claude plugin:** breaks "nothing global" and harness neutrality (`.agents/skills`).
- **Shared git submodule/subtree:** adds git ceremony to every workspace for a handful of files.

## Order

1. **Pilot on `roles/reviewer.md`:** four-way compare → one core (best version of each shared paragraph, which lands the stranded improvements) + four overlays. Confirm the split reads well in a real task.
2. Same for `dev`, `qa`, `product`, then `lead`. Define the profile keys from what differs.
3. Extend `check` (hash list from ctrl) and `sync`; add the `done` hook-in.
4. Then land new ideas once, in core: finish condition wording, verify protocol and evidence, PR body template, repro-first bug path, retro → lint. See `dev-workflow-research.md`.
5. Later: `recall` / `tidy` / `workspace` / `worktree` (diff first; `wt` scripts are half generic per the Studio notes).

## Open

- Overlay as a second file vs a marked section inside the same file (a second file keeps the hash check trivial).
- Profile home: `workspace` skill section vs `workspace.yaml`.
- Whether ctrl's `implement` becomes a consumer of the role cores or stays separate.
