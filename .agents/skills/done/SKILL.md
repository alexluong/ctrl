---
name: done
description: Wrap up a session or a task before closing it - decide what (if anything) is worth remembering, write it to memory/notes/task summary, update the board and digest, commit the vault. Use when Alex says /done, "wrap up", "we're done", or before a session ends; the lead also uses it when a task closes.
---

# Done

Close out cleanly and keep only what's worth finding later. **The default is to save nothing.** Most sessions produce no new memory; that's fine.

Workspace-agnostic: the same file lives in every `~/workspaces/<name>` (keep them identical; see ctrl `ctrl-vault/docs/workspace-setup.md` § Skills). Below, `<vault>` = the workspace's `<name>-vault/` folder at the root. Workspace specifics (note layout, stack commands, commit prefixes) come from the `workspace` and `worktree` skills and `AGENTS.md`; follow them where they're more specific than this file.

## 1. Review the session

Skim what happened: the ask, what was found or changed, decisions, surprises, anything Alex corrected. Check `git status` at the workspace root for uncommitted vault changes.

## 2. Decide what's memorable

Save something only if it passes at least one test **and** isn't already recorded (search first: the `recall` skill if the workspace has one, else `grep -ril <term> <vault>/memory <vault>/notes <vault>/work`):

- **Would change how a future session acts:** a client/system/tool quirk, an env/infra gotcha, a trap that cost time, a correction or preference from Alex.
- **A decision + its reason** that someone will otherwise re-litigate.
- **An incident or finding** someone will ask about again ("what happened with X").

Don't save: routine progress, things obvious from the code or git history, what a ticket/PR already says, restatements of skills or AGENTS.md, one-off numbers that go stale, anything with credentials.

## 3. Pick the place (at most a few writes)

| what | where |
|---|---|
| short fact worth keeping when unsure where it belongs (a capture; `tidy` sorts it later), or a trap that bites regardless of topic | `<vault>/memory/<slug>.md` + one line in `<vault>/memory/MEMORY.md` (the line is what future sessions see: make the hook specific: who/what + the key fact) |
| an existing memory that turned out wrong or changed | edit or delete it (and its index line); never add a contradicting one |
| longer write-up | a note (the default): update the living note it belongs to, or add a dated one; layout per the `workspace` skill ("Where things go" / "Notes"). If `<vault>/notes/README.md` exists, add the note's line there |
| a task's outcome | `<vault>/work/task-N/summary.md` (below) |

Memory file: name and frontmatter like the existing files in `<vault>/memory/`. If there are none yet:

```markdown
---
name: <file stem, e.g. reference_foo_bar>
description: <one line: specific enough to know when it's relevant>
metadata:
  type: user | feedback | project | reference
---

<the fact; for feedback/project add **Why:** and **How to apply:**>
```

### Task summary (when a task closes or a session finished a task's work)

`<vault>/work/task-N/summary.md`, 5–10 lines:

```markdown
# task-N: <title>
- Asked: <one line + source link>
- Outcome: <what changed; PR/branch links> | <answer> | <dropped: why>
- Decisions: <decision: reason>
- Learned: <only if memorable; also promoted to memory/notes>
```

This is what search finds later, so name what someone would search for: client/tenant, repo, feature, decision IDs, code area.

## 4. Propose, then write

- **Clear-cut** (factual notes/summaries restating verified findings, no judgment calls): just write them, then list what was saved in the final line.
- **Anything debatable** (memory entries, Alex's preferences/decisions, edits to or deletions of existing entries, anything you're unsure is worth keeping): ask with `AskUserQuestion`, one question listing the planned writes in a few lines, options **Yes** / **No**; Alex adds notes via "Other". On Yes write, on No skip, on notes adjust and write.
- If nothing qualifies, say "nothing worth saving" and skip to 5.

## 5. Tidy up

- Board: update the task status / add a closing comment if work happened on a task (`backlog` CLI, never hand-edit).
- `<vault>/digest.md`: update if the lead is in use.
- Stacks/dev servers started this session: stop them the way the `worktree` skill says; leave worktrees unless the task is done and merged.
- Commit the vault: `git add <vault> && git commit -m "<task-N:|memory:|notes:> <what>"` and push.
- If the memory index is near 150 lines or you noticed duplicates/stale entries, suggest `/tidy` (if the workspace has it).
- Final line to Alex: what was saved, what's left open.
