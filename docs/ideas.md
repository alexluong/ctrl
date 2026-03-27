# Ideas & Notes

## Interface — how to interact with ctrl without a terminal

Discord bot was the original idea, but worth exploring:
- **Discord bot** — always available on phone, natural chat interface
- **Telegram bot** — lighter weight, good API
- **SMS / iMessage** — zero-app friction but limited richness
- **Scheduled agents** — some things don't need interaction at all, just run on cron
- **Web dashboard** — for viewing state, not necessarily for input

Open question: maybe multiple? e.g. cron for routine stuff + Discord for on-demand

## Architecture

- Monorepo — each domain is a directory, no separate repos
- `arr` (plex-manager) is shell scripts + docker compose, lightweight to migrate in

## Knowledge management

Claude owns all docs/files. User interacts via conversation only.
Plain markdown in `docs/` — no Obsidian, SQLite, or MCP needed. Claude has native
file access and grep, which is sufficient for this scale.

## Open questions

- What language/framework for the bot/interface?
- How much of `arr` to bring in vs keep as-is on the VM?
- Hosting strategy for the interface layer?
