# Project: design-system-lab

Exploration of a personal/reusable design system with swappable themes.
Repo: `hub/alexluong/design-system-lab` (code-only + consumer contract in its
`docs/`; all notes here). Remote: github.com/alexluong/design-system-lab (private).

**Name:** "lab" = deliberately an exploration. Not committed to being *the* design
system yet.

**Status:** empty repo + remote created. Design discussion in progress; stack not
chosen; nothing built. (2026-08-23)

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

## Prior art: colliestudio/saasblocks-design-system (2022)

Alex's earlier system. Stack: TW3 + `class-variance-authority` + Radix primitives +
Storybook 6 + a `tailwind-saasblocks` plugin. **The DX ideas are worth carrying
forward; the deps are all stale.** What it got right:

1. **`*.css.ts` recipe layer separate from components.** `button.css.ts` exports
   `cva` recipes returning class strings; `button.tsx` does
   `import * as button from "@/styles/button.css"`. Component logic never knows
   what it looks like. **This is already the mechanism for a wireframe↔polished
   swap.**
2. **Semantic-only class names** — `bg-primary`, `text-heading`, `border-muted-3`.
   Never `blue-500` inside a component.
3. **Themes as objects** (`midnight-envy.theme`, `eggshell-delights.theme`) fed to
   the TW plugin, activated by an ancestor class → nested theming for free.
4. **Adapter layer for stack-agnosticism** — `libs/router` (Link wrapper over
   next/link) and `libs/form` (components receive `useField` **as a prop** rather
   than importing react-hook-form).
5. **Semantic variant axes**: `variant` (solid/hollow/ghost) × `tone`
   (brand/neutral/critical) × `size` × `padding` (relaxed/compact) × `radi`.

Modernization deltas: TW3 plugin → TW4 `@theme` + native CSS vars; cva →
tailwind-variants + tailwind-merge; Radix → headless choice TBD; Storybook 6 → 9.

Clone for reference: `gh repo clone colliestudio/saasblocks-design-system`.

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

## Proposals on the table (2026-08-23, not yet decided)

### Tokens: three tiers, Radix 12-step semantics

Alex's objection — "a 9- or 12-number color scale isn't scalable / too much
flexibility" — is answered by tiering, not by a shorter scale:

| tier | example | visibility |
|---|---|---|
| primitive ramp | `--blue-9`, `--gray-3` | internal, nobody uses directly |
| **semantic** | `--surface`, `--border-strong`, `--text-muted`, `--accent-solid-hover` | **the only public API** |
| component (optional) | `--button-solid-bg` | recipe authors only |

Adopt **Radix Colors' 12-step semantics** — each step has a defined job, so the
numbers stop being arbitrary: 1–2 app bg · 3–5 component bg (base/hover/active) ·
6–8 borders (subtle/default/hover) · 9–10 solid fills (9 = the brand color) ·
11 low-contrast text · 12 high-contrast text. One brand hue in → correct,
contrast-safe ramp out. Authored once per palette generator, not per component.

Format: **W3C DTCG `.tokens.json` + Style Dictionary** — the actual interchange
standard, and the mobile hedge (below).

**Spacing:** no bigger scale. 4px grid + two roles — layout spacing (gap/space) as
tokens, and component **density as a variant** (`relaxed` / `compact`), which
saasblocks already did correctly.

### Theme vs skin (correction to the original mental model)

- **Theme** = token values only. Runtime swap (`data-theme="client-a"`), nests, no
  rebuild. Light/dark, per-client, per-hotel-property.
- **Skin** = the recipe layer (`.css.ts`). Changes which classes are emitted.
  Build/provider-time swap.

**Push to make "wireframe/mocky" a THEME, not a skin** — tokenize `radius`,
`shadow`, `border-style`, `border-width`, `font-family` and wireframe becomes
`radius: 0, shadow: none, border-style: dashed, font: mono, all gray`. Falling back
to skin-swapping means maintaining two component trees, which is the thing that
kills design systems.

### Renderer-agnosticism (elevated 2026-08-23)

If hotel-backoffice is Go/templ, "stack-agnostic" is no longer a nice-to-have —
React components can't serve it at all. saasblocks already anticipated this: it
shipped **both** `apps/saasblocks-react` and `apps/saasblocks-html` over one shared
Tailwind theme plugin.

Implication: the **token layer + recipe layer (`*.css.ts` → plain class strings) is
the actual product**; React components are one thin consumer of it. Class strings
drop into templ unchanged. This also caps how much the headless library can be
allowed to leak into the recipes (Go/templ gets no Base UI / React Aria — behavior
would be hand-written or Alpine/HTMX-side).

### Headless: the date picker is the tiebreaker

| candidate | date picker + TZ | agnostic | note |
|---|---|---|---|
| Base UI | ✗ none | React only | nicest API, Radix/MUI lineage; would need react-day-picker + own TZ layer |
| React Aria Components | ✓✓ (`@internationalized/date`, full IANA) | React only | best a11y available; heavier API surface |
| Ark UI (Zag.js) | ✓ | ✓✓ React/Vue/Solid state machines | Alex already has `zag` cloned locally |

Don't mix libraries. **First real experiment: build the same DatePicker on all
three**, judged on the TZ story and on how much the recipe layer must know about
the primitive.

### Date-lib agnosticism = a rule, not a library

The DS API boundary speaks **ISO 8601 string + IANA tz id**
(`"2026-08-23T14:00:00Z"`, `"Asia/Qatar"`). Never accept or return a `Date`,
dayjs, or luxon object. Internals use whatever the headless lib needs; consumers
convert on their side. Temporal is the eventual internal representation.

### TanStack / framework coupling

Core components stay **dumb and controlled** (`value`/`onChange`/`error`/`name`).
TanStack bindings ship as separate optional entries (`ds/tanstack-form`,
`ds/tanstack-router`); router gets a `LinkProvider` at app root. Core never imports
TanStack. Same pattern as saasblocks' `useField`-as-a-prop, modernized.

### Mobile: don't unify runtimes

Recommendation against RN-Web-one-build: it means rebuilding every component on RN
primitives, losing Tailwind-as-authored, and — decisive — **ENABLE already runs 2
Flutter apps in production**, so RN adds a third runtime rather than unifying
anything.

Instead: **tokens are cross-platform, components are not.** DTCG `tokens.json` →
Style Dictionary → CSS vars (web) + Dart `ThemeData` (Flutter, if ENABLE's apps ever
adopt it) + JS object (if RN ever happens). One visual language, zero runtime coupling. This is the main
reason to adopt DTCG on day one.

### Distribution nuance

Copy-paste suits **components** (clients must diverge). But copy-pasted **tokens**
means clients drift on the visual language itself, defeating the point. Proposed
hybrid: **token/theme layer = versioned package; component layer = copy-paste.**
Shapes the repo layout, so decide early.

## Open questions

- **Stack** — leaning Tailwind (v4) for long-term stability over CSS-in-JS. Not
  formally decided.
- Headless choice — pending the DatePicker bake-off above.
- Package-vs-copy split for tokens vs components.
- Where the visual direction comes from (existing ENABLE look? fresh?).
- **hotel-backoffice frontend: React or Go/templ?** Gates renderer-agnosticism.
- If components are copied, how do fixes propagate to projects that already copied?

## Next step

Two candidate starting points; **(a) recommended** because it determines whether one
component tree suffices, the most expensive thing to get wrong:

- (a) Token layer: DTCG + Radix 12-step + prove "wireframe as a theme".
- (b) Headless bake-off with DatePicker as the test case.

## Consumers

None yet. Track here: project → version/commit copied → what broke on update.
