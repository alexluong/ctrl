# Bootstrap Stack

Personal platform for building services (fitJournal, feed, hotel, ...). Design goal: each project focuses on core logic; cross-cutting concerns (auth, billing, storage, observability) are addons. Secondary goal: architecture should transfer to enterprise contexts — same shape, swappable implementations.

Domain: `collie.studio`. Nodes: collielab VM (apps) + home Mac Mini (media: Plex, calibre, audiobookshelf).

## Auth architecture (settled 2026-07-10)

**Ory stack** (Alex is a fan; Go source = learning material; composable, enterprise-relevant).

**Decision (2026-07-10): Kratos only.** Bill of materials: Kratos + Postgres + login UI (`account.collie.studio`) + Go `auth` package. Four pieces; we build two.

- **Kratos** — identity: users, credentials, login/registration/recovery. Headless; we build the login UI. Covers ALL current needs:
  - Browser SSO: shared session cookie on `.collie.studio`, services resolve users via `/sessions/whoami`
  - First-party mobile (Flutter feed, Shortcuts): Kratos native API flows → session token as bearer header, validated via same whoami
- **Hydra** — deferred. Triggers: (1) third-party "Sign in with collie.studio", (2) own app on a non-collie.studio domain (no cookie sharing → needs OIDC redirect), (3) M2M client-credentials tokens. None exist yet. When added: Hydra has no users/login — it delegates login+consent challenges to our existing login UI, which asks Kratos; token `sub` = Kratos identity ID, so identity stays unified and nothing existing changes. Open-sourcing does NOT require us to run Hydra (adopters point the `oidc` mode at their own IdP).
- **Oathkeeper** — deferred, maybe never. For gating third-party dashboards (portainer, glances), Caddy's built-in `forward_auth` → Kratos whoami suffices. Oathkeeper earns its place only for centralized route-level policy across many services.
- **Keto** — authZ (Zanzibar-style). Only if/when hotel back office needs roles.

Ory family in one line each: Kratos = who exists & how they log in; Hydra = standard tokens outsiders can trust; Oathkeeper = who gets past the door; Keto = what they may touch inside.

### The `auth` package (Go template)

Design principle: **library-as-contract** — auth is enforced in-process but written once in the platform package, never by the service author. A service's entire auth surface:

```go
a := auth.FromEnv()              // construct
r.Use(a.Middleware())            // install
user := auth.User(r.Context())   // consume — {ID, Email, Name}
```

Modes (config-selected, same three lines):
- `dev` — hardcoded fake user, no IdP needed; `go run .` just works. Plus `auth.NewFake(user)` for tests.
- `whoami` — production: Kratos cookie → whoami; unauthenticated browsers redirected to login UI and back. Service never renders login.
- `bearer` — non-browser clients: static token now → Kratos session tokens → Hydra JWTs later, same mode.
- `local` — built-in username/password. **Open-source default** — a stranger's `docker compose up` is secure standalone.
- `oidc` — bring-your-own IdP (for open-source adopters).
- `header` — trust proxy-injected identity. **Explicit opt-in, fail closed**: requires trusted-proxy source verification + shared secret or JWT signature. Never a default. Mitigates header-spoofing (app reachable by any path other than the proxy = instant impersonation). Proxy must strip inbound identity headers.

Residual auth surface services still own: store the IdP `sub` as an opaque foreign key (`user_id`); never mirror a users table locally (cache display names at most).

Known tradeoff: whoami = one localhost network hop per request (~1ms, fine at this scale, cacheable per-session; the enterprise answer to this is stateless JWTs, i.e. Hydra).

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
