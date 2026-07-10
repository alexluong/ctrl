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

### Auth pkg interface (design liked 2026-07-10, not final)

Core: middleware produces a **Principal**, not a User — callers aren't always human.

- `Principal{Kind (user|service|api_key|agent), Subject, User *User, Actor string, Scopes []string}`
- **User vs Actor**: User = whose behalf (data attribution, permission ceiling); Actor = what mechanically called (audit, rate-limit, revocation target). Differ only under delegation: Shortcut key → `{User: alex, Actor: key:fj_...}`; agent → `{User: alex, Actor: agent:x}`; bot → `{User: nil, Actor: service:backupd}`. OAuth `act` claim analog.
- **Authenticator chain**: `auth.New(auth.OIDC(issuer), auth.Session(cfg), auth.APIKeys(store))` — tried in order, first match wins; mechanism (cookie/JWT/key) orthogonal to Kind. `auth.FromEnv()` builds the chain from AUTH_MODE so service code is identical in dev/prod/open-source.
- **API keys**: app-issued (bypass IdP), hashed in service DB, prefix-routed (`fj_live_...`), owned by a user → requests attribute to the owner. fitJournal Shortcut uses this (not a bare static token).
- **Scopes**: standard OAuth2 concept, normalized onto Principal (JWT scopes + key permissions = one field). Discipline: coarse vocabulary only (`entries:read/write`, `admin`); one scope per route-group; interactive sessions get full scope implicitly; fine-grained permissions belong to layer-3 membership/roles, not scopes. Scope explosion = authz leaking into the credential layer.
- **Agent auth**: frontier; hedge = User+Actor split. Today: user-issued scope-limited API keys. Later: OAuth token exchange (RFC 8693) as a 4th authenticator — same Principal, zero handler changes.
- **No-OIDC setups**: `dev` mode = `auth.Static(fakeUser)` (zero infra); tests = `auth.WithPrincipal(ctx, ...)` injection; `local` mode = `auth.Local(db, secret)` + `a.LocalRoutes()` (built-in bcrypt login, own session cookie, ~200 lines in kit).

### MFA & account security

All IdP-side (Kratos + login UI); services see only sessions/tokens — adding MFA = zero service changes. Kratos natively: TOTP, WebAuthn/passkeys, recovery codes. Posture: **passkey primary, TOTP fallback**. The only service-visible concept: **AAL/step-up** (`acr` claim) — sensitive routes may `Require(auth.AAL2)` (delete account, refunds, API-key management). MFA gates key *issuance*, never key *usage* (non-interactive creds are bounded by scopes+expiry instead). Package deal in same place: email verification, recovery, lockout, device/session management. Infra consequence: needs outbound email → SMTP relay (SES/Resend/Postmark) — platform-wide useful (notifs, booking confirmations).

### OTP taxonomy — classify by what the code proves

1. **Identity** (login codes, TOTP, recovery) → IdP/Kratos config. Services never see it.
2. **Channel ownership** (verify email/phone) → IdP/Kratos flows.
3. **Capability** (booking codes, guest check-in links, feed invites, share links) → **feature, owned by the service**: short-lived resource-scoped grants in service DB. Mechanics (mint/hash/expire/verify/rate-limit) = kit candidate after 2 uses (feed invites + hotel bookings).

Account-less access (hotel guests): `auth.Capability(store)` authenticator → limited principal `{Kind: guest, User: nil, Scopes: ["booking:ABC123:read"]}` — same middleware/gates, no handler special-casing. **Hard rule: guests never become Kratos identities** (capabilities, not users).

Fintech-style action OTP (authenticated user still challenged before sensitive action) = two distinct patterns:
- **Re-authentication / fresh step-up**: "prove presence recently" — auth layer (OIDC `max_age`/`acr_values`; check `auth_time` + AAL on Principal). Generic, no action binding.
- **Transaction confirmation** (PSD2 SCA "dynamic linking"): challenge bound to the *specific action + params* via pending-action record + params-hash; single-use, short TTL. Defeats session hijack (stolen session can't approve a different payee/amount). Domain feature using capability-code plumbing (`confirm` kit candidate); `action.approved` check is tier-2 business logic.

### AuthZ model — Principal is evidence, not judge

Three tiers, each a different question:
1. **Credential gate** (route middleware): may this *credential* attempt this action class? Inputs: Principal only (scopes/kind/AAL). `a.Require(auth.Scope(...), auth.AAL2)`.
2. **Domain authz** (handler/query): may this *user* touch this *resource*? Inputs: Principal.Subject + service tables (ownership/membership/role). Prefer authz-by-construction (`WHERE user_id = $1`); role checks = if-statements. Deliberately NOT centralized — it's business logic.
3. **Policy engine** (Keto/SpiceDB = ReBAC, OPA/Cedar = ABAC): only when tier-2 outgrows role-column+ifs (e.g. multi-hotel per-property permissions). Buys cross-service consistency + listing queries; costs a hop per decision + policy far from code. Feed/fitjournal: never. Hotel: maybe.

Key rule: scopes bound the credential, domain authz bounds the person — **both must pass**, neither substitutes. Collapsing them = "token was valid so we allowed it" bugs.

Clarification: scopes ARE authz — the credential half. **Scopes attenuate, never grant**: `effective permission = user's domain rights ∩ credential's scopes`. A scope means "may exercise the owner's X-rights, if the owner has any" — so scope checks can't answer resource questions, and domain checks can't keep a leaked narrow key narrow. Transaction confirmation is outside the auth layer (needs action semantics = business rules); re-auth/freshness is inside it (pure claims: auth_time, AAL).

### User / tenancy layering (the part auth doesn't solve)

Three layers, never conflated:
1. **Identity** (IdP/Kratos, global): sub, email, credentials. Kept dumb — no org/role claims in tokens (stale-authz-in-token trap).
2. **App user record** (per service): local `users` table, JIT-provisioned by middleware on first authenticated request, keyed by sub. App-specific profile/prefs; domain tables FK to this, not raw subs. Every service has this; the JIT middleware lives in the template. (Don't mirror *identity*; do own the app user record.)
3. **Tenancy/membership** (per service, domain code): `orgs`/`spaces` + `memberships(user, org, role)`. Business logic, not plumbing — modeled per app: fitjournal = none; feed = one space, two members; hotel = real orgs + staff roles (and multi-tenant if ever >1 hotel). Extract a template package for the shape after hotel proves it (2-uses rule). Keto only if roles outgrow a role column + if-statements.

### OIDC mental model (reference)

Auth code + PKCE flow: app redirects to IdP → user authenticates, IdP sets its own session cookie → IdP redirects back with one-time code → app backend exchanges code for ID token (JWT: sub/email/name, verified against IdP JWKS) → app sets own session. SSO = the IdP session cookie makes the second app's redirect bounce straight back.

## Distribution: authkit under the colliestudio org (direction liked 2026-07-10)

Repo structure (Alex's proposal, refined):

Org boundaries (revised 2026-07-10): `alexluong/` = personal apps; `collielab/` (new GitHub org) = personal infrastructure; `colliestudio/` = professional/public-facing company artifacts only.

- **`colliestudio/authkit`** — Go module, **pkg only**, auth-concern only: `auth/` (Principal, authenticator chain, Require), `apikeys/`, `confirm/`. Light deps, semver. Company org because client work importing company-owned infra is the professional arrangement; personal projects importing company OSS is fine.
  - Name collision note: WorkOS has a product literally called AuthKit. Fine for company/private use (import path disambiguates); pick a distinct name if it should be findable OSS.
- **`collielab/auth`** — deployment-specific login+account UI + Kratos admin for the homelab IdP (Go+templ, renders Kratos flows + Hydra challenges). Personal infra, NOT a colliestudio product. If client work needs a login UI, it's their deployment's thin app; genuinely generic flow-rendering emerges as importable helpers in authkit, not as a UI product.
- **`collielab/infra`** — current `alexluong/collielab` transferred: terraform, VM, `services/` compose entries incl. `services/auth/` (kratos + hydra + postgres + collielab/auth image). `arr` → `collielab/media` when the media migration happens.
- Other kit candidates (httpx, config, log) = separate module later, 2-uses rule. One concern per module; keeps authkit's dep tree clean.

The hotelacme test (validates the split): client repo `hotelacme/erp` imports authkit; client infra deploys its own kratos + hydra + their thin login UI → fully isolated identity stack per client (their userbase, their infra). Same module, different deployments.

- **Behavior goes in the module, boilerplate gets stamped** — auth/security code must propagate via version bump; main.go skeletons and compose files can be template-stamped copies.
- **Local dev**: `go.work` (`use ./authkit ./feed ./fitjournal`) — kit edits visible in services instantly, publish by tagging.

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
