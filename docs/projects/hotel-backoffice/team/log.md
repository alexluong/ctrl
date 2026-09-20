# Team log

Newest first. `YYYY-MM-DD — <agent>: what`.

- 2026-09-20 — architect: D-5 recorded. Product objective updated for second pass on existing-system.md; group bookings flagged as the hard aggregate.
- 2026-09-19 — architect: D-4 recorded (PMS exists, data-ownership rebuild, core subset). Product objective updated. All 3 agents caught up.
- 2026-09-19 — explore: Alex: `:99` = the PMS the client uses now. Rebuild motive = data ownership; target = core subset + enhancements, not a feature-by-feature copy. WS2 = map it first, via a slow walkthrough with Alex.
- 2026-09-20 — explore: Alex: **rebuild starts fresh, migration deferred** — ezFolio's Excel export is broken (data-URL truncation) but that's not a blocker; data import handled later. Full UI map + group-booking flow now in `existing-system.md`.
- 2026-09-20 — explore: existing system = **ezCloud ezFolio** (Windows on-prem, Oracle, LAN-locked). ~20 screens mapped in `existing-system.md` w/ screenshots (gitignored). Key: no rate plans (rates typed per booking), channel manager present but unused (OTA channel typed into guest name), housekeeping module unused, night audit off, 58 rooms / ~96% occupancy today. Constraints from Alex: **no card data ever**, two personas (manager, receptionist), group/company bookings are core, key cards out of scope. Excel export path deferred.
- 2026-09-19 — architect: D-3 accepted (TS Workers, no Go). Dev profile objective rev 2. Containers/paid Q moot.
- 2026-09-19 — dev: caught up; blockers: wrangler login expired, Containers needs paid.
- 2026-09-19 — architect: project dir split, requirements translated, agents + team/ created. WS1/WS3 may start; WS2 waits on Alex for `:99` + workbook.
