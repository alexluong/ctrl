# 2026-09-23 16:47 — the flow board, and why it moved off Figma

## What exists now

`board/solex-flow.excalidraw` (gitignored) — the WS2 map in visual form. 9 framed sections,
22 screenshots, 3.4 MB. Generated from `tools/excalidraw/flow.json` by `tools/excalidraw/build.py`,
both committed, so it rebuilds anywhere the screenshots exist.

Alex opens it with the VS Code extension `pomdtr.excalidraw-editor`, which saves straight back into
the file — so his edits are readable by me. **Regenerating overwrites his edits.** Rule agreed:
rebuild only when he has saved, and say so. If he starts editing in earnest, stop regenerating and
edit the file in place instead.

## Why not Figma

The FigJam board (`9450fwvpLCLPmAmt4FBsQU`) is frozen mid-update. Figma's **Starter plan caps the
MCP at 20 tool calls per month** — roughly one editing session. It ran out partway through adding
the charges and config sections; those two exist only in Excalidraw. The pending script is parked at
`tools/figjam/add-charges-config.js` in case the board is ever revived on a paid seat.

Lesson for any future visual work: prefer a file format I can write directly (Excalidraw, tldraw)
over an API with a quota. No limits, diffable, lives in the repo, and the user can edit it.

## Two bugs worth remembering

1. **Text clipped in Excalidraw.** I sized text elements by `len(s) * fontSize * 0.55`. All-caps
   headings are ~16% wider than that (363px actual vs 314px stored for "THE TWO HUB SCREENS"), and
   Excalidraw renders to the stored width — so headings lost their last character. Fixed by
   measuring with PIL against the real Helvetica. Mixed-case text was *over*-estimated, which is why
   only the headings broke and nothing else looked wrong.
2. **sips `--cropOffset 0 0` is centre-relative**, despite the man page saying "from top left
   corner". Top-cropping tall screenshots needed PIL instead.

## What Alex settled this round

- Room map + tape chart are **the two most important screens** — every role, different reasons.
  Promoted to a hub section at the top of the board and to home screens in the rebuild.
- The tape chart is a **receptionist tool**, not an owner's report (drag to move/extend a stay).
  Name it for the team: *tape chart* (PMS), *resource timeline* (generic UI pattern).
- **Hourly/day-use stays: not used.** SoLex is daily only. The `Nghỉ giờ` price policies are dead config.
- **Early check-in / late check-out are charged as catalogue items**, not via the booking form's
  +0.3/+0.5/+1 rate multipliers. The multipliers are unused.

## Still open

- Admin login → the item masters (`room`, `room_type`, `product`, `minibar`, `laundry`, `service`,
  `extra_service`, `category`, `package`, `currency`) are all permission-blocked. Nothing about
  room pricing or item pricing can be documented without it. **This is the biggest remaining gap.**
- Step-by-step posting flows can't be observed read-only. Offered Alex an "inferred steps" text
  strip per flow; he didn't take it up, and it isn't needed for the product-logic phase.
