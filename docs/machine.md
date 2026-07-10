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

- `alexluong` — personal. Notable: `ctrl` (ops hub), `collielab` (homelab VM), `arr` (media stack, migrating into ctrl), `alexluong.com`, `cv`, `dotfiles`, `template-go-templ-tailwindcss` (Go template prior art), many explorations/POCs
- `ebutler-qa` — EButler (work): enable-backend, enable_loyalty_app, ebchat-saas-backend, etc.
- `hookdeck` — Hookdeck repos (core, CLI, SDKs)
- `nirholas`, `saifulapm`, `zengm-games` — third-party clones/forks

## Shell shortcuts

- `sshmylab` → `ssh alex@149.28.40.6` (the homelab VM; managed via `hub/alexluong/collielab`)

## Other locations

- iCloud holds binary docs (RE property PDFs etc.) — see `re/notes.md`

## Repo roles (personal ecosystem)

- **ctrl** — the brain: docs, decisions, project status, domain data (bookkeeping CSVs). No app code.
- **collielab** — the muscle: VM infra, docker-compose services, terraform DNS. Deploying a new service = new entry under `services/`.
- **project repos** — one repo per project under `hub/alexluong/`, own CLAUDE.md, own lifecycle. ctrl references them by sibling path (`~/git/hub/alexluong/<repo>`) — no submodules.
