# Claude Workflow & Repo Conventions

How Claude operates across Alex's personal repos. Machine layout facts: `docs/machine.md`. Conventions set 2026-07-10, first applied to fitjournal.

## Repo roles

- **ctrl** — the notes layer for everything: project living docs (idea → design → decisions → status), cross-project notes, domain data (bookkeeping, RE). No app code.
- **project repos** — one repo per project under `hub/alexluong/`, **code-only**: no IDEAS/NOTES/TODO markdown. Allowed non-code: docs strictly part of the software (README for building/running) and `qa/` specs (see Quality bar).
- **collielab** — VM infra, docker-compose services, terraform DNS. Deploying a new service = new entry under `services/`.

## Project docs flow

`ctrl/docs/projects/<name>.md` is each project's single living doc, kept in ctrl for the project's whole life. Each project repo gets a **machine-local, untracked `CLAUDE.md`** pointing at that doc — ignored via `.git/info/exclude` (add `CLAUDE.md` line), so the repo stays 100% code even in `.gitignore`. The pointer tells sessions to read the ctrl doc at start, write decisions back to it (committing in ctrl), and never create notes files or use `~/.claude` memory. On a new machine, recreate the pointer + exclude entry per project — the `/new-project` skill does this.

## Session modes (hub-and-spoke)

Two ways to work on a project; both keep notes in ctrl:

1. **ctrl as cockpit** — Alex talks to a ctrl session; discussion/decisions land in the project doc; the session delegates impl to subagents working in the project repo (agent prompt inlines the relevant design constraints — agents start with zero context). Agent reports back → ctrl session logs status, code lands in the project repo. Best for design-heavy work and well-scoped impl tasks.
2. **Direct project session** — session started in the project repo; the untracked pointer CLAUDE.md feeds it context. Best for long interactive impl grind (build/debug loops, UI iteration).

`ctrl/.claude/settings.json` grants `additionalDirectories: ~/git/hub/alexluong` so cockpit sessions/subagents write to sibling project repos without permission prompts.

## Working conventions

Personal projects are lowkey — optimize for Claude operating solo, not team process.

- **Git flow:** default direct commits to main. Scope-dependent: branch + GitHub PR when the change is large or Alex wants to review — especially cockpit-delegated impl (agent works on a branch, opens a PR, Alex reviews on GitHub). When unsure and the change is big, prefer the PR.
- **Commits:** Conventional Commits — `feat:` / `fix:` / `chore:` / `refactor:` / `docs:` / `test:`, optional scope (`feat(capture): …`), lowercase subject, body only when the why isn't obvious. Small, coherent commits. Applies to all personal repos going forward, ctrl included (`docs:` covers most ctrl commits).
- **Code organization:** per-project call — pick what fits the project's shape at its current size, record the chosen layout in the project's ctrl doc, follow it consistently. No preemptive abstraction for hypothetical futures.
- **Quality bar:**
  - Unit tests for genuinely tricky logic (date/tz handling, transforms, parsing). No coverage targets or test-first ritual.
  - Integration/e2e tests covering the full happy-path flows.
  - **QA specs, git-based:** human-readable test cases live in the project repo under `qa/` — markdown, one file per feature area (preconditions / steps / expected). They count as part of the software, version with the code, and are updated in the same commit as behavior changes. Used as manual QA checklists and as the source for e2e automation.
