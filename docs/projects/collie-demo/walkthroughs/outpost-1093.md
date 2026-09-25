# Walkthrough: outpost#1093 (backend, no UI): 2026-09-25

Paper only (opinion, not usage), against end-state.md + dx.md drafts f94ce70.

**PR:** publish-queue failure handling in Outpost (Go). Invalid messages go to the customer's RabbitMQ dead-letter exchange; optional `PUBLISH_MAX_REDELIVERIES` cap. Manual QA: 4 scenarios (DLX yes/no, cap on/off, Redis paused mid-run). The evidence was queue depths, DLQ contents with the x-death reason, log lines and Redis keys, collected with a 90-line python helper and a scenario table.

**Verdict:** "as written I'd skip it". It wants the runner, the state probes and the text summary, not the replay.

## Their sketch
```
scenario "cap=3, queue has DLX" env {PUBLISH_MAX_REDELIVERIES: 3}
  amqp.publish("not json", {id:"A2"});  until(dlq.count == 1);  say("bad JSON rejected on first failure")
  amqp.publish({topic:"no.such.topic"}, {id:"A5"});  until(dlq.count == 2);  expect(logs).toContain("after 3 redeliveries")
  fault.pause("redis");  amqp.publish(valid, {id:"C1"});  wait(20s);  expect(dlq.count == 2);  fault.resume("redis");  until(receiver.got("C1"))
```

## Findings
1. **Reviewer wants** a scenario × input → outcome table, proof that nothing is dropped during an outage, and the actual log lines. Replay/captions/browser panels show none of that.
2. **`summarize` text is the most valuable artifact** for backend PRs: make that the product and the player optional.
3. **Missing primitives:** generic steps `r.step(name, fn)`; non-HTTP stimuli (AMQP publish); **state probes** (queue depth, DB row, Redis key); a built-in **webhook receiver** (`r.receiver()`, which is our lab `catcher`); **fault injection** (pause/stop a service); asserting on logs; an **env matrix** (scenarios with different env → clean restart).
4. **Setup is the blocker.** A single `start` doesn't fit: it needs RabbitMQ + Postgres (compose), a throwaway Redis, a migrate before start, a tenant/destination created over the API, and a receiver. Needs `services` (compose), a `setup` hook, per-scenario env + clean restart, and teardown. It hit port-in-use between restarts (and pkill was denied), so the runner owning the process lifecycle matters. It suggested `demo init` generate the config from the existing compose/test harness.
5. **Skill trigger:** it technically qualified ("API behaviour, a webhook") but the tool doesn't fit, so it would skip and feel it broke the rule. It would skip when: setup takes >10 min, non-UI evidence would have to be squeezed into a browser, or the PR is backend-only. It wants the default **off for backend-only, on for UI**.
6. **Too heavy for backend:** slides, GIF, human drag-in. **Link + step list is enough.**
7. **Got right:** the 3-attempt cap; don't publish with unexplained errors.
8. TS is fine; full Playwright is irrelevant for backend; arbitrary async steps are what matter.

## Takeaways (collie-demo, pending Alex)
- Two different products hide in one: **UI demo** (replay-first) vs **backend evidence** (scenario matrix + probes + text report, replay optional). The lab's `http` stage, `catcher` and `dbWatch` are the start of the second; the framing "stage = pluggable" holds, but the backend output wants a **table/report view**, not a card timeline.
- The environment side (services, setup, env matrix, restarts, teardown) is much bigger than "`start` command". It's close to what test harnesses already do, so reuse (compose/testcontainers) rather than reinvent. It stretches the "setup is out of scope" line in engineering.md.
- The skill needs a better trigger rule than "user-visible".
