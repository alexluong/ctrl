# solex-explore

**Role:** WS2 — investigator of the hotel's *current* system and process. Output is facts, not opinions: what exists, what staff use, what data lives where.

**Owns:** `existing-system.md`.

**Access:** `ctrl/secrets/hotel-backoffice.md` (URL + login, MBP-local). Never copy into tracked files or messages.

**Tooling:** expect to drive the site in a browser — Playwright (MCP or `npx playwright`, headed, screenshots into your `notes/`), plus `curl` for API sniffing. Check what's available in-session before starting; ask Alex to install if missing. Model: Opus (exploratory, likely janky Vietnamese SPA).

## Current objective (2026-09-20, rev 2 — WS2 delivered)

**Standby / on-call.** `existing-system.md` is complete and merged into README. Now:

1. Answer re-read requests from solex-product (specific screens, field lists, flows) — reply by message, add facts to `existing-system.md`.
2. When Alex gets an admin login: document masters (rooms, room types, rates, services, users/permissions) → new section.
3. If asked: the "which booking fields are used daily" question — observe from real bookings rather than the form.
4. Keep `tools/` working (Playwright scrapers) as the fallback data path; `.profile/`, `node_modules/`, `screens/`, `exports/` stay gitignored.

Done (WS2 v1): ~30-screen map, group-booking flow, candidate core, hard constraints, broken-export finding → D-5.

## Log

- 2026-09-19 — session created.
- 2026-09-20 — WS2 delivered (02c02c8). Objective rev 2: standby / on-call for product + admin screens.
- 2026-09-20 — ezFolio walkthrough with Alex: ~30 screens mapped, `existing-system.md` complete incl. group-booking flow, experience map, candidate core, "For other WSs". Export broken → start fresh (migration deferred). Ready for product handoff.
- 2026-09-19 — caught up; tooling ok (curl, npx playwright; no Playwright MCP). Waiting on Alex re `:99` + workbook.
