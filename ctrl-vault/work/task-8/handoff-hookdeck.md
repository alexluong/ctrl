# TASK-8 hand-off to the hookdeck lead (2026-10-04)

For a hookdeck session **on hookdeck-ws** (the workspace's home machine). ctrl does not write to the hookdeck repo; the hookdeck lead does this as a hookdeck task and commits in its own repo. On the VM, read this file from GitHub: `gh api repos/alexluong/ctrl/contents/ctrl-vault/work/task-8/handoff-hookdeck.md --jq .content | base64 -d` (and the spec next to it).

## Paste this to the hookdeck lead

> Make this workspace able to set itself up on a fresh machine, independent of the machine. Read `ctrl-vault/work/task-8/handoff-hookdeck.md` in `alexluong/ctrl` (gh api as shown at its top) and follow its § Do. Work on this machine (hookdeck-ws); verify here, then once on the MBP (pull first, push promptly). Commit to the workspace repo directly, as a hookdeck task.

## What changed around you (already done by ctrl, 2026-10-04)

- The machine side moved to collielab: every new workspace VM now gets git identity, its own GitHub SSH key, the global Claude config and plugins, IPv4-first for `*.localhost`, Playwright's browser **system libraries**, and the Docker UIs (Dozzle `:8888`, Isaiah `:8889`). So the workspace does not need to handle any of those.
- **Docker UIs are environment now** (decided 2026-10-04): hookdeck-ws's running Dozzle/Isaiah are already managed by `collielab/hosts/workspace-vm/docker-ui.sh` (compose at `~/.config/docker-ui/compose.yml`, same project name `docker-ui`, same ports; the gw pages still work). → Remove `tools/docker-ui/` and `bin/docker-ui` from the workspace, and any mention of them (skills, notes, AGENTS.md). Do not run `bin/docker-ui down` (it would stop the live containers).
- `collielab/hosts/hookdeck-ws/setup.sh` (Doppler apt repo, mise pre-install, gopls, golangci-lint, Playwright libs) gets **deleted** once this lands. Its job moves into the workspace.
- The VM can't open connections to home machines or other tailnet nodes (firewall + Tailscale policy). Nothing in the workspace should rely on `192.168.1.x` or `*.lab.alexluong.com` from the VM.

## Do

1. **Tools into `mise.toml`** (checked 2026-10-04: all resolve; versions = what hookdeck-ws runs today):

   | tool | pin | notes |
   |---|---|---|
   | Doppler CLI | `doppler = "3.76.6"` | registry → `github:DopplerHQ/cli`. Today an apt package on the VM, brew on the MBP: remove those after (VM: `sudo apt-get remove doppler` + `/etc/apt/sources.list.d/doppler-cli.list`; MBP: `brew uninstall doppler`), check `doppler me` still works (the login is in `~/.doppler`, not the binary) |
   | golangci-lint | `golangci-lint = "2.14.0"` | registry → `aqua:golangci/golangci-lint` |
   | gopls | `"go:golang.org/x/tools/gopls" = "0.23.0"` | for the Claude gopls-lsp plugin |
   | pnpm | `pnpm = "11.7.0"` | the repos' `packageManager` field stays the truth inside them; this makes it available everywhere without `corepack enable` |
   | psql, redis-cli | **not in mise** | mise's postgres/redis build from source (slow, need compilers). Keep the OS package (the VM template has `postgresql-client`, `redis-tools`; MBP: `brew install libpq redis`); a checklist row with the install line per OS, and a `doctor` check |
   | k6, goreleaser, clickhouse, ffmpeg | only when a skill needs them | all in the registry |

   Verify each installs on Debian 13 x86_64 (here) and macOS arm64 (MBP).

2. **`mise run setup`** (idempotent, no logins, no sudo): `mise trust ops/*/mise.toml`, `bin/wt init`, `gcloud components install gke-gcloud-auth-plugin` (in the workspace's gcloud), Playwright's browser at the version the repos use (`npx playwright install chromium`, no `--with-deps`: the OS libraries are the machine's), `corepack`/`pnpm install` in `wt/core/main` if missing, and `--pull-images` as an option for the stacks' public images (today `~/prepull-images.sh` on the VM; move its list in).

3. **`mise run doctor`** (read-only, one table, never prints a value, exit non-zero when something required is missing; ends with "left for you: …"): tool versions vs `mise.toml`; Docker reachable; psql/redis-cli present; logins: `gh auth status`, GitHub SSH (`ssh -T git@github.com`), `doppler me`, `railway whoami`, gcloud per env (`stg`/`prd` wrappers: account set + ADC file present), kubectl contexts, Docker Hub entry in `~/.docker/config.json`, jumpbox key + `Host` blocks (`hd_jumpbox`, `hd_jumpbox_stg`), AWS (`aws:whoami`, optional), npm token line in `~/.npmrc` (optional), Notion MCP (optional: say how to check); config files present: the 13 paths in ctrl `docs/vms/hookdeck-ws.md` § Secret files (existence only).

4. **Access checklist** (one doc in the workspace; the lead picks the place): per login: what for, reach (read / write / prod), how on a machine without a browser (device codes, `--no-launch-browser`, `railway login --browserless`, copy `.gcloud/` from the other machine), how `doctor` checks it. Source to start from: ctrl `docs/vms/hookdeck-ws.md` § Logins and § Secret files. One list shared with `doctor` (doctor reads it, or the doc is generated from it).

5. **`.env.example`** next to `.env`, `ops/stg/.env`, `ops/prd/.env`, `ops/prd/outpost/*.env`, `ops/prd-rw/.env`, and the worktree env files (`wt/core/main/local-dev/env/.env.dev`, `wt/outpost/main/.env`, …: only if those repos don't already ship an example). Names + where each value comes from. Agents may not read `ops/**/.env` or the root `.env` (AGENTS.md, settings deny): derive names from `bin/env-run`, the ops skills and scripts that use them; if that is not enough, ask Alex for a names-only extraction.

6. **`setup` skill**: on a fresh machine: `mise install`, `mise run setup`, `mise run doctor`, fix what it may, end with the human list.

7. **Rule in `AGENTS.md`** (short): new tool → `mise.toml` (no global/apt/brew/`go install` by hand); new login → checklist row + `doctor` check; new config variable → the example file; an OS package only if unavoidable, with the install line per OS in the checklist.

8. The workspace's machines note (`hookdeck-vault/notes/machines.md`) stays about where it runs; the setup doc holds no VM details.

## Done when

- `mise run doctor` passes on hookdeck-ws and on the MBP; `mise run setup` twice in a row changes nothing.
- Doppler, gopls, golangci-lint come from mise on both machines (old installs removed).
- `tools/docker-ui`, `bin/docker-ui` gone; Dozzle/Isaiah still up.
- Tell Alex (or leave a comment for ctrl TASK-8): ctrl then deletes `collielab/hosts/hookdeck-ws/setup.sh` and proves the whole flow on a throwaway VM (clone, setup, doctor shows only logins left).
