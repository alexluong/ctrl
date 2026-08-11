# collielab — homelab infrastructure repo

The lab platform: the VM, its DNS, and the docker-compose services running on it. Repo: `hub/alexluong/collielab`, remote still `git@github.com:alexluong/collielab` (transfer to the `collielab` GitHub org as `collielab/infra` is planned, not done — see `stack.md`). Machine facts: `machine.md`. Working process: `workflow.md`.

## Layout

```
services/     one directory per docker-compose service
terraform/    cloudflare DNS + vultr VM
incidents/    postmortems (2025-05-17 VM disk space)
```

No README, no CLAUDE.md at root (as of 2026-08-11).

## The VM

Vultr instance `lab` (terraform-managed): `vhp-1c-1gb-intel`, Debian 12, region `ewr` (New Jersey), weekly backups Thursdays 11:00. Reachable as `ssh alex@149.28.40.6` (alias `sshmylab` on the MBP — the alias is not in `~/.ssh/config` on every machine; use the IP if it doesn't resolve). Docker is old: `docker-compose` v1 binary, **no `docker compose` plugin**.

## Services

In `services/` (repo-managed): vaultwarden, glances, portainer, observability (grafana + prometheus + loki + promtail).

Actually running on the VM (verified 2026-08-11): **vaultwarden, glances** — plus two things not in this repo. Portainer and the observability stack are stopped; their 4 orphaned docker volumes are still on the VM.

**Not in collielab** — ad-hoc `~/services/` git clones on the VM: `eldobot`, `alexluong.com`, `caddy`, `mls`. Deliberate, unresolved (see `projects/eldobot.md`). Anything reached over HTTPS goes through the Caddy in that ad-hoc set, so a new public service needs a Caddy entry too, not just a compose file.

## Terraform

- Root module: `terraform/`. Providers: `cloudflare 5.23.0`, `vultr 2.21.0`. Migrated from v4.45.0 on 2026-08-11 (`0e24cdd`) — see below.
- **State backend is Cloudflare R2** — bucket `collielab-terraform`, key `terraform.tfstate`, S3-compatible endpoint on account `3f6713b6ee228d00951382a7f7d85fbe`. So R2 is already in production use here.
- Credentials: `terraform/.env` (untracked) → `source scripts/export_env.sh`. Needs `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` (R2 API token keys, for state) plus `TF_VAR_cloudflare_api_token` and `TF_VAR_vultr_api_key`. Secrets live in Vaultwarden, never in the repo.
- Zones managed: `alexluong.com`, `collie.studio`, `nhiluong.com`. Records are per-zone files. Note: `terraform/nhiluong_com.tf` is currently **untracked** — uncommitted local work.

### The v4 → v5 migration (2026-08-11)

Done because R2 lifecycle rules, custom domains and CORS only exist as resources from provider **v5.5+** — v4 had `cloudflare_r2_bucket` and nothing else. Since **v5.19** the provider ships automatic state upgraders, so this is no longer the hand-migration it once was.

How it went, for reference next time:

1. `terraform state pull > backup` first. The R2 state bucket's versioning status is unverified — don't rely on it.
2. Stepping stone to `4.52.5` (required), `init -upgrade`, plan to confirm the baseline.
3. [`tf-migrate`](https://github.com/cloudflare/tf-migrate) v1.1.0 rewrites the HCL and emits `moved` blocks — 11 `cloudflare_record` → `cloudflare_dns_record`, zone `zone` → `name` and `account_id` → `account.id`. It also bumps the provider pin itself and leaves `*.tf.backup` files to delete.
4. `init -upgrade`, then plan and **read it**: the bar is 0 to destroy, 0 to replace.

Expected benign diff after migrating: IPv6 records show zero-padding restored (`5400:5ff` → `5400:05ff`, same address — v4 compressed what the vultr provider returns), CNAMEs regain the trailing dot the HCL already had, and `modified_on` refreshes. Grit-based migration is deprecated; ignore older guides that reach for it.

### R2 for eldobot exports

`terraform/r2.tf` — bucket `eldobot-exports` (location `enam`), public at `exports.alexluong.com`, CORS for browser-side BBGM imports, and lifecycle rules aborting stalled multipart uploads (`exports/`, 1d) and expiring `snapshots/` (2d). Written and validated, **not applied**.

Blocked on API token permissions. `TF_VAR_cloudflare_api_token` currently lacks:

- **Workers R2 Storage: Write** — for the bucket, lifecycle and CORS
- **Zone: Create** (`com.cloudflare.api.account.zone.create`) — for `cloudflare_zone.nhi_luong`, which has been sitting unapplied in the config; this is the error it fails with

The R2 keys already in `.env` are S3 access keys for the state backend — a different credential the cloudflare provider cannot use. eldobot additionally needs its own **scoped R2 API token** (bucket-level, not the terraform one) for `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY`.

## Conventions

- New service = new directory under `services/` with its compose file; deploy = pull on the VM and `docker-compose up -d` in that directory. Public hostname = a `cloudflare_record` in the zone's tf file **and** a Caddy entry.
- Commits follow the repo conventions in `workflow.md` (Conventional Commits, direct to main).
- Incidents get a file in `incidents/` named `YYYY-MM-DD_slug.md`.
