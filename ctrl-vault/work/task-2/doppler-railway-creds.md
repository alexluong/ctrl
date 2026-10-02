# TASK-2: can Doppler and Railway logins live in the workspace folder, like gcloud? (research, 2026-10-02)

Asked by Alex while setting up the hookdeck-ws VM. Read from the CLI sources (Doppler 3.76.0, Railway v5.62.1), their docs, and how the hookdeck workspace uses both. Nothing was changed. Proposal only; adopting it is workspace work in `~/workspaces/hookdeck`.

**Short answer:** Doppler yes (`DOPPLER_CONFIG_DIR`), but each machine still logs in once because the Mac keeps the token in the Keychain. Railway no: it has no config-dir setting and a copied login logs both machines out; the path there is static tokens in the gitignored `ops/<env>/.env` files.

## Doppler

- Config lives in `$HOME/.doppler/.doppler.yaml`; `DOPPLER_CONFIG_DIR` (or `--config-dir`) moves it.
- Token storage: the CLI tries the OS keyring and stores a `secret-<uuid>` reference in the yaml; if the keyring fails (headless Linux) the plaintext token goes in the yaml. There is no switch to turn the keyring off.
- Scopes are keyed by absolute directory, so they don't transfer between the Mac and the VM (`bin/wt` recreates them per worktree).
- Precedence: flag > env (`DOPPLER_TOKEN`, `DOPPLER_PROJECT`, `DOPPLER_CONFIG`) > file. A `DOPPLER_TOKEN` in the env overrides the login for every call.
- The workspace only reads, from ~8 project/config pairs (`services` dev/stg/prd, `clients` dev/stg, `ingest` dev, `outpost-infra` dev/stg/prd), so one service token (one project + one config each) cannot cover it. A service account could, but needs a Team plan and admin rights.

Recommended: root `mise.toml` `[env]`: `DOPPLER_CONFIG_DIR = "{{config_root}}/.doppler"`, `.gitignore`: `/.doppler/`, then `doppler login` once from the workspace on each machine. Gives scoping to the workspace; not copy-a-folder from the Mac (Keychain). Care: processes started outside the mise env (a pm2 daemon, IDE terminals) won't see the variable; not checked whether the CLI's notice about the config dir goes to stderr.

## Railway

- Config is `~/.railway/config.json`; only `HOME` moves it. No `RAILWAY_CONFIG_DIR`, no XDG.
- Auth precedence: `RAILWAY_TOKEN` (project token) > `RAILWAY_API_TOKEN` (account or workspace token) > the file's OAuth tokens.
- Login is OAuth with a 1-hour access token and a **single-use refresh token**: a copied `config.json` used on two machines gets both logged out. Env tokens skip refresh.
- `railway mcp local` uses the same credentials and honours `RAILWAY_API_TOKEN` from its environment.
- Token types: account (all workspaces), workspace (one workspace, cannot query `me`), project (one environment). No read-only tokens, expiry not documented.

Recommended: workspace tokens in the env files that already travel with the workspace: `ops/stg/.env` → `RAILWAY_API_TOKEN=<Hookdeck Dev workspace token>`, `ops/prd/.env` or `ops/prd-rw/.env` → `RAILWAY_API_TOKEN=<Hookdeck workspace token>`. Optional dummy at the root so it fails closed. Care: the MCP server starts at the root (keep it on an account token, or split into two servers launched through `bin/stg` / `bin/prd`, untested); `whoami` and the `me` query in `outpost-fleet-cleanup/scripts/envs.py:57` fail with a workspace token; a QA suite exports `RAILWAY_TOKEN` as a Bearer, which the CLI treats as a project token.

## Security on an always-on VM

- Machine-wide login (today, on both machines): every process of the user has Alex's full reach (Railway workspace admin, all Doppler projects including prd).
- Workspace-scoped config: same reach, only inside the workspace env. Stops bleed between workspaces, not an agent in the workspace.
- Narrow tokens: reach limited per environment, each revocable alone. Railway tokens still write, so the guard hooks stay needed.

## Files in the hookdeck workspace that would change

`mise.toml`, `.gitignore`; wording in `AGENTS.md:111-112`, `outpost-railway/SKILL.md`, `outpost-cloud/SKILL.md:87`, `core-local-dev/SKILL.md:24`, `hookdeck-vault/notes/workspace-migration.md:76`; code in `outpost-fleet-cleanup/scripts/rw.py:22` and `envs.py:57`; if the MCP is split: `.mcp.json`, `.claude/hooks/guard-mcp.sh`, `.claude/settings.json`.

Order: Mac first (Doppler config dir + login; Railway tokens + patches; test CLI and MCP), then the VM (pull, copy `ops/*/.env`, `doppler login` in the workspace), then remove the machine-wide logins on both.

## Open

- Hookdeck's Doppler plan; whether Alex can create service accounts.
- Whether Alex can create a workspace token in the Hookdeck prod Railway workspace.
- Whether Railway tokens expire.

## From the research run itself

- `doppler configure debug`, run on the MBP by the research agent, printed the last ~29 characters of the MBP's Doppler CLI token into that agent's tool output (a local transcript file). Rolling it (`doppler login roll`) is Alex's call.
- The agent left Doppler source files in `/tmp/claude-research-src/` on the MBP (safe to delete).

Sources: https://github.com/DopplerHQ/cli/tree/3.76.0 (`pkg/configuration/config.go`, `keyring.go`, `pkg/cmd/root.go`), https://docs.doppler.com/docs/service-tokens, https://docs.doppler.com/docs/service-accounts, https://github.com/railwayapp/cli/tree/v5.62.1 (`src/config.rs`, `src/client.rs`, `src/oauth.rs`, `src/consts.rs`, `src/commands/mcp/`), https://docs.railway.com/integrations/api
