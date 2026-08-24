# Collie UI: tokens

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
   table inside a roomy app).

**Hard prerequisite:** components must never hardcode spacing. A recipe with a
literal `px-4 py-2.5` is exactly what makes app-level density impossible.
Everything routes through tokens.

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


## Braid's theming, and what to take (2026-08-24)

**Mechanism.** `vars.css.ts` is a `createThemeContract`; `tokenType.ts` is a
TypeScript interface (`BraidTokens`) every theme must satisfy; each theme is one
object of final values; `makeBraidTheme` runs `createTheme(vars, …)` to emit a
class; `<BraidProvider theme={…}>` applies it. Same architecture as ours with three
swaps: their contract ↔ our generated `contract.d.ts`, their `createTheme` ↔ our
Style Dictionary build, their provider class ↔ our `[data-theme]` attribute.

**Braid ships a `wireframe` theme** that collapses every tone to black/white/grey —
independent confirmation of the wireframe-as-a-theme approach.

**A Braid theme contains:** `color.foreground.{tone}` (+`Light`, `neutralInverted`,
`secondary`, `link`), `color.background.{tone}` (+`Hover`/`Active`/`Soft`/
`SoftHover`/`SoftActive`/`Light`), `border.color.{tone}` (+`field`, `focus`),
`border.radius`/`width`, `space.{xxsmall…xxxlarge, gutter}` plus `grid` (base unit),
`typography` (fontFamily, Capsize `fontMetrics`, weights, `heading.level 1-4`,
`text.xsmall…large`, each defined **per breakpoint**), `contentWidth`,
`touchableSize`, `focusRingSize`, `shadows`, `transitions`, `transforms`.

Their background naming is tone × prominence × state (`criticalSoftHover`) — our
`bg.{tone}.subtle-hover` with different spelling; their `Soft` is our `subtle`.

**Have that we don't, and should:** `touchableSize`, `contentWidth`,
`focusRingSize`, and typography as per-breakpoint definitions with Capsize metrics
(text sized in baseline rows with optical trimming). Adopting the typography model
is a real chunk of work and the thing that most affects how the system feels.

**We have that they don't:** a primitive tier. Braid themes hand-author every final
value, so a new theme is dozens of colour decisions with no guaranteed contrast
relationships. Our ramps + fixed step assignments generate all of it from one hue —
that is what makes "a new client brand" cheap, and it is worth keeping.

## Getting a brand colour into the system

Brand enters as a **primitive ramp**, not as a special case: one hex from the
client → twelve generated steps → the semantic accent tokens point at it. Every
component that already understands tones is then correct in that brand with no
component changes.

The complication to plan for: **a brand colour is often not a usable UI colour.**
Brand palettes are picked for logos and marketing and routinely fail contrast at
step 9 (solid fills) or step 11 (text). If the only accent is the brand hue, either
accessibility breaks or the brand renders wrong.

Braid's answer, and the right one: **two accents.**

- **brand accent** — hero moments, marketing surfaces, the literal brand colour,
  used sparingly
- **form accent** — the everyday interactive colour (emphasised action, focus
  rings, links), contrast-safe by construction

Usually both point at the same ramp. When a brand hue can't carry UI weight, the
form accent points at a nearby hue that can, and only the brand accent stays
literally on-brand. Client themes then differ by one or two ramp declarations
instead of a pile of per-component overrides.

Ramp generation from a single hue is not built yet — current ramps are hand-written
OKLCH approximations of Radix gray/blue/red/amber/green.


## Ramps are the real Radix scales now (2026-08-24)

Hand-written OKLCH approximations were replaced by the actual `@radix-ui/colors`
values, via a committed generator (`packages/tokens/scripts/sync-radix.mjs`). The
ramps stay checked in rather than read at build time, so a generated brand ramp can
replace a Radix one per theme without touching the build.

Two things this surfaced:

- **Step 9 → 10 is deliberately a small step.** `blue9 #0090ff → blue10 #0588f0`,
  `gray9 #8d8d8d → gray10 #838383`. Alex noticed hover looked nearly identical to
  rest; that is Radix's intent (a hover shouldn't jump), amplified by the earlier
  hand-written ramps having compressed it further. A more assertive hover is a
  deliberate deviation, not a bug fix.
- **`fg.on-{tone}` is per-tone data, not a constant.** `amber9` is `#ffc53d` — a
  light yellow — so white text on a solid warning fill is unreadable. `on-warning`
  is now `{gray.12}`. Radix documents amber/yellow/lime/mint/sky as needing dark
  foreground on step 9. Any generated brand ramp must decide this too.
