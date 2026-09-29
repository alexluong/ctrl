# Project: Uno Chess

For-fun POC: chess where each turn you flip an UNO card that decides what you do. Local hot-seat web game.

- Code: `~/code/uno-chess` (local git, no remote). Rules source of truth: `RULES.md` in the repo.
- Stack: Vite + React + TS, custom pseudo-legal engine (no chess.js), vitest.

## Origin

r/AnarchyChess video "Sorry, I'm new to chess. Is this legal?" (2026-09-28, via Instagram @beralo007): https://www.reddit.com/r/AnarchyChess/comments/1wsbpwa/. As played there: one shared deck, flip a card, number = that many moves, Reverse spins the board (armies swap), Draw 2 revives captured pieces, ended on checkmate.

## Rule decisions (2026-09-29)

- Win = capture the king; check not enforced (thread consensus: checkmate breaks with multi-move turns).
- Numbers 0–9 = up to N moves; optional cap-at-3 toggle (big numbers end games).
- Skip = flip again. Reverse = armies swap. Draw 2 = revive 2 at capture squares. Wild Draw 4 = revive 4 anywhere (comeback card; Alex picked this over "4 moves + flip again"). Wild = 1 move then flip again.

## Prior art

- Chuno (https://chuno.online): hand + UNO matching, moves capped 0–2, online multiplayer.
- TripleSGames Uno Chess: hand + matching, card number picks a rank/file.
- Differentiator here: the video's chaos (army swap, revives). "UNO" is a Mattel trademark and "Chuno" is taken: rename if ever public.

## Status

2026-09-29: rules locked, POC being built (dev agent + separate review/QA agent).
