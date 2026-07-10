# Project: fitJournal

Fitness/body tracking — MyFitnessPal-ish but tracking-first, food-second. Personal use.

**Name lore:** successor to weightJournal, a project Alex built ~9 years ago when learning to code (weight-only). fitJournal widens the scope: weight, progress pics, exercise, meal pics. Repo: `hub/alexluong/fitjournal`.

## Core idea

- **Weight tracking → chart** is the anchor feature
- Progress pics along the way
- Maybe exercise tracking later
- "Food tracking" = quick meal pic, NOT calorie/macro logging (nutrition maybe much later)

## Design principle (the whole point)

**Ease of use / quick action.** No opening a full app and tapping through screens to log one number. Capture must be near-instant. Tracking first; everything else expandable later.

## Plan (agreed 2026-07-10)

- **v1: iOS Shortcut → Go API + web chart.** Weekend-scale. Shortcut from widget/Action Button prompts weight / snaps pic → POST to API. Charts in simple web view. Validates the daily habit before investing in an app.
- **v2 (earned, not speculative): SwiftUI app** — only if v1 sticks and friction demands it. Unlocks lock-screen widgets, App Intents, HealthKit. This becomes the iOS-native learning project.

## Open questions

- Apple Health integration — read weight from smart scale / write to Health?
- Pics storage (VM disk? object storage?) — note prior VM disk-space incident in collielab

## Status

2026-07-10 — plan agreed, not started.
