# 2026-09-24 — post-v1: rulings, canvas badges, UX doc, D-27 familiarity, approvals 5.8

**Doing.** Spec owner after v1: applied ~25 peer rulings to product.md (D-20…D-28), then Alex's UX ask, then three spec tasks in one afternoon.

**Landed (product.md).** Two tiers (D-22); hotel-first streams; `ledger:<kind>:<id>` per account; night roll as derived query (D-25); folios lazy-open; routing/master folio group-only keyed by ChargeCategoryId; CloseBooking explicit for groups; Company entity + `company.inUse`; contact ≠ guest; `user.*` vs `staff.*`; explicit v1 role bundles; ExpenseCategory fixed in code; PII never in URLs; DisableUser deferred; BookingSource pinned (tier b, kind buckets = ezFolio Nguồn, seed from client's OTAs, default walk-in, source ≠ payer); G31 settle dialog + G32 group routing table as §3 rows; §3 Home & inbox + `NeedsAttention` projection; approvals **5.8 = D-28** (one rule, kinds void/reprice/refund/forfeit/writeOff, RepriceCharge = the only discount, grant re-checks + same batch, expiry reactions, 3 landings); 5.4 corrections (`folio.forfeit`, `depositForfeit` system category, MarkNoShow).

**Landed (ux.md, new, final for Alex → client).** Personas · journeys · IA · 14 ASCII wireframes with control → command · vi labels · gap list G1–G34 with P/C/L + familiarity column · §7 decisions. D-27 pass: "Familiar to / Departs" per screen against existing-system.md + fd-room-map / room-detail-panel / booking-detail / arrivals-today. Findings: grouped nav and tile quick panel are *closer* to ezFolio than built; stay page stays one page (rule-forced), softened by money strip + settle dialog. `diagrams/gen-solex-ux.py` → `solex-ux.excalidraw`, geometric self-check baked in (no human has opened it).

**Canvas.** gen-solex-domain.py got kind badges (TYPE/COMMAND/EVENT/PROJECTION) + legend; still pre-freeze content, no status tags (Alex never said go).

**Method that worked.** Read solex routes via a read-only Explore agent returning per-route region/control/command blocks (~6k words) instead of 3.6k lines into my context. Cross-session: fold dropped messages into the next one, never retry.

**Open.** Canvas status tags (Alex go/no-go, stale); domain canvas regen to post-freeze spec; cash handover / day close needs client; HTML artifact stale. Slice order for dev: 5.4 → 5.5 print → 5.6 polish → 5.7 coverage → 5.8 approvals.
