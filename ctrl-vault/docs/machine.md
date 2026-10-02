# Machine Organization

Alex's personal machine conventions (macOS). How Claude works across these repos: `ctrl-vault/docs/workflow.md`.

## Devices

Two Macs. Assume the MacBook Pro unless a doc says otherwise — most tooling here
is written for it.

| | MacBook Pro | Mac Mini |
|---|---|---|
| Role | primary dev machine | media/arrstack host (confirm) |
| Model | MacBookPro18,3 — M1 Pro, 32GB | (TBD) |
| Name | `Alexs-MacBook-Pro` | (TBD) |
| Disk | 460G — see `ctrl-vault/docs/machine-disk.md` | (TBD) |
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

- `alexluong` — personal apps & life: `ctrl` (ops hub; lives at `~/workspaces/ctrl`, `hub/alexluong/ctrl` is a symlink to it), `alexluong.com`, `cv`, `dotfiles`, `fitjournal`, `collie-ui`, `solex` (hotel back office), feed (planned), many explorations/POCs
- `collielab` — (org being established 2026-07) personal infrastructure: `infra` (VM/terraform/services; transfer of `alexluong/collielab`), `auth` (IdP login/admin UI, planned), `media` (arr migration, later)
- `colliestudio` — professional, public-facing company (Collie Studio LLC): `authkit` (planned)
- `ebutler-qa` — EButler (work): enable-backend, enable_loyalty_app, ebchat-saas-backend, etc.
- `hookdeck` — Hookdeck repos (core, CLI, SDKs)
- `nirholas`, `saifulapm`, `zengm-games` — third-party clones/forks

Org semantics: alexluong = personal apps (deploy onto collielab); collielab = the lab platform; colliestudio = only things with the company's name behind them.

## Shell shortcuts

- `sshmylab` → `ssh alex@149.28.40.6` (the homelab VM; managed via `hub/alexluong/collielab`)
- `svc` → `~/workspaces/ctrl/bin/svc` (symlink in `~/.local/bin`, so it works from any directory)

## Local services (svc + SwiftBar, set up 2026-10-02)

Long-running local processes (keep-awake, backlog boards, SSH tunnels) are started and stopped by `bin/svc`; the menubar bolt icon is a front end to it.

- **Services:** `services.conf` at the ctrl root: `[group]` per workspace, then `name | dir | url | command` lines; a service is named `<group>-<name>` (`hookdeck-board`). Add a line, it shows up in `svc ls` and the menubar within 10s. Commands run via `mise exec` in `dir`.
- **CLI:** `svc ls`, `svc start|stop|restart|toggle <name>`, `svc logs <name> [-f]`, `svc open <name>`.
- **Menubar:** SwiftBar (`brew install --cask swiftbar`), plugin folder = `ctrl/menubar/` (`defaults write com.ameba.SwiftBar PluginDirectory ~/workspaces/ctrl/menubar`). Services are listed under their workspace; click one to toggle; submenu has open/restart/log. Title shows the count running.
- **Logs:** `~/Library/Logs/svc/<name>.log` (SwiftBar keeps no output of what it launches, so `svc` does; trimmed to the last 200KB once past 1MB). Pids: `~/.local/state/svc/`.
- **Ports:** boards started by `svc` use 6421 (ctrl) to 6425, leaving each workspace's default 6420 free for a manual `backlog browser`.
- **Not handled:** nothing restarts after a reboot or a crash; a service that dies shows as stopped. `caffeinate` (`caffeinate -d`, Alex's usual flags) does not survive closing the lid.
- **New machine:** install SwiftBar, set the plugin folder, `ln -s ~/workspaces/ctrl/bin/svc ~/.local/bin/svc`, turn on Launch at Login in SwiftBar's preferences.

## Disk

460G volume. Usage baseline, buckets, and cleanup safety rules: `ctrl-vault/docs/machine-disk.md`.
Run `bin/disk-audit.sh` (or `/disk-audit`) when it fills up — diff against the last
snapshot to find what grew instead of re-deriving everything.

## Other locations

- iCloud holds binary docs (RE property PDFs etc.) — see `ctrl-vault/re/notes.md`
- No submodules anywhere — everything is colocated under `hub/alexluong/`, referenced by sibling path when needed.

## Secrets

`~/workspaces/ctrl/secrets/` is gitignored — machine-local credentials/URLs Claude needs at hand (one file per project). Canonical copy of every secret lives in Vaultwarden; a fresh machine repopulates `secrets/` from there. Never paste creds into tracked docs (2a4bf60 incident, scrubbed 2026-09-19).
