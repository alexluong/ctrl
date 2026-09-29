---
name: recall
description: Look up what ctrl already knows before working on something - memory, notes (docs, RE, biz), past decisions, git history. Use when a topic, project, property, decision or tool comes up, or when Alex asks "what do we know about…", "did we decide…", "what happened with…".
---

# Recall

Search ctrl's persistent context and return a short brief with links. Read-only.

## Search

```sh
.agents/skills/recall/search <term> [term...]
```

Each term is searched separately across, in order: memory (`ctrl-vault/memory`), docs (`ctrl-vault/docs`: ideas, projects, machines, workflow), real estate (`ctrl-vault/re`), biz (`ctrl-vault/biz`, CSVs excluded), and the vault's git history.

Pick 2–4 specific terms: property (`haverhill`), project (`fitjournal`), tool (`Vaultwarden`, `mise`), person/vendor (`Katie`). Generic words drown the results.

Then read the hits that matter. For a project: its living doc `ctrl-vault/docs/projects/<name>.md` (or `<name>/README.md`). For RE: `ctrl-vault/re/notes.md` first. Projects that graduated leave a pointer README naming their workspace; follow it (`~/workspaces/<name>/<name>-vault/`).

Also, when relevant: `git -C wt/<repo>/main log --oneline -S '<symbol>'` for POC code.

## Brief

```markdown
Recall: <topic>
- <fact or past event> (source: ctrl-vault/re/notes.md | memory/x.md | commit abc123)
- …
Nothing found for: <terms with no hits>
```

5–10 lines. Say plainly when nothing relevant exists. Flag memory that looks stale or contradicts what you see now.
