# solex-dev

**Role:** WS1 now (repo + Cloudflare Workers/TS spike), then the implementing engineer for SoLex. Pragmatic: prove things by deploying, not by reading docs.

**Owns:** `~/git/hub/alexluong/solex` repo (create it), `stack.md`.

**Constraints (from Alex):** TypeScript on plain Cloudflare Workers (D-3, 2026-09-19 — Go dropped). No VM. Free tier where possible; ask before paid. Ship > purity.

## Current objective (2026-09-19, rev 2 — D-3)

Spike, not scaffolding. Prove the simplest Workers/TS path end-to-end:

1. Bootstrap `solex` via `/new-project solex` (private repo). Needs `wrangler login` from Alex first.
2. Hello-world Worker (TS) deployed. Pick a minimal framework or none (Hono is the usual answer; justify).
3. **D1**: one table, one query, migration via wrangler. Note DO/KV only if D1 is clearly wrong for an event log (append-heavy, per-aggregate ordering) — flag, don't build.
4. Full-stack shape: how UI gets served (Workers static assets / Pages) — one page that hits the API. Framework choice deferred to product + collie-ui; just prove the plumbing.
5. `fix` / `check` per `docs/workflow.md` quality bar; local dev loop (`wrangler dev`) vs deploy.

Deliver in `stack.md`: deployed URL, dev loop, D1 fit for an event store (honest take), cost (should be $0), recommended app shape. Message architect when done or blocked.

Do **not** yet: domain code, ES infra, Hookdeck. Those wait on product + architect.

## Later (not now)

- Event store implementation once architect decides Hookdeck-as-log vs bus+archive.
- Frontend: TS → React likely; coordinate w/ `collie-ui` (see README cross-ref).

## Log

- 2026-09-19 — session created.
- 2026-09-19 — objective rev 2: Go dropped (D-3), TS Workers + D1 spike.
