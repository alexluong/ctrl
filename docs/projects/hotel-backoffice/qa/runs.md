# QA runs

Newest first. `date · commit · staging · cases · result · findings · blocking?`

- 2026-09-24 · 624ac57 (+ e2e ef6d242) · — · e2e: S3-13, S1-1, S1-2, S0-5 pass; S3-14 15/15 fail · N10 confirmed on every form (14 + empty room-type select); **N11** new: submit before hydration = native GET, fields in query string, nothing saved (booking form → guest name/phone in URL); **N12** mise shims re-apply `.env` over exported env (DATABASE_URL can't be overridden from a shell) · N (N11 borderline: PII in URL — asked architect)

- 2026-09-23 · 624ac57 · — · S3-9, S3-12, S3-13, S2-3, S2-4, S1-2 · pass · N10 silent `required` block (non-blocking) · N
- 2026-09-23 · f35bded · — · S1-1, S1-2, S1-5, S1-6, S1-13 · pass · N8 dev doesn't migrate, N9 checked-out style (both fixed 5b93104) · N
- 2026-09-23 · d629752 · e9c6d416 · S0-4, S0-5, S0-6, S0-7 · pass · — · N
- 2026-09-23 · 0a5aa90 · fd7bb970 · S0-1..S0-3 (code review) · **fail** · B1 retry stale, B2 silent non-atomic (fixed 3fb421a) · Y
