# Project: Shared Feed (Alex + Hannah)

Two-person shared social feed. Sharing-oriented, not algorithmic, not endless-scroll.

## Core idea

- Share reels / TikToks / YouTube / Twitter links into a shared feed
- Scroll together or independently; react/comment
- Replaces link-dumping in iMessage — dedicated space, no noise in texts

## Key mechanics

- **Ingest**: share sheet from other apps is the natural capture path (share → post to feed)
- **Display**: link unfurling/embeds — TikTok/IG embeds are notoriously hostile; YouTube/Twitter easier
- Reactions/comments per item
- "Scroll together" — possibly realtime/synced session? (clarify how literal this is)

## Notes

- Exactly 2 users — auth can be trivial, no multi-tenancy
- Candidate for the Go learning project (realtime, feed persistence, metadata scraping) though hotel project is bigger scope

## Plan (agreed 2026-07-10)

- **Flutter app** — this is the Flutter learning project (career-relevant: company uses Flutter). Both users on iOS; cross-platform is a free bonus, not a requirement.
- Share-sheet ingest via small native shim (`receive_sharing_intent` or similar)
- Go backend on collielab VM
- "Scroll together" = physically sitting together scrolling the same feed — **no synced-viewing feature needed**. Async shared feed + reactions/comments is the product.

## Open questions

- Push notifications wanted? ("Hannah posted something")
- Distribution: TestFlight vs ad-hoc?

## Status

2026-07-10 — plan agreed, not started.
