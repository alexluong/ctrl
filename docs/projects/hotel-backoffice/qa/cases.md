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
| S3-21 | receivable double-click | double-click a payment that settles the debt | posted once, not refused | scenario:(receivables.test) "is posted once when the button is double-clicked" + e2e:receivables.spec "S3-21" (two requestSubmit in one tick) | 30dbec5 **fail** (**N33**, regression from 8716fc2: a second submit while the first is in flight gets a fresh id, so it is refused "Công nợ này đã tất toán." rather than answered as the first) |
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
| S3-30 | D-12 (f) void double-click | two presses in one tick (since G3: on the reason dialog's confirm) | voided once, no refusal | e2e:expenses.spec "S3-30" | 30dbec5 pass (N31 fixed 30dbec5: one answer per asking, every Ask dialog) |
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
| S4-10 | Owner opens an account, changes nothing, presses Save | "Không có thay đổi nào." as a quiet notice, not a refusal (N22); no new history line | N18: an unchanged save records nothing | e2e "S4-10" | 4cb9908 pass |
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

### 5.1 group bookings (landing 2: 87e160d form + routing, db0c0e0 master folio)

Routing and master-folio wording is dev's placeholder until Alex's pass; the e2e asserts by key, so the words can change.

| ID | who / what they do | what they should see | rule | automated by | last run |
|---|---|---|---|---|---|
| S5-6 | Desk books **Đoàn** (group) for 3 rooms, choosing a company as **Bên thanh toán** | the booking page lists 3 stays and a group bill, settled | a group booking makes one stay per room | e2e:groups.spec "S5-6" + scenario (groups.test) | db0c0e0 pass |
| S5-14 | Desk opens a group booking's page | group bill has payment (and transfer when it owes) but **no** post-charge form | the master only gets lines through routing (by design, not a finding) | e2e "S5-14" | db0c0e0 pass |
| S5-7 | Desk books **Khách lẻ** (individual) with a company, checks in, posts a minibar | no "where charges go" section on the stay; room + minibar both on the guest's own bill; the booking page has no group bill | product §10 row 8 (4a77be0): only groups have a master and routing | e2e "S5-7" + scenario | db0c0e0 pass |
| S5-8 | Group with a company that has no agreement; desk assigns a room, checks in, posts a minibar; then takes the company's payment on the group bill | room night on the group bill, minibar on the guest's own; the payment line names no room | built-in default: room → master, rest → own; master payments are the booking's (DB check) | e2e "S5-8" + scenario | db0c0e0 pass |
| S5-9 | Company whose agreement sends something else to the group bill | charges follow the company's agreement | Company.defaultRouting beats the built-in default | scenario only (groups.test, routing.test): no screen sets an agreement yet | db0c0e0 scenario |
| S5-10 | On one group stay, desk sets **Tiền phòng** (room) to the guest's own bill, then checks in | the choice survives a reload; the room night lands on the guest's bill; group bill stays settled | a stay override beats the agreement (per category) | e2e "S5-10" + scenario | db0c0e0 pass |
| S5-11 | Group stay whose own bill is settled checks out while the group bill still owes | check-out goes through; group bill still owes | §10 row 7: check-out guards the stay's own bill only | e2e "S5-11" | db0c0e0 pass |
| S5-13 | Owner retires a company that has a future booking (no debt) | "Công ty này còn công nợ hoặc còn đặt phòng đang mở…" | §11 (product 7709bc1): company.inUse = a live stay or an unsettled master, never booking status | e2e "S5-13" | db0c0e0 pass |
| S5-15 | A company's only booking is checked in, paid, checked out; owner retires the company | retired without complaint | a finished booking is not an open one; goes green with landing 3 (auto-close + inUse reads live stays / master) | e2e "S5-15" | 624b7dd pass (N23 closed) |
| S5-16 | Same as S5-8, database check | the room night on the group bill still names the room's stay; payments and transfers on the group bill name none | routing keeps the stay a charge came from (architect) | e2e "S5-8/S5-16" | db0c0e0 pass |

### 5.1 closing a booking (landing 3, solex 624b7dd; product 7709bc1)

A group closes only by the explicit close, refused while a stay is open or the group bill owes. An individual booking closes itself when its last stay ends. Finish stays pressable while either condition holds, and the refusal says which one is in the way (architect ruling N25, per S0-5/N4; fixed d84c906). A closed group bill shows `master.closed` and no payment or transfer form (N24, fixed d84c906).

| ID | who / what they do | what they should see | rule | automated by | last run |
|---|---|---|---|---|---|
| S5-12a | Desk closes a group booking while one stay is still in-house or booked | Finish is pressable; pressing it is refused with `booking.staysOpen`; booking stays booked | §10 row 7a: every stay must be checked out or cancelled | e2e booking-close "S5-12a" | d84c906 pass (N25 closed) |
| S5-12b | Desk closes a group booking whose stays are all out but the group bill still owes | Finish is pressable; pressing it is refused with `booking.masterNotSettled`; booking stays booked | §10 row 7a: master must be 0 | e2e booking-close "S5-12b/c" | d84c906 pass (N25 closed) |
| S5-12c | Group bill paid or transferred to the company, all stays out; desk closes | booking shows "Đã kết thúc" with a "booking closed" history row; the group bill is closed in the same batch, and it offers no payment or transfer form, only a line saying it is closed; the company can now be retired | happy path; architect: master closes with the booking | e2e booking-close "S5-12b/c" | d84c906 pass (N24 closed) |
| S5-12d | An individual booking's only stay checks out (or is cancelled) | the booking shows closed right away, with no click; history has "booking closed"; the database row says `closed` | product 7709bc1 / architect: individual bookings close themselves in the same batch; projection must record `booking.closed` | e2e booking-close "S5-12d" ×2 (check-out, cancel) | 624b7dd pass |

### 5.2 the hotel's own settings (solex 5485e9e)

Setup opens with the hotel's name, time zone and the hour the business day starts. Owner only. History timestamps read in the hotel's zone; calendar dates stay plain days.

| ID | who / what they do | what they should see | rule | automated by | last run |
|---|---|---|---|---|---|
| S5-17 | Owner saves the hotel's name for the first time, then changes only the day-start hour, then saves with nothing changed | first save recorded as the hotel being defined; the second records only the hour as changed; the untouched save records nothing (still silent, N22) | profile compared against the row (N18, N20) | e2e hotel-profile "S5-17" | 5485e9e pass |
| S5-18 | Owner saves with an empty name; a tampered form sends an unknown zone or hour 25 | refused with `setup.nameRequired`, `setup.timeZoneInvalid`, `setup.rollHourInvalid`; nothing recorded; no check on the page before sending | D-24 (b); N25 | e2e hotel-profile "S5-18" | 5485e9e pass |
| S5-19 | Owner changes the zone, then goes to a room's history without reloading; then changes it back | timestamps move with the zone and come back; the hotel's default zone can be picked again | zone read in the root loader, refreshed by the command | e2e hotel-profile "S5-19" | cecd997 pass (N26 closed) |
| S5-20 | Owner moves the day-start hour | nights already posted are never posted again; the next roll uses the new boundary | D-25 | scenario `hotelDay.test` roll at 02:00, `night.test` "does not post the same night twice" | 5485e9e pass (code) |
| S5-21 | The hourly cron runs twice in one hour | nothing extra posted | D-25 idempotent per (stay, night, attempt) | scenario `night.test` "does not post the same night twice", "catches up nights a missed cron never posted" | 5485e9e pass (code) |

### 5.3 reports (solex b789aa8, 99615f6, cecd997)

Owner only. The dashboard is today. Revenue and occupancy take a range [from, to) in the URL; no range means today. Revenue is read off the ledger; a void counts against the day of the charge it cancels. Money taken counts on the day it moved, with refunds shown beside it and the net underneath. Checked by the change each action makes, because the test database is shared.

| ID | who / what they do | what they should see | rule | automated by | last run |
|---|---|---|---|---|---|
| S5-22 | Book a stay for today, check in; take a spare room out of order | arriving: one more still to come, then one more arrived; in house +1; the out-of-order room leaves the rooms that can be sold and is counted beside them | architect: out of order leaves the denominator | e2e reports "S5-22" | cecd997 pass |
| S5-23 | Post a minibar charge on a checked-in stay, then void it the same day | sold today goes up by the night and the minibar, then back down by the minibar | void nets against its charge's day | e2e reports "S5-23" | cecd997 pass |
| S5-24 | Take a deposit, refund part of it | money taken goes up by the deposit; refunds by the refund; the net line is taken minus refunds; sold today unchanged | refunds beside, never netted | e2e reports "S5-24" | cecd997 pass |
| S5-25 | Book two nights starting the day after tomorrow | the week ahead has seven rows from tomorrow; only those two nights go up | forward includes empty nights | e2e reports "S5-25" | cecd997 pass |
| S5-26 | A receptionist opens the dashboard, the revenue report and the occupancy report | the owners-only card, not an error page | a read may turn a capability refusal into data | e2e receptionist "S3-22/S5-26" | cecd997 pass |
| S5-27 | Owner opens revenue over everything the suite has done | per category equals the charges table minus voids for the range; the category and source tables each add up to the revenue total; the method table adds up to its own total; source is one "not recorded" row (until 5.7) | revenue reconciles with the books | e2e reports-range "S5-27" | 30dbec5 **fail** (**N34**: with no booking sources seeded, bookings record `walk-in` and "by source" prints the raw id `walk-in`) |
| S5-28 | Owner compares the dashboard with revenue for [today, tomorrow) and with no range | same sold and taken figures | dashboard = same helper over today | e2e reports-range "S5-28" | cecd997 pass |
| S5-29 | Owner asks for from = to, or to before from, by URL or the form | refused with `report.rangeInvalid` on the page, not an error page | half-open range | e2e reports-range "S5-29" | cecd997 pass |
| S5-30 | Owner books two nights inside a four-night range | those two nights go up by one, not the departure day; every night of the range is a row | occupancy per night | e2e reports-range "S5-30" | 755e585 pass (N27 closed) |
| S5-31 | A charge on D1 is voided on D3; a payment on D1 is refunded on D3 | revenue for D1 drops, D3 unaffected, cash unchanged; cash D1 keeps the payment, D3 shows the refund | effective date for reversals (architect) | scenario `reports.test` (needs the test clock) | cecd997 pass (code) |
| S5-32 | A stay due out today, still in | counted as leaving, still in | departures | scenario `reports.test` (check-in rewrites dates; needs the test clock) | cecd997 pass (code) |

### 5.4 no-shows and kept deposits (solex bc38f17)

"Nobody came" is its own status: offered from booking, refused until the hotel's day has turned past the arrival date, frees the nights, leaves the bill open. The owner can keep some or all of a deposit on a cancelled or no-show stay (or a cancelled group's bill), up to what was taken less refunded less already kept. It is revenue on the day it was kept, under its own category that nobody can post by hand. A refund or a keep that brings such a bill to zero closes it.

| ID | who / what they do | what they should see | rule | automated by | last run |
|---|---|---|---|---|---|
| S5-33 | Desk presses "Nobody came" on the arrival day | refused `stay.notYetDue`; still booked | the day has to turn first | e2e deposits "S5-33" | 755e585 pass |
| S5-34 | Desk marks a stay booked for yesterday as nobody came | status no-show, the closed line for it; its nights freed; the deposit still on the bill and the keep form offered | no-show leaves the folio open | e2e deposits "S5-34"; marking twice is silent: scenario | 755e585 pass |
| S5-35 | Owner on a cancelled stay with a 200 000 deposit keeps nothing typed, 250 000, then 50 000, then 150 001; refunds 150 000 | amount missing; too large; kept (credit 150 000 left); too large; refund brings it to zero and the bill closes with no forms left; revenue for today +50 000 | ceiling = taken − refunded − kept; close at zero | e2e deposits "S5-35" | 755e585 pass |
| S5-36 | A tampered charge form posts the deposit-kept category | not offered in the list; refused `folio.categoryReserved` | reserved category, like room | e2e deposits "S5-36" | 755e585 pass (wording of the refusal speaks only of room charges: sent to product) |
| S5-37 | Owner keeps the deposit on a cancelled group's bill | the same form on the group bill; the bill closes at zero | 5.4 | e2e deposits "S5-37" (fixme) | e85263b pass (N28 closed: G14 cancels a group, G19 takes a deposit on its bill; e2e cancel-booking) |
| S5-38 | Revenue report over everything, with a kept deposit in it | the kept deposit appears as its own category line; the category reconciliation (S5-27) still matches the charges table | forfeit is a charge on a reserved category | e2e reports-range "S5-27" (runs after deposits) | 755e585 pass |

Drafted for G14 (5.7), from the N28 ruling:

| ID | who / what they do | what they should see | rule | automated by | last run |
|---|---|---|---|---|---|
| S5-39 | Desk cancels a group booking whose rooms are all still booked | every still-booked stay cancelled in one batch; booking cancelled; the group bill stays open for a refund or a kept deposit and closes at zero | architect N28 ruling | todo | e85263b pass (e2e cancel-booking) |
| S5-40 | Desk cancels a group booking with one room checked in | refused `booking.stayCheckedIn`; nothing cancelled | same | todo | e85263b pass (e2e cancel-booking) |
| S5-41 | Owner voids a line on a checked-out guest's closed bill | refused with a reason on screen; no `folio.charge_voided` event (the Void button stays pressable, N25) | same | pass a204175 | e2e `void-closed.spec.ts` |


### 5.6 map, panel, history (solex 8716fc2..c8b3528)

Architect rulings of 2026-09-25: the stay's history is one stream, the stay's own events and its bill's (charges, voids, payments) in time order; the room's history is the room's own events only. A room's housekeeping badge says Clean or Dirty and nothing else; who is in it comes from the stay.

| ID | who / what they do | what they should see | rule | automated by | last run |
|---|---|---|---|---|---|
| S5-42 | Owner voids a line on an in-house guest's bill, then opens the stay's history | the charge, the void with its reason and any payment sit in the stay's history among booked / checked in, in time order; the room's history still shows only the room's own lines | architect ruling (one stream per stay, folio merged) | e2e move-history "S5-42" | 30dbec5 pass (N29 fixed 69899bc) |
| S5-43 | Desk opens an occupied, dirty room from the map | the housekeeping badge reads Dirty (or Clean) only; occupancy is shown from the stay, not in the badge | architect ruling | e2e move-history "S5-43" | 30dbec5 pass (N30 fixed 69899bc; the panel reads "Sạch · Đang ở": housekeeping word, then the stay's status) |
| S5-44 | Desk moves a minibar line from one in-house room's bill to another's (G16) | the same line on the other bill, nothing struck through on the first; both balances move; revenue for the day unchanged; the history says "moved to another bill" | a move, not a void and repost | e2e move-history "S5-44" | 30dbec5 pass |
| S5-45 | Desk tries to move a room night onto another guest's bill | refused `error.folio.roomChargeStays`; bill unchanged | a night stays with its stay | e2e move-history "S5-45" | 30dbec5 not settled (timed out under machine load) |
| S5-46a | In a group, desk moves the guest's minibar line to the group's bill | the guest owes 0; the group's bill owes the night plus the minibar | stay ↔ master allowed both ways | e2e move-history "S5-46a" | 30dbec5 not settled (machine load) |
| S5-46b | In a group, desk moves the room night from the group's bill to the room's | the group's bill owes 0; the room's bill owes the night | same | e2e move-history "S5-46b" | e85263b pass (N36 fixed b4e501e) |
| S5-47 | Desk confirms a move twice in one tick | moved once, no refusal | D-12 (f) | e2e move-history "S5-47" | 30dbec5 not settled (machine load) |

### 5.7 people (G22, solex fc17274)

| ID | who / what they do | what they should see | rule | automated by | last run |
|---|---|---|---|---|---|
| S4-27 | Desk edits a guest's phone and nationality on their page | saved; "Guest details changed" in their history; the values stay after a reload | G22 | e2e people "S4-27" | 30dbec5 pass |
| S4-28 | Desk saves an ID number with no type, then a type with no number | "Say which kind of ID that number is" on the page; then `error.guest.idDocIncomplete`; nothing recorded | page answers shape, domain answers the rule | e2e people "S4-28" | e85263b pass (N35 fixed b4e501e) |
| S4-29 | A guest who stayed is erased | their page offers no form; the stay row and its link remain; their name appears nowhere | erasure keeps the facts, drops the person | e2e people "S4-29" | 30dbec5 pass |
| S4-30 | Desk opens a booking's contact from the people list | a contact form (with company, no ID fields); no "where they stayed" list | contacts are not guests | e2e people "S4-30" | 30dbec5 pass |

### 5.7 correcting a booking, nights, setup after the fact (G14 landing 2, G15, SetRoomType, G28, G29)

| ID | who / what they do | what they should see | rule | automated by | last run |
|---|---|---|---|---|---|
| S5-48 | Desk moves a group booking to another contact and a company, then saves it unchanged | "moved to another party" in its history; the unchanged save is a quiet notice and records nothing | G14 | e2e cancel-booking "S5-48" | e85263b pass |
| S5-49 | Desk saves a booking's notes | kept after a reload; "notes changed" in its history | G14 | e2e cancel-booking "S5-49" | e85263b pass |
| S5-50 | Desk adds two rooms to a group, then takes one off (first with nothing picked, then with no reason) | 3 stays; "pick at least one room"; "say why"; then one fewer booked room, two history lines | G14 | e2e cancel-booking "S5-50" | e85263b pass |
| S5-51 | Desk adds a night at a typed rate to a booked stay and re-prices another to 0, then types 12.5 | the night at 450 000; the free night at 0; "nights changed" and "night price set"; 12.5 refused on the page | G15 | e2e nights "S5-51" | e85263b pass |
| S5-52 | Desk gives back a middle night, adds a detached one, then gives back down to the last | `nightsNotContiguous` twice; the last night cannot go (`nightsRequired`) | G15 | e2e nights "S5-52" | e85263b pass |
| S5-53 | Desk re-prices or gives back tonight after check-in | `nightPosted` both times; the bill unchanged | G15 | e2e nights "S5-53" | e85263b pass |
| S5-54 | Desk adds a night whose room is sold to the next guest | `stay.roomTaken` | G15 | e2e nights "S5-54" | e85263b pass |
| S5-55 | Owner puts a room under a new type from Setup | the type shows after a reload; "room type changed" in the room's history | SetRoomType | e2e setup-changes "S5-55" | e85263b pass |
| S5-56 | Owner sets a company's minibar to the group's bill; a group for that company posts minibar | the guest owes nothing; the group's bill owes the night plus the minibar | G28 | e2e setup-changes "S5-56" | e85263b pass |
| S5-56b | Owner puts that category back to "the usual" | saved without a refusal; the agreement withdrawn | G28 | e2e setup-changes "S5-56b" | e85263b pass |
| S5-57 | Owner turns off auto-dirty; a guest checks out | the room is not marked dirty | G29 | e2e house-rules "S5-57" | e85263b pass |
| S5-58 | With an ID required, desk checks in with no ID, then one CCCD between two guests | `stay.idRequired`; half an ID refused on the page; then checked in, the number on that guest's page | G29 | e2e house-rules "S5-58" | e85263b pass (**N37** fixed 7279fc1: check-in had no ID field, so the rule bricked check-in) |
| S3-34 | Desk submits Add-to-bill twice in one tick | posted once, no refusal | D-12 (f) | e2e money-loop "S3-34" | e85263b pass (N33 fixed 46a699e) |

### 5.8 group routing, needs attention, availability (G32, G33, G34, G35)

| ID | who / what they do | what they should see | rule | automated by | last run |
|---|---|---|---|---|---|
| S5-59 | Room 1's minibar set on its own page; the column swept to the group's bill; swept again | room 1 keeps its own (marked); room 2 moves; the column reads back the group's answer; the second sweep writes nothing | G32 | e2e group-routing "S5-59" | e85263b pass |
| S5-60 | The column swept to the group's bill, then to the guest's | both rooms move each time; no "set for this room" mark | G32 | e2e group-routing "S5-60" | e85263b pass (**N38** fixed d37bae1: sweeps wrote per-room overrides, so rooms stuck) |
| S5-61 | Room 1 set on its own; the column swept, then back to "as agreed" | room 1 keeps its own; room 2 back on the agreement | G32 (d37bae1 reading) | e2e group-routing "S5-61" | e85263b pass |
| S5-62 | An individual booking | no group routing table | G32 | e2e group-routing "S5-62" | e85263b pass |
| S5-63 | A guest arriving tomorrow (and a one-night arrival today) with no room | listed with a link; the badge equals the list; assigning the room removes it on the next load | G33 | e2e attention "S5-63", "S5-63b" | e85263b pass |
| S5-64 | A room out of order past the threshold (event dated back) | listed with its reason; leaves when back in service | G33 | e2e attention "S5-64" | e85263b pass |
| S5-65 | A checked-in guest whose departure is today still owes | not listed as an overstay | G33 | e2e attention "S5-65" | e85263b pass (N39 fixed d37bae1) |
| S5-66 | A group asks for 3 of a 2-room type with 1 sold | refused "2 short on <night>"; "Take it anyway" books it; every stay's history records the override | G34 | e2e availability "S5-66" | e1c113d pass (N41, N42 fixed e17d85b; the override is a sub-line under "stay created". An earlier "still missing" was a race in the spec) |
| S5-67 | A type full this week; a booking of it next month | booked | G34: only added nights are checked | e2e availability "S5-67" | e85263b pass |
| S5-68 | The only room of a fully-booked type is taken out of order | allowed | G34: supply never refuses | e2e availability "S5-68" | e85263b pass |
| S5-69 | The same room booked twice for one night | `stay.roomTaken`, not overbooked | G34 | e2e availability "S5-69" | e85263b pass |
| S5-70 | 3 adults in a room that sleeps 2; then 2 adults + 2 children | "That room sleeps 2. You have asked for 3." with no override; then booked | G35 | e2e availability "S5-70" | e85263b pass |
| S5-71 | Owner looks for the overbooking rule in House rules | a refuse / warn / allow control | G34 | e2e availability "S5-71" | e17d85b pass (N40 fixed e17d85b) |
| S5-72 | Overbooking set to "refused, by everybody"; the owner asks for 2 of a 1-room type | refused "1 short"; taking it anyway is refused too; nothing booked | G34 rule `refuse` | e2e availability "S5-72" | e17d85b pass |
| S5-73 | Overbooking set to "anybody's to allow"; the owner takes 2 of a 1-room type anyway | booked; `stay.overbooking_overridden` on both stays (the flag is still required) | G34 rule `allow` | e2e availability "S5-73" | e17d85b pass (receptionist under `allow` not yet automated) |

### 5.8 approvals and reprice (solex a0beb3c..1b6850f)

The desk asks from the same button; the owner answers from Needs attention. The first pass has no receptionist, so these run in the second pass (`approval.last.spec.ts`) with a throwaway desk account signed in beside the owner.

| ID | who / what they do | what they should see | rule | automated by | last run |
|---|---|---|---|---|---|
| S5-74 | Desk asks to take a minibar line off; owner approves from the card | the line reads "waiting for the owner" and its asks are gone; after Approve the card leaves and the line is voided; `folio.charge_voided` and `approval.granted` share a correlation id; the void carries `approvalId` | one batch; one open request per line | e2e approval.last "S5-74" | 1b6850f pass (N43 fixed: "Ask to reprice" / "Ask to take off") |
| S5-75 | Desk asks to reprice; owner refuses with a reason | the line reads "the owner said no — <reason>"; not voided; the desk may ask again | 5.8 | e2e approval.last "S5-75" | 1b6850f pass |
| S5-76 | Owner opens the stay while a request waits | the line shows "waiting for the owner" and no Void of the owner's own | 5.8 (re-decision at grant is not reachable from the screens; domain test) | e2e approval.last "S5-76" | 1b6850f pass |
| S5-77 | Guest checks out while a request is open | the card leaves; `approval.expired` shares the check-out's correlation id | 5.8 | e2e approval.last "S5-77" | 1b6850f pass |
| S5-78 | Owner reprices a minibar line to the same price, then with no reason, then 80 000 → 50 000 with a reason | the same price is refused quietly; no reason refused; void and repost on the bill; revenue for the day −30 000 | RepriceCharge | e2e reprice "S5-78" | 1b6850f **fail** (**N45**: the refusal shows the raw key "error.folio.nothingToChange") |
| S5-79 | Owner reads a void request on the card | who asks by name; the room, the line and its amount; the reason | 5.8 | e2e approval.last "S5-79" | 1b6850f **fail** (**N44**: "user:01M3… is asking to take a line off a bill — <reason>": raw user id, no room, line or amount) |
| S3-22 | Desk opens a company's statement | "Ask the owner to write it off"; no owners-only note | 5.8 | e2e receptionist.last | 1b6850f pass |

