# Machine Organization

Alex's personal machine conventions (macOS).

## ~/git layout

```
~/git/
  hub/<github-org>/<repo>   # GitHub clones, mirrors github.com/<org>/<repo>
  lab/                      # empty (as of 2026-07) — purpose TBD
  parallel/                 # Civ6 modding (Parallels/Windows-adjacent); repos here
                            # can still have github.com/alexluong remotes
```

### hub orgs (as of 2026-07)

- `alexluong` — personal apps & life: `ctrl` (ops hub), `alexluong.com`, `cv`, `dotfiles`, fitjournal/feed (planned), many explorations/POCs
- `collielab` — (org being established 2026-07) personal infrastructure: `infra` (VM/terraform/services; transfer of `alexluong/collielab`), `auth` (IdP login/admin UI, planned), `media` (arr migration, later)
- `colliestudio` — professional, public-facing company (Collie Studio LLC): `authkit` (planned)
- `ebutler-qa` — EButler (work): enable-backend, enable_loyalty_app, ebchat-saas-backend, etc.
- `hookdeck` — Hookdeck repos (core, CLI, SDKs)
- `nirholas`, `saifulapm`, `zengm-games` — third-party clones/forks

Org semantics: alexluong = personal apps (deploy onto collielab); collielab = the lab platform; colliestudio = only things with the company's name behind them.

## Shell shortcuts

- `sshmylab` → `ssh alex@149.28.40.6` (the homelab VM; managed via `hub/alexluong/collielab`)

## Other locations

- iCloud holds binary docs (RE property PDFs etc.) — see `re/notes.md`

## Repo roles (personal ecosystem)

- **ctrl** — the notes layer for everything: project living docs (idea → design → decisions → status), cross-project notes (bootstrap stack, org/meta), domain data (bookkeeping, RE). No app code.
- **project repos** — one repo per project under `hub/alexluong/`, **code-only**: no IDEAS/NOTES/TODO markdown; only docs strictly part of the software (README for building/running). Claude sessions for project work run in the project repo.
- **collielab** — VM infra, docker-compose services, terraform DNS. Deploying a new service = new entry under `services/`.
- No submodules anywhere — everything is colocated under `hub/alexluong/`, referenced by sibling path when needed.

Project docs flow (convention set 2026-07-10, first applied to fitjournal): `ctrl/docs/projects/<name>.md` is each project's single living doc, kept in ctrl for the project's whole life. Each project repo gets a **machine-local, untracked `CLAUDE.md`** pointing at that doc — ignored via `.git/info/exclude` (add `CLAUDE.md` line), so the repo stays 100% code even in `.gitignore`. The pointer tells sessions to read the ctrl doc at start, write decisions back to it (committing in ctrl), and never create notes files or use `~/.claude` memory. On a new machine, recreate the pointer + exclude entry per project (any ctrl session can do it).

## Claude session modes (hub-and-spoke)

Two ways to work on a project; both keep notes in ctrl:

1. **ctrl as cockpit** — Alex talks to a ctrl session; discussion/decisions land in the project doc; the session delegates impl to subagents working in the project repo (agent prompt inlines the relevant design constraints — agents start with zero context). Agent reports back → ctrl session logs status, code lands in the project repo. Best for design-heavy work and well-scoped impl tasks.
2. **Direct project session** — session started in the project repo; the untracked pointer CLAUDE.md feeds it context. Best for long interactive impl grind (build/debug loops, UI iteration).

`ctrl/.claude/settings.json` grants `additionalDirectories: ~/git/hub/alexluong` so cockpit sessions/subagents write to sibling project repos without permission prompts.

## Project repo working conventions (set 2026-07-10)

Personal projects are lowkey — optimize for Claude operating solo, not team process.

- **Git flow:** default direct commits to main. Scope-dependent: branch + GitHub PR when the change is large or Alex wants to review — especially cockpit-delegated impl (agent works on a branch, opens a PR, Alex reviews on GitHub). When unsure and the change is big, prefer the PR.
- **Commits:** Conventional Commits — `feat:` / `fix:` / `chore:` / `refactor:` / `docs:` / `test:`, optional scope (`feat(capture): …`), lowercase subject, body only when the why isn't obvious. Small, coherent commits. Applies to all personal repos going forward, ctrl included (`docs:` covers most ctrl commits).
- **Code organization:** per-project call — pick what fits the project's shape at its current size, record the chosen layout in the project's ctrl doc, follow it consistently. No preemptive abstraction for hypothetical futures.
- **Quality bar:**
  - Unit tests for genuinely tricky logic (date/tz handling, transforms, parsing). No coverage targets or test-first ritual.
  - Integration/e2e tests covering the full happy-path flows.
  - **QA specs, git-based:** human-readable test cases live in the project repo under `qa/` — markdown, one file per feature area (preconditions / steps / expected). They count as part of the software (allowed in code-only repos), version with the code, and are updated in the same commit as behavior changes. Used as manual QA checklists and as the source for e2e automation.
