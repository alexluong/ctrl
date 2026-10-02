# TASK-8 spec: workspace self-setup (2026-10-03)

From the discussion with Alex after the first workspace VM (`hookdeck-ws`, TASK-2). Background: `docs/vms/playbook.md`, `docs/vms/hookdeck-ws.md`, `work/task-2/hookdeck-vm-requirements.md`.

## Principle (Alex)

- "The ws ideally only care about what it does, not the environment around it." The workspace states its **tools** and **access**; it knows nothing about VMs, Proxmox, T3 or addresses.
- "It would be nice where it's easy to just think: get a VM and the workspace can have its own todo to set things up properly."
- OS differences: "rely on `mise` as much as possible".
- Secret files are not a list to copy: "basically just the ops/ setup"; `.env.example` files, and whoever wants to run something authenticates and fills them in.
- "Make it so that the workspace agents can add more themselves as needed."

## Why (what went wrong the first time)

What hookdeck needs was written in `collielab/hosts/hookdeck-ws/setup.sh` and ctrl docs, away from the sessions that change those needs. Within a day sessions in the workspace added `cloudflared`, `gotestsum` (mise) and Docker UIs (`tools/docker-ui`) in the workspace repo; the collielab script and ctrl tables did not follow. Logins, secret paths and images were prose tables: a rebuild means reading docs and retyping.

## Target flow

1. Machine side: `bin/new-vm <id> <name>-ws …` (collielab). Base template gives Docker, git, gh, mise, Claude Code, T3, system libraries, Linux quirks.
2. Alex: `claude` login, `gh auth login`; clone the workspace to `~/workspaces/<name>`.
3. In the workspace: `mise install && mise run setup`, or a session with the `setup` skill.
4. `mise run doctor` prints what is left for the human (logins, config values).

## Workspace side (hookdeck first)

1. **Tools in `mise.toml`.** Move in what is installed outside mise today:

   | tool | today | mise (registry checked 2026-10-03 on the MBP) |
   |---|---|---|
   | Doppler CLI | apt repo in `hosts/hookdeck-ws/setup.sh`; brew on the MBP | `doppler` (github:DopplerHQ/cli) |
   | golangci-lint | `go install` | `golangci-lint` (aqua) |
   | gopls | `go install` | not in the registry by name: `go:golang.org/x/tools/gopls` |
   | pnpm | corepack (`corepack enable`); core and website pin `pnpm@11.7.0` in `package.json` | `pnpm`, same version; the repos' `packageManager` field stays the truth for them |
   | psql, redis-cli | apt in the base template; brew on the MBP | Alex wants them in. mise's `postgres` and `redis` plugins build from source (slow, need build tools): look for a prebuilt route first (conda backend, a release binary); if none, keep the OS package and let `doctor` say how to install it |
   | k6, goreleaser, clickhouse, ffmpeg | "add when needed" | all in the registry; add when a skill needs them |

   First check: each installs cleanly on Debian 13 x86_64 and macOS arm64 (not tested yet).
2. **`mise run setup`**: idempotent; everything a fresh clone needs that is not a login: `mise trust ops/*/mise.toml`, `bin/wt init`, `gcloud components install gke-gcloud-auth-plugin`, Playwright's browser (and on Linux `playwright install-deps`, which needs sudo: use node's real path, not the shim), dependency install in `wt/core/main`, pre-pull of the stacks' images (optional flag).
3. **`mise run doctor`**: read-only, one table: tool versions against `mise.toml`, Docker reachable, each login valid (`gh auth status`, `doppler me`, `railway whoami`, `gcloud auth list` for the workspace's configs, Docker Hub entry, jumpbox key and hosts, AWS, npm, Notion), each expected config file present or missing. Never prints a value. Exit code non-zero when something required is missing.
4. **Access checklist** in the workspace (one doc): login, what it is for, reach (read / write / prod), how to do it on a machine without a browser, how it is checked. `doctor` and the doc share one list if possible (the doc generated from the list, or the list read from the doc).
5. **`.env.example`** next to each env file (`.env`, `ops/*/.env`, `ops/prd/outpost/`): variable names and where each value comes from (Doppler project, Vaultwarden item, a dashboard). Constraint: workspace agents are forbidden to read `ops/**/.env` and the root `.env` (hookdeck `AGENTS.md` line 107, enforced in `.claude/settings.json`): derive the names from the scripts and skills that use them (`bin/env-run`, the ops skills), or have Alex run a names-only extraction.
6. **`setup` skill**: on a fresh machine an agent runs setup, runs doctor, fixes what it may, and ends with the list for the human.
7. **Rule for agents** (`AGENTS.md`, short; detail in the skill): a new tool is pinned in `mise.toml` (no global install, apt, brew or `go install` by hand); a new login gets a row in the checklist and a `doctor` check; a new config variable goes into the example file. If something truly needs an OS package, it is recorded in the checklist with the install line per OS.
8. `hookdeck-vault/notes/machines.md` stays the note about the two machines; the setup doc holds no VM details.

## Machine side

1. `collielab/hosts/hookdeck-ws/setup.sh`: remove what the workspace now does (Doppler repo, mise pre-install, gopls, golangci-lint, Playwright libs). What is left should be nothing, or be moved: IPv4-first for `*.localhost` (`/etc/gai.conf`) and browser system libraries go into the base template (`hosts/g8/vm-template/provision.sh`); the VM's GitHub SSH key generation goes into `hosts/workspace-vm/setup.sh`.
2. Shared pieces every workspace VM gets, in `hosts/workspace-vm/setup.sh`: global Claude config (today copied by hand from dotfiles), git identity. **Open:** the Docker UIs (Dozzle, Isaiah) live in the hookdeck repo (`tools/docker-ui`, `bin/docker-ui`); by the principle above they are environment, not workspace: move to the common VM setup? Ask Alex. They run with no login and with actions and shell enabled.
3. Rebuild template 9000 (also carries the PATH fix `6b3a54a`). Replaces the template: Alex's OK first. Existing VMs are full clones and are not affected.
4. ctrl `docs/vms/playbook.md`: steps 2 (survey), 4 (per-workspace script), 7–9 (clone, secrets, logins) become "clone, setup, doctor"; the survey stays only for a workspace that has no setup doc yet (it is how the first checklist gets written). Copying env files from Alex's other machine stays as a shortcut there, driven by what `doctor` reports missing. Per-VM doc template shrinks to: size, address, state, services around sessions, resources, differences on this machine.
5. ctrl `docs/workspace-setup.md` (the agent-workspace playbook) and the `workspace-setup` skill: add the convention (mise tools, `setup` and `doctor` tasks, access checklist, example files, the agent rule), then port to `enable`, `solex`, `cs`.

## Constraints while doing it

- **The hookdeck workspace is live on two machines.** MBP and VM sessions both commit; task IDs collided once on 2026-10-02 (hookdeck `machines.md`: "task IDs collide across machines"), and on 2026-10-03 the MBP checkout was 3 commits ahead and 11 behind with `MEMORY.md` touched on both sides. Do the hookdeck part through the hookdeck lead on one machine as a hookdeck task; do not edit that repo from a ctrl session.
- hookdeck's own rules apply there: changes in task worktrees for team repos; the workspace repo is Alex's and is committed directly.
- No secrets in any tracked file; `doctor` and the examples carry names only.

## Ask to paste to the hookdeck lead

> Make this workspace able to set itself up on a fresh machine, independent of the machine (spec: `~/workspaces/ctrl/ctrl-vault/work/task-8/spec.md` on the MBP, § Workspace side; on the VM read it from `alexluong/ctrl`). Pin in `mise.toml` the tools installed outside mise (doppler, golangci-lint, gopls, pnpm, psql, redis-cli), add `mise run setup` and `mise run doctor`, an access checklist, `.env.example` files, a `setup` skill, and a short rule in `AGENTS.md` so agents add tools and access items there. Verify on the VM and the MBP.

## Order

1. hookdeck workspace side (items 1–7), verified on the VM where the tools already exist, then on the MBP.
2. Machine side 1–3, then a fresh throwaway VM to prove the flow.
3. Docs (machine side 4–5), then the other workspaces.
