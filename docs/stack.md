# Bootstrap Stack

Personal platform for building services (fitJournal, feed, hotel, ...). Design goal: each project focuses on core logic; cross-cutting concerns (auth, billing, storage, observability) are addons. Secondary goal: architecture should transfer to enterprise contexts — same shape, swappable implementations.

Domain: `collie.studio`. Nodes: collielab VM (apps) + home Mac Mini (media: Plex, calibre, audiobookshelf).

## Auth architecture (settled 2026-07-10)

**Ory stack** (Alex is a fan; Go source = learning material; composable, enterprise-relevant):

- **Kratos** — identity: users, credentials, login/registration/recovery. Headless; we build a small login UI at `account.collie.studio`. First-party apps on `*.collie.studio` share the session cookie and resolve users via Kratos `/sessions/whoami` — SSO without needing Hydra initially.
- **Hydra** — OIDC/OAuth2 token issuance. Add when needed: Flutter app tokens, or open-source users bringing their own IdP.
- **Oathkeeper** — identity-aware proxy (forward-auth done right: signed JWT identity headers). Add to gate third-party dashboards (portainer, glances).
- **Keto** — authZ (Zanzibar-style). Only if/when hotel back office needs roles.

### The `auth` package (Go template)

One interface (`auth.UserFromContext`), pluggable modes via config:
- `local` — built-in username/password. **Default** — safe for strangers who `docker compose up` an open-sourced service.
- `oidc` / `kratos-whoami` — delegate to IdP (ours or bring-your-own).
- `header` — trust proxy-injected identity. **Explicit opt-in, fail closed**: requires trusted-proxy source verification + shared secret or JWT signature. Never a default. Mitigates the classic header-spoofing attack (app reachable by any path other than the proxy = instant impersonation). Proxy must strip inbound identity headers.

### OIDC mental model (reference)

Auth code + PKCE flow: app redirects to IdP → user authenticates, IdP sets its own session cookie → IdP redirects back with one-time code → app backend exchanges code for ID token (JWT: sub/email/name, verified against IdP JWKS) → app sets own session. SSO = the IdP session cookie makes the second app's redirect bounce straight back.

## Component map (2 services from scratch)

Day 1:
| Component | Pick | Enterprise analog |
|---|---|---|
| Edge (TLS/routing) | Caddy (already on VM, systemd) | Ingress/ALB |
| Identity | Kratos + login UI | Ory/Okta/Entra |
| Database | One Postgres container, database-per-service | RDS, same isolation |
| Service skeleton | Go template: config, logging, health, migrations, auth pkg | same |

Near-term:
| Component | Pick | Enterprise analog |
|---|---|---|
| Object storage | Cloudflare R2 (pics off VM disk — disk incident precedent) | S3 |
| Backups | pg_dump + volumes → R2/B2 nightly; vaultwarden data = crown jewel | DB snapshots/DR |
| CI/CD | GH Actions → GHCR → compose pull on VM | Actions → ArgoCD/k8s |
| Secrets | .env on VM; SOPS when it hurts | Vault |
| Observability | existing prometheus/promtail + Grafana/Loki + uptime alerts | identical |
| Networking | Tailscale mesh: VM + Mac Mini (+ phone) | zero-trust networking |

Later (pull-based): push notifications (APNs/FCM for feed), Oathkeeper, Hydra, Keto, billing addon (Stripe wrapper pkg — not until a project charges money).

## Current VM state (observed 2026-07-10)

- Caddy on host (systemd, `/etc/caddy/Caddyfile`), services bind `127.0.0.1:<port>`, Cloudflare-proxied DNS via terraform
- Services: vaultwarden (`vault.collie.studio`, the important one), portainer, glances, observability (prometheus/promtail)
- Terraform: Cloudflare zones (collie.studio, alexluong.com, nhiluong.com) + Vultr instance

## Principles

- Addons are packages in the template + shared infra services, not per-project code
- Fail closed: insecure modes require explicit opt-in with trust anchors configured
- Extract templates after 2 uses, don't design upfront
- Compose-not-k8s and one-Postgres are deliberate scale-appropriate choices; the architecture transfers by swapping implementations
