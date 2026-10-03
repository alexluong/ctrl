# Dev skills plan: where the discussion stands

Status: **discussion in progress, nothing installed** (last updated 2026-10-03). Handoff for continuing after a context reset. Research behind it: `dev-workflow-research.md` (visual recap, Sandcastle, pstack, Matt Pocock, codebase-design, zero-tech-debt). Sync model: `workspace-sync.md`.

## Goal

Improve the local dev loop in the working workspaces (cs, enable, hookdeck, solex) by adding a few skills and improving existing ones. ctrl is not where dev happens; ctrl manages and syncs.

## Decided

- **Sync model (Alex, 2026-10-02):** each workspace sets up and adapts its own skills; ctrl ports improvements by hand (`workspace-setup` skill § port). Shared core, probably as plugins, comes later. Keep it simple for now.
- **Sandcastle:** skip (`dev-workflow-research.md` § 2).
- **`retro` (Matt Pocock) → fold into `done`** as one step: a correction made twice, or a mistake a check could have caught, becomes a proposed lint/check/skill edit. No separate skill. (Alex agreed, 2026-10-03.)
- **Suggest first, build after a yes.** A build that falls out of this becomes a board task with a spec (memory `build-as-board-task`).

## Alex's current direction (2026-10-03)

1. **Agent-Native skills (BuilderIO/skills):** wants `visual-recap` and `visual-plan` "and whatever" else is good there. Asked me to look into the whole set. This replaces my earlier suggestion of a home-made HTML recap, which Alex was unsure about ("hmm idk").
2. **Matt Pocock:** `grilling` maybe. `pr` maybe, but as a personal thing: use it to **improve `pr-description` and `gh-respond`, also pulling in ideas from `writing`**.
3. **Poteto (pstack):** incorporate ideas from it too.
4. `codebase-design`, `diagnosing-bugs`, `improve-codebase-architecture`: explained (what / why / when), no decision yet.

## Next steps when the discussion resumes

1. **Read the rest of BuilderIO/skills** and report what each does and when to use it. Read so far: `visual-recap` (SKILL.md, `references/local-files.md`, `references/connection.md`), the README, the PR GitHub Action. **Not read:** `visual-plan` (README paragraph only), `quick-recap`, `plow-ahead`, `read-the-damn-docs`, `agent-watchdog`, `plan-arbiter`, `stay-within-limits`, `efficient-fable` / `efficient-frontier`, `visual-edit`, `rewind`, `webmcp`, `an`, `turn-into-app`, `factory-*`.
2. **Settle how `visual-recap` / `visual-plan` run "local"** (open question 1).
3. **Draft the rewrite of `pr-description` + `gh-respond`** from Pocock's `pr`, `writing`, and pstack's PR playbook, as a proposal for Alex.
4. **List the pstack ideas to land** and where each goes (below).
5. Turn the agreed set into a board task + spec.

## Open questions

1. **Recap/plan hosting.** Builder's skills publish to `plan.agent-native.com` by default (account, diff stored there). Local-files mode (`AGENT_NATIVE_PLANS_MODE=local-files`) keeps content on the machine, but the viewer is still their hosted web UI reading a localhost bridge (needs network + Chrome), and it runs `npx @agent-native/core@latest`. Alex said earlier "don't really want to publish anywhere" and wanted it "slightly custom where it's local". Options: their local-files mode as-is; self-host their Plan app (source open, BuilderIO/agent-native, not evaluated); own renderer. Their no-upload claim for local-files mode is from their docs, not verified by us.
2. **What Alex dislikes about the current `pr-description`.** I read "i actually dont like that one" as the existing skill; unconfirmed. Known tension: Pocock's `pr` is a fixed template (Summary visual / Evidence before-after / Merge Danger with "Blast Radius"); the current skill says "situational sections, not a template" and bans the phrase "blast radius".
3. **Which workspaces get what.** `pr-description` and `writing` exist only in hookdeck; `gh-respond` in enable and hookdeck (diverged); enable has `ship`.
4. `grilling`: in or out. `codebase-design` and `diagnosing-bugs`: in or out.

## Candidate skills

| skill | source | status | when to use |
|---|---|---|---|
| `visual-recap` | BuilderIO/skills (MIT) | wanted; hosting open | an agent finished a large or structural change; before reviewing a big PR; skip small diffs |
| `visual-plan` | BuilderIO/skills | wanted; not read yet | a plan too important to skim in the terminal, before code starts |
| other Agent-Native skills | BuilderIO/skills | to review | — |
| retro step in `done` | Matt Pocock `retro` | agreed | session end |
| `grilling` | Matt Pocock (MIT) | maybe | vague ask; before a spec or a change to an accepted decision |
| `pr` ideas → `pr-description`, `gh-respond` | Matt Pocock `pr` + hookdeck `writing` + pstack | wanted as a rewrite, design open | opening a PR; replying to review comments |
| `codebase-design` | Matt Pocock | undecided | adding a module or abstraction; reviewing one; tests hard to write; real design fork |
| `diagnosing-bugs` | Matt Pocock | undecided | a bug that resisted one fix; flaky failures; perf regressions |
| `improve-codebase-architecture` | Matt Pocock | optional | monthly, or when an area keeps producing bugs |
| `zero-tech-debt` | Jeremy Longshore, not Matt | not adopting; ideas only | — |

## pstack ideas to place (from `dev-workflow-research.md` § 4)

| idea | likely home |
|---|---|
| Finish condition as pass/fail checks, matched to the change type | lead (acceptance criteria wording) |
| Verify on the matching surface; "inconclusive" is not a pass | qa and dev roles |
| Per-project verify recipe: Launch / Doctor / Drive / Evidence / Cleanup + feature map | per workspace; enable and hookdeck QA suites and SoLex journeys are partial versions |
| Bug fix: reproduce first, failing repro committed before the fix | dev role (overlaps `diagnosing-bugs`) |
| The author never judges its own work | already true (reviewer and qa roles) |
| `/blast-radius`: prove the one fact a change is safe because of, by running code | reviewer role, or a small skill |
| Claims labelled measured / inferred / guess | roles' report format; `writing` |
| Lessons become lints | the retro step in `done` |
| Unattended runs: predicate, decision log, different-model review | later; no unattended runs today |
| PR body: Why / Scope / Tradeoffs / Blast Radius / Verification; five narrow PRs over one large | the `pr-description` rewrite |
| Reply style: short declarative sentences, no fabricated links, evidence or label in the same sentence | `writing`, `gh-respond` |

## Constraints to respect

- **Don't write another workspace's repo from ctrl while it has live sessions or its home is another machine.** hookdeck's home is the `hookdeck-ws` VM since 2026-10-03. Put the ask in a ctrl task and hand it to that workspace's lead (memory `shared-checkouts-parallel-sessions`). The `port` mode in the `workspace-setup` skill was corrected to say this.
- ctrl is a shared checkout: pull first, add specific paths.
- Team-facing output in enable and hookdeck must not mention `task-N`, the vault, worktrees or agents.

## What was run and what was not

- Nothing from BuilderIO has been executed. A `npx @agent-native/core` call (block catalog + CLI help) was declined on 2026-10-02, during a trial recap of hookdeck/terraform-provider-hookdeck#230 that Alex then dropped.
- No skill has been installed in any workspace. The only file changes are in ctrl: the docs named here and the `port` mode in `.agents/skills/workspace-setup/SKILL.md`.

## Source clones (this MBP only, gitignored)

`~/workspaces/ctrl/local/trials/`: `builderio-skills` (eb07be6), `cursor-plugins/pstack` (c47b128), `mattpocock-skills` (d81f3a1), `visual-explainer`, `tfph` (provider repo at PR 230). Re-clone on another machine; URLs are in `dev-workflow-research.md`. `zero-tech-debt` was read through the GitHub API (jeremylongshore/tons-of-skills-marketplace), not cloned.

## Round 2 findings (2026-10-04)

### Agent-Native, rest of the set (read from clone eb07be6; nothing run)

- **`visual-plan`: skip the tool, keep the writing rules.** Plan = MDX folder (`plan.mdx`, optional `canvas.mdx`/`prototype.mdx`) of blocks (diagram, data-model, api-endpoint, file-tree, checklist, question form at the end). The comment loop (anchored comments, `get-plan-feedback`, patch, resolve) is hosted-only and needs an account. Local-files mode: agent writes MDX, `npx @agent-native/core plan local serve` runs a localhost bridge, and the browser loads the hosted page at plan.agent-native.com, which fetches from the bridge (Chrome; the docs claim pageviews and error monitoring are sanitized). No comments in local mode. Fully offline only with a self-hosted Plan app (BuilderIO/agent-native). The CLI isn't in the clone, so these claims weren't verified. Rules worth taking (`visual-plan/references/document-quality.md`): settle hard-to-reverse decisions first; name what each step reuses; in/out/deferred scope; open questions in one block, each with a recommended default; one end-to-end smoke test in verification; plan self-contained.
- **Take:** `plow-ahead` (autonomy contract: routine questions become stated assumptions; stop list = secrets, destructive, prod, force-push, reserved decisions, repeated failures; recap Goal / Key decisions / Changes / Validation / Remaining risk) → dev role. `read-the-damn-docs` (triggers that force a docs check; check the registry before adding a dependency) → always-on rule.
- **Adapt:** `agent-watchdog` → reviewer: form your own hypotheses before reading the dev's conclusions; labels Gap / Bug / Verification miss / Scope drift / No issue; say what was verified correct. `factory-babysit-pr` → evidence counts only for the current head commit; unknown ≠ clean. `factory-recover` → lead: resume only if the worktree is still the task's; never reset or stash. `quick-recap` → final status line (DONE / PENDING / BLOCKED). `plan-arbiter`: rare, optional. `factory-human-digest` → human-decision digest that states its coverage.
- **Skip:** `stay-within-limits` (ccusage), `efficient-*` (the lead/dev split already does this), `visual-edit`, `rewind`, `webmcp`, `an`, `turn-into-app`, the rest of `factory-*` (hosted or Agent-Native-specific).

### Matt Pocock, "Fixing the PR Bottleneck" (AI Engineer Paris, uploaded 2026-09-26, https://www.youtube.com/watch?v=LlgiOCmFG_w; transcript read)

- Three brakes: checks → agent review → human review. Checks are cheap; add many. Checks can lie (tautological tests, tests that read structure, mocks that can't fail).
- Coding standards live in a reviewer-only `CODING_STANDARDS.md`, not in AGENTS.md: implement = make it work, review = make it good.
- **Reviewer commits fixes itself and comments only when unsure** (talk only, not in his skills).
- PR body: Summary (visual) / Evidence (before/after) / Merge Danger (one-way vs two-way door + blast radius). A one-way door gets a full human review; a two-way door can be skimmed.
- A human review checks the system that produced the code: never write the same comment twice; every human comment becomes a lint/CI check or a standards line (retro).
- Doesn't cover: PR size, replying to review comments.

### Ponytail (DietrichGebert/ponytail, MIT, 153k★ per GitHub API on 2026-10-04, v4.10.3)

- An always-on "least code that works" ruleset plus 5 skills. Ladder: need it? → already in the repo? → stdlib → platform feature → already-installed dependency → one line → minimum. Never cut: validation at trust boundaries, data-loss handling, security, a11y, anything explicitly asked for. Non-trivial logic leaves one runnable check.
- Plugin installs hooks (SessionStart, SubagentStart, UserPromptSubmit; node) and writes `~/.claude` files. Don't install it; copy the ideas.
- **Take:** `ponytail-review` as a separate reviewer lens (one line per finding, tagged `delete:/stdlib:/native:/reuse:/yagni:/shrink:`, ends `net: -N lines`). Ladder + never-cut list → dev role. Shortcut markers that name their upgrade trigger + a ledger (`ponytail-debt` idea).
