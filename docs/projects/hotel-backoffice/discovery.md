# SoLex — Discovery brain-dump

Alex's answers to `README.md` open questions. Claude structures; append dated entries.

## 2026-09-23 — hotel day / nightly posting (Alex → architect)

Alex: "the hotel operates ~2am–2pm or something like that; if someone checks in late at night like 1am, they may still be charged for that night. The day should not be counted 12–12 (midnight) but a different mechanism, and ideally the system detects from check-in time and charges the booking correctly." Not 100% sure of exact rules — to confirm with client.

Architect's framing (for product): this is the standard PMS **business date** concept. See `team/questions.md` → "Hotel day".

## 2026-09-23 — focus areas for the product session (Alex)

When Alex sits down with solex-product, cover in this order:
1. **Schema** — aggregates/entities and their fields
2. **Roles/personas** — manager · receptionist · setup/admin
3. **Actions/interfaces** — what each persona does, on which screens (room map + tape chart as home)
4. **Rules/policy/logic** — §10 policy points + hotel day
5. **Events shape** — ES-ish vocabulary, what's an event vs mutable state
