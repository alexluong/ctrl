# vi pass 3 — the 92 keys waiting (from solex-dev)

Written at solex `8130240` because product has been unreachable for the whole
of 5.7's tail and 5.8. This is the handover so it does not live only in an
undelivered message. Regenerate with `pnpm i18n:report` in solex, or with
`untranslated()` from `src/i18n/messages.ts` for the text as well.

Everything below is English-only in `vi`. The D-29 fallback means every one of
them currently renders as the English sentence to a Vietnamese reader, so
nothing is broken — they are just not translated yet.

## Where they came from

- **G28** company routing on Setup — `setup.companyRouting*`, `setup.saveCompany`,
  `setup.routingDefault`. `setup.routingDefault` ("The usual") is the empty
  option in a routing select: it is a real answer meaning "nothing agreed for
  this category, fall through", **not** a placeholder, and it sits beside
  "Hoá đơn riêng của khách" / "Hoá đơn đoàn", which you have already done.
- **G29** House rules — `setup.rules*`, `setup.autoDirty*`, `setup.idEnforcement`,
  `setup.idOptional`, `setup.idRequired`, `setup.overbooking`, `overbooking.*`,
  `setup.receivableAgeDays`, `setup.oooDays`, `setup.days`, `setup.saveRules`.
  `setup.autoDirty` and `setup.idEnforcement` are label halves of a sentence
  the select completes ("A room a guest leaves is" → "Marked dirty
  automatically"), so they want to read as one sentence in Vietnamese too.
- **G32** the group routing table — `routing.group*`, `routing.room`,
  `routing.ownShort` / `masterShort`, `routing.setForGroup`,
  `routing.overridden`, `routing.noRooms`. `routing.room` is deliberately
  "Which room" rather than "Room", because one of the charge categories
  beside it is also called Room.
- **G33** Needs attention — `attention.*`.
- **G34 / G35** overbooking and capacity — `error.availability.overbooked`,
  `error.stay.overCapacity`, `error.stay.adultsRequired`,
  `booking.takeAnyway`, `booking.overbookedHint`, `stay.occupancy*`,
  `stay.adults`, `stay.children`, `stay.saveOccupancy`,
  `eventType.stay.overbooking_overridden`, `eventType.stay.occupancy_set`.
- **5.8 approvals** — `approval.*`, `approvalKind.*`, `folio.ask*`,
  `folio.awaitingApproval`, `folio.approvalRefused`, `folio.reprice*`,
  `folio.newPrice`, `receivable.askWriteOff`, `error.folio.nothingToChange`,
  `error.approval.*`.
- **QA fixes** — `people.idNumberMissing`, `error.stay.idRequired`,
  `error.setup.ruleInvalid`, `error.folio.billClosed`, and the seven refusal
  sentences added in `a129a06` after an audit found rules whose codes were
  being printed at the reader (`error.approval.*`, `error.booking.notRoutable`,
  `error.booking.categoryRequired`).

## Two of them are sentence fragments, on purpose

`approvalKind.*` are the tail of `attention.approvalPending` = "{who} asks to
{what}" — "take a line off a bill", "give money back". They have to read as a
continuation, which may want a different shape in Vietnamese; if so, change
`attention.approvalPending` with them and say so.

## The keys

Includes the eight `eventType.*` names added in `8130240` — six for the
approval events and two (`stay.routing_set` / `_cleared`) that had been
printing their own type in a stay's history since routing was built.

```
attention.title = Needs attention
attention.hint = Facts about the hotel that nobody is told about unless they look. A row leaves when the thing it is about stops being true — there is nothing to dismiss.
attention.none = Nothing needs attention.
attention.approvalPending = {who} asks to {what}
attention.approvalLine = {line}
attention.approvalWhere = room {room}
approvalKind.void = take a line off a bill
approvalKind.reprice = charge a line at a different price
approvalKind.refund = give money back
approvalKind.forfeit = keep a deposit
approvalKind.writeOff = write off a debt
approval.grant = Approve
approval.decline = Refuse
approval.declineReason = Why not?
approval.declineHint = The desk reads this on the line they asked about, so say the thing they need to do instead.
attention.receivableAged = {company} has owed {amount} for {days} days
attention.oooLong = Room {room} has been out of order for {days} days
attention.unassignedTomorrow = A room arriving {date} has not been assigned
attention.overstayBalance = A guest is past their departure date and owes {amount}
attention.go = Open
setup.rules = House rules
setup.rulesHint = How the hotel wants the system to behave. Everything here has a default, and a hotel that never opens this is running on it.
setup.autoDirty = A room a guest leaves is
setup.autoDirtyOn = Marked dirty automatically
setup.autoDirtyOff = Left as it was
setup.idEnforcement = At check-in, an ID is
setup.idOptional = Asked for if they have one
setup.idRequired = Required from somebody in the room
setup.overbooking = Selling past the rooms of a type is
overbooking.refuse = Refused, by everybody
overbooking.warn = The owner's to allow
overbooking.allow = Anybody's to allow
setup.receivableAgeDays = A company's debt needs attention after
setup.oooDays = A room out of order needs attention after
setup.days = {count} days
setup.saveRules = Save rules
setup.companyRouting = What this company pays for
setup.companyRoutingHint = The standing agreement, used as the starting point for every group booking billed to them. A room of theirs can still be set differently on its own page. Left unsaid means the default: the room on the group's bill, everything else on the guest's.
setup.saveCompany = Save
setup.routingDefault = The usual
people.idNumberMissing = Type in the number on that document.
routing.group = Who pays for what
routing.groupHint = One answer for the whole group, and every room follows it unless it was told otherwise. A room somebody set differently keeps what it was set to and carries a mark saying so; its own page is where that changes. "As agreed" withdraws the group's answer and lets the company's agreement decide again.
routing.room = Which room
routing.ownShort = Guest
routing.masterShort = Group
routing.setForGroup = This group agreed
routing.overridden = set for this room
routing.noRooms = No rooms in this booking yet.
folio.askReprice = Ask to reprice
folio.askVoid = Ask to take off
folio.askRefund = Refund — ask the owner
receivable.askWriteOff = Ask the owner to write it off
folio.awaitingApproval = waiting for the owner
folio.approvalRefused = the owner said no — {reason}
folio.askVoidTitle = Ask the owner to take this line off
folio.askRepriceTitle = Ask the owner to charge this line differently
folio.askHint = The owner sees this on their home page and answers there. The line stays on the bill until they do.
folio.reprice = Reprice
folio.repriceTitle = Charge this at a different price
folio.repriceHint = The line is taken off and put back at the price you agreed, both shown on the bill. It is the only discount there is — and the month-end sees it, which a percentage in a box would not.
folio.newPrice = New unit price
eventType.stay.routing_set = Where a charge goes changed
eventType.stay.routing_cleared = Back to what was agreed
eventType.booking.routing_set = The group agreed who pays
eventType.booking.routing_cleared = The group's agreement withdrawn
eventType.approval.requested = Asked the owner
eventType.approval.granted = The owner approved it
eventType.approval.declined = The owner said no
eventType.approval.expired = The request ran out — the guest had gone
error.approval.notFound = That request is not there any more.
error.approval.notOpen = That request has already been answered, or the guest has left. Nothing was applied.
error.approval.alreadyOpen = Somebody has already asked the owner about this. One question at a time.
error.approval.kindInvalid = That is not something the owner can be asked for.
error.approval.reasonRequired = Say why. The owner is being asked to decide on it.
error.booking.notRoutable = Only a group has two bills to choose between.
error.booking.categoryRequired = Say which kind of charge this is about.
error.folio.nothingToChange = That is the price this line already has.
error.availability.overbooked = {short} short on {date} — the hotel does not have that many rooms of that type free.
eventType.stay.overbooking_overridden = Sold past the rooms of that type
booking.takeAnyway = Take it anyway
booking.overbookedHint = The hotel does not have that many rooms of the type on at least one of those nights. Taking it anyway is allowed and is recorded against whoever does it.
error.stay.overCapacity = That room sleeps {capacity}. You have asked for {adults}.
error.stay.adultsRequired = A room is for at least one adult.
eventType.stay.occupancy_set = Who is in the room changed
stay.occupancy = People in the room
stay.occupancyHint = Adults are what the room's size is about. Children under the age in Setup are free and are not counted against it.
stay.adults = Adults
stay.children = Children
stay.saveOccupancy = Save
error.stay.idRequired = This hotel needs an ID from somebody in the room. Add a guest with their document number.
error.setup.ruleInvalid = That is not one of the answers to this rule.
```
