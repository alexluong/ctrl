# Project: design-system-lab

Exploration of a personal design system reusable across projects, with swappable
themes. Repo: `hub/alexluong/design-system-lab` (code-only + consumer contract in
its `docs/`; all notes here).

**Name:** "lab" = deliberately an exploration. Not committed to being *the* design
system yet; rename/fork out when the shape is proven.

**Status:** empty repo created, discussion phase. Nothing built, no stack chosen. (2026-08-23)

## Goal

One place where visual/interaction decisions are made once, then reused across
Alex's projects, with different projects able to look different (theme options)
without forking the components.

## Decisions

- **2026-08-23 — sibling repo, not a ctrl submodule.** Considered vendoring the
  repo into ctrl as a git submodule. Rejected: submodules pin a commit (ctrl would
  carry a stale SHA or a permanently dirty pointer for a notes repo that ships no
  code), `docs/machine.md` states "no submodules anywhere" and one exception makes
  every future session guess which repos are special, and cockpit mode already
  gives a single session write access to sibling repos via `additionalDirectories`.
  Standard hub-and-spoke it is.
- **2026-08-23 — repo `docs/` is allowed here, narrowly.** Unlike an app repo, this
  is a library with consumers: a project using it must be able to learn the token
  names and theme contract without reading ctrl. So the consumer contract versions
  with the code in the repo's `docs/`. Notes/status/ideas still never live there.
- **2026-08-23 — distribution leaning copy-paste/template**, shadcn-style: consumers
  copy source in and own it, rather than installing a versioned package. Not final.

## Open questions

- Target surface / stack — React + Tailwind v4 CSS vars vs framework-agnostic CSS
  vs React without Tailwind. **Deferred, to discuss next.**
- What "theme" actually means here: just color/typography token sets, or can themes
  change component structure & density?
- If copy-paste is the model, how do fixes propagate to projects that already
  copied? (The known cost of shadcn-style; needs an answer before committing.)
- Which projects are the first real consumers (alexluong.com? feed? hotel-backoffice?)
  — a design system with zero consumers proves nothing.
- Where do the visual decisions come from — existing look of alexluong.com, or a
  fresh direction?

## Consumers

None yet. Track here: project → which version/commit copied → what broke on update.
