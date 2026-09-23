# Test cases

Seeded 2026-09-24 by architect from the walkthroughs in `../team/qa.md`. `last run` = the commit the case was last exercised at by hand or by suite. IDs are stable; retire with ~~strike~~, never renumber.

## Slice 0 — foundation

| ID | rule | steps | expected | automated by | last run |
|---|---|---|---|---|---|
| S0-1 | D-8 atomicity | tier (b) write whose row statement fails | no event written | scenario:"leaves no event behind when the row write fails" | 3fb421a pass |
| S0-2 | D-8 retry redecides | two writers, same room, take out of order | second gets `room.alreadyOutOfOrder`, one event | scenario:(store) "retries must re-decide" | 3fb421a pass |
| S0-3 | D-8 non-atomic write | pass a non-batchable statement | throws, nothing written | scenario:(store) | 3fb421a pass |
| S0-4 | no-op = no event | mark dirty twice | exactly one `room.marked_dirty` | scenario + manual | d629752 pass |
| S0-5 | N4 disable only for no-op | mark clean on an OOO room | click goes through, alert with reason, no event | e2e (todo) | d629752 pass (manual) |
| S0-6 | D-23 redaction | open `/system/tables/user`, `/session` | name/email/token columns `••• redacted` | scenario:(queries.test) + manual | 5b93104 pass |
| S0-7 | D-22 replay leaves tier (b) | rebuild projections | `rooms` row unchanged, events count unchanged | scenario:"leaves the tier (b) tables alone" + manual | 5b93104 pass |
| S0-8 | D-12 idempotency | same commandId twice | one write, original result returned | scenario:(log.test) | ca19a48 pass |
| S0-9 | D-12 upcaster gap | event behind current schema, no upcaster | fold path throws; display path marks `upcastPending` | scenario:(upcast.test) | c2d725e pass |
| S0-10 | N8 migrations | schema-changing deploy | D1 migrated before Worker flips; `pnpm dev` migrates | manual | 5b93104 pass |

## Slice 1 — occupancy loop

| ID | rule | steps | expected | automated by | last run |
|---|---|---|---|---|---|
| S1-1 | §11a nights [arrive, depart) | book 23→26 | nights 23, 24, 25 held; form shows "3 đêm" live | scenario:"holds every night of the stay on the calendar" + e2e (todo) | f35bded pass |
| S1-2 | D-15 no double sale | second booking on 101 for a held night | refused "Phòng đã có khách trong những đêm này", rendered as alert, not listed | scenario:"refuses to sell a night that is already held" + e2e (todo) | f35bded pass |
| S1-3 | §10 turnover day | stay A departs 26, stay B arrives 26 same room | allowed | scenario:"allows the turnover day, because departure is exclusive" | 42c55cb pass |
| S1-4 | D-8 stale availability read | two desks race for the last room | exactly one wins; loser re-decides, sees clash | scenario:"gives the last room to exactly one of them" + guard.test | 92aa083 pass |
| S1-5 | §10 6a early check-out | check-in 23, depart 26, check out on 23 | `stay.nights_changed` then `stay.checked_out` in one batch; 24–25 freed; stay shows 1 night | scenario:"shortens the stay and frees the remaining nights" + manual | f35bded pass |
| S1-6 | §10 auto-dirty | check out | room dirty, `room.marked_dirty {cause:'checkout', stayId}` in room history | scenario:"leaves the room dirty behind it" + manual | f35bded pass |
| S1-7 | §11 check-in needs serviceable room | take room OOO, then check in | refused `stay.roomOutOfOrder`, rendered | scenario:"refuses a check-in into a room that is out of order" | 92aa083 pass |
| S1-8 | B3 check-in vs OOO race | withdraw room and check in concurrently | whole check-in rolled back | guard.test:"rolls the whole check-in back when a withdrawal got in first" | 6e25418 pass |
| S1-9 | §10 6b OOO under assigned nights / with guest | OOO a room with a checked-in stay | refused `room.occupied`; with only future nights: warn + allow, availability versioned | scenario:"refuses to withdraw a room with a guest in it" | 92aa083 pass |
| S1-10 | §10 6c check-in normalises nights | early walk-in (arrive tomorrow, check in today) | night today added at first night's rate, availability versioned; late arrival drops unposted nights before today | scenario:(early/late check-in cases) + manual | 93e796d pass |
| S1-11 | cancel frees nights | cancel a booked stay | nights back on sale; cancel a booking takes every stay | scenario:"puts the nights back on sale", "takes every stay under a booking with it" | 92aa083 pass |
| S1-12 | D-20 ids only | create booking with contact name/phone | events carry contactId/guestIds only; names in `contacts`/`guests` rows | scenario:(people.test) | cef9f36 pass |
| S1-13 | N9 grid states | checked-out stay's held night | rendered muted with own legend entry; OOO hatched | manual (e2e todo) | 5b93104 pass |

## Slice 2 — setup minimum

| ID | rule | steps | expected | automated by | last run |
|---|---|---|---|---|---|
| S2-1 | slug ids | define "Phòng đôi" | id `phong-doi`; existing free-string rooms adopted; rename keeps id; collision → `setup.alreadyExists` | scenario | 1245a45 pass |
| S2-2 | rate ranges half-open, no overlap | two live rates covering one night for one type | second refused; retire frees nights | scenario | 1245a45 pass |
| S2-3 | §10 row 9 no rate → refuse | book a date outside every rate range, no typed price | refused `rate.notFound` "Chưa có giá cho một số đêm. Hãy nhập giá."; preview shows unpriced night before submit | scenario + manual | b65acd2 pass |
| S2-4 | rate prefill | book inside a range with rate field empty | nights priced from the table; typed price wins | manual (e2e todo) | 624ac57 pass |
| S2-5 | D-20 erasure | erase a guest | row blanked + `erasedAt`; `guest.erased {}`; edit after erase refused; twice = no-op; survives rebuild | scenario:(people.test ×5) + manual | b65acd2 pass |
| S2-6 | D-20 stream clean | stringify a guest's stream | no name/phone/ID number anywhere; updates carry field names only | scenario:"keeps the name in the row and out of the log" | cef9f36 pass |
| S2-7 | D-18 capabilities | receptionist tries setup edit / erase / add staff | refused, told so | scenario:(staff.test ×4) | 71402c8 pass |
| S2-8 | last owner | deactivate the only owner | refused `staff.lastOwner` | scenario | 71402c8 pass |
| S2-9 | first-owner bootstrap | empty hotel, system operator | acts as owner with warning; adding first staff row closes it permanently | manual | b65acd2 pass |
| S2-10 | roomType retire in use | retire a type a live room references | refused `roomType.inUse` | scenario (todo verify) | — |
| S2-11 | script emits event | `create-user.mjs --role` | `staff.added` beside the row, actor `system:bootstrap` | manual | f5591d1 pass |

## Slice 3 — money

| ID | rule | steps | expected | automated by | last run |
|---|---|---|---|---|---|
| S3-1 | D-17 zero-sum, immutable | post entry with lines Σ≠0 | refused `ledger.entryUnbalanced`; void = reversal, never edit | scenario:(ledger.test) | 61819a7 pass |
| S3-2 | D-17 replay | rebuild projections | balances identical | scenario:"replays to the same balances" | 61819a7 pass |
| S3-3 | close only at zero | close folio with balance | refused; at zero closes and refuses more | scenario | 61819a7 pass |
| S3-4 | one batch per money command | void a charge | line void + reversal + status in one batch, shared correlationId | scenario:"voids the line and reverses the money in one batch" | 077088d pass |
| S3-5 | idempotent money | double-click record payment | posted once | scenario:"is posted once when the button is double-clicked" | c9bab9f pass |
| S3-6 | refund cap | refund more than paid | refused | scenario:"never refunds more than was taken" | c9bab9f pass |
| S3-7 | `room` category reserved | post a room charge by hand | refused; only the night roll may | scenario:"will not let the desk post a room charge by hand" | c9bab9f pass |
| S3-8 | void/refund owner-only | receptionist voids | refused | scenario:"is the owner's, not the desk's" | c9bab9f pass |
| S3-9 | D-25 check-in posts tonight | check in | room charge for tonight on the bill immediately, night `posted:true`, immutable | scenario:"puts tonight on the bill straight away" + manual | 624ac57 pass |
| S3-10 | D-25 roll | day rolls / cron + lazy both fire / 3-day outage | next night posted once; catch-up; never posts nights ahead | scenario:(night.test ×6) | b3c7597 pass |
| S3-11 | voided night re-posts | void tonight's room charge, roll again | charge re-posted (attempt id) | scenario:"becomes owed again, and the roll posts it next time" | b3c7597 pass |
| S3-12 | §10 check-out guard | check out with balance | refused "Hoá đơn chưa thanh toán. Hãy thu tiền hoặc chuyển sang công nợ công ty"; credit balance passes; race with a landing charge re-runs | scenario + manual | 624ac57 pass |
| S3-13 | money loop on screen | category list → rate → book → check-in → minibar → refused → cash → check-out | bill correct at each step, forms removed after close | manual (e2e todo, the headline spec) | 624ac57 pass |
| S3-14 | N10 no silent block | submit any form with an invalid/empty required field or an empty select | message on the page, never a silent no-op (`step`, `required`, empty options) | e2e (todo, all forms) | — |
| S3-15 | receivable transfer | company booking, transfer remainder, check out | `ledger.account_opened` on `ledger:receivable:<companyId>`, folio at zero, check-out allowed | scenario (todo verify) | — |
