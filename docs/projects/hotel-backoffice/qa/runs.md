# QA runs

Newest first. `date · commit · staging · cases · result · findings · blocking?`

- 2026-09-24 · db0c0e0 (e2e f-up) · — · S5-8/S5-16 · pass · architect ruled N23 (landing 3: individual auto-close, group explicit close, inUse = live stay or master > 0) and master charges keep their stay (S5-16). Flake fixed: after a group submit the URL changes before the booking page renders, so stay links were read off the /bookings list · N

- 2026-09-24 · db0c0e0 (e2e b03e8d4) · 68192888 (not walked) · full e2e 92: all pass except S5-15 · new S5-6..8, S5-10, S5-11, S5-13, S5-14 pass; S5-9 scenario only (no screen for a company agreement) · **N23** a checked-out, paid booking keeps status `booked` (no close command yet, and individual bookings may never get one), so `bookingsOfCompany` says in use forever: any company that was ever booked can never be retired · N (retire is admin, not money; asks architect whether landing 3 closes individual bookings too). Q to architect: master room charges carry the originating stay_id (entries + charges); only payments/transfers are stay-less. The "no stayId" rule was checked on payments

- 2026-09-24 · d607656 (e2e 423606d) · 38ecc5ac (not walked) · full e2e 84/84 pass; new S5-1..S5-5 (companies) pass; on d896f3c S3-20 was red from the spec (reached the statement by name; id is now the slug), fixed in e2e · N20 closed (dev d607656, scenario). **N21** history tabs don't group by correlationId (architect: they must; S4-3 pending). **N22** guest/contact/room type/rate unchanged saves are silent, accounts say "Không có thay đổi nào." (architect: uniform nothingToChange; scheduled 5.6) · N

- 2026-09-24 · 4cb9908 (e2e aa34fd7) · be0647d5 (not walked) · full e2e 78/78 pass; S4-21 **pass** (N19 closed) · code read for S4-22..26: guest/contact/room type unchanged saves write nothing; **N20** an unchanged rate update still writes `setup.rate.updated` (`setup/domain.ts` rate update has no diff check; there is no rate edit screen yet, so only the command can hit it). Same class as N18 · N

- 2026-09-24 · b364ccd (+ e2e aa34fd7) · d006aa47 (not walked) · full e2e 78: all pass except S4-21 · **N17** hyphen usernames created but never able to sign in (Better Auth default validator; fixed 7b9a923) · **N18** untouched account save wrote `user.updated` (fixed b364ccd) · **N19** contact created by a booking has a row and no `contact.created` event (S4-21 red; same class as guests-at-check-in) · N17 Y (fixed), N18 Y (fixed), N19 open

- 2026-09-24 · 2cd38a8 (+ e2e) · acf36ff1 (not walked) · full e2e 56: all pass except S3-33 · new sweep S3-32: on 3cafabc 601-char text threw on room add, OOO, cancel stay, transfer, room type, guest, contact, write-off + both void prompts (N15, now closed); green on 2cd38a8 · **N16** refund form substitutes "Hoàn tiền" when reference is blank → `folio.reasonRequired` unreachable from the screen (screen inventing an answer to a rule); also `error.folio.reasonRequired` reads "lý do huỷ" on a refund (wording → product) · N

- 2026-09-24 · 9fd031b (+ e2e) · 98e73650 (not walked) · full e2e 43: S3-14 ×15, S3-24 ×7, S2-16 now **pass** (N10, N11, N12 closed); expenses S3-26..28, S3-30, S3-31 pass; S3-29 ×2 **fail** · **N14** a void `prompt()` answered empty returns silently (expenses + folio void) — N10 class; **N15** blank/whitespace reason fails the API adapter's zod (`reason.trim().min(1)`, expenses/folio void+refund) → thrown, rendered as "Không kết nối được máy chủ…" (wrong reason, and the commandId is kept for a retry that can't succeed) — should be a rule code · N

- 2026-09-24 · dba5704 (+ e2e 2dc835f) · 81fdef66 (not walked) · full e2e: S0-5, S1-1, S1-2, S3-13, S3-15, S3-19..23, S2-9 (receptionist pass) **pass**; S3-14 ×15, S3-24 ×7, S2-16 **fail** (known: N10, N11, N12 — dev's sweep after expenses) · no new findings; receivable forms already N10-clean, but no `method="post"` (in N11 sweep) · N (N11 open, blocking before slice 4)

- 2026-09-24 · 624ac57 (+ e2e S2-16) · — · S2-16 · **fail** (`/guests?q=<name>`) · N12 ruled non-blocking, fix before go-live (latest slice 5); rule to product §6: PII never in a URL · N

- 2026-09-24 · 624ac57 (+ e2e S3-24 sweep) · — · S3-24 · **fail** 6/6 screens, every form has no method · N11 ruled **blocking** (architect): fix = `method="post"` on all forms before slice 4. Open question: /guests search navigates to `?q=<name>` by design — same PII-in-URL class · **Y**

- 2026-09-24 · 624ac57 (+ e2e ef6d242) · — · e2e: S3-13, S1-1, S1-2, S0-5 pass; S3-14 15/15 fail · N10 confirmed on every form (14 + empty room-type select); **N11** new: submit before hydration = native GET, fields in query string, nothing saved (booking form → guest name/phone in URL); **N13** (was N12, renumbered: architect's N12 = guest search) mise shims re-apply `.env` over exported env (DATABASE_URL can't be overridden from a shell) · N (N11 borderline: PII in URL — asked architect)

- 2026-09-23 · 624ac57 · — · S3-9, S3-12, S3-13, S2-3, S2-4, S1-2 · pass · N10 silent `required` block (non-blocking) · N
- 2026-09-23 · f35bded · — · S1-1, S1-2, S1-5, S1-6, S1-13 · pass · N8 dev doesn't migrate, N9 checked-out style (both fixed 5b93104) · N
- 2026-09-23 · d629752 · e9c6d416 · S0-4, S0-5, S0-6, S0-7 · pass · — · N
- 2026-09-23 · 0a5aa90 · fd7bb970 · S0-1..S0-3 (code review) · **fail** · B1 retry stale, B2 silent non-atomic (fixed 3fb421a) · Y
