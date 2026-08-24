# Collie UI: architecture

### Theme vs skin — revised 2026-08-25: "skin" is mostly dead

Alex pushed back on the distinction ("idk i like or fully appreciate the
differentiation"). He was right, and an experiment settled it.

**A theme is token values only. It has never required a line of component CSS.**
Four themes ship and nothing in `packages/ui` or `packages/recipes-tw` knows any
of them exists.

The old theory said a *visual* change is a theme and a *structural* change needs a
skin. That line does not exist. Where it falls is decided by **where you put the
knob**, not by the kind of change:

- Wireframe was the poster child for "needs a skin" — square, dashed, grey,
  monospace. It is a theme, entirely.
- "`secondary` is an outline" vs "`secondary` is a tonal fill" looks structural.
  It was hard-coded in the recipe, so it looked like it needed a second recipe.
  Moved into a component-tier token (`--collie-button-secondary-bg`), it became a
  four-line theme override — sandstone ships it.

So it is a dial, not a dichotomy: the more component-tier tokens a recipe reads,
the more a theme can reach. **Cost:** every such token is public API forever. Add
one when a second theme actually needs it, never speculatively.

What genuinely cannot be a token is anything that changes **what renders** — slot
count or order, element type, a native checkbox vs a custom one, an image
replaced by a placeholder box, real copy replaced by lorem. That is a DOM
difference, not a value difference, and it is the *only* surviving skin use case:
the wireframe dev-mode idea below.

**Vocabulary going forward: theme (token values) and variant (a component prop).**
Drop "skin" unless and until the wireframe dev-mode is actually built.

### The original theory, kept for context

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
