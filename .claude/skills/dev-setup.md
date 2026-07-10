---
name: dev-setup
description: Set up a project for local dev on this machine (fresh clone or new machine) — follow its README setup doc, recreate the pointer CLAUDE.md, verify the build. Also creates/updates a project's setup doc.
user_invocable: true
---

# Local Dev Setup

Get a project running locally, driven by its own setup doc. Conventions: `docs/workflow.md`.

## Instructions

Given a project name (ask if not provided):

1. **Clone if missing** — `gh repo clone alexluong/<name> ~/git/hub/alexluong/<name>`.
2. **Pointer** — recreate the untracked CLAUDE.md + `.git/info/exclude` entry (see /new-project step 4) if absent.
3. **Follow the setup doc** — README's "Local setup" section: install prereqs/tooling, project deps, any codegen. Check the ctrl living doc (`docs/projects/<name>.md`) for personal/machine-specific steps the README can't hold (secrets, signing, service credentials — typically in Vaultwarden).
4. **Verify** — run the documented build + test commands; setup isn't done until they pass.
5. **Repair the doc** — if the README setup section is missing, stale, or a step failed/was undocumented, fix it by inspecting the repo, and commit (`docs: update local setup`). The doc must let a fresh machine go from clone to passing build without guesswork.
