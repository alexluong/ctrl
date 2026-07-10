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

- **ctrl** — portfolio level only: project index (what exists, why, one-line status), cross-project notes (bootstrap stack, org/meta), domain data (bookkeeping, RE). No app code, no project internals.
- **project repos** — one repo per project under `hub/alexluong/`, fully self-contained: code + docs + decisions + TODOs + own CLAUDE.md. Claude sessions for project work run in the project repo. No back-pointers to ctrl.
- **collielab** — VM infra, docker-compose services, terraform DNS. Deploying a new service = new entry under `services/`.
- No submodules anywhere — everything is colocated under `hub/alexluong/`, referenced by sibling path when needed.

Project docs flow: `ctrl/docs/projects/<name>.md` is each project's living doc (idea → plan → status), kept in ctrl even after the code repo exists. New Claude sessions in a project repo get context by pasting the project doc (pbcopy) — no standing back-pointers.
