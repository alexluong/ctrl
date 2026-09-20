# tools — ezHotel exploration scripts (WS2)

Read-only walkthrough tooling for the hotel's current PMS. Owner: solex-explore.

- `chrome.sh` — launch a visible Chrome with a debug port + its own profile (`.profile/`, untracked).
- `lib.mjs` — reads creds from `ctrl/secrets/hotel-backoffice.md`, connects over CDP, redacts host/user/pass from all output, **aborts every non-GET request** (read-only guard).
- `login.mjs` — log in.
- `visit.mjs <slug> '<query>'` — GET one page, screenshot to `../screens/<slug>.png`, print title/path/text/tables/forms/links.

Setup: `npm i` (playwright-core only). Screenshots and profile are gitignored — they contain guest PII.
