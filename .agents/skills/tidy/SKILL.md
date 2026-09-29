---
name: tidy
description: Organize ctrl - memory (small index, long memories into notes, stale entries), broken vault links, and code leftovers (stale worktrees, leftover branches). Use when Alex says /tidy, when the memory index nears 150 lines, when `done` or `recall` notices duplicates or stale entries, or roughly monthly.
---

# Tidy

`done` adds; `tidy` organizes. Run the mechanical check, then fix, then propose the judgment calls to Alex.

## 1. Check

```sh
.agents/skills/tidy/check
```

Reports: memory file/index counts, index↔file mismatches, long memories, over-long index lines; backticked `ctrl-vault/…` paths that no longer exist; per worktree: last commit, commits ahead of main; local branches without a worktree; unknown files at the root.

## 2. Fix mechanically (no approval needed)

- Memory index ↔ files: add missing index lines, remove lines whose file is gone.
- Broken vault paths: point them at the moved file (`git log --follow`) or remove them. Don't rewrite paths in dated logs (`re/log/`) unless the file clearly moved.
- Over-long memory index lines: one line, under ~150 chars.

## 3. Judgment calls (propose, then apply after Alex's OK)

- **Sort each capture:** a cross-cutting trap stays in memory; knowledge joins the domain doc it belongs to (`docs/…`, `re/notes.md`, `biz/BOOKKEEPING.md`, a project's living doc); a preference or convention moves into the skill/AGENTS.md where it applies; stale → delete. A memory longer than ~25 lines is always a note.
- **Merge** duplicates; **delete** stale or disproven memories.
- **Projects:** a living doc in `docs/projects/` with no activity in months → ask Alex: park (status line), drop, or graduate (`workspace-setup`).
- **Keep the memory index under ~150 lines**, grouped: traps (by domain) · recent captures.

Show Alex the plan as a short list (moves, merges, deletes, counts before → after). Apply after OK.

## Worktrees and branches (propose, then apply after Alex's OK)

- Branch merged → `bin/wt rm <repo> <name>`, then `git -C repos/<repo>.git branch -d <name>` (never `--force` while it has unpushed work).
- Worktree idle 2+ weeks → ask Alex: finish, park, or drop.
- Repo whose project graduated → remove `repos/<repo>.git` + `wt/<repo>` once the new workspace has its clone.

## 4. Commit

`git add ctrl-vault && git commit -m "memory: tidy (<summary>)"` (or `docs(<area>):`), push. Report before → after counts.
