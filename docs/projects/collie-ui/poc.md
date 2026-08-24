# Collie UI: POC space & layout primitives

Planned 2026-08-24. Nothing built yet.

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
