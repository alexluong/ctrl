# FigJam board scripts

Board: https://www.figma.com/board/9450fwvpLCLPmAmt4FBsQU (file key `9450fwvpLCLPmAmt4FBsQU`).

Scripts here are bodies for the Figma MCP `use_figma` tool (Plugin API, top-level await, `return`
for output). They are kept so a board change survives a rate limit or a new session.

## Pending: `add-charges-config.js` (written 2026-09-21, not yet applied)

Blocked by the Figma MCP Starter-plan call limit. To apply:

1. `use_figma` with the contents of `add-charges-config.js`. It returns `frames` — a map of
   frame name → new node id for five empty frames.
2. `upload_assets` with `count: 5` and `nodeIds` set to those ids in this order, then POST each
   PNG from `../../screens/` to its submit URL (`curl -F file=@<name>.png <url>`):
   `fd-room-detail-panel` · `fd-laundry-invoice` · `rpt-fd-revenue` · `sys-charge-config` ·
   `sys-booking-rules`.
3. `get_screenshot` on the page to check it.

Three calls in total. It adds a RECEPTIONIST · 3b · CHARGES section and an ADMIN · CONFIG
section, restacks every section, moves the findings column clear of the widest section, and
rewrites the early/late sticky (`11:75`) to say they're charged as catalogue items.
