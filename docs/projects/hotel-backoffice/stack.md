# SoLex — Stack (WS1)

Owner: `solex-dev`. Repo: `alexluong/solex` (private), local at `~/git/hub/alexluong/solex`.

## Status

- 2026-09-23 — **spike done and deployed**. https://solex-stg.collie.studio is live, server-rendered, writing to D1. Repo bootstrapped, `fix`/`check` green, GitHub remote pushed.

## The stack (D-3 + Alex, 2026-09-23)

One application, not a frontend plus an API.

| layer | choice | why |
|---|---|---|
| framework | **TanStack Start** (React 19, SSR, file routes, server functions) | Alex: "embrace as much TanStack as possible". One app, server-rendered, no separate API service |
| language | TypeScript | D-3 |
| database | **SQLite**: a local file in dev, **Cloudflare D1** deployed | D1 *is* SQLite, so one schema and one set of queries serve both |
| query layer | Drizzle (`sqlite-core`) + `drizzle-kit` migrations | one migration set applied to the file locally and to D1 by wrangler |
| hosting | Cloudflare Workers, one Worker serving app + assets | D-1 (no VM), D-3 |
| local stack | Docker Compose, one service | per-worktree ports, room for more services later |
| quality gate | Biome + `tsc`, as `fix` / `check` | `docs/workflow.md` bar |

### Cloudflare is a build target, not the dev environment

Alex's constraint, 2026-09-23: *"i want cloudflare as deployment platform, not coupled the full dev experience to it if we can avoid it."* The official TanStack-on-Cloudflare setup puts the Workers Vite plugin in the dev loop, so `vite dev` runs inside workerd. The spike avoids that:

- `vite dev` runs the app on **Node** against a local SQLite file. No Cloudflare anything.
- `DEPLOY_TARGET=cloudflare vite build` adds the Workers plugin and swaps one module.
- That one module, `src/server/db/driver.cloudflare.ts`, is the **entire** Cloudflare-specific surface of the app: it is the only file importing `cloudflare:workers`. Vite aliases `#db-driver` to it for the Cloudflare build and to `driver.node.ts` otherwise.
- `pnpm preview:cloudflare` runs the real Workers build locally in workerd against a local D1, so parity is one command away rather than discovered at deploy.

Cost of this arrangement: two runtime paths, and divergence is caught only by running the preview. Mitigation is the preview command plus a smoke test; if it ever gets annoying, the fallback is the standard single-target setup with workerd in dev.

### Per-worktree isolation

`mise run setup` writes a gitignored `.env` with a port and a Compose project name derived from the checkout's directory name, so several worktrees run side by side. Same pattern as collie-ui.

## What was proven, by doing it

Both runtimes were driven in a real browser (Playwright, headless Chromium): type into the form, submit, confirm the row appears, reload, confirm it came back from the server, confirm the label is in the server-rendered HTML.

| path | result |
|---|---|
| Node + local SQLite (`pnpm dev`) | pass, no console errors |
| Workers + local D1 (`pnpm preview:cloudflare`) | pass |
| Deployed Worker + remote D1 | pass |

Deployed request latency, 10 requests to the live URL: min 0.283s, p50 0.359s, max 1.493s (the max is the first, cold). Worker startup time reported by wrangler at deploy: 15 ms. Upload size 1.05 MB, 224 KB gzipped.

Cost: $0. Workers free plan, D1 free tier, no paid resources created.

### Two things that bit, both now documented

1. **TLS on a two-level subdomain.** `stg.solex.collie.studio` deploys fine and then fails TLS: Cloudflare's free universal certificate covers `collie.studio` and `*.collie.studio`, one label only. A second level needs Advanced Certificate Manager (~$10/mo). Staging is therefore **`solex-stg.collie.studio`**. Same trap applies to any future `*.solex.collie.studio` scheme.
2. **Hydration mismatch from `toLocaleString()`.** The server and the browser formatted the same timestamp differently and React threw away the server markup. Dates now render through a fixed locale and time zone. This will come back as a real product question: which time zone is "hotel-local", and the answer should be explicit rather than the server's.

Also worth knowing: the Workers custom domain creates its own DNS record, which `collielab/terraform` does not know about. Changing the route removed the old record cleanly, but terraform and wrangler both believe they own DNS for this zone.

## Dev loop

```sh
mise install && mise run setup   # ports, deps, database
mise run dev                     # http://localhost:<PORT_APP>
mise run fix && mise run check   # before landing
pnpm preview:cloudflare          # the Workers build, locally
pnpm deploy                      # build + ship
```

Compose (`mise run up`) runs the same dev server in a container for worktrees that want it.

## Storage shape for event sourcing (desk exercise for architect, 2026-09-23)

Read against `product.md` §5–6. Product proposes a single-writer Durable Object per hotel for Reservations, with D1 for projections. **I'd recommend against the DO, and against a second storage system, for v1.** Reasoning:

### The problem DO solves is real but small here

The only invariant needing a consistency boundary wider than one aggregate is availability (per-room overlap, per-type per-night count). Product §6 is right about that. But a single-writer DO is one way to serialise writes, not the only one, and SQLite gives another: **optimistic concurrency on the event stream**, `UNIQUE (stream_id, version)`, append with an expected version, retry on conflict. Availability becomes a stream of its own (per hotel, or per room if contention ever appears), so two conflicting assignments collide on the version number and one loses. That is the same serialisation the DO buys, expressed as a constraint instead of as a runtime.

At 58 rooms, one hotel, and humans typing at reception, contention is close to zero and a retry costs nothing.

### DO-as-event-store: feasible, but the wrong trade here

Technically it fits: DO storage is SQLite-backed, gives strict single-threaded ordering for free, has alarms for scheduled work, and 10 GB per object is far beyond a hotel's event volume. Replay is a table scan inside the object.

What it costs:
- **It breaks the constraint Alex just set.** Durable Objects exist only inside workerd. There is no local, Cloudflare-free way to run one, so adopting DO puts Cloudflare back in the middle of the dev loop, which is the thing we deliberately kept out today.
- **Two storage systems** (DO for the log, D1 for projections) means two migration stories and cross-system consistency between an event and the projection derived from it.
- Testing an aggregate becomes testing a DO.

### D1 for both, with projections written in the same transaction

D1 has no interactive transactions, but `batch()` is atomic, which is all this needs: append the event and update its projections in one batch, or neither lands. That covers the `Need` cascade from `requirements.md` §1 — one event, several projection tables, one atomic write.

This matches Alex's own instinct on 2026-09-23: *"we can make the event store and all the projection as in-process workload maybe? just to simplify the system."* Yes, and it stays correct as long as projections are pure functions of the event. The projections that must be synchronous are the ones a user reads immediately after acting (room board, folio balance). Anything genuinely slow or external gets moved out later.

Known D1 limits worth stating: 10 GB per database (a hotel writing ~200 events/day will not approach it), single writer, read replication available via the sessions API. Nothing here is close to a ceiling.

### Feeding projections, and rebuilds

- **v1**: synchronous, same batch as the append. No queue, no bus.
- **Rebuild**: read the event table in order, re-fold. At this volume it is seconds, and it is the thing that makes the event log worth having.
- **Later, if needed**: Cloudflare Queues for anything slow or external (email, OTA push). Worth adding when there is a real consumer, not before.

### Hookdeck's role under D-3

Honest answer: **none right now, and probably none for the event log ever.** Hookdeck is good at inbound webhook delivery, retries and replay-in-window. The event store needs a permanent, per-aggregate-ordered, replayable log, which is a database's job and now is D1's. When OTA webhooks arrive as a real integration, Hookdeck is a reasonable front door for *ingest* — and so is a plain Worker route, given Workers already terminate HTTP for us. I'd defer the decision until an actual channel integration exists, and close the retention question as moot for the event log.

Concretely, the shape I'd build first:

```
events(stream_id, version, type, payload, occurred_at, actor)   UNIQUE(stream_id, version)
<projection tables per read model>
```

Aggregates from `product.md` §6 map onto streams directly: `booking:<id>`, `stay:<id>`, `room:<id>`, `folio:<id>`, `receivable:<id>`, `guest:<id>`, plus `availability:<hotel>` as the serialisation point.

## Open questions

- Which time zone is "hotel-local" for rendering? (Surfaced by the hydration bug; belongs to product.)
- Does staging want authentication before it holds anything real? It is a public URL today, with a throwaway table.
- `stg.solex.collie.studio` is available for ~$10/mo (Advanced Certificate Manager) if the naming matters. Currently not spent.

## For other WSs

- **product**: the stack imposes no modelling limits at this scale. Per-night rates, routing and the 8-bucket charge enum all fit a plain SQLite schema. The one thing worth knowing is that synchronous projections mean a read model is only as fresh as the write that fed it, which is what the dashboard wants anyway.
- **architect**: D-3 decided the runtime; the open decision is the storage shape above. My recommendation is D1 for log and projections, optimistic concurrency instead of a Durable Object, Hookdeck deferred. That keeps one storage system and keeps Cloudflare out of the dev loop.
