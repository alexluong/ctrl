# SoLex — Agent roster

Each SoLex session is a named Claude Code agent with a profile here. **Session start: read your profile, then `../README.md`.** Profiles are living: the architect updates "Current objective" as work moves; agents append to "Log".

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
- **Decisions** are architect's. Propose in your file under "Proposals" or by message; architect records in `../README.md` → Decisions.
- **Alex** talks to any agent directly. If Alex tells you something that changes scope/direction, write it in your file *and* message architect.
- **Secrets**: `ctrl/secrets/` only. Never in tracked files or messages.
- No code outside the `solex` repo. No notes/TODO files inside `solex` — all notes live in ctrl.
