# Playbook: put a workspace on a VM

How to take a workspace that runs on the MBP (`~/workspaces/<name>`) and give it an always-on VM on g8 where its agent sessions run, driven from T3 on the MBP. Written from the first run (`hookdeck-ws`, 2026-10-02); follow it for `enable`, `solex`, `cs` and any later workspace. A new Proxmox box first needs `new-host.md`.
Scripts: `collielab` (`bin/new-vm`, `hosts/g8/`, `hosts/workspace-vm/`, `hosts/<vm>/`). Record per VM: `vms/<vm>.md`. Example of every step done: `../../work/task-2/log.md`.

**Time:** about 1 hour, of which 15 minutes are Alex's (logins). The VM itself takes 40 seconds.

## What is fixed, what varies

| Fixed (the base template gives it) | Varies per workspace (this playbook finds and installs it) |
|---|---|
| Debian 13, user `alex` with passwordless sudo, the fleet's SSH keys | size (cores, RAM, disk) |
| Docker + compose, git, gh, mise, Node 22, Claude Code, T3 Code server binary | tools pinned by the workspace `mise.toml`; extra system packages |
| raised file-watch and open-file limits, capped container logs | CLIs outside mise (e.g. Doppler), language servers, browsers for tests |
| T3 service on loopback, reached over SSH | Docker images of its dev stacks |
| | logins and secret files |
| | services around sessions (tunnels, board: what the MBP menubar ran for it) |
| | Mac-only assumptions in its scripts |

## Steps

**Two paths (TASK-8).** A workspace that **sets itself up** (`mise run setup` and `mise run doctor` in its repo, access checklist, `.env.example` files: `../workspace-setup.md` § Self-setup) skips steps 2 and 4: after step 3 it is logins → clone → `mise run setup` → `mise run doctor`, and steps 8–9 shrink to what `doctor` reports missing. A workspace without it yet follows every step below, and the survey (step 2) becomes the first draft of its checklist. hookdeck: being converted (hand-off `../../work/task-8/handoff-hookdeck.md`); enable: next.

The machine side is the same for both: `bin/new-vm` gives the firewall (on before first boot), T3 server, git identity, the VM's GitHub key, the global Claude config and plugins (the same small user-level layer as the MBP: preferences and permissions, every plugin installed but disabled; tools and MCP stay per workspace, `../claude-config.md`), and with `--tailscale` the tailnet.


Who: **C** = Claude from the ctrl session on the MBP, **A** = Alex.

### 1. Decide name, number, size (C proposes, A confirms)

- Name `<workspace>-ws`. The same name is the Proxmox name, hostname, DNS label, SSH alias and T3 environment. **Pick it before creating the VM**: renaming later regenerates the VM's SSH host keys.
- ID = last number of the address, next free in g8's block `101–149` (`vms/README.md` lists what is taken).
- Size: measure the workspace's stacks on the MBP (`docker stats --no-stream`, plus the memory of its node/go processes). RAM decides; idle CPU is small. hookdeck: one full stack ≈ 8.5GB, VM 32GB. Disk is a ceiling, not reserved: 250GB for a heavy workspace, 64–120GB for a light one. Total RAM of running VMs must stay under ~60GB.

### 2. Survey the workspace on the MBP (C, read-only, ~8 minutes)

Run an agent with the prompt in § Survey prompt. Save its report as `work/task-N/<vm>-requirements.md`. It answers: system packages, tool versions, repos and how they are cloned, Docker images and ports, Mac-only paths, Claude config, logins, secret files, workload shape, disk sizes.

### 3. Create the VM (C, 1 minute)

```sh
cd ~/git/hub/alexluong/collielab && git pull
bin/new-vm <id> <name>-ws <cores> <memory_mb> <disk_gb> [--tailscale]   # clone, host keys, SSH alias, DNS snippet, T3 service (+ tailnet)
cd terraform && source scripts/export_env.sh && terraform apply   # <name>-ws.lab.alexluong.com
```

Every new VM gets the Proxmox firewall (`hosts/g8/firewall.sh`): it can't start connections into the home network, no IPv6; internet, DNS, Tailscale fine.

`--tailscale` (opt-in): the VM joins the tailnet as `tag:vm` and its name points at its Tailscale address, so `ssh <name>-ws` and T3 work at home and away. Can be done later with `bin/vm-tailnet <name>-ws`. Needs `ctrl/secrets/tailscale/vm-join.key`. What it means and the rules a VM gets: `../tailscale.md`.

Wait a minute before the first lookup of the new name (check with `dig +short <name>-ws.lab.alexluong.com @1.1.1.1` first): a lookup made too early gets a "not found" that the MBP and Viettel's DNS keep for 30 minutes. Until then use the address. Commit only the files `bin/new-vm` touched (`ssh/config`, `ssh/known_hosts`, `terraform/alexluong_com.tf`), then push.

### 4. Workspace-specific setup script (C, 10–20 minutes)

Write `collielab/hosts/<name>-ws/setup.sh` from the survey (the last example is hookdeck's, in collielab git history before 2026-10-04: `git show 4425eff^:hosts/hookdeck-ws/setup.sh`); better: give the workspace self-setup first (`../workspace-setup.md` § 7a): apt repos and CLIs outside mise, pre-install of the tools the workspace `mise.toml` pins, language servers, test browsers' system libraries, an SSH key for GitHub, anything the stacks need from the OS. No logins, no secrets, idempotent. Run it: `ssh <name>-ws 'bash -s' < hosts/<name>-ws/setup.sh`. Add `hosts/<name>-ws/README.md` (three lines, pointing at `vms/<name>-ws.md`).

Done by `bin/new-vm` since TASK-8 (not here): global Claude config from dotfiles, Claude plugins, git identity, the VM's GitHub key, IPv4-first for `*.localhost` and browser system libraries (template). Docker UIs are hookdeck's own (`bin/docker-ui` in that workspace).

Also by hand until the workspace does it (`mise run setup` with a pre-pull flag):

- Pre-pull the stacks' public images (list from the survey) with a small script left in the VM's home, run under `nohup`.

### 5. Snapshot `clean-setup` (C)

`ssh g8 'qm snapshot <id> clean-setup --description "tools, no login or secret"'`. The state to roll back to if the logins go wrong.

### 6. First logins (A, 5 minutes)

The VM has no browser: every login prints a link and a code to finish in the MBP's browser.

```sh
ssh <name>-ws
claude                 # log in
gh auth login          # GitHub.com, SSH, upload the existing key ~/.ssh/id_ed25519.pub, title <name>-ws
```

The key is the VM's own (made by `setup.sh`), so it can be revoked alone. Orgs with single sign-on need the key authorized (GitHub → Settings → SSH keys → Configure SSO).

### 7. Clone and install (C, 5–10 minutes)

```sh
ssh <name>-ws
git clone [-b <branch>] git@github.com:alexluong/<name>-workspace.git ~/workspaces/<name>   # same path as on the MBP
cd ~/workspaces/<name> && mise trust && mise install
mise run setup && mise run doctor      # self-setup workspaces; otherwise: bin/wt init + what the survey lists
```

`doctor`'s list of what is missing (logins, config files) drives steps 8 and 9.

Then the project installs the survey names (hookdeck: `corepack enable && pnpm install` in the core worktree). Tools pinned by the workspace only exist inside its folder: run their commands from there.

### 8. Secret files (C, on Alex's say-so)

From the MBP, the gitignored files the survey listed, paths kept:

```sh
cd ~/workspaces/<name> && rsync -aR <paths…> <name>-ws:workspaces/<name>/
```

Outside the workspace folder too, when the survey lists them: SSH keys and `Host` blocks for tunnels (`~/.ssh/config` on the VM holds only this workspace's hosts; add the hosts' fingerprints to `known_hosts` so a background tunnel does not stop at a prompt), `~/.npmrc`, `~/.aws/config`. Never print their contents. After: env files to mode 600, `git status` on the VM must show none of them, grep the copied config folders for `/Users/` paths. A workspace that keeps cloud state in its own folder (hookdeck: `.gcloud/`, `.kube/`) gets that login by this copy.

### 9. Remaining logins (A, as the survey lists)

Machine-wide CLIs log in again on the VM (Doppler, Railway: their logins cannot be copied, `../../work/task-2/doppler-railway-creds.md`). Then C runs the per-directory setup they need (`doppler setup --no-interactive`) and checks each with a read (`whoami`, a list of names, one read against staging).

### 10. Connect T3 (A, 2 minutes)

T3 app → Settings → Connections → Add environment → SSH → `<name>-ws`; Settings → Providers → that environment → enable Claude (binary `/home/alex/.local/bin/claude`); add project `/home/alex/workspaces/<name>`. Details and the version rule: `../t3-code-remote.md`.

Phone (T3 iOS app), VMs on the tailnet only: the HTTPS route is already there (`--tailscale` set up `tailscale serve`); pair once with `bin/vm-t3-pair <name>-ws iphone` and paste the link in the app (Tailscale app on). `../t3-code-remote.md` § iPhone.

### 11. Bring over unpushed work (C)

Fetch on the MBP, list branches with commits that are on no remote, copy them straight to the VM's clones (no GitHub), carry uncommitted changes as patches. Commands: `hookdeck-ws.md` § Syncing work from the MBP.

### 11a. Services around sessions (C, with Alex)

What the MBP's menubar ran for this workspace (`ctrl/services.conf`: tunnels, board): sessions on the VM need them on the VM. Until there is a switch (TASK-6 or the control-panel idea), record in `vms/<name>-ws.md` the command for each and test it once. Check each tunnel's forwarded ports against the ports the dev stacks publish (`docker ps`, compose files): hookdeck's staging tunnel and its outpost stack both want 26379.

### 12. Record and snapshot (C)

- `vms/<name>-ws.md` from the template in `vms/README.md`; add the row to the index there.
- In the workspace's own repo: a short note on the two machines (hookdeck: `hookdeck-vault/notes/machines.md`). Do not add it to that workspace's always-on rules unless Alex asks.
- `home-systems.md`: the VM's row and DNS name.
- `ssh g8 'qm snapshot <id> ready --description "logged in, secrets copied, deps installed"'`.
- Check it survives a restart: `ssh g8 'qm reboot <id>'`, then Docker and `systemctl --user is-active t3code` on the VM. Proxmox's memory graph should show real use, not 100% (balloon; `maintenance.md`).

## Checks at the end

| Check | Command |
|---|---|
| alias and name | `ssh <name>-ws hostname` |
| tools | `ssh <name>-ws 'cd ~/workspaces/<name> && mise ls --current'` |
| T3 | `ssh <name>-ws 'systemctl --user is-active t3code; curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3773/'` |
| GitHub | `ssh <name>-ws 'gh auth status; git ls-remote git@github.com:<org>/<repo>.git HEAD'` |
| secrets invisible to git | `ssh <name>-ws 'cd ~/workspaces/<name> && git status --short'` |
| a stack starts | the workspace's own start command |
| a session starts | T3 on the MBP: new thread in the project, a first prompt answers |
| tunnels, if any | start each once on the VM; `ss -ltn` shows its ports |

## Traps met the first time

- **DNS "not found" sticks for 30 minutes** if a new name is looked up before it has spread.
- **Renaming a VM in Proxmox** makes cloud-init treat it as new: host keys change (home folder and logins survive).
- **`sudo npx …`** fails through the user's mise shims; use node's real path (`$(mise where node@<v>)/bin`).
- **`*.localhost`** answers IPv6 first on Debian; a service bound to `127.0.0.1` only needs IPv4 first (`/etc/gai.conf`).
- **mise sends Go tools to the Go install's own `bin`**, not `~/go/bin`.
- **Shell scripts with `set -o pipefail`**: `ls missing-dir | …` aborts the script.
- **zsh on the MBP:** `"$b:refs/…"` applies a modifier to `$b`; write `"${b}:refs/…"`. Unquoted variables are not split into words.
- **Outpost-style containers running as root** leave root-owned files in bind-mounted worktrees on Linux.
- **A tunnel and a dev stack can want the same local port** (hookdeck: 26379); the tunnel then refuses to start.
- **systemd user services do not get the shell's PATH**: `~/.config/environment.d/` expands `${HOME}`, not `%h`; call tools by full path or through `mise exec`.
- **T3 server and app versions must match**; bump `T3_VERSION` in `provision.sh` and run `t3 update` in each VM when the app updates.
- **Shared checkouts:** other sessions work in `ctrl` and `collielab` at the same time: pull first, add files by name.

## Survey prompt

Fill in `<name>` and the stack hints, run as a read-only agent on the MBP.

```
Read-only research task. Do NOT modify, create or delete any files, do not run installs, do not
start/stop services or containers. Only read files and run read-only commands. Never print the
contents of .env files or any token; names and paths only.

Context: Alex is moving his <name> workspace (~/workspaces/<name> on this MacBook Pro, macOS) onto an
always-on Linux VM (Debian 13, x86_64, Docker installed, tools managed with mise). Claude Code
sessions started from the T3 Code app will run there. The VM's base already has: Docker + compose,
git, gh, mise, Node 22, Claude Code, build-essential, jq, ripgrep, Postgres and Redis clients,
raised inotify and open-file limits, passwordless sudo (see
~/git/hub/alexluong/collielab/hosts/g8/vm-template/provision.sh). I need to know exactly what this
workspace needs beyond that. Alex does the logins and decides which secrets are copied.

Investigate:
1. The workspace root: AGENTS.md / CLAUDE.md, mise.toml, bin/ scripts, .claude/ (settings, hooks,
   skills), repos/ and wt/ layout, vault docs about machine or dev setup. How is a fresh machine
   meant to be set up?
2. The workspace repo's remote and branch, and every repo it clones (org/repo, base branch,
   private or not), and the command that sets them up.
3. Toolchain: every tool and version pinned in mise.toml files (root and inside each repo),
   .nvmrc, .tool-versions, go.mod, packageManager fields, global tools used outside mise (brew),
   language servers and linters.
4. Dev stacks: docker compose files: services, images (public or needing registry login), ports
   and bind addresses, volumes, host requirements (hosts entries, local DNS, certificates, sysctl),
   how a stack is started, how many can run at once.
5. Anything macOS-specific in scripts, hooks and skills that could break on Linux x86_64
   (file:line): hardcoded /Users or /opt/homebrew paths, `open`, pbcopy, Docker Desktop
   assumptions, arm64-only images.
6. Claude Code config the workspace relies on: .claude/settings.json (hooks, permissions, plugins),
   .mcp.json servers and what each needs, global ~/.claude files it depends on.
7. Logins the workspace uses (CLI, what for, read or write reach, Docker registries included) and
   every gitignored secret or credential file Alex would have to copy (path and purpose only),
   including cloud config folders, and SSH keys and Host blocks in ~/.ssh/config used for tunnels.
7b. Services Alex runs around sessions on the Mac for this workspace: its group in
   ~/workspaces/ctrl/services.conf (menubar: tunnels, board), launch agents, anything a skill says
   "Alex starts". For each: the command, the local ports it opens, and whether those ports clash
   with ports the dev stacks publish.
8. Workload shape from the 10 most recent session transcripts under ~/.claude/projects/ for this
   workspace (count tool calls with grep/jq, do not dump them): commands run most, test and build
   tools, browsers, background jobs, how many sessions and worktrees at once.
9. Sizes: repos/, a typical worktree with dependencies, Docker images/volumes/build cache for the
   stacks, language build caches. Memory of the running stacks if they are up (docker stats).

Return a concise structured report with file paths: A system packages (apt names), B tools and
versions, C repos and setup commands, D Docker stacks (images, ports, host needs), E Mac-specific
things to adapt, F Claude config, G logins and secret files for Alex, H workload and sizing,
I risks and surprises. Say "not found" rather than guessing. Mark what the base template already
covers and what is a gap.
```
