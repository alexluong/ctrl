# Showcase journeys

Five short screen recordings, one user-visible flow each (mvp.md §2, D-30). Filmed in English from `solex/e2e/journeys/*.journey.ts` with `pnpm journeys`. Each one ships as a `.webm` and an rrweb replay; the player lists them all. Read these pages beside the player.

| # | Journey | Persona | Length |
|---|---|---|---|
| R1 | [Desk walk-in](R1-desk-walk-in.md) | Linh, front desk | 0:53 |
| R2 | [Owner morning](R2-owner-morning.md) | Mai, owner | 0:54 |
| R3 | [Group + company](R3-group-company.md) | Mai, then Linh | 1:47 |
| R4 | [Ask the owner](R4-ask-the-owner.md) | Linh (receptionist account), Mai | 1:21 |
| R5 | [House rules](R5-house-rules.md) | Mai | 1:08 |

## How they are made

- **Seed (off camera).** `seed.setup.ts` sets up a disposable database: the hotel "Hoa Sen Hotel" (12 Tran Phu, Nha Trang), a Double type at 500,000 with rooms 101–303, a Twin type at 550,000 with rooms 401–402, the standard charge categories, one company (Blue Sea Travel Co.) and guests already in house:
  - 101 Tran Van Nam, 3 nights, 2 mineral waters on the bill.
  - 103 Le Thi Hanh, 2 nights, 2 Saigon beers and a laundry line that isn't theirs.
  - 201 Pham Quoc Bao, tonight moved to the company's account.
  - 202 Nguyen Minh Anh, arriving in two days.
- **Language.** All hotel data is typed in English, and people's names are written without diacritics. On the English screens, any Vietnamese left is the app's own. `sweep.journey.ts` checks for it and writes `recordings/english-sweep.json`.
- **Nobody signs in on camera.** Personas are the dev user renamed. R4's receptionist is a real account signed in off camera, and its session is handed to the filmed browser.
- **"Next morning".** A step off camera moves the hotel's day start (Setup → "The day starts at": 23:00, then back to 00:00). This lets a guest check in "last night" and check out on their departure day without waiting a day. It matters because, since B1, a check-out on the day of arrival gives the night back.
- **Order.** The journeys run R1 → R5 on one database; each starts where the one before left off.

## Do not demo

- **Never void a room line of an in-house guest.** Since wave 1 it is refused; a change goes through Reprice. Void a room line only after check-out, or void a non-room line.
- **Don't check a guest out on the day they arrived** unless the point is an early departure. The night comes off the bill (B1), and a bill that was paid in advance is then in credit: check-out is refused and the settle dialog offers a refund (B3).
- **"Take it anyway" is only on the new-booking form.** Extending a stay, checking in and adding rooms to a group all refuse an oversell under the owner's-to-allow rule.
- **Group routing table cells are read-only.** Change a whole category from the header select. A single room's exception is set on that stay's page, and the table then shows it marked. "As agreed" does not clear a room's own setting.
- **At check-in with an ID required, type the guest's name as well as the ID.** The name shown in grey is a placeholder, and an ID beside it is dropped (N46, open).
