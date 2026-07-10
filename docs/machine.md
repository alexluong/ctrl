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
