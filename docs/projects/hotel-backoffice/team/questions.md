# Open questions

Format: `- [ ] Q (asked by, date) → for: Alex | client`. Check off + answer inline; move durable answers to `discovery.md`.

- [ ] Which booking-editor fields does reception actually use daily? Parked, not blocking (explore, 2026-09-20) → Alex/client
- [ ] Must the rebuild keep the PA18 guest declaration export? (explore, 2026-09-20) → Alex/client
- [ ] (deferred) Ask ezCloud for a **database export** of history — only when migration comes up; rebuild starts fresh. (explore, 2026-09-20) → Alex/client
- [x] Admin account for ezFolio config screens? **Closed 2026-09-23** — not pursuing. Setup/config is a scope the rebuild owns, not something to reverse-engineer (Alex).
- [x] Hotel-local time zone → `HotelProfile.timeZone`, the only zone (D-12). Value = client's (Asia/Ho_Chi_Minh presumably; confirm).
- [ ] Should staging get auth before it holds anything real? Public URL today. (dev, 2026-09-23) → Alex
- [x] Hookdeck retention — moot, D-8 (log lives in D1).
- [x] What is the system at `:99`? → **The PMS the client uses today.** (answered by Alex via explore, 2026-09-19)
- [ ] Does the Excel workbook implied by `requirements.md` exist? Can we get it? (architect, 2026-09-19) → Alex/client
- [ ] Whose hotel; relationship; who are the users (front desk / owner)? (architect, 2026-07-10) → Alex
- [~] Size: **58 rooms, ~96% occ tonight** (explore, 2026-09-20). Bookings/day + history depth still open → Alex
- [ ] OTA channels; channel manager or manual entry; commission rates per OTA? (architect, 2026-09-19) → client
- [ ] Seasonal / per-night rate changes? VAT / red invoice? (architect, 2026-09-19) → client
- [ ] Timeline / urgency? (architect, 2026-07-10) → Alex
- [x] ~~Containers paid~~ moot — D-3 TS Workers, free tier.
- [x] `wrangler login` expired on MBP — done 2026-09-23 (spike deployed).
## Decisions needed (Alex) — surfaced by explore, 2026-09-23

- [x] **Hotel day / business date** → D-7: configurable roll (default 02:00) + rules; nights from timestamps. (Alex, 2026-09-23)
- [x] **Overbooking** → warn + explicit override (D-15, §10 #2).
- [x] **Guest identity** → optional; PA18 later (§10 #4).
- [x] **OTA commission basis** → deferred, no OTA logic v1 (D-13).
- [x] **Cancellation / no-show** → manual compensation charge; explicit ForfeitDeposit (§10 #3).
- [x] **Group billing default** → `Company.defaultRouting` (room → master, rest → own), editable per stay (§10 #8).
- [x] **VAT / red invoice** → deferred (D-16).
- [x] **D-8 storage shape** — accepted de facto 2026-09-23 (Alex had dev build it).
- [ ] **D-11 auth** — OIDC stance; which IdP (Pocket ID on homelab / Cloudflare Access / other)? Staging auth before Booking? (architect, 2026-09-23)
All §10 points closed in the 2026-09-23 product session; table in `product.md` §10.

## Alex walkthrough needed (explore, 2026-09-23) — closes exploration

- [ ] Group rooms: assigned by tape-chart drag or per room-stay edit? (in practice, since waiting list is always empty)
- [ ] Deposit: is it a payment record w/ method + date, or just a number on the booking? (`rpt-deposit` suggests method exists)
- [ ] Room status: auto-dirty on checkout? clean required for check-in? INSPECTED ever used? OOO needs reason?
- [ ] OTA receivable: gross or net of commission? Compare one Agoda folio to its booking's Hoa hồng.
- [ ] Cancellation base: 149 in Sept vs how many bookings? (explore can count the reservation list)

## Open questions

- [ ] PA18 / guest declaration export — legally required to keep? (explore, 2026-09-20) → Alex/client
- [x] **Admin login for ezFolio** — **closed 2026-09-23 by Alex**: not worth chasing. The masters stay invisible; instead *setup/configuration becomes its own scope with its own persona* (rooms + prices, item catalogues + prices, tax/service behaviour, booking rules). WS3 designs it fresh; ezFolio's version is a checklist of what needs configuring, not a model to copy.
- [ ] Which of the ~60 booking-editor fields does reception use daily? (explore, 2026-09-20) → client — before booking form scope
- [ ] Staff internet reliability at the hotel (Cloudflare-hosted = no LAN fallback)? (explore, 2026-09-20) → Alex
- [ ] Ask ezCloud for a DB export? Parked, not critical path (D-5). (explore, 2026-09-20) → Alex
