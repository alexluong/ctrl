# hookdeck-ws VM

Named `hookdeck-ws` (renamed from `hookdeck` 2026-10-02). Hookdeck work (core, outpost, the Ampersand customer repos) for agent sessions started from T3 on the MBP. VM 101 on g8, home address `192.168.1.101`, tailnet `100.113.20.22` (`tag:vm`, since 2026-10-04); `hookdeck-ws.lab.alexluong.com` = the tailnet address, so `ssh hookdeck-ws` (user `alex`) and the T3 environment work at home (router → gw, no app) and away (Tailscale app on). See § Network. 8 vCPU, 32GB RAM, 250GB disk. Built 2026-10-02.
Workspace: `alexluong/hookdeck-workspace`, branch `workspace`, at `~/workspaces/hookdeck` (the path is hardcoded in its `.claude/settings.json`).
Setup: the workspace sets itself up since 2026-10-04 (TASK-8, hookdeck `task-105`): `mise install && mise run setup && mise run doctor`; its access checklist is `access.md` in the workspace. collielab holds nothing hookdeck-specific (`hosts/hookdeck-ws/setup.sh` deleted). Full survey behind this doc: `work/task-2/hookdeck-vm-requirements.md`. Build decisions: `work/task-2/hookdeck-vm.md`.

## Tools beyond the base

In the workspace: its `mise.toml` (incl. doppler, gopls, golangci-lint, pnpm since 2026-10-04) and `mise run setup` (gcloud plugin, Playwright browser, worktrees, deps). The VM's base gives IPv4-first for `*.localhost` and the browser system libraries; psql/redis-cli are OS packages in the base. Old apt Doppler removed 2026-10-04 (`doppler` now from mise; login kept). `mise run doctor` passed on the VM 2026-10-04.

Not installed (used by a few skills; add when needed): `hookdeck` CLI, clickhouse client, ffmpeg, cloudflared, k6, goreleaser, speakeasy.

## Logins

All run on the VM (`ssh hookdeck-ws`); each prints a link and a code to finish in the MBP's browser. **Run them from `~/workspaces/hookdeck`**: railway, gcloud, kubectl, terraform and aws are pinned by the workspace `mise.toml` and only exist inside that folder (outside it: "No version is set for shim"). Doppler, gh and claude work anywhere.

| What | Command on the VM | Used for | State (2026-10-02) |
|---|---|---|---|
| Claude | `claude` | every session | done |
| GitHub CLI + SSH key | `gh auth login` (SSH, upload `~/.ssh/id_ed25519.pub`) | clone/push, `gh pr`; key covers `alexluong`, `hookdeck`, `amp-labs` | done, all repos reachable |
| Doppler | `doppler login`, then `doppler setup --no-interactive` in `wt/core/main/local-dev` and `server` | core dev stack env (projects services, clients, ingest, outpost-infra) | done (machine-wide login; `services/dev` set up in core main) |
| Railway | `railway login --browserless` (from the workspace folder) | Railway MCP server, outpost fleet reads | done (machine-wide login) |
| gcloud | copied from the MBP with `.gcloud/` and `.kube/` (the workspace keeps its gcloud state in its own folder). Fresh login instead: from `~/workspaces/hookdeck`, `gcloud auth login alex.luong@hookdeck.com --no-launch-browser`, `gcloud auth application-default login --no-launch-browser`, then unset the account on config `none` and move the ADC file to `.gcloud/adc-hookdeck.json` | `stg`, `prd` wrappers, terraform, kubectl | done 2026-10-02 (copied; `bin/stg kubectl --context outpost-staging-us get ns` works) |
| Notion MCP | in a Claude session in the workspace: `/mcp` → notion → authenticate | `notion-publish-spec` skill | done (Alex, 2026-10-04). If redone: the sign-in redirects to `localhost` on the VM, so paste the final URL back into Claude if the page fails to load |
| AWS | `~/.aws/config` copied from the MBP, then `aws sso login --profile personal --use-device-code` | Ampersand work | to do, when needed |
| Docker Hub | `docker login` | only to push dev images | done (Alex, 2026-10-02; `~/.docker/config.json` has the entry) |
| npm | `~/.npmrc` (one token line) copied from the MBP | publishing | when needed |
| Jumpbox tunnels (prod, staging) | `~/.ssh/id_ed_hookdeck` + the `hd_jumpbox`, `hd_jumpbox_stg` blocks from the MBP's `~/.ssh/config` | `prd pg`, staging PG | **copied 2026-10-02** (key, host blocks, host fingerprints; login tested, no tunnel running). The same key also opens Alex's GitLab on the MBP. Undo: `rm ~/.ssh/id_ed_hookdeck* ~/.ssh/config` on the VM. Next: a switch in the MBP menubar (TASK-6) |

Doppler and Railway logins are machine-wide and can write. gcloud `prd` is Alex's own account and can write; the workspace's guard hooks ask on mutating commands but are not a boundary.

## Secret files

Paths under `~/workspaces/hookdeck`, all gitignored; canonical copies on the MBP's workspace (and Vaultwarden where noted there). Copy from the MBP:

```sh
cd ~/workspaces/hookdeck && rsync -avR --ignore-missing-args \
  .env ops/prd/.env ops/prd-rw/.env ops/stg/.env ops/prd/outpost/ .gcloud/ .kube/ \
  wt/core/main/local-dev/env/.env.dev wt/outpost/main/.env wt/outpost/main/.outpost.yaml \
  wt/outpost/main/spec-sdk-tests/.env wt/terraform-provider-hookdeck/main/.env.test wt/amp-server/main/.env \
  hookdeck-ws:workspaces/hookdeck/
```

| Path | Purpose | Reach |
|---|---|---|
| `.env` | root dev/test values | dev |
| `wt/core/main/local-dev/env/.env.dev` | core dev overrides | dev |
| `wt/outpost/main/{.env,.outpost.yaml,spec-sdk-tests/.env}` | outpost dev config | dev |
| `ops/stg/.env` | staging (empty today) | staging |
| `ops/prd/.env`, `ops/prd/outpost/*.env` | core Postgres read-only, Outpost fleet connections | **prod read** |
| `ops/prd-rw/.env` | Grafana, BetterStack | **prod** |
| `.gcloud/`, `.kube/*.yaml` | cloud identity and cluster contexts | **prod, can write** |
| `wt/terraform-provider-hookdeck/main/.env.test` | acceptance tests | **prod API keys** |
| `wt/amp-server/main/.env` | Ampersand | customer |

State: all 13 paths copied 2026-10-02 (rsync from the MBP, no Mac-only paths inside `.gcloud` / `.kube`; env files set to mode 600; git sees none of them). On the VM, `bin/wt` cannot copy env files into new worktrees from the old MBP clone (`$HOME/git/hub/alexluong/hookdeck` does not exist there), so `wt/<repo>/main` is the place they must be.

## First run (from a fresh VM)

1. `bin/new-vm 101 hookdeck-ws 8 32768 250 --tailscale` (collielab): firewall, tailnet, T3, git identity, GitHub key, Claude config.
2. On the VM: `claude`, `gh auth login` (upload the VM's key).
3. `git clone -b workspace git@github.com:alexluong/hookdeck-workspace.git ~/workspaces/hookdeck && cd ~/workspaces/hookdeck && mise trust && mise install && mise run setup && mise run doctor`.
4. Do what `doctor` lists: logins (the workspace's `access.md` says how on a machine without a browser), config files (copy from the MBP, § Secret files).
5. T3 app on the MBP: Settings → Connections → Add environment → SSH → `hookdeck-ws`; Providers → enable Claude; add project `~/workspaces/hookdeck`.

As built on 2026-10-02 (before self-setup): `../../work/task-2/log.md`.

## Running the stack

- Core: `HTTP_INGESTION_PATH=<wt/http-ingestion/…> pnpm start -n hookdeck-local` in a core worktree (skill `core-local-dev`). Outpost: `make up` / `make up/test`.
- One core and one outpost stack at a time (fixed compose project names and ports).
- Core URLs are `http://<ns>.localhost` on the VM's own port 80. From the MBP's browser: `ssh -L 80:127.0.0.1:80 hookdeck-ws` while no stack runs on the MBP; later the gateway (TASK-3) or `pnpm start --tailscale`.
- Outpost and the PM2 services listen on all addresses, so they are reachable at `hookdeck-ws.lab.alexluong.com:<port>` (at home, and away with the Tailscale app) and at `192.168.1.101:<port>` at home.

## Network

- On the tailnet since 2026-10-04 (`collielab/bin/vm-tailnet hookdeck-ws`; Tailscale installed in the VM, joined as `tag:vm`, `--accept-dns=false`, no restart). Tested: ssh and T3 (ssh tunnel to `:3773`) from the MBP through router → gw → VM; Dozzle through gw; Docker, container internet and DNS unchanged; the VM cannot open connections to the Mini or gw over the tailnet (it does not even see the Mini).
- What the VM may do: answer only. On the tailnet: `tag:vm` (`collielab/terraform/tailscale.tf`). On the home network: Proxmox firewall (`collielab/hosts/g8/firewall.sh`, since 2026-10-04): no connections to `192.168.1.x` (g8, gw, the Mini, the router page, other devices), Docker containers included; internet, router DNS and Tailscale allowed. **No IPv6** on this VM (dropped at the firewall); everything uses IPv4.
- Restart tested 2026-10-04: after `qm reboot 101` Tailscale (same address), Docker, T3 and the firewall all came back by themselves.
- Need the VM to reach a home machine or another machine on purpose? A rule in `firewall.sh` for this VM and a grant in `tailscale.tf`; both explicit.
- Undo: `ssh hookdeck-ws sudo tailscale down` (instant), DNS record back to `192.168.1.101`. (The pre-join copy of its firewall rules was in `/tmp` and went with the 2026-10-04 reboot; not needed: `tailscale down` removes Tailscale's rules.)
- Explainer: `../tailscale.md`.

## Services around sessions

What the MBP's menubar (`ctrl/services.conf`) ran for this workspace, and its state on the VM. A switch for these is open: TASK-6 (menubar reaching into the VM, parked) or a control panel on the VM (Collie Studio idea: `~/workspaces/cs/cs-vault/notes/studio/workspace-control.md`).

| Service | On the VM today |
|---|---|
| Prod jumpbox tunnel | by hand: `ssh hookdeck-ws`, then `ssh -N hd_jumpbox` (keep the shell open, or `ssh -fN hd_jumpbox` and `pkill -f "ssh -fN hd_jumpbox"` to close). `prd pg` then works in VM sessions. Off after a VM reboot |
| Staging jumpbox tunnel | `ssh -N hd_jumpbox_stg`. **Fails while the outpost stack is up**: the tunnel forwards local port 26379 (staging Dragonfly) and the outpost stack's Redis publishes 26379. Same clash on the MBP; it comes from the workspace, not the VM. Stop the outpost stack first, or run the tunnel without that forward |
| Board (`backlog browser -p 6422`) | not run on the VM yet. It binds 127.0.0.1 only: from the MBP `ssh -L 6422:127.0.0.1:6422 hookdeck-ws`, later the gateway (TASK-3). The MBP's menubar board shows the MBP's checkout |
| Docker UIs (compose project `docker-ui`) | Dozzle (logs) `:8888`, Isaiah (manage) `:8889`. Through the gateway: `https://dozzle.hookdeck-ws.lab.alexluong.com`, `https://isaiah.hookdeck-ws.lab.alexluong.com`; cards on `https://lab.alexluong.com` (2026-10-02) |
| Keep-awake | not needed: the VM does not sleep |

## Resources

Allocated: 8 of g8's 16 CPU threads (shared, not reserved), 32GB of 64GB RAM (fixed, reserved while the VM runs; balloon on since 2026-10-04 so Proxmox shows real use, `maintenance.md`), 250GB disk as a ceiling on g8's 816GB pool (thin: only what is written takes space).

Measured 2026-10-02 23:30 with 6 Claude sessions and both stacks up (22 containers): RAM 15GB used of 32GB (containers 7.4GB), load 1.2 on 8 threads, disk 50GB of 250GB (Docker images 26GB, build cache 7GB, volumes 5GB). On g8: the pool is 7% used; 27GB RAM and 8 threads are left for other VMs.

Change the size (on g8): `qm set 101 --cores N`, `qm set 101 --memory MB` (both need a VM restart), `qm resize 101 scsi0 +50G` (live, grow only).

## Syncing work from the MBP

Team repos keep task branches in each machine's own bare clones, so unpushed work has to be carried over. Without touching GitHub, from the MBP's `~/workspaces/hookdeck`:

```sh
git -C repos/<repo>.git push hookdeck-ws:workspaces/hookdeck/repos/<repo>.git "refs/heads/${b}:refs/heads/${b}"
```

(Refused when the VM already has a newer version of that branch from GitHub: push it as `mbp/<branch>` instead.) Uncommitted changes: `git -C wt/<repo>/<task> diff HEAD --binary > x.patch`, copy to the VM's `local/`. The workspace repo itself goes through GitHub (`git push`, then `git pull` on the VM). First sync 2026-10-02: `work/task-2/log.md`. The VM has only the `main` worktrees; a task continues there after `bin/wt add` for it.

## Differences from the MBP

- Mac-only paths in the workspace scripts (`wt`, `sample_pod.sh`, `test-guards.sh`): fixed (hookdeck-workspace `ae258a6`, 2026-10-04).
- Outpost dev containers run as root and write into the worktree: files end up root-owned on Linux (`sudo` to clean; `bin/wt rm` may need it).
- `open` does nothing; Bruno and Obsidian stay on the MBP.
- Go: mise pins 1.26.1, outpost and amp-server want 1.27.1 (Go downloads the newer toolchain by itself).

## Open points

1. **Decided 2026-10-03 (Alex): the VM is where hookdeck sessions run from now on;** the MBP is the client. Reason it matters: with sessions on both machines the workspace repo collided within a day (two `task-86`, one renumbered to `task-89`; the MBP checkout 3 ahead / 11 behind with `MEMORY.md` changed on both sides). The MBP's workspace commits were rebased and pushed by a Mac session (checkout level with the remote, 2026-10-03 00:15). Left to do, from a hookdeck session: carry any task branches that exist only in the MBP's bare clones (method: § Syncing work from the MBP), (done, per Alex 2026-10-04). Refined 2026-10-04 (Alex): the VM is preferred, MBP sessions stay possible when a case needs them (pull first, push promptly, not alongside VM sessions writing the board or memory); `hookdeck-vault/notes/machines.md` updated to the rule (2026-10-04). The general learning (git-based workspace state assumes one writer) is noted in the Collie Studio workspace, `cs-vault/notes/studio/multi-writer.md`.
2. The prod-reaching files and logins (the bold rows above) are now on the VM, on Alex's say-so (2026-10-02). Kubeconfigs have no default context by design: pass `--context`.
3. Saving the VM's identity (GitHub key, optionally the gh and Claude logins) to `ctrl/secrets/hookdeck-ws/` so a rebuilt VM needs no re-registration: offered, not decided.
4. ~~Template rebuild~~ done 2026-10-04: template 9000 carries the service PATH fix (`collielab` `6b3a54a`).
4a. No backups yet (TASK-13). Snapshot on g8: `idle-20261004` (after two days of use). `clean-setup` and `ready` deleted 2026-10-04 (keep-2 rule, `maintenance.md`).
5. Doppler and Railway logins are machine-wide today. Moving them into the workspace like gcloud: possible for Doppler (`DOPPLER_CONFIG_DIR`), not for Railway (use workspace tokens in `ops/<env>/.env`): `work/task-2/doppler-railway-creds.md`.
