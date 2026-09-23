# Alex session → product.md v1 (2026-09-23)

Full walkthrough in agenda order; Alex had not read v0.1, so ran high-level → drill-in. All landed as Proposed D-9…D-17; product.md bumped to v1 (96d3b04).

Decisions (Alex): multi-tenant by design, one tenant (D-9); event naming `agg.past_verb` + strong envelope + LocalDate/Instant (D-10); Booking minimal, no OTA/commission, deposit on folio, source = Setup list (D-11); Booking/Stay names, Stay v1 (D-12); **night is the unit** — Stay = Night[] w/ room+rate, move never splits (D-13); money v1, Setup-defined charge categories, no due date, no discount approvals (D-14); **generic Ledger context** (Alex's idea) under Billing/Expenses; Setup upstream reference data (D-15); users per person, two roles, three apps, **capability-based authz per command** (D-16); screens v1 (D-17). Rules §10 assumed where Alex said "no idea" (expenses/receivables by both roles; room move no reprice; extend from rate table).

Also: told architect D-8 availability stream covers invariants w/ condition (every supply/demand command versions it). DO dropped from §9.

Format lessons: Alex wants TS types + tables, not prose field lists; American English; write to the doc as we agree, not after.

Open for client: expenses/receivables owner or reception; inspected step; sales rep use; group assign now vs later (assumed now).
