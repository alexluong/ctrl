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

## Research (2026-08-23/24)

### What has actually advanced since saasblocks (2022)

Four of the old stack's assumptions are obsolete, not merely dated:

1. **Tailwind v4 CSS-first `@theme`** — tokens compile to real CSS custom
   properties, OKLCH color. v3 baked the theme into a JS object at build time
   (which is why `tailwind-saasblocks` had to exist); v4 themes are
   runtime-swappable var sets. That plugin no longer needs to be written.
2. **The shadcn registry became a distribution mechanism.** CLI v4 (March 2026):
   namespaced private registries with header auth, `--monorepo`, and
   `registry:base` distributing an **entire design system as one payload**. This
   is the answer to copy-paste-vs-package: copy-paste *with* an update path and a
   versioned source of truth.
3. **shadcn/ui defaults to Base UI since July 2026** (Radix still supported for
   existing projects). Alex's Base UI preference is now the ecosystem default.
4. **DTCG reached its first stable spec Oct 2025** — implemented by Figma, Style
   Dictionary v4, Terrazzo, Tokens Studio, Penpot, Sketch. Token interchange is a
   settled standard now, not a research project.

Modern CSS that changes component design vs 2022: `@layer` (working override
order), **container queries** (density per container, not viewport), `:has()`,
`color-mix()` + OKLCH (generate ramps from one hue at runtime), `light-dark()`.
RSC killed runtime CSS-in-JS; build-time (Tailwind, Panda) won — which suits the
"stable, long-term" requirement.

### Established token systems (full systems, not just color)

| system | structure | why look |
|---|---|---|
| **Adobe Spectrum 2** | published as open data (`adobe/spectrum-design-data`), DTCG-shaped | most complete modern system adoptable wholesale; built for high-density pro tooling; has a real density/scale model |
| **Fluent 2** (Microsoft) | global → alias → component, 600+ tokens | ships identical tokens to React, RN, WinUI — the multiplatform proof |
| **Atlassian** | 391 semantic tokens | best *taxonomy* to copy; `space.100` = 8px (number = % of base unit) |
| **Carbon** (IBM) | background/layer/component + explicit density modes | the "layer" model suits nested surfaces |
| **Open Props** | pure CSS vars, no framework | relevant if hotel-backoffice is Go/templ |
| Radix Colors | color only | a component of a system, not a system |

Underlying naming grammar for all of them: EightShapes / Nathan Curtis —
`namespace-category-concept-property-variant-scale-state`.

**Recommendation: Spectrum 2's structure + Atlassian's naming clarity, expressed
in DTCG, built with Style Dictionary.** Not Material — MD3's tokens drag Material's
visual opinions and component taxonomy along with them.

### Tokens: three tiers

| tier | example | visibility |
|---|---|---|
| primitive ramp | `--blue-9`, `--gray-3` | internal, never used directly |
| **semantic** | `--surface`, `--border-strong`, `--text-muted`, `--accent-solid-hover` | **the only public API** |
| component (optional) | `--button-solid-bg` | recipe authors only |

**Radix's 12-step scale usage IS explicitly documented per step** (Alex asked;
confirmed at radix-ui.com/colors/docs/palette-composition/understanding-the-scale):
1 app bg · 2 subtle bg · 3 component bg normal · 4 hovered · 5 active/selected ·
6 subtle borders/separators · 7 element border + focus ring · 8 hovered border ·
9 solid bg (highest saturation) · 10 hovered solid · 11 low-contrast text ·
12 high-contrast text. So it's 12 shades per hue with an assigned job each — you
never pick a shade because it looks nice. That constraint is the "less
flexibility" Alex wants, but it covers color only.

Format: **W3C DTCG `.tokens.json` + Style Dictionary** — the standard, and the
mobile hedge.

### Density: correction — it is BOTH a scale and a variant

Earlier note said "density is a variant, not a token." Wrong for Alex's case (one
roomy app, one info-dense app). Spectrum solves this with **scale**: the same
semantic token resolves to different px under a different scale (Spectrum ships
desktop vs mobile scales; Carbon discussed condensed/default/cozy modes). Three
levels:

1. **Semantic space tokens** — `space.100`, `space.200` (Atlassian style).
2. **Scale = app-level density**, swapped like a theme:
   `[data-density=compact] { --space-100: 6px; ... }`. Roomy app vs dense app is
   one attribute, zero component changes.
3. **Per-component density variant** — `relaxed | compact`, for exceptions (a data
   table inside a roomy app). This is what saasblocks already had.

**Hard prerequisite:** components must never hardcode spacing. saasblocks'
`button.css.ts` has literal `px-4 py-2.5` — exactly what makes app-level density
impossible. Everything routes through tokens.

### Theme vs skin, and the dev-mode/prod-mode wireframe

The distinction is only *what changes*:

- **Theme** — token VALUES change, class strings identical.
  `[data-theme=wireframe] { --radius-md: 0; --shadow-1: none; --font-sans: mono }`.
  Nests natively, zero JS.
- **Skin** — the RECIPE changes; different classes emitted for the same component.
  `skins/wireframe/button` vs `skins/polished/button`.

**Clarified 2026-08-24: Alex does NOT need skins side-by-side.** The use case is
whole-app modes — a wireframe dev-mode running the full app, polished mode in
production. That is much cheaper: it can resolve at **build time** (one import
indirection aliased per build) rather than through React context with both skins
in the prod bundle. Runtime cost zero, one skin ships.

Two things that keep it cheap long-term:

1. **One import seam, enforced** — components get styles through a single
   indirection, with a lint rule banning direct skin imports and raw Tailwind
   classes in component files. **The seam's shape is undecided** (path alias?
   provider? something else) — depends on decisions not yet made.
2. **The wireframe skin should be mostly generated, not hand-maintained.** If
   tokens carry radius/shadow/border-style/font, wireframe is largely
   `theme(wireframe)` plus a thin overlay for genuinely structural differences
   (images → placeholder boxes, copy → lorem). Target a few hundred lines, not a
   parallel copy of every recipe — otherwise every new component costs 2x forever.

Bonus: wireframe dev-mode doubles as a **conformance test**. Any component that
hardcoded a style instead of using a token will still look polished in wireframe
mode, which makes violations visible. It also surfaces layout/hierarchy bugs that
color and shadow hide.

### Headless: Base UI, with a known gap

Base UI is at **1.7.0**. Ships Combobox, Number Field, OTP Field, Field/Fieldset/
Form, Autocomplete, Menubar, Drawer, Toolbar, etc. **Ships no Calendar, Date
Picker, Date Field, or Time Field** — and that gap is unlikely to close soon.
Alex prefers Base UI over React Aria Components and Ark UI. Accepted; the date
picker becomes a build.

**Build our own date picker — yes, if scoped right:**

- **Don't write:** date arithmetic, DST, tz resolution, non-Gregorian calendars
  (Hijri matters — ENABLE is Qatar) → use `@internationalized/date` (headless, no
  React, tz-aware).
- **Do write:** popover + calendar grid + segmented date field, over Base UI's
  Popover/Field.
- Effort estimate: date field + single-date calendar ≈ a few days; adding range,
  time, and tz picker ≈ 1–2 weeks to production quality.
- Good first build for the lab: exercises tokens, recipes, and the headless seam
  at once.

### Date boundary: ISO string, not `Date`

Alex asked whether a `Date` object would do. No. `Date` is a bare timestamp with no
timezone; it cannot represent "2026-08-23 09:00 **in Asia/Qatar**", and
calendar-only dates (a checkout date) shift by a day depending on the reader's
offset — the classic hotel-booking bug. Boundary is **ISO 8601 string + IANA tz
id**; Temporal is the eventual internal type.

### Formatting layer (Alex flagged as needed across the board)

Needed: number formatter, number text input, currency formatter, date formatter.
`Intl.NumberFormat` / `Intl.DateTimeFormat` handle output; the hard part is
**parsing localized input back** (Arabic-Indic digits, `1.234,56`, currency
symbols) — `@internationalized/number`'s `NumberParser`, same family as the date
lib.

Proposal: `<FormatProvider locale currency timeZone>` at app root + a `useFormat()`
hook (`formatNumber`, `formatCurrency`, `formatDate`, `formatRelative`), with
`NumberInput` / `CurrencyInput` / `DateField` built on it. One provider drives
every formatter and input — the same seam that makes ENABLE's Arabic locale work.

### Renderer-agnosticism (elevated 2026-08-23)

If hotel-backoffice is Go/templ, "stack-agnostic" is not a nice-to-have — React
components can't serve it at all. saasblocks already anticipated this: it shipped
**both** `apps/saasblocks-react` and `apps/saasblocks-html` over one shared Tailwind
theme plugin.

Implication: the **token layer + recipe layer (→ plain class strings) is the actual
product**; React components are one thin consumer. Class strings drop into templ
unchanged. This also caps how much the headless library may leak into recipes —
Go/templ gets no Base UI, so behavior would be hand-written or Alpine/HTMX-side.

### TanStack / framework coupling

Core components stay **dumb and controlled** (`value`/`onChange`/`error`/`name`).
TanStack bindings ship as separate optional entries (`ds/tanstack-form`,
`ds/tanstack-router`); router gets a `LinkProvider` at app root. Core never imports
TanStack. Same pattern as saasblocks' `useField`-as-a-prop, modernized. Base UI's
Field/Form primitives help here.

### Mobile: don't unify runtimes

Recommendation against RN-Web-one-build: it means rebuilding every component on RN
primitives, losing Tailwind-as-authored, and — decisive — **ENABLE already runs 2
Flutter apps in production**, so RN adds a third runtime rather than unifying
anything.

Instead: **tokens are cross-platform, components are not.** DTCG `tokens.json` →
Style Dictionary → CSS vars (web) + Dart `ThemeData` (Flutter) + JS object (if RN
ever happens). Fluent 2 is the proof this works at scale. One visual language, zero
runtime coupling. Main reason to adopt DTCG on day one.

### Distribution

Copy-paste suits **components** (clients must diverge); copy-pasted **tokens** means
clients drift on the visual language itself, defeating the point. The shadcn
registry (CLI v4) now makes the hybrid concrete: token/theme layer as a versioned
package or `registry:base` payload, components pulled from a **private namespaced
registry** so there is a canonical source and an update path.

### Styling engine: Tailwind for ENABLE, Panda as a lab experiment

**Constraint (Alex, 2026-08-24): ENABLE must be Tailwind** — team aspect, not a
technical call. So Tailwind is the primary target. Panda CSS is genuinely
interesting and Alex wants to see how the two stack up.

This is cheap because of the zero-style component architecture: **one `tokens`
package, two recipe implementations** (`recipes-tw`, `recipes-panda`) over the same
anatomies and the same component layer. One extra package buys a real comparison.

**Panda assessment** (researched 2026-08-24):

- Build-time codegen: `panda.config.ts` → generated local `styled-system/` folder →
  static analysis of source → emitted CSS. No runtime.
- Fits the architecture natively: `defineSlotRecipe`, `defineSemanticTokens` with
  conditions, multi-theme output, DTCG-shaped token input are all first-class.
  With Tailwind we hand-assemble three of those four.
- **Non-React story is better than first assumed.** Config recipes emit stable
  semantic class names (`button button--variant_solid button--size_lg`), and
  `staticCss: { recipes: '*' }` pre-generates CSS for all recipe variants
  regardless of JS usage. A templ/Rails/Django template can emit those names
  against a prebuilt stylesheet — nicer than the Tailwind equivalent, where the
  same button is a 40-utility soup the template must reproduce exactly. Panda docs
  frame `'*'` as mainly for Storybook and warn about combinatorial blowup; for a
  ~30-recipe design system that is the intended use.
- **Risks:** v2 is in beta now (`2.0.0-beta.14`, Aug 15 2026) — start on 1.12
  stable, expect a migration. Bus factor: 18 of the last 40 commits are Segun
  Adebayo personally. **Chakra v3 does NOT use Panda** (only
  `@pandacss/is-valid-prop`; it ships its own styled-system) — so "backed by
  Chakra" is false; Park UI is the main downstream. Codegen is a papercut for
  copy-paste consumers (`panda codegen`, gitignored `styled-system/`). Choosing
  Panda alone would forfeit the shadcn component corpus.
- Health check (Aug 2026): Tailwind 4.3.3 / 97.3k stars · Panda 1.12.0 / 6.2k ·
  vanilla-extract 1.21.2 / 10.4k (adoption plateaued ~450k wk) · StyleX 0.19.0 /
  9.8k (still pre-1.0) · UnoCSS 18.9k (API churn). None is a maintenance risk
  near-term; StyleX and UnoCSS ruled out.

### Component architecture: zero-style components + slot recipes

**Alex's stance (2026-08-24), adopted:** components carry NO styling at all. Break
every component into its shape (Base UI style) and let recipes supply everything.

- **Every component needs a documented anatomy** — the named parts/slots. This is
  the public API of the styling layer. Example: `Button → root, icon`;
  `Field → root, label, control, description, error`;
  `DatePicker → root, field, segment, trigger, popup, calendar, header, nav, grid,
  weekday, cell, day`.
- **Recipes become slot recipes**, returning a class string per slot.
- **State travels via data attributes, not props.** Base UI already emits
  `data-disabled`, `data-selected`, `data-highlighted`, `data-open`, `data-checked`.
  Recipes style off those; the component never passes state into the recipe. Only
  design variants (size, tone, variant, density) cross the boundary. This is what
  keeps the recipe layer React-free and portable.
- **Payoff: the wireframe skin can be generated, not written.** Because a skin is
  just "functions returning class strings per slot", a JS Proxy can return a
  dashed-outline fallback for any unknown component/slot, with a few hand-tuned
  exceptions for layout-bearing slots. New components get wireframe support for
  free — this kills the earlier "2x maintenance forever" objection and makes the
  provider seam (Option 3) cheap enough to be the default rather than a fallback.
- **Costs to watch:** over-slotting (a slot exists only when it can be styled
  independently AND something plausibly would); and **layout has to live
  somewhere** — `flex`, `grid-cols-7`, `gap` are structural, so either the
  component keeps them (violating "zero style") or skins must honor a layout
  contract. Leaning toward the latter, with layout-bearing slots documented.

### Semantic tokens: the grammar

Role first, then intent, then prominence, then state:

```
color.{role}.{intent}.{prominence}.{state}
      bg      accent    solid       hover
      fg      neutral   subtle      active
      border  critical  muted
              success / warning / info
```

Role-first because it reads correctly at the point of use (`bg-accent-solid`,
`text-fg-muted`).

**The mapping that hides the 12-step scale** — semantic names as a fixed function
of Radix step, written once and applied to every intent:

| semantic token | step |
|---|---|
| `color.bg.canvas` | 1 |
| `color.bg.surface` | 2 |
| `color.bg.{intent}.subtle` | 3 |
| `color.bg.{intent}.subtle.hover` | 4 |
| `color.bg.{intent}.subtle.active` | 5 |
| `color.border.{intent}.subtle` | 6 |
| `color.border.{intent}` | 7 |
| `color.border.{intent}.hover` | 8 |
| `color.bg.{intent}.solid` | 9 |
| `color.bg.{intent}.solid.hover` | 10 |
| `color.fg.{intent}` | 11 |
| `color.fg.{intent}.strong` | 12 |

Plus `color.fg.on-{intent}` (contrasting text on a solid fill — Radix ships this as
a "contrast" color, not a step). Six intents × the table ≈ 60 generated tokens,
and nobody ever types a number.

**Structure: the semantic layer is written once; modes swap what it references.**

```
packages/tokens/src/
  primitive/  color.light.tokens.json, color.dark.tokens.json, scale.tokens.json
  semantic/   color.tokens.json (references only, mode-agnostic), space, typography
  theme/      wireframe.tokens.json, compact.tokens.json (override semantic)
```

Dark mode needs zero changes in the semantic layer — `{gray.1}` resolves against
whichever primitive set is loaded. Light/dark/high-contrast/per-client are all
primitive swaps; the semantic tier is the stable contract.

**Non-color semantics matter equally:** `space.100` (Atlassian convention: number =
% of the 8px base; density = a theme repointing these), typography as **composite
tokens** (one token = family+size+line-height+weight+tracking, preventing the
classic size/line-height drift), `radius.{sm,md,lg,full}`,
`shadow.{raised,overlay,sunken}` (named by elevation purpose, not blur),
`border.width.*`, `duration.*`, `easing.*`, `z.*`.

**Build output from one DTCG source:** `theme.css` (`:root` + `[data-theme]` +
`[data-density]`), `tailwind.css` (`@theme`), `panda.tokens.ts`, and `tokens.d.ts`
— the **contract**: a union of every semantic token name, asserted in CI so a theme
missing a token fails the build instead of silently falling back.

**Two rules:** (1) a semantic token exists because of a *reason it differs*, not a
*place it is used* — `color.bg.button` is a tier-3 component token, not semantic;
(2) components may only reference semantic tokens — a primitive in a recipe is a
lint error.

### Where the naming grammar actually comes from (attribution)

Alex asked for sources. Separated by kind, because they are not equivalent:

**Actual spec — one, and it does not cover naming.** W3C DTCG specifies the file
format only (`$value`, `$type`, `$description`, groups, `{group.token}` aliases,
composite types `typography`/`shadow`/`transition`/`border`). **Naming is
explicitly out of scope.** No spec anywhere mandates `color.bg.accent.solid`.

**Documented conventions from real systems:**

- **GitHub Primer** (verified directly): `--[category]-[role]-[prominence]`.
  Categories `fgColor`, `bgColor`, `borderColor`, `shadow`; roles `accent`,
  `danger`, `success`, `attention`, `neutral`, `muted`, `default`; prominence
  `emphasis` (high contrast) / `muted` (reduced) / `default` (base). Examples:
  `--bgColor-danger-emphasis`, `--fgColor-default`. Component tier:
  `--button-primary-bgColor-rest|hover|active`. **Role-first with a prominence
  modifier is Primer's published grammar — the word "prominence" is theirs.**
- **Atlassian**: `color.background.accent.blue.subtle`, `color.text.subtlest`,
  `space.100`. Prominence is a ladder (subtlest → subtler → subtle → default →
  bold → bolder → boldest). The `space.100` = 8px convention is confirmed; the
  ladder terms are from memory (their token table is JS-rendered and could not be
  fetched).
- **Radix Colors**: the per-step usage table is verbatim from their docs, verified.
- **Three tiers**: universal under different names — MD3 (reference/system/
  component), Fluent 2 (global/alias/component), SLDS (primitive/alias/styling
  hook), Carbon (background/layer/component).
- **EightShapes / Nathan Curtis, "Naming Tokens in Design Systems"** (2020): the
  cited taxonomy — namespace, object, base, modifier; category / concept /
  property / variant / state / scale. Influential blog post, **not a standard**.

**What is Claude's synthesis, not received wisdom** (flagged so it can be
challenged):

- The step→semantic-name mapping table above. The step *usages* are Radix's
  documented ones; the names assigned to them are synthesis.
- **State suffixes at the semantic tier** (`.hover`, `.active`) — a **real
  divergence from Primer**, which keeps rest/hover/active at the *component* tier
  only and leaves the semantic tier stateless. Primer's is arguably more
  disciplined; ours means fewer component-tier tokens. **Open decision.**
- "Prominence" stretched to cover `subtle | muted | solid` — mixes Primer's
  vocabulary with Radix Themes' variant names.
- The CI theme-contract check — from vanilla-extract's `createThemeContract`, not a
  token naming convention.
- The two rules above — a formulation of a widely-held principle, not a citation.

**Standing recommendation: adopt Primer's grammar wholesale** rather than
synthesizing one, so the naming decision is defensible by reference instead of
argument. That leaves only the stateless-semantic-tier question to decide.

Reference links: primer.style/foundations/primitives/color ·
radix-ui.com/colors/docs/palette-composition/understanding-the-scale ·
w3.org/community/design-tokens · atlassian.design/foundations/spacing ·
medium.com/eightshapes-llc/naming-tokens-in-design-systems-9e86c7444676 ·
panda-css.com/docs/concepts/recipes

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

- (a) Token layer: DTCG + Spectrum/Atlassian structure + Radix 12-step color +
  space scale, then prove how far "wireframe" gets on tokens alone before any skin.
- (b) DatePicker build on Base UI + `@internationalized/date` (no longer a bake-off
  — Base UI is chosen; this is now a build that also stress-tests the token/recipe
  seam).

## Consumers

None yet. Track here: project → version/commit copied → what broke on update.
