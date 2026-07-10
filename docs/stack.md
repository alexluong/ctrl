# Bootstrap Stack

Personal platform for building services (fitJournal, feed, hotel, ...). Design goal: each project focuses on core logic; cross-cutting concerns (auth, billing, storage, observability) are addons. Secondary goal: architecture should transfer to enterprise contexts — same shape, swappable implementations.

Domain: `collie.studio`. Nodes: collielab VM (apps) + home Mac Mini (media: Plex, calibre, audiobookshelf).

## Auth architecture (settled 2026-07-10)

**Decision (2026-07-10, revised same day): OIDC-first, Ory as swappable implementation.**

Core requirement (Alex): build feed/fitjournal so auth is swappable with little-to-no change. Achieved with two insulation layers:

1. **Auth package interface** — services only touch `auth.Middleware()` + `auth.User(ctx)` → `{ID, Email, Name}`. Any auth change = package/config change; service code change = zero by construction.
2. **Standard OIDC as the package's production mode** — core is `go-oidc` + JWKS validation + standard redirect flow. Swapping the IdP = config only (`AUTH_ISSUER` + client creds): Hydra ↔ Keycloak ↔ Okta ↔ Pocket ID, no code change even in the package. This also means the open-source posture is dogfooded daily, not a rotting side mode; and token validation is stateless (no per-request whoami hop).

**Irreducible lock-in surface**: data keyed by IdP `sub` (`user_id` columns). IdP swap = user remap migration (match by email, or import identities preserving IDs — Kratos supports this). Data migration, not code. Trivial at 2 users; know it exists.

**Chosen implementation behind the protocol** (because Alex likes Ory + learning value; the stack no longer depends on this choice):

- **Kratos** — identity source of truth: users, credentials, login/registration/recovery flows. Headless.
- **Hydra** — OIDC provider, in from day 1. Has no users/login itself — delegates login+consent challenges to our login UI (~2 extra endpoints), which drives Kratos. Token `sub` = Kratos identity ID. Consent auto-skipped for trusted first-party clients.
- **Login UI** (`account.collie.studio`) — small Go+templ app; renders Kratos self-service flows + handles Hydra login/consent challenges.
- **Oathkeeper** — deferred, maybe never. Gating third-party dashboards (portainer, glances): Caddy built-in `forward_auth` suffices. Oathkeeper only for centralized route-level policy across many services.
- **Keto** — authZ (Zanzibar-style). Only if/when hotel back office needs roles.

Ory family in one line each: Kratos = who exists & how they log in; Hydra = standard tokens outsiders can trust; Oathkeeper = who gets past the door; Keto = what they may touch inside.

Known Hydra-posture tradeoffs (accepted): token lifecycle to manage (short-TTL JWTs + refresh; revocation isn't instant), logout-everywhere is fiddlier than a shared cookie, more moving parts day 1. This is deliberate overengineering for learning + enterprise transferability.

### The `auth` package (Go template)

Design principle: **library-as-contract** — auth is enforced in-process but written once in the platform package, never by the service author. A service's entire auth surface:

```go
a := auth.FromEnv()              // construct
r.Use(a.Middleware())            // install
user := auth.User(r.Context())   // consume — {ID, Email, Name}
```

Modes (config-selected, same three lines):
- `oidc` — **primary production mode**: standard OIDC RP (redirect flow for browsers, JWT/JWKS validation for bearer tokens). Works against Hydra or any other IdP. Service never renders login.
- `dev` — hardcoded fake user, no IdP needed; `go run .` just works. Plus `auth.NewFake(user)` for tests.
- `local` — built-in username/password. **Open-source default** — a stranger's `docker compose up` is secure standalone.
- `header` — trust proxy-injected identity. **Explicit opt-in, fail closed**: requires trusted-proxy source verification + shared secret or JWT signature. Never a default. Mitigates header-spoofing (app reachable by any path other than the proxy = instant impersonation). Proxy must strip inbound identity headers.
- (`whoami` — optional Kratos-direct optimization; demoted from primary, may never be built.)

Residual auth surface services still own: store the IdP `sub` as an opaque foreign key (`user_id`); never mirror a users table locally (cache display names at most).

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
