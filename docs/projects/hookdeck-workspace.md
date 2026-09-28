# Project: Hookdeck workspace (`~/workspaces/hookdeck`)

Alex's personal agent workspace for Hookdeck work (Outpost, core/Event Gateway, CLI, Terraform provider, website) and the Ampersand FDE engagement. Second workspace built from `../workspace-setup.md` (first: `enable-workspace.md`).

**Status (2026-09-27): set up, pending Alex's logins (gcloud) and the MCP decision (Railway, Notion).** Repo `alexluong/hookdeck-workspace` (private), branch **`workspace`** (orphan). `main` = the old single-clone layout, kept as a reference; the old clone `~/git/hub/alexluong/hookdeck` is untouched.

## Why

The old setup was one personal repo with the team repos as submodules, parallel `outpost-wt-<slug>/` worktrees as siblings, a root `.env` that loaded prod credentials everywhere, `OUTPOST_TARGET` defaulting to prod, global gcloud with Hookdeck prod active, and project MCPs (Railway, Notion, Figma). The workspace pattern fixes access (no prod by default), gives work a board + notes + memory in the repo, and keeps code out of the personal repo.

## Decisions (2026-09-27, with Alex)

- **No "systems".** Enable needed them (one super-repo, sets of submodules). Hookdeck has independent repos: one bare clone per repo, worktrees `wt/<repo>/<name>`; a task picks the repos it needs (usually one).
- **No ticket source.** Work comes from asks, GitHub issues/PRs and incidents; `gh` covers GitHub. Backlog.md still tracks the work (`task-N`).
- **Team-facing branch names** (`feat/<slug>`, amp `alexl/<slug>`), never task IDs: the workspace must not surface to the team (`wt add` rejects `task-*` branches).
- **fde = Ampersand (amp-labs):** a customer's own repos and infra (GCP `ampersand-*`). Repos `amp-server`, `amp-argocd` in the same workspace; notes in `hookdeck-vault/notes/amp-labs/`. Their infra is not wired into `ops/` (kube contexts left out of the workspace kubeconfig; guard asks on `ampersand-prod`). `amp-labs/client` is no longer accessible (repo not found) → dropped.
- **Railway + Notion MCPs:** wanted; to discuss at the end (skills say "not wired yet").

## As built (2026-09-27)

- **Layout:** as Enable (AGENTS.md + CLAUDE.md symlink, `.agents/{skills,roles,references}`, `.claude/` wiring, `hookdeck-vault/`, `ops/`, `bin/`, `local/`), plus `bruno/` (collections; secret values stay in Bruno's app storage) and `hookdeck-vault/qa/suites/`.
- **Repos:** outpost (main), core (staging), hookdeck-cli, terraform-provider-hookdeck, website (main), http-ingestion (staging), amp-server, amp-argocd (main). `bin/wt init` clones with `--reference` to the old clone.
- **Worktrees:** `wt/<repo>/main` detached at `origin/<base>` (read-only); `bin/wt add task-N <branch> <repo...> [--from <ref>]` (tracks `origin/<branch>` if it exists, e.g. a PR), `rm` (refuses dirty), `sync`, `ls` (shows which worktree runs a stack). Copies local env files from `wt/<repo>/main` (outpost `.env`, `.outpost.yaml`; tf-provider `.env.test`; amp-server `.env`); core gets `doppler setup`. No `.claude` symlink where the repo tracks its own `.claude` (core, hookdeck-cli, amp-argocd).
- **Stacks:** no slots. outpost (`name: outpost`) hardcodes compose name + ports → one machine-wide; verified end to end from a task worktree (`make up/health/smoke/down`, ~2 min). core: `pnpm start -n <namespace>` separates worktrees on one compose project; default one at a time, not booted yet. core needs an http-ingestion task worktree (`HTTP_INGESTION_PATH`), see `core-local-dev`.
- **Content migrated from `main`:** `notes/` → `hookdeck-vault/notes/` (same blobs, so no repo growth), `qa/suites` → `hookdeck-vault/qa/`, QA tools → `qa` skill, `.bruno` + amp bruno → `bruno/`, 30 skills → `.agents/skills/` (rewritten for wrappers/worktrees; `notes` skill retired into the `workspace` skill), `AGENTS_{outpost,core}.md` → `.agents/references/`. Auto-memory (123 files) from `~/.claude/projects/-Users-alexluong-git-hub-alexluong-hookdeck/memory/` → `hookdeck-vault/memory/` (+ 14 older ones in `hookdeck-vault/memory/legacy/`).
- **Secrets found in content:** the Ampersand dev/staging QA API key (memory + amp notes) → root `.env` (`AMPERSAND_QA_*`), vault references `$AMPERSAND_QA_API_KEY`. Still in `main` history (dev/staging only). A staging static-IP proxy basic-auth password sits in notes (a tfstate backup, a QA script): left as is, flagged.
- **Tools (mise):** node 22.22.0, go 1.26.1, gcloud 572.0.0 (+ `gke-gcloud-auth-plugin` component; reinstall after a gcloud bump), kubectl, terraform 1.15.2, awscli, gh, jq, backlog.md, `@railway/cli`. doppler, psql, redis-cli, clickhouse still from brew.
- **Infra:** `../infra-access.md` § hookdeck, as built.
- **Claude:** `settings.json` (memory → `hookdeck-vault/memory`, gopls-lsp, SessionStart env hook, prod guard, deny secrets reads and edits under `repos/`, `wt/*/main/`), role wrappers, `lead`/`workspace`/`worktree` skills.

## Alex to do

- `cd ~/workspaces/hookdeck`, check `echo $CLOUDSDK_CONFIG` → `…/hookdeck/.gcloud`, then `gcloud auth login alex.luong@hookdeck.com` and `gcloud auth application-default login` (then Claude unsets the account on `none` and moves ADC to `.gcloud/adc-hookdeck.json`; a copy of the old `hookdeck_adc.json` is there now).
- Obsidian: open `hookdeck-vault/`.
- Bruno: open `bruno/hookdeck` and `bruno/amp-labs`; re-enter secret env values (Bruno keys them by collection path).
- Verify: core stack from a worktree; `prd pg` with the tunnel up.
- Decide: Railway + Notion MCP (project `.mcp.json`?); read-only Grafana viewer SA and BetterStack read token (then move to `prd`); staging Outpost targets (`ops/stg/outpost/<target>.env`); prod write creds for fleet cleanup (`ops/prd-rw/outpost/`); the one-core-stack rule vs namespaces; Ampersand env dirs; delete global `~/.config/gcloud/hookdeck_adc.json` once the old clone is retired.
