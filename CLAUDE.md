# ctrl

Personal operations hub. Monorepo. Alex's repo, Claude-operated.

## Working conventions

- Alex does not edit files. Claude owns all file/doc management — organize for Claude's own searchability.
- Claude owns all git operations (commits, branches, PRs). Write good commit messages; commit when work is done or when asked.
- **All durable context lives in this repo, not machine-local memory.** Do not use `~/.claude` memory — it doesn't follow Alex across machines. Document facts, decisions, and preferences in the relevant repo file instead.

## Domains

- `re` — real estate: deals, notes, logs, bookkeeping (`re/notes.md` for conventions & context)
- `biz` — bookkeeping, invoices (`biz/BOOKKEEPING.md` for the system)
- `docs` — ideas, project discussions, cross-domain notes; `docs/machine.md` = machine/repo layout; `docs/workflow.md` = how Claude works across repos (session modes, git/commit conventions, quality bar); `docs/projects/<name>.md` (or `docs/projects/<name>/` with a `README.md` entry point) = each project's living doc
- `media` — plex/arr stack (migrating from `hub/alexluong/arr`)
- `finance` — personal budgeting, tracking
- `career` — resume, job search

## Alex context

- Software engineer; runs a homelab (Vaultwarden among other services)
- Personal projects are for fun/convenience/learning unless stated otherwise
- Out-of-country RE investor (Detroit metro portfolio) — see `re/`
- Binary docs (PDFs, media) live on iCloud, not git: `~/Library/Mobile Documents/com~apple~CloudDocs/Documents/REI/` for RE (see `re/notes.md` for structure)
