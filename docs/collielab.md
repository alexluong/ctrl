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

### R2 for eldobot exports — applied 2026-08-11

`terraform/r2.tf` — bucket `eldobot-exports` (location `enam`), public at `exports.alexluong.com`, CORS allowing browser GET/HEAD, and a lifecycle rule aborting stalled multipart uploads under `exports/` after 1 day. Applied and verified: object PUT → public fetch returns 200 with `content-type: application/json`.

Also applied in the same run: `cloudflare_zone.nhi_luong` was **imported**, not created — the zone already existed in Cloudflare (`dca266ff…`), so the long-pending create would have failed regardless of permissions.

## Tokens

Three, with distinct jobs. Values live in Vaultwarden and untracked `.env` files, never here.

| Token | ID | Used by | Scope |
|---|---|---|---|
| `collielab-terraform` | `a1f74a44…` | terraform: cloudflare provider **and** R2 state backend | account-wide + all zones (DNS/Zone read+write) |
| `eldobot-exports-rw` | `001ee362…` | eldobot at runtime | that one bucket, object read+write only |
| *(legacy user token)* | `cd18900d…` | nothing — superseded | zone-scoped, no account access |

**R2 derives S3 credentials from a token**: `Access Key ID` = the token's ID, `Secret Access Key` = `SHA-256(token value)`. So one token serves both the provider (as a Bearer token) and the state backend (as S3 keys) — and **rolling a token silently breaks the S3 secret while the access key ID stays the same**. That failure looks like `SignatureDoesNotMatch` on `terraform init/plan`, and the fix is to re-derive the secret from the new value, not to hunt for a new key pair.

Gotcha that cost real time: a token can carry account-scoped permissions (R2, Workers, etc.) and still 403 on every DNS call, because zone permissions are a **separate policy** with zone-scoped resources. `GET /accounts` returning `count: 0` is the quick tell for "no account resources"; DNS 403s with account access working is the tell for "no zone policy". The working form is one policy per scope — an account policy plus a zone policy listing each zone as `com.cloudflare.api.account.zone.<zone_id>`. The nested "all zones in account" form did not take effect. Policy edits take ~20–30s to propagate.

eldobot's credential is in `~/.cache/eldobot-r2-creds.env` (mode 600) on the MBP until it's placed on the VM.

## Conventions

- New service = new directory under `services/` with its compose file; deploy = pull on the VM and `docker-compose up -d` in that directory. Public hostname = a `cloudflare_record` in the zone's tf file **and** a Caddy entry.
- Commits follow the repo conventions in `workflow.md` (Conventional Commits, direct to main).
- Incidents get a file in `incidents/` named `YYYY-MM-DD_slug.md`.
