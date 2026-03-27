# Ideas & Notes

## Direction: OpenClaw as foundation

After researching Claude Code Channels, OpenClaw, and building from scratch —
going with **OpenClaw** as the agent layer. It solves interface, memory, and
session routing. ctrl becomes the OpenClaw workspace, not a codebase.

### Why OpenClaw over alternatives
- **Claude Code Channels**: raw pipe into one session, no per-thread isolation, no persistent memory, requires machine running
- **Building from scratch**: ~2 months minimum for bare-bones, reimplements solved problems
- **OpenClaw**: multi-platform gateway, SQLite+vector memory, skill system, session isolation, open source

### What ctrl becomes
Not an app. An OpenClaw workspace:
- `SOUL.md` — agent identity and boundaries
- `skills/` — domain-specific instructions (invoicing, RE, bookkeeping, etc.)
- `data/` — structured data (SQLite, CSV)
- `docs/` — ideas, decisions, notes
- Git tracks everything — skill changes, data, history

### Interface plan
- **Primary**: Slack (thread-level sessions confirmed)
- **Also exploring**: Discord (channel-level sessions confirmed, thread isolation unclear)
- **Scheduled tasks**: OpenClaw cron for routine work
- **Data viewing**: export to CSV/Sheets when needed, SQLite as source of truth

## Domains (as OpenClaw skills)

Each domain = a `skills/<domain>/SKILL.md`:
- `invoicing` — generation & delivery
- `re-analysis` — real estate analysis
- `bookkeeping` — RE + other business
- `finance` — personal budgeting, tracking
- `media` — plex/arr stack (migrating from `hub/alexluong/arr`)
- `career` — resume, job search

## Open questions

- Discord thread-level session isolation — does it work like Slack threads? Need to test.
- How much of `arr` to bring in vs keep as-is on the VM?
- Hosting: where does OpenClaw run? Mac mini? Always-on server?
- Data strategy: what lives in SQLite vs flat files vs external (Google Sheets)?
