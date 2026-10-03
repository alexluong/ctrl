# T3 Code: quirks and upstream

App use and the upstream repo (`pingdotgg/t3code`). Remote/VM setup: `t3-code-remote.md`. Checked 2026-10-03 against 0.0.44 (app and hookdeck-ws server).

## Known bugs

- **Re-snooze to the same wake time does nothing.** A snoozed thread with activity after its snooze stamp (`snoozedAt`) shows in the inbox again. Snoozing it again with the same preset (same `snoozedUntil`) keeps the old `snoozedAt`, so it stays visible; every retry "succeeds" server-side. Workaround: pick a different wake time (another preset or Custom), or unsnooze then snooze. Upstream: issue #14298, fix PR #14887 (open, not in 0.0.45). Seen 2026-10-03 on a hookdeck-ws thread; looked like a cross-environment problem, wasn't.
- Debug path: server state is `~/.t3/userdata/state.sqlite` (`orchestration_events`, `projection_threads.snoozed_until/snoozed_at`); no `sqlite3` on the VMs, use `python3`. Command traces: `~/.t3/userdata/logs/server.trace.ndjson`.

## Snooze presets

Hardcoded in `packages/client-runtime/src/state/threadSettled.ts` (`resolveSnoozePresets`): +1h, +3h, this evening 18:00, tomorrow 09:00, next Monday 09:00 (local time). No setting. Requests already open: Ideas #11399 (configurable hours/offsets), #13881 (save custom durations).

## Filing upstream

- Bugs: issues (template `bug_report.yml`; blank issues off). Feature requests: Discussions → Ideas only.
- Search first; Julius (core, often via a Grok reply "on behalf of Julius") closes duplicates fast and points to the original: upvote + comment there instead.
- No feature PR without a maintainer approving direction in the discussion (`CONTRIBUTING.md`). Small obvious bug fixes can go straight to a PR with evidence. Maintainers: `.github/TRIAGE_EXEMPTIONS.td`.
- Post shape people use (from the removed feature-request template): Problem → Proposal → Scope → Alternatives / "Relationship to #X" (why it isn't a duplicate) → optional "Prepared by <model> on behalf of @user" line. Neither the sections nor the disclosure is documented; CONTRIBUTING says they don't judge whether an agent wrote it.
