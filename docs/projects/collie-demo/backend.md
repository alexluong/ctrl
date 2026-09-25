# Collie Demo: backend demos (evidence runs)

**DRAFT, pending Alex's review (date 2026-09-25).** Paper research + a design proposal. Inputs: [walkthroughs/outpost-1093.md](walkthroughs/outpost-1093.md) (the backend "I'd skip it"), [walkthroughs/solex-qa.md](walkthroughs/solex-qa.md), [dx.md](dx.md), [engineering.md](engineering.md), lab `~/code/replay-lab` (`src/backend.js`, `run.js`, `journeys/webhooks.js`). Names (`demo`, `@collie/demo`, `.demo`) are placeholders.

## TL;DR

- For backend PRs the product is a **text report** (case × input → expected / actual, with the evidence inline), not a replay. The player is the "click to see why" layer under it.
- Same `.demo` file, same journey, same clock. Add two streams (`cases.json`, `probes.json`) and one command (`demo report --md`).
- Worth it for **async / side-effect PRs**: webhooks, queue workers, retries/failure handling. Not worth it for plain CRUD endpoints (tests + one curl) or perf (benchmarks). Migrations: maybe (before/after row counts).
- Fits "tool, not framework, env not ours": **probes** = read-only functions or shell commands the author writes; the **receiver** (lab `catcher`) is built in; **log capture** from any command (`docker compose logs -f`); **variants** = N runs of the same journey, each wrapped by the project's own `reset`/`start` commands. **Fault injection stays out**: it's just a shell step the journey runs (`docker pause redis`), recorded as a step.
- Nobody in prior art combines "narrated cases + side-effect probes + one PR-pasteable summary + a drill-down trace". Hurl/Bruno/Step CI stop at HTTP asserts; Venom has AMQP/Redis but outputs xUnit; Tracetest has trace assertions but needs its own server. That's the gap, and it's narrow.
- Default: **opt-in** for backend-only PRs (the skill suggests it only when the change has an async side effect the reviewer can't see from tests).

## 1. What a backend reviewer wants, per PR type

| PR type | Reviewer's question | Best evidence | Demo shape? |
|---|---|---|---|
| New API endpoint | "What does it accept/return; errors right?" | tests + an example req/res per case (Hurl-like) | **Report only**, small. A demo adds little over tests. |
| Webhook / outbound delivery | "Does it arrive, signed, retried, dead-lettered?" | receiver hits per attempt, timing, final state | **Yes.** Timing + outbound payloads are invisible in tests. The lab's best case already. |
| Queue / async worker | "Message in → what happens, where does it end up?" | queue depths, DLQ contents, DB rows, logs, before/after each case | **Yes: report + probes.** Timeline optional. |
| Failure handling / retries | "What happens when X is down; is anything lost?" | case matrix (config × input × fault) → outcome; "nothing dropped" proof | **Yes, this is outpost#1093.** Matrix report is the core. |
| Data migration | "Did every row move right; reversible?" | row counts / sample diffs before→after, down-migration run | **Report**, probes before/after. No timeline. (Lean; unverified with a reviewer.) |
| Performance | "How much faster, under what load?" | benchmark numbers vs base, flame graphs | **No.** Use benchmark tools; at most paste numbers. |

Rule of thumb: a demo earns its place when **the effect is async, external, or spread over time** (something a unit test asserts but a reviewer can't *see*). Narration (`say`) still matters, but as the **case label + "what to notice"**, not captions over a replay (matches solex-qa: step list + "what to notice" was the most-used part).

## 2. Prior art

| Tool | Produces | Missing for "show a reviewer my backend change" |
|---|---|---|
| [Hurl](https://hurl.dev/docs/running-tests.html) | plain-text HTTP files; captures + asserts; HTML / JUnit / TAP reports | HTTP only; no side effects (queues, DB, inbound webhooks); no narration; no PR summary |
| [Bruno CLI](https://docs.usebruno.com/bru-cli/builtInReporters) / Newman | collection runs; JSON / JUnit / HTML reporters | same: HTTP req/res + asserts only |
| [Step CI](https://github.com/stepci/stepci) | YAML workflows (REST/GraphQL/gRPC/SOAP), pass/fail console summary | no async/side-effect view; CI-shaped output |
| [Venom (OVH)](https://github.com/ovh/venom) | YAML suites with executors incl. **AMQP, RabbitMQ, Redis**, SQL; xUnit / JSON / YAML / TAP | closest to outpost's needs, but output is a test result, not a readable case table; no timeline/trace |
| [Tracetest](https://docs.tracetest.io/concepts/what-is-trace-based-testing) | trigger + **assertions on OTel spans** via selectors; each test has its trace attached | needs its server + a trace backend; spans only (no DB/queue probes); not narrated |
| [Keploy](https://keploy.io/record-replay-testing) | eBPF capture of real traffic (HTTP, Postgres, Redis, Kafka…) → tests + mocks, replayed | regression tool; replays with mocks, so it proves "same as before", not "what the change does" |
| Testcontainers | throwaway real deps from test code; Toxiproxy module for faults (unverified which langs) | env tooling, not evidence. It's what the project's own harness would use; we shouldn't reinvent it |
| [Runme](https://docs.runme.dev/getting-started/cli/) / Jupyter-style API docs | markdown with runnable cells + their outputs | closest to "narrated evidence", but outputs are frozen text per cell; no shared clock, no async wait/probe, no trace |
| asciinema | `.cast`: NDJSON `[t, "o", data]` on one clock | a precedent for our format and a future `terminal` stage; no structure (steps, asserts) |
| Allure | steps + per-step attachments + history; HTML report | nearest "evidence report"; test-framework-bound; no backend capture; heavy for a PR |
| [Schemathesis](https://schemathesis.readthedocs.io/) | property-based API fuzzing; **curl reproducer per failure**; JUnit / VCR / HAR / Allure | great failure evidence, but it generates cases; not a story of a feature |

Takeaways to borrow: Hurl's plain-text readability; Schemathesis's "copy-paste reproducer per finding"; Venom's broker/Redis executors (as probe *examples*, not built-ins); Tracetest's "trace attached to every case".

## 3. Outpost asks vs "tool, not framework, env not ours"

| Ask | Verdict | Shape |
|---|---|---|
| Generic steps `r.step(name, fn)` | **In** | Already "arbitrary async code"; name it `r.case(title, fn)` for backend (a step with a verdict). |
| Non-HTTP stimuli (AMQP publish) | **In, as user code** | The journey imports the project's own client (`amqplib`, `redis`). We record nothing magic; `r.note(obj)` logs what was sent. |
| State probes (queue depth, DB row, Redis key) | **In, pluggable, read-only** | `r.probe(name, fn \| {sh})`. Sampled at every case start/end and inside `until`. Values land in `probes.json`. A few recipes in docs (rabbitmq mgmt API, `redis-cli`, `psql -c`), no bundled drivers. |
| Webhook receiver | **In, built in** | The lab `catcher`, public as `r.receiver()`. |
| Log assertions | **In** | Logs from the child we started, **or any command** (`capture.logs: "docker compose logs -f --since 0s api"`). `r.expectLog(/after 3 redeliveries/)` checks the window since the case started. |
| Env matrix | **In, thin** | `variants` = N runs of one journey. Per variant the runner only calls the project's **`reset`** then **`start`** with extra env, and kills what it started. No compose/orchestration logic of ours. |
| Fault injection | **Out** | A shell step in the journey (`await r.sh("docker pause redis")`) is recorded as a step like any other. The docs show the pattern; we ship no fault API. |
| Services/setup/teardown | **Out** | Project's `start`/`reset` commands (docker compose, make targets). `demo init` may *suggest* them from an existing compose file (cheap, optional). |

Port-in-use between restarts (outpost finding 4): the runner owns the process group it started and waits for the port to free before the next variant. That's lifecycle of *our* child, not env setup.

## 4. Proposed artifact: the backend evidence run

### Journey (outpost scenario)

```ts
import { demo } from "@collie/demo";
import amqp from "amqplib";                                   // the project's own client

export const stage = "http";
export const variants = {                                     // N runs; reset+start per variant
  "DLX, cap=3":   { PUBLISH_MAX_REDELIVERIES: "3" },
  "DLX, no cap":  { PUBLISH_MAX_REDELIVERIES: "" },
  "no DLX, cap=3":{ PUBLISH_MAX_REDELIVERIES: "3", DEMO_NO_DLX: "1" }, // the reset script reads it
};

export default demo("Publish-queue failure handling", async (r) => {
  const ch = await (await amqp.connect(process.env.AMQP_URL)).createChannel();
  const dlq = r.probe("dlq.depth", { sh: "rabbitmqctl -q list_queues name messages | awk '$1==\"publish.dlq\"{print $2}'" });
  r.probe("redis.retry.A5", { sh: "redis-cli GET retry:A5" });
  const hook = r.receiver();                                  // tenant destination points here (set up in `reset`)

  await r.case("Bad JSON → DLQ on first failure", async () => {
    ch.publish("publish", "", Buffer.from("not json"), { messageId: "A2" });
    await r.until(() => dlq.value == 1);
    await r.expectLog(/A2 .*rejected.*invalid json/i);
  });
  await r.case("Unknown topic → DLQ after 3 redeliveries", async () => {
    ch.publish("publish", "", Buffer.from(JSON.stringify({ topic: "no.such.topic" })), { messageId: "A5" });
    await r.until(() => dlq.value == 2, { timeout: 30_000 });
    await r.expectLog(/A5 .*after 3 redeliveries/);
  }, { only: ["DLX, cap=3"] });
  await r.case("Redis paused: valid message held, not dropped", async () => {
    await r.sh("docker compose pause redis");                 // fault = a recorded shell step, not our API
    ch.publish("publish", "", Buffer.from(JSON.stringify(valid)), { messageId: "C1" });
    await r.wait(20_000);
    r.expect(dlq.value).toBe(dlq.at("case.start"));           // nothing dead-lettered
    await r.sh("docker compose unpause redis");
    await r.until(() => hook.got({ id: "C1" }));
  });
});
```

### CLI output (`demo run outpost-failures.demo.ts --logs`)

```
demo run · 3 variants · reset: make demo-reset · start: make demo-up · logs: docker compose logs -f api
DLX, cap=3     ✓ Bad JSON → DLQ first failure      1.2s   dlq.depth 0→1   log ✓
               ✓ Unknown topic → DLQ after 3        9.8s   dlq.depth 1→2   log ✓  redis.retry.A5 3
               ✓ Redis paused: held, not dropped    24.1s  dlq.depth 2→2   receiver C1 ✓ (+3.1s after unpause)
DLX, no cap    ✓ ✓ –(only)  ✓
no DLX, cap=3  ✓ Bad JSON                        …  dlq n/a (no DLX): message nacked, log "dropped: no dlx" ⚠
               ✓ Redis paused                     …
9 cases: 8 ✓ 0 ✗ 1 ⚠ · 3 runs · 1m52s · out/outpost-failures.demo (41 KB)
next: demo report out/outpost-failures.demo --md
```

`⚠` = an expectation passed but a probe/log shows something the author should explain (e.g. "dropped" in logs). Explain or ask (same rule as UI bugs in dx.md).

### What the PR gets (`demo report --md`)

```md
### Demo: publish-queue failure handling  ·  [open ▶](https://demo.collie.studio/d/abc123)
| Case | DLX, cap=3 | DLX, no cap | no DLX, cap=3 |
|---|---|---|---|
| Bad JSON → DLQ on first failure | ✓ dlq 0→1 | ✓ dlq 0→1 | ⚠ nacked, dropped (no DLX) |
| Unknown topic → DLQ after 3 redeliveries | ✓ dlq 1→2, retry:A5=3 | – | – |
| Redis paused 20s: held, not dropped | ✓ dlq 2→2, delivered +3.1s after unpause | ✓ | ✓ |

<details><summary>Evidence (log lines, DLQ headers)</summary>

`api | A5 publish failed after 3 redeliveries, dead-lettering (topic=no.such.topic)`
`x-death: [{reason: rejected, count: 1, queue: publish}]`
</details>
```

Short enough to paste; each cell links to that moment in the player (`#v=1&t=12.4`). This is the **main artifact**; `demo publish` prints it.

### What the player shows (backend view)

- Top: **the same case × variant table**, clickable.
- Click a cell → that variant's **timeline**: case banners, stimulus cards (`sh`, publish notes), **probe sparklines** (dlq.depth steps 0→1→2; flat during the Redis pause is the "nothing dropped" proof), receiver hits, log lines filtered to the case window, and the OTel waterfall when `--otel` is on.
- No rrweb pane, no slides. Reuses the lab's `http` stage cards + waterfall.

### Format additions (v0 → v0.1)

| File | Shape |
|---|---|
| `cases.json` | `{variant, case, t, end, status:"pass"\|"fail"\|"warn"\|"skip", expects:[{text, ok, t}], note?}` |
| `probes.json` | `{t, variant, name, value}` (sampled at case edges + during `until`) |
| `manifest.variants` | `[{name, env (redacted), startedAt}]`; streams gain a `variant` field |

## 5. Lab spike (≤1 day, collie-lab, in `~/code/replay-lab`)

Goal: find out if the **report** is useful to a backend reviewer, not polish the player.

1. (2h) `r.case`, `r.probe` (fn + `{sh}`), `r.expectLog`, `r.sh` in `src/recorder.js`; `cases.json` + `probes.json` via `bundle.js`.
2. (1h) `variants` in `run.js`: loop over env, kill child + wait for port, fresh `DB_PATH` (= a trivial `reset`), restart. The app's webhook `MAX_ATTEMPTS` and backoff become env vars.
3. (1h) Rewrite `journeys/webhooks.js` as 3 cases × 2 variants (`MAX_ATTEMPTS=4` vs `2`); probes: `deliveries` row count by status (SQLite), `receiver.hits`. Fault: `r.respond([503…])` stands in for a paused dependency (no docker in the lab).
4. (1h) `report.js --md` → the table + evidence block above. Print it at the end of `run.js`.
5. (1h, optional) Player: case table on top of the `http` stage, cell → seek.
6. (1h) **Test:** hand the markdown (no player) to a fresh backend-minded agent as a PR reviewer, and to Alex. Ask: "would you approve on this? what's missing?" Compare with the outpost python-helper output (the bar to beat).

Success = the reviewer answers the PR's questions from the table alone and opens the player only for "why". Fail = they'd rather read the test file; then backend demos stay a parked opt-in and we stop here.

## Open

- Probe sampling: case edges + `until` only, or continuous (like `dbWatch`)? Continuous gives sparklines but is noisier.
- `variants` in the journey vs the config vs CLI `--variant k=v`? Journey keeps it next to the cases.
- Should `demo report --md` exist without a `.demo` (pure text mode, no player) for teams that won't use the player at all?

## Reality check: hookdeck/outpost PRs (2026-09-25)

Alex asked whether we're overfitting to outpost#1093. Read the ~15 non-bot merged PRs in hookdeck/outpost (#1042–#1087; e.g. #1087 RabbitMQ resubscribe, #1086 publish proxy, #1079 latency metrics, #1069 compat signature, #1063 suppression race, #1050 topic filter before suppression).
- **The descriptions are already strong:** behaviour, scope, config examples, the tests that prove it, benchmark tables. The evidence is **integration/e2e tests**, described in prose.
- **A time-based demo would add little to most of them.** Reconnect and proxy are proven by tests; metrics by benchmark tables; a race (#1063) can't be reproduced on demand anyway.
- **Where there's a real gap:**
  1. **Flow explanations are written as prose or ASCII** (#1063's numbered 5-step race across replicas + Redis; #1050's `suppression → emitter → topic filter`). A generated **sequence diagram** (static, from spans or hand-written Mermaid) would read faster. It's an explanation, not a recording.
  2. **"Show the real output"**: e.g. #1069 could attach the actual delivered request with both signature headers, captured by the catcher. A small evidence snippet, not a replay.
- **Takeaway:** backend PRs don't need the same level of demo. At most: diagrams + captured real requests/logs as evidence snippets. Opt-in; not the core of the tool. Pending Alex.

## Prototype: graph-stage demo of outpost#1087 (2026-09-25)

Artifact (private): https://claude.ai/artifact/6NEDyB41hMeFEQhR1GwZv5. It's a real recording, not a mock-up.
- **Setup:** Outpost built from source at edd46a32 (before) and 68d6214f (#1087), with throwaway RabbitMQ/Redis/Postgres containers (compose project `collie-od`, torn down afterwards). The runner owns the Outpost process and adds a local webhook receiver, a RabbitMQ management-API probe (200 ms), Outpost's JSON logs, and the fault `rabbitmqctl close_all_connections`. Scratch code (not kept in a repo): `runner.mjs` + `build.mjs` + `template.html`.
- **Result:** before, the delivery consumer goes to 0, there are 16× "channel/connection is not open", and orders #2/#3 sit in the queue and are never delivered (✗✗). After: 2 warnings, then resubscribed, and all 3 orders delivered within 5 s (✓✓✓).
- **Player:** nodes (app → Outpost API → RabbitMQ → delivery worker → webhook) with live state, stepped ◀ ▶ through actions (no autoplay), a detail panel per action (request/response, headers, log repeats, probe before→after), a before/after toggle, and a generated text tree for the PR.
- **Learned:**
  - RabbitMQ management stats lag a few seconds, so probe-derived state can trail reality. Don't color on it alone.
  - Collapsing repeated warnings into one event (×N) is essential.
  - Outpost's API port is `API_PORT`.
  - The runner must always kill its child process, or orphans hold ports.
