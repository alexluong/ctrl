# Machine Organization

Alex's personal machine conventions (macOS). How Claude works across these repos: `docs/workflow.md`.

## Devices

Two Macs. Assume the MacBook Pro unless a doc says otherwise — most tooling here
is written for it.

| | MacBook Pro | Mac Mini |
|---|---|---|
| Role | primary dev machine | media/arrstack host (confirm) |
| Model | MacBookPro18,3 — M1 Pro, 32GB | (TBD) |
| Name | `Alexs-MacBook-Pro` | (TBD) |
| Disk | 460G — see `docs/machine-disk.md` | (TBD) |
| macOS | 26.5.2 | (TBD) |

The Mac Mini runs the arrstack (`hub/alexluong/arr`) — that repo's README
describes Colima setup that applies to the Mini, **not** the MBP. Colima was
removed from the MBP on 2026-08-02.

Anything device-specific should say which device it's for. `bin/disk-audit.sh`
and the `/disk-audit` skill are **MacBook Pro only** — the buckets, paths, and
budgets are all sized for it.

## ~/git layout

```
~/git/
  hub/<github-org>/<repo>   # GitHub clones, mirrors github.com/<org>/<repo>
  lab/                      # empty (as of 2026-07) — purpose TBD
  parallel/                 # Civ6 modding (Parallels/Windows-adjacent); repos here
                            # can still have github.com/alexluong remotes
```

### hub orgs (as of 2026-07)

- `alexluong` — personal apps & life: `ctrl` (ops hub), `alexluong.com`, `cv`, `dotfiles`, `fitjournal`, `design-system-lab`, feed (planned), many explorations/POCs
- `collielab` — (org being established 2026-07) personal infrastructure: `infra` (VM/terraform/services; transfer of `alexluong/collielab`), `auth` (IdP login/admin UI, planned), `media` (arr migration, later)
- `colliestudio` — professional, public-facing company (Collie Studio LLC): `authkit` (planned)
- `ebutler-qa` — EButler (work): enable-backend, enable_loyalty_app, ebchat-saas-backend, etc.
- `hookdeck` — Hookdeck repos (core, CLI, SDKs)
- `nirholas`, `saifulapm`, `zengm-games` — third-party clones/forks

Org semantics: alexluong = personal apps (deploy onto collielab); collielab = the lab platform; colliestudio = only things with the company's name behind them.

## Shell shortcuts

- `sshmylab` → `ssh alex@149.28.40.6` (the homelab VM; managed via `hub/alexluong/collielab`)

## Disk

460G volume. Usage baseline, buckets, and cleanup safety rules: `docs/machine-disk.md`.
Run `bin/disk-audit.sh` (or `/disk-audit`) when it fills up — diff against the last
snapshot to find what grew instead of re-deriving everything.

## Other locations

- iCloud holds binary docs (RE property PDFs etc.) — see `re/notes.md`
- No submodules anywhere — everything is colocated under `hub/alexluong/`, referenced by sibling path when needed.
