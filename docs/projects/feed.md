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

## Open questions

- Native iOS vs PWA? (share-sheet ingest pushes toward native or a Shortcut workaround)
- How literal is "scroll together" — synced realtime viewing, or just a shared list?
- Push notifications wanted? ("Hannah posted something")

## Status

2026-07-10 — idea captured, discussing scope/stack.
