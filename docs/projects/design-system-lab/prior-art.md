# design-system-lab: prior art

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
