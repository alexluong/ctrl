# hookdeck VM

Hookdeck work (core, outpost, the Ampersand customer repos) for agent sessions started from T3 on the MBP. VM 101 on g8, `hookdeck.lab.alexluong.com` = `192.168.1.101`, `ssh hookdeck` (user `alex`). 8 vCPU, 32GB RAM, 250GB disk. Built 2026-10-02.
Workspace: `alexluong/hookdeck-workspace`, branch `workspace`, at `~/workspaces/hookdeck` (the path is hardcoded in its `.claude/settings.json`).
Scripts: `collielab/hosts/hookdeck/setup.sh`. Full survey behind this doc: `work/task-2/hookdeck-vm-requirements.md`. Build decisions: `work/task-2/hookdeck-vm.md`.

## Tools beyond the base

| What | Why | Installed by |
|---|---|---|
| node 22.22.0, go 1.26.1, jq, gh, gcloud 572, kubectl 1.37.1, terraform 1.15.2, awscli 2.34.61, railway 5.62.1, backlog.md 1.53.0 | pinned in the workspace `mise.toml` | `setup.sh` pre-installs; `mise install` in the workspace is the source of truth |
| Doppler CLI | core `pnpm start` refuses to run without it | `setup.sh` |
| gopls, golangci-lint | Claude's gopls plugin, linting | `setup.sh` (`go install`) |
| Playwright Chromium system libraries | QA skill, website tests | `setup.sh` |
| IPv4 first for `*.localhost` | core's Caddy listens on 127.0.0.1:80 only | `setup.sh` (`/etc/gai.conf`) |
| 26 public Docker images of the core and outpost stacks | first stack boot without a long pull | `~/prepull-images.sh` on the VM |
| `gke-gcloud-auth-plugin` | kubectl against GKE | **to do**: `gcloud components install gke-gcloud-auth-plugin` in the workspace |

Not installed (used by a few skills; add when needed): `hookdeck` CLI, clickhouse client, ffmpeg, cloudflared, k6, goreleaser, speakeasy.

## Logins

All run on the VM (`ssh hookdeck`); each prints a link and a code to finish in the MBP's browser.

| What | Command on the VM | Used for | State (2026-10-02) |
|---|---|---|---|
| Claude | `claude` | every session | done |
| GitHub CLI + SSH key | `gh auth login` (SSH, upload `~/.ssh/id_ed25519.pub`) | clone/push, `gh pr`; key covers `alexluong`, `hookdeck`, `amp-labs` | done, all repos reachable |
| Doppler | `doppler login`, then `doppler setup --project services --config dev --no-interactive` in `wt/core/main/local-dev` | core dev stack env (projects services, clients, ingest, outpost-infra) | to do |
| Railway | `railway login --browserless` | Railway MCP server, outpost fleet reads | to do |
| gcloud | from `~/workspaces/hookdeck` (`echo $CLOUDSDK_CONFIG` must end in `/hookdeck/.gcloud`): `gcloud auth login alex.luong@hookdeck.com --no-launch-browser`, `gcloud auth application-default login --no-launch-browser`; then unset the account on config `none` and move `.gcloud/application_default_credentials.json` → `.gcloud/adc-hookdeck.json`. **Or** copy `.gcloud/` and `.kube/` from the MBP | `stg`, `prd` wrappers, terraform, kubectl | to do |
| Notion MCP | in a Claude session in the workspace: `/mcp` → notion → authenticate | `notion-publish-spec` skill | to do; the sign-in redirects to `localhost` on the VM, so paste the final URL back into Claude if the page fails to load |
| AWS | `~/.aws/config` copied from the MBP, then `aws sso login --profile personal --use-device-code` | Ampersand work | to do, when needed |
| Docker Hub | `docker login` | only to push dev images | when needed |
| npm | `~/.npmrc` (one token line) copied from the MBP | publishing | when needed |
| Prod Postgres tunnel | `~/.ssh/id_ed_hookdeck` + the `hd_jumpbox`, `hd_jumpbox_stg` blocks from the MBP's `~/.ssh/config` | `prd pg` | when needed |

Doppler and Railway logins are machine-wide and can write. gcloud `prd` is Alex's own account and can write; the workspace's guard hooks ask on mutating commands but are not a boundary.

## Secret files

Paths under `~/workspaces/hookdeck`, all gitignored; canonical copies on the MBP's workspace (and Vaultwarden where noted there). Copy from the MBP:

```sh
cd ~/workspaces/hookdeck && rsync -avR --ignore-missing-args \
  .env ops/prd/.env ops/prd-rw/.env ops/stg/.env ops/prd/outpost/ .gcloud/ .kube/ \
  wt/core/main/local-dev/env/.env.dev wt/outpost/main/.env wt/outpost/main/.outpost.yaml \
  wt/outpost/main/spec-sdk-tests/.env wt/terraform-provider-hookdeck/main/.env.test wt/amp-server/main/.env \
  hookdeck:workspaces/hookdeck/
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

State: none copied yet (2026-10-02). On the VM, `bin/wt` cannot copy env files into new worktrees from the old MBP clone (`$HOME/git/hub/alexluong/hookdeck` does not exist there), so `wt/<repo>/main` is the place they must be.

## First run (from a fresh VM)

1. `bin/new-vm 101 hookdeck 8 32768 250` and `hosts/hookdeck/setup.sh` (collielab).
2. On the VM: `claude`, `gh auth login`.
3. `git clone -b workspace git@github.com:alexluong/hookdeck-workspace.git ~/workspaces/hookdeck && cd ~/workspaces/hookdeck && mise trust && mise install && mise trust ops/*/mise.toml && bin/wt init` (done 2026-10-02: 8 repos, `repos/` 1.2GB).
4. Secret files (above), then the logins in the table.
5. T3 app on the MBP: Settings → Connections → Add environment → SSH → `hookdeck`; Providers → enable Claude; add project `~/workspaces/hookdeck`.
6. Core, first time: in `wt/core/main`: `corepack enable && pnpm install`.

## Running the stack

- Core: `HTTP_INGESTION_PATH=<wt/http-ingestion/…> pnpm start -n hookdeck-local` in a core worktree (skill `core-local-dev`). Outpost: `make up` / `make up/test`.
- One core and one outpost stack at a time (fixed compose project names and ports).
- Core URLs are `http://<ns>.localhost` on the VM's own port 80. From the MBP's browser: `ssh -L 80:127.0.0.1:80 hookdeck` while no stack runs on the MBP; later the gateway (TASK-3) or `pnpm start --tailscale`.
- Outpost and the PM2 services listen on all addresses, so they are reachable from the home network at `hookdeck.lab.alexluong.com:<port>`.

## Differences from the MBP

- `.agents/skills/worktree/wt:30` (`OLD=…/git/hub/alexluong/hookdeck`): no env-file source on the VM.
- `.agents/skills/outpost-dev-image/scripts/sample_pod.sh:4`, `.claude/hooks/test-guards.sh:26,37`: hardcoded `/Users/alexluong/...`.
- Outpost dev containers run as root and write into the worktree: files end up root-owned on Linux (`sudo` to clean; `bin/wt rm` may need it).
- `open` does nothing; Bruno and Obsidian stay on the MBP.
- Go: mise pins 1.26.1, outpost and amp-server want 1.27.1 (Go downloads the newer toolchain by itself).

## Open points

1. Sessions on the MBP and the VM at once will conflict (board, memory, digest are committed from where sessions run). Push the MBP's unpushed work, then pick one place.
2. Which prod-reaching files and logins belong on an always-on agent machine (the bold rows above).
3. Saving the VM's identity (GitHub key, optionally the gh and Claude logins) to `ctrl/secrets/hookdeck/` so a rebuilt VM needs no re-registration: offered, not decided.
4. No backups yet; snapshot `clean-setup` is from before the logins.
