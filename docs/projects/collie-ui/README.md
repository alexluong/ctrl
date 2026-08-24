# Project: Collie UI

> **Notice:** Collie UI is an *opinionated experiment*, not a finished product. It
> exists to test a specific set of ideas — zero-style components over slot recipes,
> DTCG-driven semantic tokens, whole-app theme and skin swapping, one system serving
> unrelated products. Expect it to change shape. Nothing here is stable API.

A reusable design system with swappable themes, meant to serve unrelated products
from one codebase. Repo: `hub/alexluong/collie-ui` (code-only; all notes here).
Remote: github.com/alexluong/collie-ui (private).

**Name:** renamed from `design-system-lab` on 2026-08-24. Kept in the `alexluong`
org for now — worth revisiting whether it belongs under `colliestudio`, since
`docs/machine.md` reserves that org for things carrying the company's name.

**Status:** empty repo + remote created. Design discussion in progress; stack
converging (Tailwind primary, Panda as an experiment); nothing built. (2026-08-24)

**Doc map** — Collie UI's notes are a directory (see `docs/workflow.md`):

| file | holds |
|---|---|
| `README.md` | what/why, consumers, decisions, open questions, next step |
| `stack.md` | styling engine, headless, date/tz, i18n, renderer & platform reach |
| `tokens.md` | token systems surveyed, semantic grammar, density, attribution |
| `architecture.md` | zero-style components, anatomy, themes vs skins |
| `tooling.md` | build order, package layout, workshop, playroom, lint, docs |

## Goal & real consumers

Same DX, different UI, across unrelated products:

- **ENABLE** (work, EButler-QA) — this is the actual POC target. `enable-frontend`
  is a pnpm monorepo, ~5 React apps (main / callcenter / operations / passes /
  public) deployed on Cloudflare via wrangler.
- **Hotel back office** — Alex's own project (`ctrl/docs/projects/hotel-backoffice.md`),
  the Go-at-scale learning project: Go backend, web back office, no mobile.
  **NOT TenX / not an EButler product** (corrected 2026-08-23). Same DX, different
  UI. **Open: is its frontend React, or server-rendered Go/templ?** Alex has
  `hub/alexluong/template-go-templ-tailwindcss` locally. If templ, a React
  component library cannot serve it — see "Renderer-agnosticism" below.
- Personal projects later.

## Decisions

- **2026-08-23 — sibling repo, not a ctrl submodule.** Submodules pin a commit
  (ctrl would carry a stale SHA or a dirty pointer for a notes repo that ships no
  code), `docs/machine.md` says "no submodules anywhere" and one exception makes
  future sessions guess which repos are special, and cockpit mode already gives one
  session write access to sibling repos via `additionalDirectories`.
- **2026-08-23 — repo `docs/` allowed here, narrowly.** This is a library with
  consumers; the consumer contract (token names, theme contract, component API)
  versions with the code. Status/ideas/TODOs still never live in the repo.
- **2026-08-23 — distribution leaning copy-paste/template** (shadcn-style),
  because client A and client B genuinely need to diverge. Not final.

## Documentation stance (2026-08-24)

**No "official" docs yet.** Notes and ideas live here in ctrl for now; the repo gets
no `docs/` until the shape settles. Two things to carry forward when official docs
do happen:

1. **Every convention must cite its source** — spec vs. borrowed-from-a-real-system
   vs. our own synthesis, kept distinct (the attribution section above is the
   model). Alex explicitly wants references/inspiration recorded, not conventions
   presented as received wisdom.
2. **Component anatomy is a first-class documented artifact**, not an
   implementation detail. It is the public API of the styling layer — slot names,
   which slots are layout-bearing, and which data attributes each exposes. Needs a
   consistent per-component format when docs happen.

## Open questions

- **Stack** — leaning Tailwind (v4) for long-term stability over CSS-in-JS. Not
  formally decided.
- **`intl` vs `formatter` vs `formatting`** as the package name — leaning `intl`.
- Whether docs stay in Storybook MDX or graduate to a dedicated site.
- **The style-seam shape** — how a component gets its recipes so the skin can be
  swapped (path alias at build time? provider? other?). Undecided; depends on
  renderer-agnosticism and the distribution model.
- Headless: **Base UI preferred** (Alex, 2026-08-24). Remaining question is the
  date/time build, not the library.
- Package-vs-copy split for tokens vs components.
- Where the visual direction comes from (existing ENABLE look? fresh?).
- **hotel-backoffice frontend: React or Go/templ?** Gates renderer-agnosticism.
- If components are copied, how do fixes propagate to projects that already copied?

## Next step

Two candidate starting points; **(a) recommended** because it determines whether one
component tree suffices, the most expensive thing to get wrong:

**Agreed 2026-08-24:** build the full vertical slice with ONE component (Button)
first, then expand component by component. See `tooling.md` for what the slice must
prove. Earlier framing kept below:

- (a) Token layer: DTCG + Spectrum/Atlassian structure + Radix 12-step color +
  space scale, then prove how far "wireframe" gets on tokens alone before any skin.
- (b) DatePicker build on Base UI + `@internationalized/date` (no longer a bake-off
  — Base UI is chosen; this is now a build that also stress-tests the token/recipe
  seam).

## Consumers

None yet. Track here: project → version/commit copied → what broke on update.
