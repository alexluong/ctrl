# Open questions

Format: `- [ ] Q (asked by, date) → for: Alex | client`. Check off + answer inline; move durable answers to `discovery.md`.

- [ ] Which booking-editor fields does reception actually use daily? Parked, not blocking (explore, 2026-09-20) → Alex/client
- [ ] Must the rebuild keep the PA18 guest declaration export? (explore, 2026-09-20) → Alex/client
- [ ] (deferred) Ask ezCloud for a **database export** of history — only when migration comes up; rebuild starts fresh. (explore, 2026-09-20) → Alex/client
- [x] Admin account for ezFolio config screens? **Closed 2026-09-23** — not pursuing. Setup/config is a scope the rebuild owns, not something to reverse-engineer (Alex).
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

- [ ] **Hotel day / business date** (reframed 2026-09-23 after Alex's note): ezFolio rolls at 23:59 = calendar day, which is the thing Alex wants changed. Proposed model:
  - Config: `businessDayStart` (e.g. 05:00). Business date D runs D 05:00 → D+1 05:00. A "night" = one business date.
  - Check-in at 01:00 Tue → business date Mon → charged Mon night (their reserved night). Check-in at 08:00 Tue → business date Tue; before `checkInTime` (14:00) = early check-in surcharge (catalogue item) or free per policy.
  - Check-out at 12:00 → normal. After `checkOutTime` → late-checkout surcharge. After next `businessDayStart` → another night.
  - Nights charged = business dates in [arrival_bd, departure_bd), derived from actual timestamps + policy thresholds, not from typed dates. Reserved dates are the *plan*; actual timestamps drive posting; mismatch = event (early/late/extra night).
  - Room charge posts at `businessDayStart` roll (or at check-in for the current night). "Revenue today" = posted charges for business date; occupancy × rate = forecast view.
  - **To confirm w/ client**: what time does the day actually roll (Alex says ~2am?); is a 1am arrival always charged the prior night; grace rules.
- [ ] **Overbooking**: allowed today (`allow_over_room` ON; >100% on turnover days). Keep as a receptionist override, or hard-block?
- [ ] **Guest identity**: ID missing on all revenue rows; PA18 export legally depends on it. Enforce ID at check-in, or keep optional?
- [ ] **OTA commission basis**: OTA remits net (receivable = net) vs hotel pays commission out? Per-Company setting. (product §10, 2026-09-23)
- [ ] **Cancellation / no-show charging**: per-channel policy or manual `compensation` charge? Product recommends manual for v1. (product §10)
- [ ] **Group billing default**: all buckets → master (today's usage) vs room-only → master (corporate norm)? Default per Company. (product §10)
- [ ] **VAT / red invoice**: out for v1 unless client says otherwise? (product §10; also in open Qs)
Product's recommendations for each are in `product.md` §10 — Alex can just accept/override there.

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
