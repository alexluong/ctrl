# Collie Demo: sample end state

**DRAFT, pending Alex's review (2026-09-25).** This is a strawman of "done": one concrete scenario to test with agents that have real finished PRs (the walkthroughs). Everything here is hypothetical. Names are placeholders: the `demo` CLI, the `.demo` file and `demo.collie.studio` (Alex's domain idea; see README § Naming).

## Cast

- **Author:** a coding agent that just finished a PR (e.g. `solex-dev`, feature "move a guest to another room mid-stay").
- **Reviewer:** Alex, on GitHub or on his phone.
- **Second viewer:** a non-technical teammate (e.g. the hotel owner) who wants to see what changed, not how.
- **Server:** Alex's instance at `demo.collie.studio`, team workspace `solex`.

## The flow

### 1. The author decides to demo
The agent's skill says: after a user-visible change, record a demo before opening or updating the PR. The repo has a `demo.config` with the app's start command and seed state (seeding and sign-in are the journey's or the app's job, not ours).

### 2. It writes a throwaway journey
It creates `.demo/room-move.demo.ts` (gitignored), ~20 lines of plain Playwright plus our few verbs:

```ts
import { demo } from "@collie/demo";

export default demo("Move a guest mid-stay", async (r) => {
  await r.slide.title("Room move", "Guests can switch rooms without a new booking");
  await r.slide.diff({ base: "main", paths: ["src/stay/move.ts"] });

  await r.go("/stays/S-1042");
  await r.say("Guest in 204 wants a quieter room");
  await r.click("Move room");
  await r.pick("New room", "311");
  await r.say("Charges split at the move date; one folio stays");
  await r.click("Confirm");

  await r.expect(r.page.getByText("Room 311")).toBeVisible();
  await r.say("Folio shows both rooms, no duplicate night");
});
```

### 3. It runs it
```
$ demo run .demo/room-move.demo.ts --logs
browser  system Chrome 131 (headless)
app      started via demo.config `start: pnpm dev` → http://localhost:5173
steps    6 · 1 slide · 1 diff · 1 expect ✓
wrote    out/room-move.demo  (11 KB, 24 s)
```

### 4. It checks its own work before sharing
```
$ demo summarize out/room-move.demo
00:00 [slide] Room move
00:03 [diff]  src/stay/move.ts  +41 −6
00:06 step 1  Guest in 204 wants a quieter room
00:11 step 2  Charges split at the move date…   POST /api/stays/S-1042/move 200 (84 ms)
00:18 step 3  Folio shows both rooms…           ✓ expect
console: 0 errors · network: 0 failures · storage: 1 change
```
If something looks off (a spinner, a 500, a console error), it runs `demo frame --step 3` for a PNG, fixes the journey or the code, and re-runs.

### 5. It publishes
```
$ demo publish out/room-move.demo
https://demo.collie.studio/d/7fq2k   (team-only)
teaser   out/room-move.gif   (local; drag into the PR)
```
It authenticates through `DEMO_TOKEN`, a workspace token that can only publish, so this works in cloud/CI too. Redaction runs before upload (auth headers, cookies, secrets, password fields).

### 6. It links the demo in the PR
```md
## Demo
[▶ Move a guest mid-stay (24 s)](https://demo.collie.studio/d/7fq2k)
<GIF teaser attached from out/room-move.gif>
1. Guest in 204 wants a quieter room · 2. Charges split at the move date · 3. Folio shows both rooms ✓
```
GitHub won't embed the player. The **full demo is team-only** on the server; the GIF is only a **local teaser file** that the CLI generates, never served publicly by us (Alex, 2026-09-25).

- GitHub has no official API for uploading images into PR bodies (`gh` can't), so by default a human drags the GIF in (the CLI prints its path). On a private repo the attachment is visible only to repo members, which matches the team model.
- Alternatives: commit the GIF to a demo branch/assets path, or an opt-in per-workspace public preview URL (off by default).
- Without the GIF, the PR still gets the link + the step list. **Walkthrough question:** is that enough for agents working alone?

### 7. Alex reviews it
He opens the link and sees the **dev view**:

```
┌───────────────────────────────┬──────────────────────────┐
│                               │ Steps  Console  Network  │
│   replay of the app           │ Storage  Server          │
│                               │ ▸ 1 Guest in 204…        │
│                               │ ▸ 2 Charges split… ← now │
│ ▌caption: Charges split…      │   POST /move 200  ⧉ trace│
├───────────────────────────────┴──────────────────────────┤
│ ▶ ──●──────◆────◆──────◆─────  0:11 / 0:24   1× 2×       │
└──────────────────────────────────────────────────────────┘
```
He jumps to step 2 and clicks the POST to see the body and the trace waterfall. If he's curious, he checks the diff slide against the code. He approves without checking out the branch.

### 8. The teammate watches it
The same link with `?view=reviewer`: big captions, it pauses at each step with a Next button, and there are no dev panels. Or an mp4 exported for a chat app.

## Also in the end state (not in this scenario)

- **Local only:** `demo open out/room-move.demo` opens the player with no server and no account.
- **Before/after:** `demo run … --compare main` for bug fixes.
- **Backend-only features:** the `http` stage (API calls → responses, spans, DB diff, webhooks received).
- **Humans record too:** the in-page widget in the app's dev mode, same file, same publish.

## What "done" means (success criteria)

1. An agent goes from "PR finished" to "link in the PR" **without human help, in under 5 min**, with a journey under ~30 lines.
2. The reviewer understands the change **without running the branch**.
3. A non-technical viewer can follow it with no explanation.
4. The file stays under ~100 KB without the trace, and plays offline.
5. No secrets are ever published (redaction is on by default).
6. Self-hosting is one binary (or one container) plus SQLite.

## Open, for review

- **`--logs` needs the runner to own the app process.** We can't capture the stdout of an app that's already running. So either a `demo.config` start command (like Playwright's `webServer`; assumed above), or logs from a file or `docker logs`. (collie-lab)
- Lab feasibility of the rest: nothing is impossible. Slides as player-side events, not DOM injected into the app; `frame` and mp4/GIF need a headless browser (mp4 also needs system ffmpeg). Full rundown: [engineering.md](engineering.md).

- Is the journey in TS/Playwright the right authoring surface for agents, or should it be a smaller DSL/YAML?
- Is `r.slide.diff` in scope, or does the PR diff speak for itself?
- Should the agent demo every PR, or only when asked or when the change is user-visible?
- Where do demos live over time: in the PR only, or in a workspace list/collections?

## Walkthrough prompt (for step 2 of the plan)

> Here's a sample end state for a tool called Collie Demo (end-state.md). It doesn't exist yet. Take the PR you just finished and, **as if the tool existed**: (1) write the journey you'd record, (2) list the commands you'd run, (3) write the PR "Demo" section. Then tell us: what you reached for that isn't there, what felt wrong or too heavy, what you'd skip, and what a reviewer of *your* PR would most want to see.
