# Walkthrough: solex-qa (UI, built the original film() + player): 2026-09-25

Paper only (opinion, not usage), against the end-state.md + dx.md drafts. Based on filming 9 SoLex journeys plus suite-wide rrweb capture.

**Verdict:** would use it and follow the skill. "Your API is cleaner; mine was a pile of helpers." The real work is seed/state, not recording.

## Findings

**Environment / state: the real work**
- Journeys break each other when run as a set (leftover settings, a shifted business day, oversell). Needs a **DB snapshot/restore per journey**, not "seed before each run" on a shared DB.
- **Several seeds/servers** (e.g. an empty hotel on its own server).
- **`r.offstage(async page => …)`** for unrecorded steps mid-journey.
- **Time:** date logic (checkout next morning) needs a clock hook or offstage.
- **Personas:** switching roles mid-film → named auth states `r.as("desk")`; **dev-bypass auth** first-class (never type a password).
- A runner-owned `start` is right (it relied on Playwright's webServer).

**Recording craft**
- Pacing: highlight before the click, hold captions long enough to read, type key by key, select-all then type (not `fill("")`: a React number box showed "03").
- Flakes: hydration (wait for networkidle after navigation), the URL changes before render, a DB write lock (~20 s), CPU load → generous timeouts, 1 worker.
- **Selectors:** visible text breaks on copy changes and i18n. Offer an **i18n key resolver** (`t("stay.checkIn")`).
- UI churn broke journeys on nearly every landing. Throwaway PR demos dodge it; showcase sets don't.

**Self-check: the biggest gap**
- `summarize` would have caught **none** of ~20 real findings. All were *wrong on screen*: the wrong language, a stale amount, the wrong message, a missing price, a caption claiming something that didn't happen.
- Found by **contact sheets** (ffmpeg tiles, 1 frame every 4 s) and reading every film. → **`demo sheet <file>` as the default self-check**, `frame --step` to zoom.
- Cheap built-in lints: a raw i18n key on screen; wrong-language text.
- Keep "one expect per caption claim" (a false caption became a finding).

**Skill:** additions: "read the contact sheet before publishing"; "if the demo exposes a bug, file it; never script around it silently". Skip: the GIF drag, `slide.diff`. It would skip changes that need time to pass or two roles, unless offstage/`as` exist.

**Reviewer side (Alex):** the visuals get watched (Alex caught Vietnamese labels). Asks that came back: per-journey docs (steps, **what to notice**, seed, length), real persona names, coverage ("do five show the full system?" → nine). **Nobody asked for console/network panels.** The step list + "what to notice" was used more than anything technical.

**Player:** lazy-load each recording; one page with 9 embedded got too big to publish.

**Open DX questions:** 1 full Playwright (a DSL dies at the first native dialog/date/select) · 2 default on for user-visible, with a cheap skip · 3 seed/auth are the main reason to skip → invest in snapshots, personas, clock · 4 `summarize` isn't enough → a sheet every time · 5 link + steps is enough, the GIF is garnish · 6 skill file + AGENTS.md, no MCP · 7 backend = tests + logs unless a webhook round-trip is the point.

Sample journey (N64, guest erase, ~10 lines): offstage checked-out stay with a same-name contact → say "guest asks to be forgotten" → /guests, search, Erase, confirm → expect the notice naming the contact → say → Erase in the notice → expect no dangling notice. `slide.diff` would add nothing.
