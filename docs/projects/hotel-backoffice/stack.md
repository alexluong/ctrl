# SoLex — Stack (WS1)

Owner: `solex-dev`. Repo: `alexluong/solex` (private), local at `~/git/hub/alexluong/solex`.

## Status

- 2026-09-23 — **i18n in** (VN + EN, Vietnamese default, server-resolved; rule failures carry codes so they can be translated).
- 2026-09-23 — **event-sourcing skeleton built and deployed**. Event store, first aggregate (Room), projections, and a system console for browsing the log and the database. All of it live on https://solex-stg.collie.studio, keyed by hotel per D-9.
- 2026-09-23 — spike done and deployed. Repo bootstrapped, `fix`/`check` green, GitHub remote pushed.

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

## The ES skeleton as built (2026-09-23)

Alex asked to see event-driven architecture working, to browse the events, and to have a system-admin tool for the database. All three are deployed. D-8's shape is what got built, so the desk exercise below is now also a description of the code.

**Event store** (`src/server/events/`):

- One `events` table. `seq` is the global order for replay; `version` is the position within a stream.
- `UNIQUE (stream_id, version)` is the concurrency control. A writer working from stale state loses the insert and retries from a fresh read. No Durable Object, no lock, no single-writer runtime.
- `handleCommand` is the only write path: load stream → fold to state → decide → append.
- Projections are written **in the same atomic batch** as the event. D1 has no interactive transactions; a batch is atomic, which is enough. A test proves the event does not land when its projection fails.
- `rebuildProjections` drops derived tables and replays the log. A test proves replay reproduces byte-for-byte what live writes produced. On staging it replayed in ~500 ms over D1.

**First aggregate: Room.** Events: `RoomDefined`, `RoomMarkedDirty/Clean/Inspected`, `RoomTakenOutOfOrder`, `RoomReturnedToService`, `RoomNoteSet`. The invariant that earns its keep already: housekeeping cannot change while a room is out of order. `product.md` §6 has Room's real vocabulary; this matches it. Occupancy is deliberately absent — it derives from stays, which do not exist yet.

**Multi-tenancy (D-9)** is in from the first line of schema: stream ids are `<hotel>/room:101`, `events.hotel_id` and every projection row carry the hotel, and `rooms` is keyed by `(hotel_id, id)`. A test proves two hotels with the same room number do not share history. The current hotel comes from config (`SOLEX_HOTEL_ID`, default `solex`) until Setup and real users exist.

**System console** at `/system` — operator-facing, not the hotel's admin persona:

- Event log browser, filterable by stream or type, newest first, with payloads.
- Every table, read-only, paginated, including `events` itself.
- Replay button that rebuilds all projections from the log.
- Each room's own stream is also shown on its detail screen, so the fold is visible where it matters.

**Console access**: a token compared in constant time, held in a cookie. Locally, with no token configured, the console is open. Deployed, a missing token means **closed** — fail closed, never guess. The staging token is set and recorded in `ctrl/secrets/hotel-backoffice.md`.

**Also browsable outside the app**: `pnpm db:studio` (local file) and `pnpm db:studio:remote` (deployed D1, needs a Cloudflare API token with D1 rights — not created, and it belongs in Vaultwarden). `wrangler d1 execute` covers ad-hoc SQL.

### Where the code is, in one screen

```
src/routes/            file routes; index = room board, system.* = operator console
src/server/events/     store.ts (append/read/replay), stream.ts (ids), types.ts
src/server/rooms/      domain.ts (pure rules), projection.ts, commands.ts
src/server/system/     access.ts (token gate), queries.ts, api.ts
src/server/runtime/    node.ts | cloudflare.ts — the ONLY Cloudflare-aware files
src/server/tenant.ts   current hotel (server-only; never import from a route)
src/i18n/              messages.ts (en source + vi typed against it), context, format
drizzle/migrations/    one SQL set, applied to local SQLite and to D1
```

Commands: `mise run setup` · `mise run dev` · `pnpm check` (biome + tsc + vitest) · `pnpm deploy` · `pnpm db:studio` · `pnpm db:generate` / `db:migrate` / `db:migrate:remote`.

**Internationalisation (Alex, 2026-09-23)**: Vietnamese + English, Vietnamese as default. Resolved on the server (cookie, else `Accept-Language`) and passed down, so SSR and hydration agree — picking locale in the browser would guarantee a mismatch. English is the source dictionary and Vietnamese is typed against it: a missing key is a build error, not a blank label.

The part that matters architecturally: **domain rules now fail with a code, not a sentence** (`room.isOutOfOrder`, not "room is out of order"). The server cannot know the reader's language, so any message baked into an aggregate is untranslatable by definition. Anything product adds later should keep this shape. Adding a third language = one dictionary file.

Vietnamese wording is my own and worth a native pass — Alex can check it. Terms used: Trống sạch (vacant clean), Bẩn (dirty), Đã kiểm tra (inspected), Ngừng sử dụng (out of order). Money (VND) formatting is not done yet; it lands with the first charge.

The console stays English on purpose: operator tool, code's vocabulary.

### The system console, and whether it should have been built

Alex asked whether it was all hand-built. It was: ~350 lines, four routes and two server modules. The honest split:

- The **generic table browser duplicates Drizzle Studio** (`pnpm db:studio`, already wired). If this grows, that part should go and Studio should own table browsing.
- The **event log, stream/type filters and the replay button** are not duplicative — no general-purpose database tool knows what an event stream is, or that projections are disposable.
- Console access is one shared token, constant-time compared, open locally and **closed when deployed unless configured**. Stopgap until D-11.

### What I'd want before calling this production-shaped

- **Authentication.** The room board is public on staging and the console is only as strong as one shared token. Real auth is a decision for architect + `docs/stack.md`'s auth stance.
- **Event versioning.** Payloads are unversioned JSON. Fine now; a rename of a field later needs an upcaster, and deciding that early is cheaper.
- **A second aggregate** will tell us whether the store's shape holds. Booking is the real test, because of the cross-aggregate availability rule.

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
