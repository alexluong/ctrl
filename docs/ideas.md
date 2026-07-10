# Ideas & Notes

## Projects discussion (started 2026-07-10)

Alex has several personal projects planned (list TBD — discussion in progress). Context:
- Motivation: fun/convenience + learning. Will flag if anything else drives a project.
- Likes experimenting; wants to develop a personal **bootstrap stack** for starting projects quickly.
- Runs a **homelab** with self-hosted services, most notably Vaultwarden.
- Repo organization + Claude skills-as-shortcuts should evolve incrementally, not be scaffolded upfront.

Answers so far (2026-07-10):
- **Skillset**: JS + Golang, full stack. Wants to explore **Go at larger scope/scale** — a bigger Go project is a learning goal.
- **Homelab**: single VM (`sshmylab` → `ssh alex@149.28.40.6`), managed via `hub/alexluong/collielab` repo — docker-compose services (vaultwarden, portainer, glances, observability) + terraform (DNS for alexluong.com, nhiluong.com, collie studio).
- **OpenClaw direction (below)**: dead — no longer pursuing. Kept for historical context only.

The 3 projects (each has a file in `docs/projects/`):
1. [tracker](projects/tracker.md) — fitness/body tracking, friction-free capture
2. [feed](projects/feed.md) — 2-person shared social feed (Alex + Hannah)
3. [hotel-backoffice](projects/hotel-backoffice.md) — semi-professional hotel booking back office

Cross-cutting: bootstrap stack candidate — Go + docker-compose deploy to collielab VM; Alex has `template-go-templ-tailwindcss` repo as prior art.

## ~~Direction: OpenClaw as foundation~~ (SUPERSEDED 2026-07-10 — not pursuing)

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
