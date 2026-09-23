# Test cases

Seeded 2026-09-24 by architect from the walkthroughs in `../team/qa.md`. `last run` = the commit the case was last exercised at by hand or by suite. IDs are stable; retire with ~~strike~~, never renumber.

## Slice 0 — foundation

| ID | rule | steps | expected | automated by | last run |
|---|---|---|---|---|---|
| S0-1 | D-8 atomicity | tier (b) write whose row statement fails | no event written | scenario:"leaves no event behind when the row write fails" | 3fb421a pass |
| S0-2 | D-8 retry redecides | two writers, same room, take out of order | second gets `room.alreadyOutOfOrder`, one event | scenario:(store) "retries must re-decide" | 3fb421a pass |
| S0-3 | D-8 non-atomic write | pass a non-batchable statement | throws, nothing written | scenario:(store) | 3fb421a pass |
| S0-4 | no-op = no event | mark dirty twice | exactly one `room.marked_dirty` | scenario + manual | d629752 pass |
| S0-5 | N4 disable only for no-op | mark dirty, then OOO, then mark clean | dirty button disabled (no-op); clean enabled, click → alert with reason, no event | e2e:rooms.spec "S0-5" | ef6d242 pass |
| S0-6 | D-23 redaction | open `/system/tables/user`, `/session` | name/email/token columns `••• redacted` | scenario:(queries.test) + manual | 5b93104 pass |
| S0-7 | D-22 replay leaves tier (b) | rebuild projections | `rooms` row unchanged, events count unchanged | scenario:"leaves the tier (b) tables alone" + manual | 5b93104 pass |
| S0-8 | D-12 idempotency | same commandId twice | one write, original result returned | scenario:(log.test) | ca19a48 pass |
| S0-9 | D-12 upcaster gap | event behind current schema, no upcaster | fold path throws; display path marks `upcastPending` | scenario:(upcast.test) | c2d725e pass |
| S0-10 | N8 migrations | schema-changing deploy | D1 migrated before Worker flips; `pnpm dev` migrates | manual | 5b93104 pass |

## Slice 1 — occupancy loop

| ID | rule | steps | expected | automated by | last run |
|---|---|---|---|---|---|
| S1-1 | §11a nights [arrive, depart) | book 23→26 | nights 23, 24, 25 held; form shows "3 đêm" live | scenario:"holds every night of the stay on the calendar" + e2e:booking.spec "S1-1" | ef6d242 pass |
| S1-2 | D-15 no double sale | second booking on 101 for a held night | refused "Phòng đã có khách trong những đêm này", rendered as alert, not listed | scenario:"refuses to sell a night that is already held" + e2e:booking.spec "S1-2" | ef6d242 pass |
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
| S2-9 | first-owner bootstrap (D-11) | empty hotel, system operator; add first staff row (operator as receptionist) | acts as owner (all e2e setup runs this way); after the row, owner-only controls gone (write-off → note). Staging re-opens it after each wipe (D-26) | e2e:hotel.setup + receptionist.last.spec | 2dc835f pass |
| S2-10 | roomType retire in use | retire a type a live room references | refused `roomType.inUse` | scenario (todo verify) | — |
| S2-12 | §10 row 9 zero only when typed | book with rate field `0` | booked at 0 (FOC); blank field + no table rate → `rate.notFound` | scenario (todo verify) | — |
| S2-13 | §2 re-add staff | add a user already on staff | refused `staff.alreadyStaff` | scenario (todo verify) | — |
| S2-14 | §2 last owner demote | demote the only active owner to receptionist | refused `staff.lastOwner` (deactivate is S2-8) | scenario (todo verify) | — |
| S2-15 | D-20 contact erase owner-only | receptionist erases a contact | refused (`guests.erase`); owner: row blanked, `contact.erased {}` | scenario (todo verify) | — |
| S2-16 | N12 no PII in URL (non-blocking, before go-live; dev latest slice 5) | search people by name on /guests | term sent in a server-fn body, results in client state; URL has no query | e2e:no-pii-in-url.spec "S2-16" | 9fd031b pass |
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
| S3-13 | money loop on screen | category list → rate → book → check-in → minibar → refused → cash → check-out | bill correct at each step, forms removed after close | e2e:money-loop.spec "S3-13" | ef6d242 pass |
| S3-14 | N10 no silent block | submit any form with an invalid/empty required field or an empty select | message on the page, never a silent no-op (`step`, `required`, empty options) | e2e:no-silent-block.spec (14 forms) + empty-hotel.setup (empty select) | 9fd031b pass |
| S3-15 | receivable transfer | checked-in stay with balance → "Chuyển công nợ công ty" → check out | folio at zero, check-out allowed, company listed on /receivables with the amount | scenario:(receivables.test) + e2e:receivables.spec "S3-15" | dba5704 pass |
| S3-16 | D-25 businessDayStart | receptionist changes it; owner changes it while tonight unposted | both refused; owner after roll allowed | scenario (todo verify) | — |
| S3-17 | §6 folio lazy open | book, don't check in | no `ledger.account_opened`/folio stream until first charge/payment; bill shows "Đã thanh toán" | scenario (todo verify) + e2e:money-loop (balance before check-in) | ef6d242 pass (screen half) |
| S3-18 | §6 deposit before charge | booked stay, take deposit | allowed; balance shows credit; check-in posts tonight against it | e2e (todo) | — |
| S3-19 | receivable payment cap | pay a company more than it owes | refused "Vượt quá số công ty còn nợ", rendered | e2e:receivables.spec "S3-19" | dba5704 pass |
| S3-20 | receivable settles | pay exactly the outstanding | company drops off /receivables; statement still opens with every line | e2e:receivables.spec "S3-20" | dba5704 pass |
| S3-21 | receivable double-click | double-click a payment that settles the debt | posted once, not refused | scenario:(receivables.test) "is posted once when the button is double-clicked" + e2e:receivables.spec "S3-21" (two requestSubmit in one tick) | dba5704 pass |
| S3-22 | write-off owner-only, reason required | receptionist opens /receivables; owner writes off with blank/whitespace reason | receptionist sees a note, no form; blank reason refused on page | e2e:receivables.spec "S3-22" + receptionist.last.spec | dba5704 pass |
| S3-23 | N10 on receivables forms | submit empty company / amount / reason | message on page (forms are noValidate) | e2e:receivables.spec "S3-23" (transfer, payment; reason in S3-22) | dba5704 pass |
| S3-24 | N11 no GET fallback (**blocking**, D-20; architect 2026-09-24) | every form on /, /rooms/:id, /bookings, /stays/:id, /setup, /guests, /receivables | `method="post"` in server markup, so a pre-hydration submit never puts fields (guest name/phone) in the URL/access log | e2e:no-get-forms.spec (7 screens incl. /receivables) | 9fd031b pass |
| S3-25 | D-12 (f) double-clicked void | owner voids, same commandId twice | one reversal, same answer twice, never "already voided" | scenario:(folios.test) "voids once when the button is double-clicked" | dba5704 pass |

## Slice 3 — expenses (landing 7, 9fd031b)

Category ids change once more to the client's list (groceries, incidental, hk_overtime, advance, other) — e2e uses only the form default and the reserved `writeOff`.

| ID | rule | steps | expected | automated by | last run |
|---|---|---|---|---|---|
| S3-26 | desk records an expense | record description + amount | listed with amount; period total up | e2e:expenses.spec "S3-26" | 9fd031b pass |
| S3-27 | `writeOff` category reserved | category not offered; forced via tampered select | refused "Khoản mục này chỉ dành cho công nợ đã xoá." rendered, nothing listed | e2e:expenses.spec "S3-27" | 9fd031b pass |
| S3-28 | void = reversal, row stays | owner voids with reason | row struck through with reason, no void button, period total back to before | e2e:expenses.spec "S3-28" | 9fd031b pass |
| S3-28b | void reversal dated today; owner-only | void an expense from an earlier day; receptionist voids | reversal's business date = today (not the expense's); receptionist refused / no button | scenario (todo verify) | — |
| S3-29 | void needs a reason, said on the page | answer the prompt with blank / empty | refused `expense.reasonRequired`, rendered by the command (screen never re-checks a rule with its own message); Cancel = silent by design | e2e:expenses.spec "S3-29" ×2 | 2cd38a8 pass |
| S3-30 | D-12 (f) void double-click | two clicks in one tick | voided once, no refusal | e2e:expenses.spec "S3-30" | 9fd031b pass |
| S3-31 | write-off lands in expenses | write off a receivable | /expenses by-category has the "Công nợ đã xoá" line | e2e:expenses.spec "S3-31" | 9fd031b pass |
| S3-32 | D-24 (b), N15: input is never "network" | every form, fresh screen per form × variant: blank, 601-char text, 1e21/-5 numbers; void prompts blank/oversize | no 5xx, never "Không kết nối được máy chủ…"; shape failures = `input.invalid` | e2e:no-network-for-input.spec (10 screens) | 2cd38a8 pass (3cafabc: 9 forms + 2 prompts fail) |
| S3-33 | D-24 (b) refund reason (hole found by N15) | owner refunds with no reason typed | refused `folio.reasonRequired` by name, before the ceiling check; nothing refunded | e2e:money-loop.spec "S3-33" + scenario (todo verify) | 2cd38a8 **fail** (N16: screen sends "Hoàn tiền") |

## Slice 4 — accounts, roles, history

**How to read this block (Alex).** Each row is one thing the app must do. *Who / what they do* is the walk. *What they should see* is the pass condition; quoted text is the exact Vietnamese message on screen. *Rule* is the decision or finding it proves. "Signed out" means the other browser is sent to the sign-in page on its next page load, not instantly. An **event** is one line in a record's history table ("Lịch sử…"). A record "born with an event" has a first line that says it was created. **e2e** = checked by the automated browser suite on a fresh database. **scenario** = checked by dev's unit tests. **code** = checked by reading the code only; no test yet.

| ID | who / what they do | what they should see | rule | automated by | last run |
|---|---|---|---|---|---|
| S4-6 | Owner opens **Tài khoản** (/accounts), fills name, username and a 12+ character password, leaves position empty, creates | new row listed as "Không giữ vị trí nào", 0 sessions | accounts exist without a position | e2e:accounts.spec "S4-6" | 4cb9908 pass |
| S4-7 | Owner creates `lan`, then another account `LAN` | second one refused: "Tên đăng nhập này đã có người dùng." | usernames are case-blind | e2e "S4-7" | 4cb9908 pass |
| S4-8 | Owner tries usernames `e2e lan` (space), `e2e!lan`, `ab` (2 characters), 33 characters | each refused: "Tên đăng nhập viết thường, 3–32 ký tự, chữ và số cùng . _ hoặc -" | username rule: 3–32 characters, letters, digits, `.` `_` `-` | e2e "S4-8" ×4 | 4cb9908 pass |
| S4-17 | Owner creates `e2e-hyphen-…` (hyphens); that person signs in in another browser | sign-in works; session count on /accounts becomes 1 | N17: a hyphen accepted at creation must also sign in | e2e "S4-17" | 4cb9908 pass |
| S4-9 | Owner creates an account with an 11-character password | "Tối thiểu 12 ký tự." | password ≥ 12 | e2e "S4-9" | 4cb9908 pass |
| S4-10 | Owner opens an account, changes nothing, presses Save | "Không có thay đổi nào."; no new history line | N18: an unchanged save records nothing | e2e "S4-10" | 4cb9908 pass |
| S4-11 | Staff member is signed in in another browser; owner presses **Đặt lại mật khẩu** and types a new 12+ password | session count 1 → 0; the other browser is signed out on reload | a password reset ends every session | e2e "S4-11" | 4cb9908 pass |
| S4-12 | Owner resets a password to `short` | "Tối thiểu 12 ký tự." | same password rule on reset | e2e "S4-12" | 4cb9908 pass |
| S4-15 | Receptionist is signed in elsewhere; owner presses **Đánh dấu đã nghỉ** | row shows "đã nghỉ", sessions 0; the other browser is signed out on reload | deactivating ends sessions in the same request | e2e:accounts.last.spec "S4-15" | 4cb9908 pass |
| S4-18 | Receptionist is signed in elsewhere; owner changes their position to owner | sessions 0; signed out on reload | a role change ends sessions (new rights on the next sign-in) | e2e "S4-18" | 4cb9908 pass |
| S4-16 | A receptionist signs in and opens /accounts, then /setup | /accounts: "Tài khoản thuộc quyền chủ khách sạn.", no create button. /setup: "Chỉ dành cho chủ khách sạn" | D-18: account and setup screens are owner-only | e2e "S4-16" (+ S3-22 for receivables) | 4cb9908 pass |
| S4-13 | Someone with no position signs in | lands on **Sơ đồ phòng** (room board); no server error | no position ≠ broken screen | e2e "S4-13" | 4cb9908 pass |
| S4-14 | Owner creates an account, then the event log is inspected | the creation line carries the username; no event anywhere contains the person's name or password | D-20: no personal data in events | e2e "S4-14" | 4cb9908 pass |
| S4-19 | Desk books a stay, types a guest name at check-in, then opens that guest in **Khách & liên hệ** (/guests) | history starts with "Đã thêm khách" | a guest named at check-in is born with an event | e2e:people.spec "S4-19" | 4cb9908 pass |
| S4-20 | Owner erases that guest (**Xoá dữ liệu**), then opens the guest's page | "Đã xoá thông tin"; history shows "Đã thêm khách" then "Đã xoá dữ liệu khách"; the name appears nowhere | D-20: erasure admits itself and keeps the history | e2e "S4-20" | 4cb9908 pass |
| S4-21 | Checklist. Guest, room, room type, rate, staff, account and a contact typed on the booking form are all made through the screens, then the database is inspected | every row has a creating event; none has an empty history | D-22: every tier (b) row is born with an event | e2e "S4-21" (whole-DB check) | 4cb9908 pass (b364ccd **fail** N19) |
| S4-22 | Checklist: the sign-in library checks the username with the same rule as account creation | a username that creation accepts signs in; one it refuses cannot exist | library re-validation = domain rule (N17 root cause) | e2e S4-17 + code (`auth/options.ts` calls `isUsername`) | 4cb9908 pass |
| S4-23 | Desk opens a guest, changes nothing, saves | no new history line | unchanged save records nothing (as S4-10) | code (`people/domain.ts` update); test todo. Silent, no "Không có thay đổi nào." (N22, scheduled 5.6) | 4cb9908 code pass |
| S4-24 | Desk opens a contact, changes nothing, saves | no new history line | same | code; test todo; silent (N22) | 4cb9908 code pass |
| S4-25 | Owner edits a room type, changes nothing, saves | no new history line | same | code (`setup/domain.ts`); test todo; silent (N22) | 4cb9908 code pass |
| S4-26 | A rate is saved with nothing changed (no edit screen yet; command only) | no new history line | same | scenario (hotel/setup.test, dev d607656); silent (N22) | d607656 pass (4cb9908 **fail** N20) |
| S4-3 | Any click that writes more than one line (check-out, void, payment) | every line from one click shares one correlationId; no line outside a group | one click = one history entry (architect: tabs group by correlationId, no raw column) | scenario (folios.test void); e2e todo (DB check now, screen once N21 lands) | pending history grouping (N21) |
| S4-1 | A receptionist visits stay (void/refund), receivables (write-off), expenses (void), guests (erase) | owner-only buttons absent or replaced by a note; the commands still refuse if called directly | D-18 | partial: S4-16, S3-22; rest todo | — |
| S4-2 | A deactivated person's session and a new sign-in attempt | session ended; sign-in refused | — | covered by S4-15 (session); refused sign-in todo | — |
| S4-4 | Receptionist opens account create/edit/disable; the last owner tries to step down | refused / hidden; the last owner cannot step down (`staff.lastOwner`) | D-18, S2-8 | S4-16 + scenario | 4cb9908 pass |
| S4-5 | Links and forms on /accounts and /guests | ids only in URLs; forms POST | N11, N12 | e2e no-get-forms, no-network-for-input include /accounts; no-pii-in-url covers /guests | 4cb9908 pass |

## Slice 5 — companies and group bookings

Plain-language, same reading as slice 4. Company names below are examples; the e2e uses stamped names.

### 5.1a companies (d896f3c)

| ID | who / what they do | what they should see | rule | automated by | last run |
|---|---|---|---|---|---|
| S5-1 | Owner opens **Thiết lập**, fills a name under **Công ty**, presses **Thêm công ty** | company listed with its id (the name made lowercase with hyphens) and a **Ngừng dùng** button | companies are defined, not typed at the desk | e2e:companies.spec "S5-1" | d607656 pass |
| S5-2 | Desk checks a guest in and transfers the bill, picking the company from the list | bill settled; **Công nợ** lists the company by name; its statement heading shows the name | pick from the list; the name is shown, never the id | e2e "S5-2" | d607656 pass |
| S5-3 | Owner presses **Ngừng dùng** on a company that still owes | "Công ty này còn công nợ hoặc còn đặt phòng đang mở. Hãy tất toán hoặc đóng trước."; the company stays live | §11: no retiring while a receivable is open | e2e "S5-3" | d607656 pass |
| S5-4 | Company pays in full, then owner retires it; desk opens a transfer | retired without complaint; it's gone from the transfer list | retire once settled; retired ≠ choosable | e2e "S5-4" | d607656 pass |
| S5-5 | Desk transfers a bill before any company exists | "Chưa khai báo công ty nào. Chủ khách sạn thêm trong phần Thiết lập." (not "Chọn công ty nhận công nợ.") | an empty list says who has to act (N10 class) | e2e:hotel.setup "S5-5" | d607656 pass |

### 5.1 group bookings (drafted; runs when landing 2 screens land; domain 98f0989)

| ID | who / what they do | what they should see | rule | automated by | last run |
|---|---|---|---|---|---|
| S5-6 | Desk makes one group booking for 3 rooms | 3 stays under one booking, one master folio | a group booking makes one stay per room | todo (e2e + scenario) | — |
| S5-7 | Desk makes an individual booking for a company traveller, posts a charge | no master folio; the charge is on the guest's own folio; settled at check-out by transfer to the company | product §10 row 8 (4a77be0): routing and master only for groups | todo | — |
| S5-8 | Group, company without default routing: room night + minibar | room charge on the master; minibar on the guest's own folio | built-in default: room → master, rest → own | todo | — |
| S5-9 | Group, company whose default routing differs | charges follow the company's default | Company.defaultRouting beats built-in | todo | — |
| S5-10 | Group, desk sets a per-stay routing for one category | that stay's charges in that category follow the override | stay override beats company default (per category) | todo | — |
| S5-11 | One group stay checks out while the master still owes | check-out allowed once the stay's OWN folio is settled | §10 row 7: check-out guards own folio only | todo | — |
| S5-12 | Desk closes the group booking while the master owes / while a stay is still in-house | refused, with a message; closes only when master is 0 and every stay is checked out or cancelled | §10 row 7a | todo | — |
| S5-13 | Owner retires a company with an open booking (no debt) | refused "Công ty này còn công nợ hoặc còn đặt phòng đang mở…" | §11: open booking half of company.inUse | todo | — |
