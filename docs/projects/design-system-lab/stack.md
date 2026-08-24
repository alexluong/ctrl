# design-system-lab: stack

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
