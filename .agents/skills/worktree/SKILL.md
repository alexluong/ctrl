---
name: worktree
description: Check out code for an exploration/POC in ctrl - bare clones in repos/, worktrees at wt/<repo>/<name>. Use whenever work in ctrl needs code checked out, a new POC repo, or cleaning up worktrees.
---

# Worktree

Everything goes through the `wt` script next to this file (`bin/wt` from the root). Don't run `git worktree` by hand. Repos = whatever is in `repos/`; `<repo>` alone means `alexluong/<repo>`.

```sh
bin/wt init poc-foo                      # bare clone + wt/poc-foo/main (read-only reference)
bin/wt init someorg/lib                  # other owners
bin/wt add poc-foo try-sqlite            # wt/poc-foo/try-sqlite on branch try-sqlite from origin/main (reuses the branch if it exists)
bin/wt add poc-foo v2 --from try-sqlite  # stack on another branch
bin/wt ls                                # worktrees: branch, vs origin/main, dirty
bin/wt sync                              # refresh every wt/<repo>/main
bin/wt rm poc-foo try-sqlite             # remove (branch kept)
```

`add` also symlinks `.claude` (sessions started inside get the workspace wiring), runs `mise trust`, and `mise run setup` if the repo defines it.

## New POC repo

1. Living doc first: `ctrl-vault/docs/projects/<name>.md` (what/why, status, plan).
2. `gh repo create alexluong/<name> --private --add-readme` (ask before anything public), then `bin/wt init <name>` and `bin/wt add <name> <branch>`.
3. Work only in named worktrees (`wt/<repo>/main` stays read-only). Land per `ctrl-vault/docs/workflow.md`: PR for review, or `git push origin HEAD:main` for the direct flow.

Existing personal repos in `~/git/hub/alexluong/<name>` stay there; `wt init` borrows their objects (`--reference`) if you do pull one in.

## Graduating

When a POC moves to its own workspace (`workspace-setup` skill), remove its worktrees here (`wt rm`), then `rm -rf repos/<repo>.git wt/<repo>` once the new workspace has its clone.
