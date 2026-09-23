# Folded explore's 09-20..09-23 findings; wrote product.md v0

**Doing:** architect asked to fold in four findings (folio routing, two booking use cases, one charge shape / 8 buckets, Alex's calls on home screens + daily-only + early/late as items + child<6). They answered most of my interview list, so I wrote `product.md` v0 instead of another sketch.

**Model changes vs my 09-20 notes:**
- Folio: own per stay + master per group booking; charge posted against stay, routed by `stay.routing[bucket]`. Buckets = one enum shared by charges/reports/routing.
- Booking kind individual|group, same RoomStay underneath; `StayMergedIntoBooking` for Ghép đoàn.
- Availability = per-room overlap + per-type per-night count; recommended single-writer DO per hotel to dev rather than per-room streams.
- Dropped rate multipliers, hourly stays. Room state VC/VD/VCI/OC/OD/OOO w/ occupied derived.
- Commission default from Company, override per booking.

**Open:** §10 policy points (8) for Alex — three already in team/questions. Item masters still unseen.

**Next:** architect feedback on aggregate list; Alex on §10; then v1 (tighten events, add command list, maybe sequence for group flow).
