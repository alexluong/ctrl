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

- Root module: `terraform/`. Providers: `cloudflare ~> 4.0`, `vultr 2.21.0`.
- **State backend is Cloudflare R2** — bucket `collielab-terraform`, key `terraform.tfstate`, S3-compatible endpoint on account `3f6713b6ee228d00951382a7f7d85fbe`. So R2 is already in production use here.
- Credentials: `terraform/.env` (untracked) → `source scripts/export_env.sh`. Needs `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` (R2 API token keys, for state) plus `TF_VAR_cloudflare_api_token` and `TF_VAR_vultr_api_key`. Secrets live in Vaultwarden, never in the repo.
- Zones managed: `alexluong.com`, `collie.studio`, `nhiluong.com`. Records are per-zone files. Note: `terraform/nhiluong_com.tf` is currently **untracked** — uncommitted local work.

### R2 via terraform — what's actually possible

Yes for buckets, no for the rest at the pinned version:

| Resource | In `~> 4.0` | Needed for |
|---|---|---|
| `cloudflare_r2_bucket` | **yes** | creating the bucket |
| `cloudflare_r2_bucket_lifecycle` | no — v5.5+ | TTL / auto-expiry |
| `cloudflare_r2_custom_domain` | no — v5.5+ | public `exports.*` domain |
| `cloudflare_r2_bucket_cors` | no — v5.5+ | browser-side fetches |

The v4→v5 provider jump is a rewrite with breaking schema changes across every existing `cloudflare_record`, so it is not a free upgrade. Three ways forward, in order of preference:

1. **Second root module** `terraform/r2/` pinned to `cloudflare ~> 5`, own state key in the same bucket. DNS stays on v4 and untouched; R2 gets full IaC. Provider constraints are per-root-module, so this is legitimate, not a hack.
2. Bucket in TF on v4, lifecycle/domain/CORS clicked in the dashboard. Fastest, but the interesting config is then undocumented.
3. Upgrade the whole config to v5. Cleanest end state, biggest blast radius — a separate piece of work, not a side quest.

The `TF_VAR_cloudflare_api_token` also needs **Workers R2 Storage: Write** (and zone DNS edit for a custom domain). The R2 keys already in `.env` are S3 access keys for the state backend — different credential, not usable by the cloudflare provider.

## Conventions

- New service = new directory under `services/` with its compose file; deploy = pull on the VM and `docker-compose up -d` in that directory. Public hostname = a `cloudflare_record` in the zone's tf file **and** a Caddy entry.
- Commits follow the repo conventions in `workflow.md` (Conventional Commits, direct to main).
- Incidents get a file in `incidents/` named `YYYY-MM-DD_slug.md`.
