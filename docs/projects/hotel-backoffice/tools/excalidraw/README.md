# Excalidraw boards

Replaces the FigJam board as the working canvas (Figma MCP's Starter plan caps at 20 calls a
month). File-based, so there is no API and no limit.

- `build.py <spec.json> <out.excalidraw>` — generates a board from a spec + `../../screens/*.png`.
  Screenshots are resized to 1000 px JPEGs; anything taller than `maxImageHeight` is cropped from
  the top and captioned as such. Needs Python 3 + Pillow.
- `test.json` — the 4-screen test board (hub screens + walk-in).
- Output goes to `../../board/`, which is **gitignored**: boards embed the screenshots, and those
  contain live guest data. Only specs and the script are committed.

Open with the VS Code extension `pomdtr.excalidraw-editor` so edits save straight to the file and
Claude can read them back. excalidraw.com also works but loads a copy — changes then have to be
saved back over the file by hand.

Collision rule: Claude regenerates a board only when Alex has saved, and says so when it does.
