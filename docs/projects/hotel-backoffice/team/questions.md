# Open questions

Format: `- [ ] Q (asked by, date) → for: Alex | client`. Check off + answer inline; move durable answers to `discovery.md`.

- [ ] Which booking-editor fields does reception actually use daily? Parked, not blocking (explore, 2026-09-20) → Alex/client
- [ ] Must the rebuild keep the PA18 guest declaration export? (explore, 2026-09-20) → Alex/client
- [ ] (deferred) Ask ezCloud for a **database export** of history — only when migration comes up; rebuild starts fresh. (explore, 2026-09-20) → Alex/client
- [ ] Admin account for ezFolio config screens? Parked, not blocking (explore, 2026-09-20) → Alex/client
- [ ] Hookdeck: stock SaaS retention, or something making long retention a non-issue? Decides log vs bus. (architect, 2026-09-19) → Alex
- [x] What is the system at `:99`? → **The PMS the client uses today.** (answered by Alex via explore, 2026-09-19)
- [ ] Does the Excel workbook implied by `requirements.md` exist? Can we get it? (architect, 2026-09-19) → Alex/client
- [ ] Whose hotel; relationship; who are the users (front desk / owner)? (architect, 2026-07-10) → Alex
- [~] Size: **58 rooms, ~96% occ tonight** (explore, 2026-09-20). Bookings/day + history depth still open → Alex
- [ ] OTA channels; channel manager or manual entry; commission rates per OTA? (architect, 2026-09-19) → client
- [ ] Seasonal / per-night rate changes? VAT / red invoice? (architect, 2026-09-19) → client
- [ ] Timeline / urgency? (architect, 2026-07-10) → Alex
- [x] ~~Containers paid~~ moot — D-3 TS Workers, free tier.
- [ ] `wrangler login` expired on MBP — Alex to run in solex-dev session. (dev, 2026-09-19) → Alex
## Decisions needed (Alex) — surfaced by explore, 2026-09-23

- [ ] **Day boundary**: ezFolio rolls charges at 23:59, night audit off, days never formally closed. SoLex: hotel-local calendar day w/ implicit roll at a fixed time? or explicit day-close? (needed before reports)
- [ ] **Overbooking**: allowed today (`allow_over_room` ON; >100% on turnover days). Keep as a receptionist override, or hard-block?
- [ ] **Guest identity**: ID missing on all revenue rows; PA18 export legally depends on it. Enforce ID at check-in, or keep optional?

## Open questions

- [ ] PA18 / guest declaration export — legally required to keep? (explore, 2026-09-20) → Alex/client
- [ ] **Admin login for ezFolio** — biggest remaining gap; all item masters + pricing config invisible without it. (explore, 2026-09-20, re-raised 2026-09-23) → Alex/client
- [ ] Which of the ~60 booking-editor fields does reception use daily? (explore, 2026-09-20) → client — before booking form scope
- [ ] Staff internet reliability at the hotel (Cloudflare-hosted = no LAN fallback)? (explore, 2026-09-20) → Alex
- [ ] Ask ezCloud for a DB export? Parked, not critical path (D-5). (explore, 2026-09-20) → Alex
