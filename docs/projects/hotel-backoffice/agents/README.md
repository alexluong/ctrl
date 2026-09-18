# SoLex — Agent roster

Each SoLex session is a named Claude Code agent with a dir here: `agents/<name>/README.md` = profile (role, owned files, current objective, log), `agents/<name>/notes/` = personal journal, one timestamped file per entry (owner-only). Shared notes across agents: `../team/` (decisions, questions, log).

**Session start: read your profile, your newest notes, `../README.md`, `../team/log.md`.** Architect updates "Current objective"; agents append to their Log + write a notes entry per session.

| agent | role | owns | reports to |
|---|---|---|---|
| `solex-architect` | cockpit — coordination, decisions, README, this roster | `../README.md`, `agents/`, `../requirements.md` | Alex |
| `solex-dev` | WS1 — repo, stack spike, later implementation | `solex` repo, `../stack.md` | architect |
| `solex-explore` | WS2 — existing system analysis | `../existing-system.md` | architect |
| `solex-product` | WS3 — domain discovery / product modeling | `../product.md` | architect |

## Protocol

- **One owner per file.** Write only what you own. Need something changed elsewhere → message its owner.
- **Git**: `git pull --rebase` before commit; commit as `docs(hotel-backoffice/<agent-short>): …` (short = dev/explore/product/architect). Push after each commit; others pull.
- **Messaging** (`SendMessage` by session name): short, factual, one topic. Use for: a finding another agent needs now, a blocking question, "done with X". Don't use for status chatter — that goes in your file's Status section.
- **Decisions** are architect's. Propose in `../team/decisions.md` (status Proposed) or by message; architect flips to Accepted.
- **Questions** for Alex/client → `../team/questions.md`. **Handoffs / done-notices** → `../team/log.md` (newest first). Personal thinking / progress → a new file in your `notes/`.
- **Alex** talks to any agent directly. If Alex tells you something that changes scope/direction, write it in your file *and* message architect.
- **Secrets**: `ctrl/secrets/` only. Never in tracked files or messages.
- No code outside the `solex` repo. No notes/TODO files inside `solex` — all notes live in ctrl.
