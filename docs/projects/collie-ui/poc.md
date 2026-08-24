# Collie UI: POC space & layout primitives

Planned 2026-08-24. Built 2026-08-24 — results at the bottom.

## Why

Two things are unresolved in the abstract and cheap to resolve against real
screens:

1. **The closed-system goal** ("app code writes no CSS") is only credible once
   layout is expressible through components. Until `Stack` / `Inline` / `Columns` /
   `Box` exist, the rule just blocks people.
2. **The mechanism needs evaluating against real UI**, not one Button. Alex wants a
   space to build POC screens, share them with the team, and judge the DX.

Evidence it is needed: the Button stories already reach for
`<div className="flex items-center gap-100">` because there is no `Inline` — the
first app-shaped code written against the system immediately wanted a utility.

## Layout primitives (first set)

Modelled on Braid's, adapted to Tailwind class strings:

- **`Box`** — the escape valve with a constrained API: padding, margin, background,
  border, radius. Token values only.
- **`Stack`** — vertical rhythm, `space` prop. The most-used component in any
  Braid-shaped system.
- **`Inline`** — horizontal flow with wrapping and alignment.
- **`Columns`** — proportional side-by-side layout, responsive.
- Later: `Tiles`, `ContentBlock` (max-width container), `Divider`.

Open: whether responsive values use Braid's prop-object syntax
(`padding={{ mobile: 'small', tablet: 'large' }}`) or Tailwind-style breakpoint
props. Earlier leaning was against the prop-object form since `p-100 md:p-200` is
terser and familiar — but under the closed-system goal, app code never writes
either, so this is purely about the component API's own shape.

## POC screens

A dedicated space in the workshop (not shipped, not part of the component library)
for full-screen composition:

- **Settings page** — form-heavy: labelled fields, grouped sections, save/cancel
  actions, destructive zone. Exercises Field, Stack, hierarchy + tone on actions.
- **Order list** — data-heavy: table or list, status badges (the *status* tones
  that buttons should not have), filters, pagination, empty state. Exercises
  density, patterns, and the tone split between actions and status.

Both must be buildable **without a single utility class in the page file** for the
closed-system goal to hold. Where that fails, the gap is a missing primitive — and
that list is the actual output of the exercise.

These double as the "share a full UX with the team" surface Alex asked for: a POC
screen rendered in Storybook, in both themes, at any viewport.

## Results (2026-08-24)

Both screens were built and **neither page file contains a single `className`**.
The closed-system goal holds for these two shapes of screen.

### The bug the exercise found

Button's tone variants were built by interpolation:

```ts
const tone = (name) => `[--btn-solid:var(--collie-color-${name}-solid)]`;
```

Tailwind finds utilities by **scanning source text**, so none of those classes
were ever generated. Every tone had `--btn-solid` unset — the tone axis had been
dead the whole time, and the docs page that showed tones was reading token JSON,
so nothing looked wrong. The only such class in the built CSS came from a code
sample inside an MDX doc.

Rule from this: **recipes write every class out in full.** A shared constant is
fine (its literal text is in the file); interpolation is not. Worth a lint rule
later.

### Tokens that had to exist before layout could

Tailwind's own defaults were leaking in for anything we had not tokenised —
`text-sm`, `font-medium` and `leading-normal` were all Tailwind's, not ours. Added
as semantic tiers, with the matching namespace resets so the defaults no longer
compile: `text` (font size), `leading`, `weight`, `container` (max widths), and
`space.0 / 400 / 600` for page-level gutters.

Verified: `p-4` and `bg-blue-500` do not compile; `p-400` does.

### Data point for the space-naming question

Numeric token keys (`100`, `200`) become **number** keys in TypeScript, which
forced `<Stack space={200}>` — braces at every call site. Quoting the keys in the
recipe (`"200"`) restores `space="200"`. So the numeric scale is usable in JSX,
but only because of that detail; a t-shirt scale would never have hit it.

### Primitives the screens demanded

Beyond the planned four: `Container` (max-width), `Divider`, `Text`, `Heading`,
`Badge`, `TextField` / `TextAreaField` / `SelectField` / `CheckboxField`, and
**`Table`** — Braid has no table, but a back-office system (ENABLE, hotel) cannot
do without one. Two smaller gaps surfaced mid-build: `Box` needed an `overflow`
variant (horizontal table scroll), and fields needed `hideLabel` (a filter bar
wants the label for screen readers only).

### Tone subsetting, tested for real

Button and Badge became the first two consumers of the tone system, and they want
different subsets. Button takes `neutral | accent | critical` — the tones an
*action* can have. Badge takes all five, because `warning` and `success` describe
the state of a thing, not the intent of a click. Same tokens, different reachable
subset per component. This is now documented on the Hierarchy docs page.

### Still open after the exercise

- Breakpoints are not tokenised — `Columns collapseBelow` uses Tailwind's default
  `sm`/`md`. The responsive-syntax question above is still unanswered.
- `min-h-[6rem]` on the textarea is a raw value with no token behind it.
- No focus-ring token; focus borrows `border-{tone}`.
- No icon story at all — `leading`/`trailing` on Button take any node.

## Second round (2026-08-24): four more screens + overlays

Screens now in the workshop under **POC/Screens**: dashboard, tenant list, tenant
detail, integrations, settings, order list (plus an empty state). A generic SaaS,
so the team can read them without domain context.

Still **zero `className` in every POC file**, including the shared `parts.tsx`
(PageHeader, Card, Panel, DetailRow, Page).

### Base UI is in, and the headless seam works

Installed `@base-ui/react@1.7.0` to build Dialog, Drawer and Tabs. This was the
first test of whether recipes can dress a *headless library* rather than plain
DOM, and it holds: Base UI parts take `className`, so a slot recipe styles them
exactly like our own elements, and component state arrives as data attributes
(`data-selected`, `data-starting-style`, `data-ending-style`) which Tailwind
targets directly. No wrapper divs, no style props, no CSS file.

Two things worth knowing about 1.7.0:

- It ships a **`Drawer`** with swipe/snap points, built for mobile sheets. Our
  `Drawer` is a side-anchored `Dialog` instead — full control of the transition,
  no swipe machinery to fight. The real one is there if a mobile sheet is wanted.
- It ships **`internals/temporal`** with date-fns and Luxon adapters. Relevant
  whenever the date/timezone boundary question comes back.

### The bug this round found: portals escape the theme

`data-theme` was being set on a wrapper `<div>`. Dialogs portal to `<body>`, which
is *outside* that wrapper — so every overlay would have rendered in the default
theme regardless of the toolbar. Fixed by putting the attributes on
`document.documentElement` in both Storybook's decorator and Playroom's frame.

Rule: **the theme belongs on the document root.** Any app adopting this has to do
the same, and a wrapper-div theme is a bug waiting for the first modal.

### Tokens added this round

`color.bg.overlay` (the scrim — needed a new alpha primitive, `blackA`) and
`shadow.overlay`. Wireframe theme overrides the shadow to `none`.

### Components added

`Tiles` (responsive grid), `Avatar` (initials), `Dialog` / `DialogPanel`,
`Drawer` / `DrawerPanel`, `Tabs` / `TabList` / `Tab` / `TabPanel`, and a bare
`Checkbox` (the field-wrapped one is wrong inside a table cell).

### Smoke test

`mise run smoke` server-renders all six screens through Vite's SSR pipeline and
is part of `mise run check`. It catches what typechecking cannot — a component
that throws on first render. Not a substitute for Storybook Test later; it is
about 30 lines and costs a second.

### Docs

Added **Foundations/Typography**, rendered from the token JSON like the other
token pages, plus stories for Overlays, Tabs, Layout, Typography and Fields.

### Gaps still open after this round

- **No icon system.** Every screen leans on text-only buttons. This is the most
  obvious next hole.
- Breakpoints still untokenised; `Tiles` and `Columns` use Tailwind's defaults.
- No toast/notification surface, no menu, no tooltip, no pagination component
  (the tenant list hand-composes one from Buttons and Text).
- `Table` has no sorting, selection state or sticky header — the tenant list
  fakes bulk selection with `defaultChecked`.
