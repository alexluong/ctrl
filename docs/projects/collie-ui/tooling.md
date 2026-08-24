# Collie UI: tooling & package layout

Decided/proposed 2026-08-24. Nothing built yet.

## Build order: one component proves the whole vertical slice

**Alex's plan, adopted:** build the full system end-to-end with ONE component
(Button), get happy with it, then expand component by component. Button is small
but exercises tokens, variants, slot recipes (root + icon), state-via-data-
attributes, both recipe engines, and the theme swap.

What the slice must prove — if any of these is painful at n=1 it is fatal at n=40:

1. One DTCG source → generated `theme.css` + Tailwind `@theme` + Panda config
2. A recipe with zero React and zero primitive tokens
3. A component with zero style literals
4. Same component, both recipe engines, identical rendering
5. Wireframe theme correct **without touching Button**
6. Density scale swap **without touching Button**
7. Lint rules actually failing on violations
8. Story + Playroom snippet + a11y test

## Package layout (Alex likes this; adopted)

```
packages/
  tokens          DTCG source → theme.css, tailwind @theme, panda config, tokens.d.ts
  recipes-tw      class-string recipes (primary — ENABLE must be Tailwind)
  recipes-panda   the experiment
  ui              primitives — Button, Field, Select, DatePicker. zero logic, zero data
  patterns        composed presentational blocks — PageHeader, DataTable, FormLayout,
                  FilterBar, EmptyState. still pure props
  hooks           UI logic only — useDisclosure, usePagination, useTableState,
                  useFilters. headless, no JSX, NO fetching
  intl            (naming TBD — see below) FormatProvider + Intl wrappers
  icons
apps/
  workshop        Storybook (DS components + patterns)
  playroom        Playroom sandbox
```

**Hard boundary: `hooks` never touches TanStack Query or any transport.**
Data-fetching hooks live in the app (or a `data` package on ENABLE's side). The
moment the DS knows how to fetch, it stops being portable to the hotel app.

`patterns` is the package that earns its keep at ENABLE scale — five apps sharing a
DataTable and a FormLayout saves far more than sharing a Button.

## Presentation / logic split (Alex's stance)

Alex wants presentation and logic separated, with logic sprinkled in via hooks. The
payoff: **a whole screen becomes renderable in Storybook and Playroom** — no
network, no mocking, no auth. Shape at ENABLE:

```
apps/operations/src/features/orders/
  OrdersScreen.tsx            presentational, props only → renders in SB + Playroom
  OrdersScreen.container.tsx  TanStack Query/Form, maps data → props. thin & boring
  orders.fixtures.ts          sample props, shared by stories AND Playroom snippets
  useOrderFilters.ts          UI logic, no fetching
```

Two failure modes to avoid:

- **Over-applying it** — split at the screen / data-owning boundary, not per
  component. A Button never needs a container.
- **Fixtures rotting** — if stories and Playroom snippets invent their own sample
  data, screen stories drift and die. One fixtures module per feature, imported by
  both. This is the underrated glue.

## Workshop: Storybook AND Playroom, they solve different problems

| | Storybook | Playroom |
|---|---|---|
| unit of work | one component, many states | many components, one screen |
| durable? | yes — stories are committed source | no — snippets are URL-encoded, throwaway |
| tests | interaction / a11y / visual / coverage | none |
| themes | one canvas at a time (addon toggles) | **all themes side by side, natively** |
| audience | you, building the component | you + ENABLE's team, exploring a layout |

**Storybook state (checked 2026-08-24): v10.5.10.** Alex's memory of it as heavy and
emotion-based is out of date — SB9 cut the bundle 48% and flattened deps; SB10 went
ESM-only and another 29% lighter, with typesafe CSF Factories. `storybook@10`'s
public dep list is ~10 packages (ws, recast, semver, esbuild, three `@vitest/*`,
icons, global, testing-library) — **no emotion**; `@storybook/theming` never
published past 8.6.14, absorbed into core. The manager UI always ran as a separate
app from the preview iframe, so its styling never entered component bundles; the
real complaint was install weight, and that is the part that got fixed.

**The reason to take Storybook is Storybook Test** — interaction, a11y, visual and
coverage testing over stories, Vitest-powered. For 40 components × variants ×
themes that matrix is the thing you cannot cheaply rebuild. (Approximable with
Vitest browser mode + axe, so not a monopoly.)

**Playroom is the tool Alex remembered:** `seek-oss/playroom`, same org as
vanilla-extract and the Braid design system. Alive — v1.3.0, published 2026-08-12,
4.6k stars. Write JSX in the browser, live preview **across multiple themes and
viewport widths simultaneously**, snippet encoded in the URL so it is shareable.
For a system whose premise is theme swapping, closer to what you want to look at
than Storybook's one-story-one-canvas model. Needs a small adapter: a components
barrel plus a frame component supplying the theme provider.

**This is also Alex's "POC space"** — somewhere to build out a full UX as a
prototype and share it with the team without touching the app. Playroom for
throwaway exploration; Storybook screen-stories (presentational screen + fixtures)
for a POC that should persist.

Landscape checked 2026-08-24: React Cosmos 7.4.0 (8.7k stars, 5 open issues,
active) is a genuinely lightweight alternative. **Ladle is cooling** — npm last
published Nov 2025 — avoid for a long-lived system. Histoire is Vue-first and
stalling (203 open issues). Chromatic = paid visual regression.

**Storybook Composition** (`refs`) lets a top-level Storybook aggregate others —
relevant to where stories live in ENABLE's monorepo. MSW only if container-level
stories are wanted; prefer presentational stories.

## Linting — the value is in the custom architectural rules

Off-the-shelf lint buys little here. The rules that matter:

| rule | catches |
|---|---|
| no raw Tailwind classes in `packages/ui` | components sneaking in styles |
| no primitive tokens in recipes (`gray.7`, `blue-500`) | theming silently breaking |
| no hardcoded spacing/radius/color literals anywhere | density and themes breaking |
| import boundaries `tokens ← recipes ← ui ← patterns` | the layering rotting |
| no `react` import in `packages/recipes-*` | portability rotting |

Tooling: **ESLint 9 flat config + typescript-eslint** (custom rules needed; Biome's
plugin story is not there yet), plus `eslint-plugin-boundaries` or
`no-restricted-imports` zones — or `dependency-cruiser` as a separate graph check.
**Prettier + `prettier-plugin-tailwindcss`** for class sorting, configured to sort
inside `tv()`/`cva()` calls too. Configure **Tailwind IntelliSense** to recognise
those calls early — small setting, disproportionate DX. **Deferred (2026-08-24):**
`syncpack` (dep version consistency) and `knip` (dead exports) — useful later, not
worth setting up now.

## Naming: `formatting` → probably `intl`

Alex dislikes "formatting"; "formatter" reads better but both are too narrow. The
package will hold parsing (localized number input), pluralization, list joining,
RTL direction, and probably message translation — **ENABLE is Qatar, so Arabic and
RTL are coming regardless**. `intl` is honest about that scope and matches the
underlying APIs (`Intl.*`, `@internationalized/*`). Not final.

Formatters to anticipate beyond date/currency/number: percent, compact numbers
(`1.2k`), relative time, duration, file size, units, ordinals, `Intl.ListFormat`,
`Intl.PluralRules`, phone numbers, name/initials, address formatting. Most are thin
wrappers; the value is centralization + locale-awareness by default. Whether it is
one formatter object or several: decide at build time.

## Other tooling to consider

- **Visual regression across themes** — highest-value addition after Storybook,
  because theme swaps break things invisibly. Chromatic (paid, easiest), or free:
  Storybook test-runner + Playwright screenshots, Lost Pixel, Argos.
- **Automated contrast checking in CI** — assert every fg/bg token pair meets
  contrast in every theme. Falls out of the Radix step mapping; catches a broken
  client palette before a human sees it.
- **Token contract check** — the `tokens.d.ts` CI assertion (see `tokens.md`).
- **Figma sync** — Style Dictionary → Figma variables (Tokens Studio), Code Connect
  if ENABLE's designers work in Figma. Defer; DTCG is what keeps it possible.
- **CSS size budget** — Panda vs Tailwind output size is a real datapoint for the
  comparison.
- **Skip Changesets** — no versioning under copy-paste distribution.

## Built so far (2026-08-24, uncommitted)

- `packages/tokens` — DTCG source → `theme.css` (`:root` + `[data-theme=wireframe]`
  + `[data-density=compact]`), `tailwind.css` (`@theme inline`), `contract.d.ts`,
  `tokens.json` + `primitives.json` (feed the docs). Watch mode; ~2–3s from source
  edit to served CSS.
- `packages/recipes-tw` — Button slot recipe. Tone sets component-tier vars,
  hierarchy reads them: 5 + 3 declarations instead of 15 combinations.
- `packages/ui` — Button. Zero class strings.
- `apps/workshop` — Storybook 10 + Tailwind v4, theme/density toolbar globals.
- `apps/playroom` — Playroom 1.3. **Webpack-only**, so the repo now has two
  bundlers; its CSS rule is scoped to `issuer: /node_modules\/playroom/` so our
  stylesheet needed its own style/css/postcss chain, and its babel rule only covers
  `.jsx?` in cwd so workspace TypeScript needed one too (plus `extensionAlias` for
  `./x.js` → `.tsx`). Health: 4.6k stars, last push 2026-08-20, v1.3.0 July 2026 —
  maintained, low volume. Alex is lukewarm on simultaneous multi-theme frames; if
  the second bundler grates, Storybook's viewport addon + theme toolbar cover the
  same ground one-at-a-time and Playroom can be dropped.
- **The compiler now enforces two of the three architectural rules**: the generated
  CSS sets `--spacing: initial`, `--color-*: initial`, `--radius-*: initial`, so
  `p-4`, `bg-blue-500` and `rounded-lg` do not compile. Only "components carry no
  class strings" still needs a lint rule.
- Dev setup: `mise` with per-worktree ports (`scripts/setup-env.mjs` hashes the
  worktree directory name, then probes the port is actually free). `mise run dev`
  runs tokens:watch ::: storybook ::: playroom.

## Docs pages (Storybook MDX, built 2026-08-24)

`Introduction`, `Foundations/Base tokens`, `Foundations/Semantic tokens`,
`Foundations/Tones`, `Foundations/Hierarchy`, `Guides/Anatomy`,
`Guides/Inspirations`. Token tables and swatches render from
`packages/tokens/dist/{tokens,primitives}.json`, so the reference cannot drift from
the source; swatches reference the live CSS variables, so the theme and density
toolbars repaint them.

## Documentation approach

Alex wants a space documenting the full system — anatomy, naming conventions,
principles, token reference. Cheapest-first plan:

1. **Storybook Docs (MDX) to start — agreed 2026-08-24.** Conceptual pages (naming grammar, anatomy
   rules, theming model, contribution rules) plus autodocs per component from
   types. Zero extra infra, colocated, one dev server.
2. **Graduate to a dedicated site** (Astro Starlight or Fumadocs) only if the prose
   outgrows Storybook's reading experience — likely eventually, since Storybook's
   docs UX suits API reference better than essays.

**The anti-rot rule, non-negotiable either way: generate reference docs from
source.** Slot names live in the slot recipe; token names live in the DTCG JSON.
Both are data, so the token reference table and the per-component anatomy table are
**generated, not typed**. Hand-written prose covers the *why* and the conventions;
generated tables cover the *what*. This is what stops the anatomy docs — which Alex
called a huge aspect — from silently drifting from the code, the failure mode that
kills every design system doc site.
