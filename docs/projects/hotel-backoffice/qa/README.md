# SoLex QA — how the plan works

Owner: `solex-qa` (session live from 2026-09-24; worktree `~/git/hub/alexluong/solex-qa`). Findings history before this dir existed: `../team/qa.md`.

## Files

- `cases.md` — the test cases, one table per slice. Columns: **ID** (`S<slice>-<n>`) · **rule** (product.md §10 row / §11 command / D-n) · **steps** · **expected** · **automated by** (`scenario:<test name>` in `src/server/**/*.test.ts`, `e2e:<spec>` in `solex/e2e/`, or `manual`) · **last run** (`<short sha> pass|fail`).
- `runs.md` — newest first: date, commit, staging version, cases run, results, findings filed (link to dev message / issue), blocking Y/N.
- Findings that change a rule go to architect → `team/decisions.md` or product → `product.md`; the case is updated to the new expectation, never left contradicting the spec.

## Three tiers

1. **Scenarios** (`solex/src/server/hotel/*.test.ts`, D-24) are the automated truth for domain rules. QA maps every rule to a scenario; a rule with no scenario is a finding for dev.
2. **E2E** (`solex/e2e/`, Playwright against local `pnpm dev` with the stub user) for what scenarios cannot see: a submit that silently does nothing, a control disabled for a rule, a refusal not rendered, navigation after a command, prefill from Setup.
3. **Manual** only for staging smoke after deploy and Alex's Vietnamese/wording pass.

## Local login (no passwords)

Dev-only bypass, unreachable on Cloudflare (see D-11 / stack.md): in your worktree `.env` add `SOLEX_DEV_USER=qa` and seed the row:

```
sqlite3 data/solex.db "insert into user (id,name,email,email_verified,username,display_username,system_operator,created_at,updated_at) values ('qa-local','QA','qa@local.invalid',1,'qa','qa',1,strftime('%s','now')*1000,strftime('%s','now')*1000)"
```

An empty hotel treats a system operator as owner (first-owner bootstrap, D-11); add a staff row through Thiết lập to exit that mode when testing receptionist vs owner. Never type a password; never use staging credentials.

## Finding numbers

`N<n>` ids are minted here, by solex-qa only (architect ruling 2026-09-24); others describe a finding and ask for a number. Never reuse. **Next free: N27.** (N12 = guest search in URL, N13 = mise re-applies `.env` over exported env.)

## Blocking vs non-blocking

Blocking = violates an accepted decision (`team/decisions.md`), the spec (`product.md` §10–12) or data safety (PII in a payload, unredacted console column, money not one batch, missing availability versioning). Dev fixes before the next landing. Everything else: dev's call when.
