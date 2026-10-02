# TASK-2: what the hookdeck workspace needs on the VM (survey, 2026-10-02)

Read-only survey of `~/workspaces/hookdeck` on the MBP, its repos, docker stacks, Claude config and the 10 most recent sessions (of 62, plus 58 subagent transcripts). Both stacks (core, outpost) were running during it. Not inspected: contents of any `.env`.
What was installed from this list: `collielab/hosts/g8/vm-template/provision.sh` (base) and `collielab/hosts/hookdeck/setup.sh`. What is left for Alex: `hookdeck-vm.md`.

## A. System packages (Debian 13)

In the base template: build-essential, pkg-config, make, git, jq, ripgrep, lsof, netcat, python3, postgresql-client, redis-tools, docker-ce + compose/buildx, gh, inotify + `vm.max_map_count` + nofile limits, passwordless sudo, linger. Added to the base after the survey: `libssl-dev libsasl2-dev` (node-rdkafka, isolated-vm native builds; `wt/core/main/local-dev/README.md:316`), the `docker-compose` name (outpost `Makefile`, core `local-dev/package.json` call it), `libnss-myhostname`, `git-delta`.

In `hosts/hookdeck/setup.sh`: Doppler CLI (hard prerequisite of core `pnpm start`, `scripts/start.ts:696`), Playwright Chromium system libraries, IPv4-first for `*.localhost`.

Optional, not installed (used by some skills): clickhouse client, ffmpeg, cloudflared, k6, `hookdeck` CLI, goreleaser, speakeasy.

## B. Tools and versions

Workspace root `mise.toml`: node 22.22.0, go 1.26.1, jq 1.8.1, gh 2.97.0, gcloud 572.0.0, kubectl 1.37.1, terraform 1.15.2, awscli 2.34.61, npm:backlog.md 1.53.0, railway 5.62.1 (all pre-installed on the VM). After install: `gcloud components install gke-gcloud-auth-plugin`.
Env set by the root `mise.toml`: `CLOUDSDK_CONFIG=.gcloud`, fail-closed `GOOGLE_APPLICATION_CREDENTIALS` and `KUBECONFIG`, `GOPRIVATE=github.com/amp-labs/*`, `SHARP_IGNORE_GLOBAL_LIBVIPS=1`, `pnpm_config_side_effects_cache=false`, `bin/` on PATH. `ops/{stg,prd,prd-rw,amp-stg,amp-prd}/mise.toml` are env only; each needs `mise trust`.

Per repo (none has its own mise.toml):

| Repo | Pins |
|---|---|
| core | `.nvmrc` v22; `packageManager pnpm@11.7.0` via `corepack enable`; pm2 ^7 and tsx are local devDeps |
| http-ingestion | node ^22, pnpm 11.7.0, wrangler, vitest |
| website | node 22, pnpm 11.7.0, Playwright, vitest |
| outpost | `go.mod` go 1.27.1; dev image `golang:1.27-alpine` + air |
| hookdeck-cli | `go.mod` 1.26.0 |
| terraform-provider-hookdeck | `go.mod` 1.25.8 |
| amp-server | `go.mod` 1.27.1 |

Global on the Mac outside mise: doppler, psql, redis-cli, clickhouse, goreleaser, speakeasy, cloudflared, hookdeck, k6, ffmpeg (brew); `gopls` and `golangci-lint` (`go install`; done on the VM).

## C. Repos

- Workspace: `git@github.com:alexluong/hookdeck-workspace.git` (private), **branch `workspace`**, cloned to exactly `~/workspaces/hookdeck` (`.claude/settings.json` hardcodes that path; `origin/HEAD` is `main`, the old layout).
- Then `mise trust && mise install`, `mise trust ops/*/mise.toml`, `bin/wt init`: bare clones in `repos/` and `wt/<repo>/main` for outpost (hookdeck/outpost, main), core (hookdeck/core, staging), hookdeck-cli, terraform-provider-hookdeck, website, http-ingestion (staging), amp-server (amp-labs/server), amp-argocd (amp-labs/argocd).
- All remotes are SSH, so the VM's key needs access to both orgs.
- Per task: `bin/wt add task-N <branch> <repo...>`. Core worktree: `corepack enable && pnpm_config_side_effects_cache=false pnpm install`, then `HTTP_INGESTION_PATH=<wt/http-ingestion/task-N> pnpm start -n hookdeck-local`. Outpost: `make up` / `make up/test`. QA tool: `cd .agents/skills/qa/tools && npm install`.

## D. Docker stacks

All images are public (pre-pulled on the VM by `~/prepull-images.sh`).

**core** (compose project `hookdeck`): postgres:17.5, redis, caddy:2.10-alpine, envoy v1.31, dragonfly, google-cloud-cli emulators (583 and 580), cp-zookeeper / cp-kafka / cp-schema-registry / cp-kafka-connect 7.8.1, kafka-ui, clickhouse-server:24.10; profile-only coredns and k3s. Two local builds (`hookdeck-bigtable`, `hookdeck-kafka-connect`). Ports on 127.0.0.1: 80, 15432, 6379, 6380, 3129, 9901, 8085, 8086, 2181, 9092, 29092, 8081, 8083, 9021, 18123, 19000 (16443, 9100 with k3s). PM2 on the host: 3000, 3002, 9000, 9003-9006, 7001, 8787, inspectors 9229-9232. State outside the repo: `~/.hookdeck/local-dev/`, `~/.pm2`.

**outpost** (project `outpost`): local builds `outpost` and `outpost-portal`, redis-stack-server, clickhouse 24-alpine, rabbitmq:3-management; optional many more. Ports on 0.0.0.0: 3333, 26379, 28123, 29000, 25672, 25673, 25432. Test stack `outpost-test` on 3xxxx ports.

One core and one outpost stack at a time per machine (fixed project names and ports). No mkcert, CA or `/etc/hosts` entries needed.

## E. macOS-specific things in the workspace

- `.agents/skills/worktree/wt:30`: `OLD=$HOME/git/hub/alexluong/hookdeck` is where `wt init` copies env files from; absent on the VM, so env files go into `wt/<repo>/main` by hand.
- `.agents/skills/outpost-dev-image/scripts/sample_pod.sh:4`: hardcoded `/Users/alexluong/workspaces/hookdeck`.
- `.claude/hooks/test-guards.sh:26,37`: test cases use `/Users/alexluong/...` (the guard itself derives its root).
- `.mcp.json:6`: appends `/opt/homebrew/bin` to PATH (harmless).
- `wt/core/main/local-dev/k3s/resolv.conf`: first nameserver is Docker Desktop's; only matters with `pnpm start --outpost`.
- Docker Desktop-only notes in the `core-local-dev` skill (gcr cred helper, rdkafka dylib) don't apply.
- 195 vault files mention `/Users/alexluong` (prose only). `bruno/` and Obsidian stay on the MBP. 25 `open` calls in recent sessions do nothing headless.

## F. Claude Code config

- From the workspace repo: `.claude/settings.json` (memory in `hookdeck-vault/memory`, plugin `gopls-lsp`, SessionStart hook `session-env.sh` needing `mise`, PreToolUse guards needing `jq`, deny rules, MCP servers railway + notion), `.claude/agents/{dev,product,qa,reviewer}.md`, 36 skills, `.mcp.json` (railway via `mise exec -- railway mcp local`; notion over HTTP with OAuth).
- Global, from `alexluong/dotfiles` (`dot/.claude/{settings.json,CLAUDE.md}`, symlinked on the Mac): model, 239 allow / 32 deny rules, `autoMemoryEnabled: false`, `disableClaudeAiConnectors: true`. `scripts/setup-claude.sh` installs the gopls-lsp and frontend-design plugins.
- T3: sessions use T3's own MCP tools.

## G. Left for Alex

Logins: `claude`, `gh auth login` (key with access to hookdeck and amp-labs), `doppler login`, `railway login`, Notion MCP OAuth (`/mcp`), `gcloud auth login` + application-default (or copy `.gcloud/` and `.kube/`), `aws sso login --profile personal`, `docker login` (only to push images), `hookdeck login`.

Secret files (all gitignored; paths under `~/workspaces/hookdeck`):

| Path | Purpose |
|---|---|
| `.env` | root dev/test values |
| `ops/prd/.env`, `ops/prd-rw/.env`, `ops/stg/.env` | prod read, Grafana/BetterStack, staging |
| `ops/prd/outpost/{prod-us,prod-eu,prod-us-legacy}.env` | Outpost fleet connections |
| `.gcloud/`, `.kube/{stg,prd,amp-stg,amp-prd}.yaml` | cloud identity and contexts |
| `wt/core/main/local-dev/env/.env.dev` | core dev overrides |
| `wt/outpost/main/{.env,.outpost.yaml,spec-sdk-tests/.env}` | outpost dev config |
| `wt/terraform-provider-hookdeck/main/.env.test` | prod API keys |
| `wt/amp-server/main/.env` | customer |

Also: `~/.ssh/config` hosts `hd_jumpbox`, `hd_jumpbox_stg` with key `~/.ssh/id_ed_hookdeck` (`prd pg` needs the tunnel running where the session is), `~/.npmrc` (one npmjs token line), `~/.aws/config` profiles.

## H. Workload shape

- ~2,900 Bash calls in the sample; subagents make 84% of them. 56 Agent spawns (reviewer 25, dev 15, qa 10). Up to ~6 lead sessions overlapped on the evening of 2026-10-01.
- Mostly grep/cat/sed/python3/git, then `backlog`, `gh pr`. Test and build: `go test` / `go vet` / `go build`, `pnpm test:server` (jest, real DBs), `tsc`, `make up/test`, `make testacc`, goreleaser, terraform. Prod reads: `prd pg`, `prd kubectl`.
- 66 background commands; ~500 with timeouts of 5 minutes or more. Browser: headless Playwright Chromium only, rare.
- 45 worktrees exist: 18 core (16 with `node_modules`), 11 outpost, 6 http-ingestion.
- RAM on the MBP now: core containers ~4.7GB, outpost ~3.0GB, node ~2.3GB, 13 claude processes ~1.3GB. 32GB is comfortable for one core stack, one outpost stack and a handful of agents.
- Disk on the MBP: `repos/` 1.1GB; a core worktree 2.1GB (`wt/core` 31GB); docker images 43GB (~20GB these stacks), volumes 22GB, build cache 16GB; go build cache 33GB, go mod cache 3.3GB; pnpm store 9.7GB. 250GB is fine if worktrees and the go cache get pruned (`go clean -cache`, `bin/wt rm`).

## I. Risks and surprises

- **Dashboard from the MBP:** core URLs are `http://<ns>.localhost` through Caddy on the VM's 127.0.0.1:80, so the Mac's browser can't open them directly. The repo's remote path is `pnpm start --tailscale` with `LOCAL_DEV_TAILSCALE_DOMAIN` (Tailscale deferred); otherwise an SSH forward of local port 80 or a gateway route.
- **Root-owned files in worktrees:** outpost dev containers run as root and bind-mount the worktree; on Linux their files land root-owned, so `bin/wt rm` / `git clean` can fail. Passwordless sudo is the workaround.
- **LAN exposure:** outpost publishes on 0.0.0.0 and core PM2 services bind 0.0.0.0; Docker bypasses ufw.
- **Two machines, one vault:** board, memory and digest are committed from wherever sessions run. Working on both the MBP and the VM will conflict; pick one.
- **Unpushed work stays on the MBP:** task branches live in its bare clones; `wt/core/task-23` was dirty. Push before switching.
- **Go version drift:** mise pins 1.26.1 while outpost and amp-server need 1.27.1 (works through Go's automatic toolchain download).
- **Secrets with real reach on an always-on agent box:** `.env.test` (prod API keys), gcloud `prd` (Alex's own account, can write), Railway and Doppler logins. The guard hook prevents accidents but is not a boundary.
- **Dotfiles `.gitconfig`:** sets `core.pager = delta` and a credential helper; `delta` is installed for that reason.
- **First boot of core:** pulls ~10 images and builds two; known snags are in the `core-local-dev` skill.
