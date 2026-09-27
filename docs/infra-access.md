# Infra access from workspaces (agents + humans)

How workspaces reach cloud accounts, databases and clusters, and the target pattern. Related: `claude-config.md` (tools/MCP), `projects/enable-workspace.md` (first workspace to adopt this). Key names only here; values live in gitignored `.env` files, with canonical copies in Vaultwarden.

## Principle: no access by default

Environment names: **`stg`**, **`prd`**, **`prd-rw`** (not staging/prod), used in folder names, wrappers, `DEPLOY_ENV` values and gcloud config names.

**Read vs write:**

```
ops/stg/      ← stg, read + write (low stakes)
ops/prd/      ← prd, READ-ONLY credentials only
ops/prd-rw/   ← prd write credentials; the hook always asks, in every permission mode
```

- `prd <cmd>` can only read; a write needs `prd-rw <cmd>` (explicit, in the approval prompt, always confirmed).
- No prefix → no prod access. `prd` → read only. Every mistake fails safe.
- A system without a read-only credential gets **nothing** in `prd`: reachable only via `prd-rw` until a read-only user exists. That makes the missing read-only users visible.

| system | `prd` (read-only) | `prd-rw` | status |
|---|---|---|---|
| Enable Mongo | `ENABLE_MONGO_READ_URL` | `ENABLE_MONGO_WRITE_URL` | split exists; verify the READ user has read roles only |
| hookdeck prod ClickHouse | `alexluong_readonly` (enforced) | none (not needed) | ✓ |
| hookdeck core PG | none | current user | request/create a read-only role |
| hookdeck stg ClickHouse | the Railway creds (can write) | same | fine for stg; optional read-only user |
| GCP | gcloud config `prd` impersonating a **viewer service account** (`auth/impersonate_service_account`) | config `prd-rw` = user account | needs a viewer SA per project (IAM) |
| Terraform | `plan` from `prd` (viewer SA) | `apply` only from `prd-rw` | follows GCP |
| kube | read-only RBAC context if available | current contexts | later |

- **The default environment of a workspace has no prod credentials.** A command that forgets to name its environment fails ("no access"). It never lands on prod by accident.
- **An environment is a directory**, not a shell variable: `ops/stg/`, `ops/prd/`, each a `mise.toml` (+ gitignored `.env`) that inherits the workspace root's `mise.toml` and overrides only what differs.
  - Humans: `cd ops/prd`, and that shell is prd until you leave.
  - Agents and one-offs: sessions stay at the root; each command names its env, e.g. `mise -C ops/prd x -- <cmd>`, via `prd <cmd>` / `stg <cmd>` wrappers (mise tasks or scripts). Nothing carries over to the next command, and `ops/prd` shows in every approval prompt.
- **Why not `MISE_ENV`:** a shell variable you have to remember, which is easy to get wrong silently.
- **Why not a worktree per env:** worktrees are code branches; which environment and which code are separate questions. Task worktrees always run local/staging.
- **gcloud:** each workspace has its own `CLOUDSDK_CONFIG` folder (logins, named configs, ADC for Terraform/SDKs). The root selects a staging or empty config; only `ops/prd` selects prod (`CLOUDSDK_ACTIVE_CONFIG_NAME`). Terraform reads ADC from the same folder (to verify with `terraform plan`).
- **Terraform:** no prod workspace or var-file at the root; `ops/prd` sets `TF_WORKSPACE` or a var-file.
- **kube:** a workspace-scoped `KUBECONFIG` with **no current-context**, so every call passes `--context` (hookdeck already does this).
- **Backstops:**
  - read-only prod credentials wherever they exist
  - a PreToolUse hook that rejects commands mentioning a prod host, project or cluster without `ops/prd`, and asks before writes
  - wrappers print `[env: prd]`; findings name the env they came from
- **Claude shell caveat (tested 2026-09-27):** mise `[env]` reaches only mise-managed tools (their shims load it); plain commands in Claude's non-interactive shell don't get it because mise's cd hook never runs. So install CLIs through mise, and add a SessionStart hook that exports `mise env` into the session as a backstop.

## Current state (audited 2026-09-27)

### Enable (`ebutler-qa/workspace`, `mise.toml` → `_.file = ".env"`)

- **Root `.env` loads prod everywhere in the workspace:**
  - `ENABLE_MONGO_READ_URL` and `ENABLE_MONGO_WRITE_URL` (prod; the DB is `use("production")`)
  - `CLOUDSDK_ACTIVE_CONFIG_NAME` + `CLOUDSDK_CORE_PROJECT`
  - `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`
  - `METABASE_URL` + `METABASE_API_KEY`
- **Guards:**
  - the `guard-write-access.sh` hook asks when a command contains `WRITE_URL`/`getWriteClient`
  - `references/mongodb.md`: "ALWAYS ask before write"
  - READ vs WRITE URL split (good)
- **GCP:** commands pass `--project` explicitly (`enable-production-8178` prod, `enable-staging-9f3a` staging, `festive-oxide-441216-u5` ebchat/Shopify, `enable-cloud-368511` dead). No staging env split for Mongo; staging GCP exists.
- The gcloud `enable` config lives in the **global** gcloud dir (account alex.luong@enable.tech); the global active config is hookdeck `outpost-production`.
- wrangler is installed via `bun install -g` (sharp postinstall fails under mise's npm backend), so it isn't workspace-scoped.
- Scripts: `scripts/src/lib/db` → `getReadClient` / `getWriteClient`.

### hookdeck (`hub/alexluong/hookdeck`, `mise.toml`)

- **Root `.env` loads prod everywhere:**
  - `CORE_PROD_PG_*` (core Postgres via the jumpbox SSH tunnel; read-only **by convention only**)
  - `OUTPOST_PROD_CLICKHOUSE_*`, `OUTPOST_PROD_DRAGONFLY_*`
  - `GRAFANA_*` SA token, `BETTERSTACK_API_TOKEN`
  - `CLOUDSDK_ACTIVE_CONFIG_NAME`
  - `AMPERSAND_DEV_*` keys
- **Outpost targets:** `OUTPOST_TARGET` picks `.env.outpost/<target>.env` (prod-us, prod-eu, prod-us-legacy), **defaulting to `prod-us`**, so the default is prod.
- **ClickHouse:** the prod user is `alexluong_readonly`, with SELECT enforced (good). Staging CH creds come off Railway variables and are **not** read-only.
- **kube, already fail-safe:** `KUBECONFIG=~/.kube/outpost-gke.yaml` (holds staging + prod) with `current-context` unset on purpose, so every kubectl call names `--context`. The shared `~/.kube/config` has no current-context either.
- **GCP:** `GOOGLE_APPLICATION_CREDENTIALS=~/.config/gcloud/hookdeck_adc.json` (explicit ADC file); gcloud configs `outpost-development/staging/production` + `default` are in the **global** gcloud dir.
- **AWS:** SSO profile `personal`, used through mise tasks.
- **Verbs as mise tasks:** `outpost:targets|target|ch|df`, `gke:creds|whoami`, `aws:login|whoami`, `s3:ls|count|rm|cat`.

### Gaps vs the principle

1. Both workspaces load prod credentials at the root by default. hookdeck's Outpost target also defaults to prod.
2. gcloud is global in both, and the global active config is Hookdeck prod.
3. Write protection is by convention (hookdeck PG) or by a pattern-matching hook (enable Mongo). Only hookdeck prod CH is enforced read-only.
4. Some CLIs live outside mise (wrangler via bun, gke-gcloud-auth-plugin via brew path, kubectl), so they don't get workspace env inside Claude.

**Good patterns to keep:** hookdeck's no-current-context kubeconfig; READ/WRITE URL split; read-only DB users; explicit `--project`; mise tasks as the verbs.

## Migration (per workspace, at setup)

- root `.env` → only non-prod/dev values
- prod read-only values → `ops/prd/.env`; prod write values → `ops/prd-rw/.env`; staging → `ops/stg/.env`
- per-workspace `CLOUDSDK_CONFIG` + `gcloud auth login` + `gcloud auth application-default login`
- `stg` / `prd` / `prd-rw` wrapper tasks
- hook: always ask on `ops/prd-rw`; reject prod identifiers without `ops/prd` or `ops/prd-rw`
- `AGENTS.md` rules (prod read-only via `prd …`, cite env in findings)
- Enable first; hookdeck later (also flip the Outpost target default off prod).
