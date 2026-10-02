# ctrl

Alex's personal operations hub and incubator workspace (`~/workspaces/ctrl`, repo `alexluong/ctrl`). Holds notes for every personal domain (real estate, bookkeeping, machines, projects) and small explorations/POCs until they graduate into their own workspace. Alex's repo, Claude-operated.

## Working conventions

- Alex does not edit files. Claude owns all file/doc management: organize for Claude's own searchability.
- Claude owns all git operations (commits, branches, PRs). Write good commit messages; commit when work is done or when asked.
- **All durable context lives in this repo.** Auto-memory writes to `ctrl-vault/memory/` (in git, follows Alex across machines); never `~/.claude` memory. Facts, decisions and preferences go in the relevant vault file.

## Layout

```
AGENTS.md            this file (always-on rules; CLAUDE.md is a symlink to it)
.agents/skills/      skills (SKILL.md + scripts)
.claude/             Claude wiring only: skills symlink, hooks/, settings.json
bin/                 wt (worktrees), disk-audit.sh, svc (start/stop local services)
menubar/             SwiftBar plugins (svc.10s.sh = menubar front end to bin/svc)
media/               media stack on the Mac Mini: compose, scripts, catalog, docs (`media-ops` skill)
ctrl-vault/          Obsidian vault: all notes
  docs/              ideas, projects, machines, workflow, workspace playbook
  re/                real estate: deals, logs, bookkeeping (`re/notes.md` = conventions)
  biz/               bookkeeping, invoices (`biz/BOOKKEEPING.md` = the system)
  backlog/           Backlog.md board (change tasks only through the `backlog` CLI)
  work/task-N/       per-task notes when a task needs more than comments; summary.md at close
  memory/            agent memory (auto-memory; `MEMORY.md` index)
backlog.config.yml   board config
mise.toml            workspace tools
services.conf        services for bin/svc (keep-awake, boards, tunnels)
repos/               bare clones of exploration/POC repos (gitignored, pristine)
wt/                  worktrees (gitignored): wt/<repo>/main (read-only), wt/<repo>/<name>
secrets/             machine-local secrets (gitignored; canonical copy in Vaultwarden)
local/               scratch, exports (gitignored)
```

Maintaining the workspace (where things go, memory vs notes, adding skills): `workspace` skill.

## Domains (in `ctrl-vault/`)

- `re`: real estate: deals, notes, logs, bookkeeping (`ctrl-vault/re/notes.md` for conventions & context)
- `biz`: bookkeeping, invoices (`ctrl-vault/biz/BOOKKEEPING.md`)
- `docs`: ideas (`ideas.md`), cross-domain notes; `machine.md` = machine/repo layout; `home-systems.md` = home network, devices, IPs, access (`home-network-handoff.md` = earlier router notes); `workflow.md` = how Claude works across repos (session modes, git, quality bar, project lifecycle); `workspace-setup.md` = the agent-workspace playbook; `projects/<name>.md` (or `projects/<name>/` with a `README.md`) = each project's living doc
- `media` lives at the repo root (`media/`, not in the vault): Plex/Jellyfin/arr stack that runs on the Mac Mini from its own ctrl clone; work on it over `ssh mini`. Machine doc: `ctrl-vault/docs/mac-mini.md`
- Planned: `finance`, `career`

## Projects: incubate here, graduate out

Idea (`ctrl-vault/docs/ideas.md`) → exploration/POC in ctrl (living doc `ctrl-vault/docs/projects/<name>.md`, code in `wt/<repo>/…` via `bin/wt`) → own workspace `~/workspaces/<name>` when it needs its own board/memory, holds client data, needs infra credentials, spans several repos, or gets busy enough to crowd ctrl (`workspace-setup` skill). Details: `ctrl-vault/docs/workflow.md` § Project lifecycle. Older personal projects stay in `~/git/hub/alexluong/<name>` with a pointer `CLAUDE.md`.

## Work items

- The board tracks work that spans sessions: explorations/POCs, RE to-dos (tenant, taxes, insurance), machine/infra chores, workspace work. One-shot asks answered in a session don't need a task.
- Labels: `re`, `biz`, `project` (plus the project's name as a label), `infra`, `machine`, `workspace`. Statuses: `To Do`, `In Progress`, `Done`.
- CLI from anywhere in the workspace; always `--plain` when reading. Short events → task comments (`--comment "…" --comment-author @claude`); longer notes → `ctrl-vault/work/task-N/*.md`. Durable knowledge still goes to the domain doc (a task links to it, doesn't replace it).
- Worktree names for task code: `bin/wt add <repo> task-N-<slug>`. Alex's board UI: `backlog browser` (port 6421; other workspaces use 6420).

## Where commands run

Sessions start at `~/workspaces/ctrl`. Code paths are relative to a worktree: run `cd wt/<repo>/<name> && <cmd>` (or `git -C`). `repos/` and `wt/*/main` are read-only (edits denied); changes go in `wt/<repo>/<name>`.

## Using what we know

- Before working on a topic: `recall` skill (memory, vault, git history).
- End of a session: `done` skill (default: save nothing). Organizing memory/notes and stale worktrees: `tidy`.
- Memory is pushed (index loads every session; keep it small); notes are pulled (`recall` finds them).

## Git (this repo)

Conventional prefixes with a scope: `docs(<area>):`, `re:`/`re(<property>):`, `biz:`, `memory:`, `feat(skills):`, `chore:`. Push to `origin` freely (private).

## Alex context

- Software engineer; runs a homelab (Vaultwarden among other services)
- Personal projects are for fun/convenience/learning unless stated otherwise
- Out-of-country RE investor (Detroit metro portfolio): see `ctrl-vault/re/`
- Binary docs (PDFs, media) live on iCloud, not git: `~/Library/Mobile Documents/com~apple~CloudDocs/Documents/REI/` for RE (see `ctrl-vault/re/notes.md` for structure)
