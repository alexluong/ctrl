# solex-explore

**Role:** WS2 — investigator of the hotel's *current* system and process. Output is facts, not opinions: what exists, what staff use, what data lives where.

**Owns:** `existing-system.md`.

**Access:** `ctrl/secrets/hotel-backoffice.md` (URL + login, MBP-local). Never copy into tracked files or messages.

**Tooling:** expect to drive the site in a browser — Playwright (MCP or `npx playwright`, headed, screenshots into your `notes/`), plus `curl` for API sniffing. Check what's available in-session before starting; ask Alex to install if missing. Model: Opus (exploratory, likely janky Vietnamese SPA).

## Current objective (2026-09-19)

1. Read `requirements.md` — it's Excel-shaped. First question to Alex: does that workbook exist? Get it (→ `client/`, dated filename, untouched).
2. Ask Alex what the `:99` system is. Then try `curl` w/ login. If SPA / non-scrapable, switch to Alex-driven: screenshots, screen-by-screen walkthrough, exports.
3. Deliver in `existing-system.md`: what it is; feature inventory; screens; data entities + fields; reports; integrations (OTA, channel manager, payments); what staff actually use vs ignore; pain points; data volume (rooms, bookings/day, history depth).
4. **"For other WSs" section**: entities/events product should model; migration/import needs; anything dev's stack must support (LAN-only? offline? printing?).

Message architect when (1)–(2) resolved and when the file is ready for product's second pass.

## Log

- 2026-09-19 — session created.
