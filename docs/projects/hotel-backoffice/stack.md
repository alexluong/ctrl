# SoLex — Stack (WS1)

Owner: `solex-dev`. Repo: `alexluong/solex` (private), local at `~/git/hub/alexluong/solex`.

## Status

- 2026-09-24 — **slice 3 complete**: ledger, folios, night roll, check-out guard, the bill, receivables and expenses. Every form swept for silent refusals and PII-in-URL (N10/N11/N12). 255 scenarios + solex-qa's 27 browser tests green. Staging on version `0094e999`, database wiped (D-26).
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
pnpm deploy                      # migrate D1, build, ship
```

Compose (`mise run up`) runs the same dev server in a container for worktrees that want it.

**Migrations run first, on both paths** (N8). `pnpm dev` applies local migrations before starting Vite, and `pnpm deploy` applies them to D1 before the Worker flips. Both orderings are the same bet: schema ahead of code is harmless, code ahead of schema is a 500 on the first page that touches the new table — which reads as a broken feature rather than as a missing migration. It cost an architect a confused half hour on `/calendar`. The bet holds only while migrations stay additive; a destructive one needs expand/contract across two deploys, and this ordering will not save it.

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
src/routes/            file routes; index = room board, calendar = occupancy grid,
                       bookings = take a booking, stays.$id = the desk's loop + the bill,
                       setup = room types/rates/rooms/staff/charge categories,
                       guests = people, system.* = operator console
src/server/hotel/      THE application layer: index.ts (the Hotel object), rooms/bookings/stays,
                       current.ts (composition root — the only caller of getDatabase)
src/server/store/      the Store port: index.ts (interface + sqliteStore), log, projections,
                       people, rooms — the ONLY place drizzle is imported (biome-enforced)
src/server/api/        server fns, adapters only: result.ts (the one catch), rooms.ts, booking.ts
src/server/testkit/    testHotel, memoryStore, fixedClock, countingIds, given.*, rejects.rule
src/server/rules.ts    RuleError base — one catch covers every aggregate
src/server/events/     stream.ts (ids), types.ts, upcast.ts
src/server/rooms/      domain.ts (pure rules, tier b)
src/server/setup/      domain.ts (room types, rate table, quoting — tier b)
src/server/ledger/     domain.ts (accounts, balanced entries, reversal — tier a)
src/server/folio/      domain.ts (charges, payments, refund ceiling, reserved `room`)
src/server/people/     domain.ts (guest + contact rules, PII never in payloads)
src/server/staff/      domain.ts (roles, capability bundles, membership rules)
src/server/auth/       options.ts (static) + index.ts (lazy instance), session.ts, api.ts, directory.ts
src/server/booking/    domain.ts (pure) · dates.ts · input.ts (zod)
src/server/stay/       domain.ts (pure aggregate: check-in/out, cancel, nights)
src/ui/command.tsx     useCommand + CommandError — one way to run a command and show a refusal
src/ui/folio.tsx       the bill: charges, payments, void (owner), take payment
src/server/system/     access.ts (operator gate), queries.ts, api.ts
src/server/runtime/    node.ts | cloudflare.ts — the ONLY Cloudflare-aware files
src/server/tenant.ts   current hotel (server-only; never import from a route)
src/i18n/              messages.ts (en source + vi typed against it), context, format
drizzle/migrations/    one SQL set, applied to local SQLite and to D1
```

Commands: `mise run setup` · `mise run dev` · `pnpm check` (biome + tsc + vitest) · `pnpm deploy` · `pnpm db:studio` · `pnpm db:generate` / `db:migrate` / `db:migrate:remote`.

**Internationalisation (Alex, 2026-09-23)**: Vietnamese + English, Vietnamese as default. Resolved on the server (cookie, else `Accept-Language`) and passed down, so SSR and hydration agree — picking locale in the browser would guarantee a mismatch. English is the source dictionary and Vietnamese is typed against it: a missing key is a build error, not a blank label.

The part that matters architecturally: **domain rules now fail with a code, not a sentence** (`room.isOutOfOrder`, not "room is out of order"). The server cannot know the reader's language, so any message baked into an aggregate is untranslatable by definition. Anything product adds later should keep this shape. Adding a third language = one dictionary file.

Vietnamese wording is my own and worth a native pass — Alex can check it. Terms used: Trống sạch (vacant clean), Bẩn (dirty), Đã kiểm tra (inspected), Ngừng sử dụng (out of order). Money (VND) formatting is not done yet; it lands with the first charge.

Everything on screen is translated, **including the console**. Leaving it in English was a deliberate call I got wrong: because the header and language picker follow the locale, console pages rendered half in one language and half in the other, which reads as unfinished rather than as a choice. Identifiers stay literal — table names, stream ids, column names, event payloads. Those are not prose.

### The system console, and whether it should have been built

Alex asked whether it was all hand-built. It was: ~350 lines, four routes and two server modules. The honest split:

- The **generic table browser duplicates Drizzle Studio** (`pnpm db:studio`, already wired). If this grows, that part should go and Studio should own table browsing.
- The **event log, stream/type filters and the replay button** are not duplicative — no general-purpose database tool knows what an event stream is, or that projections are disposable.

**The table browser also turned out to carry a cost.** Adding authentication put password hashes and live session tokens in the same database as the room board, and a browser that shows any table it finds showed those too. A session token on screen is not a record of a credential, it *is* the credential. Fixed by redacting on column name rather than table name, so a future table with a `token` column is covered the day it is added; `src/server/system/queries.test.ts` is the test that has to keep passing. Worth noting as an argument for the smaller console: the fewer generic surfaces, the fewer of these.

## Money: one ledger, two vocabularies (D-16 / D-17)

Folios, receivables and expenses are three views of one double-entry ledger. Reception never sees
the word "account": it sees a bill, a payment, what a company owes.

- **One stream per account**, and an entry is appended to *every* account it touches. Each account's
  stream is therefore its own statement (`events.ofAccount(folio)` **is** the bill), and the version
  guard is per account — closing a folio cannot race a charge landing on it. The projector upserts
  by entry id, so N appends make one entry.
- **Every command writes two families in one batch**: `folio.charge_posted` (what was sold: quantity,
  description, category) and `ledger.entry_posted` (what moved: two balanced lines). Neither is
  redundant and neither can exist without the other.
- **Balances are never stored.** `balance(account)` sums the lines every time. A cached total is a
  second source of truth that can disagree with the entries under it.
- **Nothing is edited.** A wrong charge is voided: the line stays, struck through, with its reason,
  and a reversing entry carries *today's* business date so yesterday's report does not move.
- **Amounts are VND integers.** A fraction anywhere is a bug, not a rounding question.

Money inputs on screen use `step={1}` for the same reason — `step={1000}` makes 650,000 an invalid
value in a browser and the submit is refused **silently**, which shipped in three forms before the
folio screen found it.

**The money loop, end to end** (built through 2026-09-24): the night roll or the desk puts a charge
on a folio → the desk takes payment → whatever is left can be **transferred to a company
receivable** at check-out → the company pays against one balance, or the owner **writes the debt
off** with a reason → the write-off lands in `expense:writeOff` and reads in the expense totals
beside the money the desk spent on gas. Receivables are grained by **company, not folio**: one
balance is what "what does ABC owe us" has to mean. Expenses use a fixed category list in the
domain — the client's own (đi chợ, chi phí phát sinh, tăng ca buồng phòng, tạm ứng, khác) — with
`writeOff` reserved from hand-posting so a purchase cannot be filed as a bad debt.

## Idempotency: the lookup happens before the rules (D-12 (f))

A command id stops a double click writing twice. It used to do that at the **unique index**, which
is too late: the rules refuse first, and a second click on the payment that settled a debt is a
payment against a settled receivable, a second click on a void is a void of an already-voided
charge. Both are the right answer to a new command and the wrong answer to the same one.

`commit` now looks the command id up **before the first `plan()`** and returns the events the
original attempt wrote. Two consequences that are easy to get wrong:

1. **Every read and every rule runs inside `plan()`, and nothing is minted before it.** Deciding
   outside the thunk puts the rules in front of the lookup, where they can refuse a repeat the
   guard was meant to absorb. It also means a retry after a collision re-reads and re-decides,
   which is the property the whole write path rests on.
2. **Commands derive their answers from the events `commit` returns**, not from ids minted before
   it — otherwise a second click is handed an id that belongs to nothing. `hotel/replay.ts` is the
   three-line helper for reading an answer back out of what was written.

## Forms: nothing refuses in silence, nothing leaks on the way (N10 / N11 / N12)

Every form in the app carries `method="post"` and `noValidate`, and validates in its handler.

- **`noValidate`** because the browser's own refusal is a bubble that vanishes on the next click and
  may never be drawn at all — an empty `required` select or a `step` the amount does not divide by
  produces a button that does nothing, which is indistinguishable from a broken app.
- **`method="post"`** because a submit before React hydrates is handled by the browser alone, and a
  form with no method does a **GET** — every field into the query string and from there into
  Cloudflare's access log. That was a guest's name and phone on /bookings and a password on
  /sign-in (D-20).
- **PII never goes in a URL**, opaque ids are fine: the people search posts its term and keeps
  results in component state rather than `?q=<name>`.

`src/ui/form.tsx` holds the shared piece — `useFormNotice`, `firstProblem`, `isMoney`, `filled` —
so twenty forms say things one way.

## Two tiers, and the guard that holds them together (D-22 / D-8)

**Tier (a) — the log is truth**: Booking, Stay, Ledger. Folded on read, guarded
by `UNIQUE(stream_id, version)`.

**Tier (b) — a mutable row is truth**: Room, Setup items, Guest/Contact, User.
Every write still appends an event to the same log, in the same batch, so
history and projections see one story. No fold, no version guard beyond the row.

Room started as tier (a) and moved. The argument that settled it: a room is a
handful of independent fields with no invariant spanning time, and folding a log
buys you exactly that. Stay does have such invariants — whether it can be
checked out depends on whether it was checked in — so it stays tier (a).

### The bug class this project keeps producing

Three separate findings, one shape. **If a command's guard reads a table another
command writes, both sides must serialise on the same guard — not just the
writer.**

`availability:<hotel>` (ours: `<hotel>/availability:all`) is that guard. It has
no history worth reading; it is a version counter. Anything that changes what
can be sold — holding nights, releasing them, taking a room out of order,
checking in — appends there at an expected version, so two writers collide on
the index and one is told to look again.

Each instance looked correct in isolation and none was visible to a unit test:

- `takeOutOfOrder` not versioning availability → a room withdrawn in the same
  instant it is sold, both batches committing.
- `checkIn` reading the rooms row without versioning → a guest checked into an
  out-of-order room.
- A retry replaying a decision made against state that had moved.

The fix for the last one generalises: **`prepare` is a thunk**, re-run on every
attempt, so a retry re-reads and re-decides rather than re-appending.

### What an integration test is for here

The pure rules cannot prove the thing that matters. Three layers, each for what
the one below it cannot reach:

1. `*/domain.test.ts` — fold and decide, pure and synchronous.
2. `src/server/hotel/scenarios.test.ts` — the **main suite**. Scenarios against
   the real `Hotel` methods the screens call, on an in-memory database. Reads
   like the rule: "refuses a check-in into a room that is out of order", "gives
   the last room to exactly one of them", "early check-out frees the remaining
   nights".
3. `src/server/store/guard.test.ts` and `log.test.ts` — the interleavings a
   scenario cannot express, because they need one command's read held open
   across another's write. The case worth keeping: **a stale availability read
   rejected even where the room calendar would have said yes.** That is the
   only failure the calendar cannot catch alone, and it is the whole reason the
   guard exists.

The test store is the real `SqliteStore` on an in-memory database with the
deployed migrations — deliberately not a hand-written fake. A fake would need
its own `roomFree`, which is a second implementation of the exact query whose
bugs cost this slice; one that is subtly right where SQL is wrong makes the
suite pass while production breaks. The UNIQUE indexes the race tests lean on
are therefore the real indexes.

## One Hotel object, and why the commands left the server functions (D-24)

The commands used to be server functions with the domain inlined. Every test
then either drove the transport or rebuilt the command beside it — and the
rebuilt copy drifts. `occupancy.test.ts` had its own `book()` reimplementing
createBooking, and could have gone on passing against a command that no longer
existed.

`hotel.stays.checkIn({stayId, guests})` is now the application layer. A server
function parses, authenticates, calls the method, maps a rule failure to a
code, and contains no domain logic. Tests call the same method with no
transport in the way.

Three things fell out of it that are worth keeping separately in mind:

- **`Store` is a port, and it is wide on purpose.** It covers the reads —
  `roomFree`, the rooms row, the stays under a booking — because those are what
  the commands decide against. A port that covers the append but not the read
  it was decided under is a hole, not a boundary. A biome rule keeps drizzle
  imports inside `src/server/store`.
- **Three write paths became one.** `handleCommand` and `recordChange` were
  `handleAcross` with fewer options, and each had to get the retry right
  independently. A single stream is now a plan with one entry. The thunk stays:
  it is the whole safety property.
- **Every rule error extends `RuleError`.** The adapter catches the base rather
  than a list of classes. The list version meant a new aggregate's failures
  silently became "something went wrong" to the receptionist who was supposed
  to read them.

## Authentication (D-11 / D-18, built 2026-09-23)

**Better Auth 1.7.5**, self-hosted, username + password. Alex's call; architect accepted under D-21.

Why not the alternatives: Auth.js treats credentials as second-class (JWT-only sessions, no password lifecycle); Lucia is sunset as a library; hosted providers (Clerk, WorkOS) add a third-party hop from a Worker for accounts an owner creates by hand anyway.

**The Workers gotcha, for whoever hits it next.** Better Auth hashes with pure-JS scrypt (`@noble/hashes`), roughly 80ms of CPU. The Workers *free* tier allows 10ms per request, so sign-up and sign-in fail outright there. We are on a paid plan (30s), so the default stands and staging signs in fine. If that ever changes, the fix is a custom `emailAndPassword.password.hash/verify` using `node:crypto.scryptSync` — `nodejs_compat` is already on. Upstream: better-auth#8860, #8456.

### The three decisions inside it

**Usernames, not emails.** Product's D-18 #2: housekeeping is not a user at all, and a small hotel's receptionists may have no work address, so an email requirement would block onboarding. Better Auth still wants a unique email per user, so we mint `<username>@staff.invalid`. `.invalid` is reserved by RFC 2606 and can never resolve — if a stray code path ever tries to mail a user it fails loudly rather than quietly reaching a stranger. A real address, when someone has one, lives in `contactEmail` and carries no auth meaning. There is no email dependency anywhere: no verification, no self-service reset. An owner sets a new password.

**Identity is not event-sourced; roles will be.** Better Auth's four tables (`user`, `session`, `account`, `verification`) are ordinary mutable state. A password hash must never reach an append-only log — there would be no way to take it back. But *who granted whom access, and when* is exactly what an audit trail is for, so staff membership and roles belong in the log as events once the staff aggregate lands. Better Auth's organization plugin is deliberately unused for that reason, and because `hotel_id` is already our own convention.

**Operator access is a flag, not a role.** `/system` is gated on `user.system_operator`, not on `owner`. Alex's framing: system admin, not admin personas. `owner` and `receptionist` are positions inside a hotel; reading the raw log and rebuilding projections is a property of whoever runs the servers, and neither implies the other. It is set by a database write, never by a request (`input: false`), which is the friction we want. It is also the one piece of access deliberately outside the event log — infrastructure, not hotel history.

### What this replaced, and what it bought

The shared console token is gone, and `SYSTEM_CONSOLE_TOKEN` is deleted from the Worker. No credential to rotate, paste into a chat, or leave going stale in a password manager.

`SYSTEM_CONSOLE_FALLBACK` went with it — the flag that made the console open locally and locked when deployed. Convenient, but it was a behavioural difference between dev and prod sitting on exactly the code path where such a difference costs most. Developers make an account like everyone else.

The real gain is the audit trail. `events.actor` had been the literal string `"reception"` since the store was written. It now records `user:<id>` — an id, never a name, because the log is permanent and a name is not (people marry, get corrected, leave). Display names resolve at read time in `server/auth/directory.ts`, so history stays true when a name changes; an id with no matching row renders as the raw id rather than "unknown", because a deleted account should look odd enough to ask about. Events written before this keep saying `"reception"`, which is correct — the log is not rewritten to flatter the new design.

### Shape

One gate, in the root route's `beforeLoad`: everything reads hotel data and there is no public page to fall back to, except `/sign-in` itself. Sign-in is a server function rather than Better Auth's browser client — every other mutation in the app returns `{ ok }` with a code the screen translates, and the auth library stays out of the browser bundle entirely (verified: no `better-auth` in `dist/client`). "No such user" and "wrong password" give the same message, so nobody can enumerate who works at the hotel.

Accounts are created by `scripts/create-user.mjs`, which reads the password from stdin (not a flag, so it stays out of shell history and the process list) and has a `--sql` mode that emits statements for `wrangler d1 execute` against deployed D1.

### Still open

- **No change-password screen.** Changing one today means recreating the account. Lands with the staff screen.
- **No staff aggregate yet**, so no hotel roles and no per-command capabilities — product's D-18 #1 defines them (`owner`, `receptionist`, capability-based). Until then every signed-in user can run every command.
- **No rate limiting** on sign-in.
- Architect's `requireUser()` contract (D-21) wants `{id, username, name, hotelId, role}`; we have the first three. `hotelId` and `role` arrive with the staff aggregate.

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
- Does staging want authentication before it holds anything real? It is a public URL today, with a throwaway database (D-26) — and after a wipe the first-owner bootstrap reopens, so the first person to sign in becomes owner.
- The cron entry for the night roll (D-25) is still deferred: `main` is `@tanstack/react-start/server-entry` and a `scheduled` handler needs a custom entry around it. Pre-go-live.
- `stg.solex.collie.studio` is available for ~$10/mo (Advanced Certificate Manager) if the naming matters. Currently not spent.

## For other WSs

- **product**: the stack imposes no modelling limits at this scale. Per-night rates, routing and the 8-bucket charge enum all fit a plain SQLite schema. The one thing worth knowing is that synchronous projections mean a read model is only as fresh as the write that fed it, which is what the dashboard wants anyway.
- **architect**: D-3 decided the runtime; the open decision is the storage shape above. My recommendation is D1 for log and projections, optimistic concurrency instead of a Durable Object, Hookdeck deferred. That keeps one storage system and keeps Cloudflare out of the dev loop.
