# Project: Tracker (fitness/body tracking)

MyFitnessPal-ish but tracking-first, food-second. Personal use.

## Core idea

- **Weight tracking → chart** is the anchor feature
- Progress pics along the way
- Maybe exercise tracking later
- "Food tracking" = quick meal pic, NOT calorie/macro logging (nutrition maybe much later)

## Design principle (the whole point)

**Ease of use / quick action.** No opening a full app and tapping through screens to log one number. Capture must be near-instant. Tracking first; everything else expandable later.

## Open questions

- Capture surface: native iOS app? PWA? iOS Shortcut → API? Widget? Share sheet? (friction requirement basically dictates this choice)
- Apple Health integration — read weight from smart scale / write to Health?
- Where does data live — Go API + SQLite/Postgres on collielab VM?
- Pics storage (VM disk? object storage?) — note prior VM disk-space incident in collielab

## Status

2026-07-10 — idea captured, discussing scope/stack.
