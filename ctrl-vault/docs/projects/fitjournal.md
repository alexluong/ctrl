# Project: fitJournal

Personal fitness/body tracking — tracking-first, food-second. The photo timeline is
the product; weight is the spine it hangs on. Capture must be near-instant —
that's the whole point. Personal use.

**Name lore:** successor to weightJournal, a project Alex built ~9 years ago when learning to code (weight-only). fitJournal widens the scope: weight, progress pics, exercise, meal pics. Repo: `hub/alexluong/fitjournal` (code-only; all notes live in this doc).

**Status:** idea/design phase, nothing built. (2026-07-10)

**Plan history:** morning 2026-07-10 plan was "v1: iOS Shortcut → Go API + web chart, v2: SwiftUI app if it sticks" — superseded the same day by the local-first SwiftUI / no-backend stance below (HealthKit lock-in makes local-first the natural v1; no server to run or breach).

## Design principle (the whole point)

**Ease of use / quick action.** No opening a full app and tapping through screens to log one number. Tracking first; everything else expandable later. No gamification, streaks, goals, or nudges — habit is assumed; minimizing capture cost is the product.

## Architecture stance

- **Local-first SwiftUI app. No backend.** SwiftData on device, iCloud/CloudKit
  for sync/backup. No Go API, no VM, no object storage.
- **HealthKit is the source of truth for applicable numerics** — anything
  Health has a sample type for (weight, steps, workouts, nutrition). We keep
  no weight table; charts query Health live (`HKStatisticsCollectionQuery`
  buckets for us). Health syncs these across devices via iCloud — Apple's
  problem. Any chart cache is explicitly a cache, rebuildable from Health,
  never truth. Numerics Health can't represent (estimate ranges/confidence,
  photo metadata) stay app-owned.
- **fitJournal = visualization layer + photo memory over Health.** Owned
  schema is only what Health can't hold:
  - `ProgressPhoto` (timestamp, image)
  - `Meal` (timestamp) → `MealPhoto[]` (+ later: macro estimate fields)
- HealthKit is on-device only, which locks in local-first anyway.
- Charts: Swift Charts, in-app.

## Privacy / data plane

The advertisable claim: **no accounts, no sign-up, no servers of ours,
nothing to breach — your data lives on your device and your iCloud.**
Structurally true, not policy-true:

- **Photos**: app's sandboxed container (SwiftData blobs with
  `.allowsExternalStorage`), encrypted at rest via iOS Data Protection
  (`NSFileProtectionComplete`). No file storage to provide.
- **Sync/backup**: CloudKit **private database** — data lives in the user's
  iCloud, against their quota; developer structurally cannot read it. With
  Advanced Data Protection it's E2E-encrypted past Apple too. SwiftData
  CloudKit mirroring gives this nearly free.
- **Numerics**: HealthKit — on-device, permission-gated, synced via user's
  iCloud.
- **The one asterisk: meal parsing.** The Claude API call is the single place
  data leaves the user's plane. Strictly opt-in, clearly labeled ("sends this
  photo to Anthropic"), possibly on-demand-only. Watch Apple's on-device
  Foundation Models as a path to deleting the asterisk.

## Capture surface (App Intents)

Declared in code via `AppShortcutsProvider` — auto-registered on install, no
shortcut assembly. Placement (Action Button, lock-screen widget) is one-time
user setup, unavoidable iOS UX.

1. **Log Weight** — background intent, number param. System dialog floats over
   lock screen; app never opens. Haptic + "80.4 ✓". Optional "add progress
   pic?" follow-up.
2. **Progress Pic** — launch straight to viewfinder, snap, done.
3. **Snap Meal** — launch to viewfinder, multi-shot: snap → thumbnail stacks →
   snap → Done. One session = one meal, N photos.
4. **Open Journal** — deep-link to chart. (Action Button gets Snap Meal —
   highest frequency.)

## Data domains

Split is semantic, not by media type:

- **Body tracking** — weight + progress pics. Sparse, trend-oriented.
  Weight lives in HealthKit; progress pics in-app, correlated by time.
- **Meals** — event with N photos. Bursty, context-oriented. Fully app-owned.
  Photos are an attribute of a meal, not an entity.
- **Activity** (read-only from HealthKit) — steps, workouts. We never write
  these; Watch/other apps do.

Schema TBD — deliberately deferred until the journal view design settles.

## HealthKit integration

| Type | Direction | Use |
|---|---|---|
| Weight | write + read | We write weigh-ins; chart reads Health as source of truth (also picks up scale-app syncs). Scale app becomes irrelevant. |
| Steps | read | Hourly buckets (`HKStatisticsCollectionQuery`) for day view; daily totals for trend context. |
| Workouts | read | Typed blocks (type, start/end, energy) from Watch/gym apps, placed on the day timeline. |
| Nutrition | write (later) | Meal-pic macro estimates written as `dietaryEnergyConsumed` / protein / carbs / fat samples. Numbers go to Health, pics stay ours. |

## Meal parsing (OUT OF SCOPE — future addon/service)

Explicitly not part of the app for now; revisit as an addon later. Notes for
when we do: meal pic → vision model (Claude API) → rough kcal/macro estimate →
written to Health as nutrition samples, shown in journal.

- **Never in the capture path.** Snap-and-done stays sacred; parsing runs in
  background, estimate appears in journal later, editable/discardable.
- **Honest roughness.** Vision estimates are ±30–50% — display as ranges or
  fuzzy badges, not "487 kcal". Trend context, not precision logging.
- **First network dependency** — everything else is on-device. Personal use:
  app calls Claude API directly, still no backend.
- Bolts on cleanly after v1 since photos are already stored.

## Journal views

- **Trend chart** (top level) — weight over weeks/months, daily noise smoothed,
  gaps handled gracefully. Progress pics markers on the timeline.
- **Day timetable** (day detail) — vertical time axis: weigh-in dot, meal
  thumbnails at their times, workout blocks spanning duration, hourly step
  bars as faint background strip.
- **Progress compare** — side-by-side pics across dates.
- Separate Claude Design session running for the journal view; let it drive
  the model.

## UX decisions

- **Ghost overlay** on progress-pic camera — previous pic at ~30% opacity for
  pose/framing consistency. Best feature-per-line-of-code in the app.
- **Fat-finger guard** — confirm/reject implausible weights (804, 8.4).
- Capture is append-only; edit/delete lives in the journal view, never in the
  capture path. Backdating exists but out of the happy path.
- Multiple weigh-ins/day allowed; chart plots first-of-day (morning weight is
  the consistent one).
- Dessert case: "+ pic" on last meal in journal — explicit beats a
  time-window auto-merge.
- Photos app-only (not camera roll). Progress pics FaceID-gated.
- Hardcode units (kg) day one. Store timestamp + tz offset; "day" = local day
  at capture.

## Practical notes

- **Do now, zero code:** 2-action shortcut (`Ask for Input` → `Log Health
  Sample`) logging weight to Health. Starts accumulating data today; app
  reads the full backlog via HealthKit later.
- Free dev account = 7-day signing expiry (weekly re-install). Budget the
  $99/yr (TestFlight, 90-day builds) or the ritual kills a daily-use app.
- iOS 18 extras when relevant: lock-screen Controls, `LockedCameraCapture`.

## Open questions

- Schema details for photos/meals (deferred until journal design settles;
  numeric schema is solved — it's HealthKit's).
- Meal pics: keep long-term or auto-expire after N months? (Storage/iCloud.)
- Meal parsing: on-demand (tap to estimate) vs automatic on every meal pic
  (API cost, probably trivial at personal volume)?
- Exercise logging of our own (vs. read-only from Health) — later, if ever.
- Web/export story if ever needed — read-only export is the escape hatch.
- If ever distributed: meal parsing payment model — user-provided API key vs
  small paid proxy (breaks "no servers") vs on-device model when Apple's
  matures. Everything else survives distribution unchanged; $99 account is
  fine.
