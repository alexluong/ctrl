# replay — market / prior-art scan

Checked 2026-09-25 by web and GitHub research across 5 parallel tracks. Sources are inline. Items marked **(unverified)** come from third parties, from memory, or from a model-summarized fetch; check them before relying on them.
Context: [README.md](README.md) (idea, lab state, SDK).

## TL;DR

- **Nothing does ≥70% of replay.** The closest are **tracelane** (OSS, ~55–60%, alpha, stalled), **ProofShot** (OSS, video + logs + PR comment), and **Playwright 1.59+ screencast chapters** (native narrated video).
- **The gap is real but narrow.** Nobody combines: agent-written script → **continuous DOM replay** + captions/step markers + synced **console / network bodies / storage** → **small single-file** player that works in any PR without an account.
- **Biggest threat: Playwright itself.** It already has narration (as video) and devtools data (as trace snapshots), in two separate artifacts. If it ever merges them, replay's core overlaps.
- **Build on rrweb, don't fork anything.** rrweb 2.x now ships official network record/replay plugins (with bodies), so capture is mostly upstream. What would be ours: the storage plugin, the `.replay` container, the player with devtools panels, the Playwright fixture, and the agent CLI/skill.
- For Alex's own use it's clearly worth building. As a product it's a niche: the market is moving toward **video** proofs (Cursor, Devin, Factory, Browserbase and Steel all dropped rrweb for video).

## Comparison

Closeness to replay: 1–5, where 5 = replay.

### Tracks closest to the idea

| Tool | Capture | Agent / PW | Console / Net bodies / Storage | Narration | Sharing | Price | Close |
|---|---|---|---|---|---|---|---|
| [tracelane](https://github.com/Cubenest/rrweb-stack) `@tracelane/playwright` | rrweb | PW fixture + reporter; `peek` MCP | ✓ / off by default / ✗ | ✗ | single HTML file | OSS (Apache-2.0); 7★, 45 dl/mo, last push Jul 2026 | **4** |
| [ProofShot](https://github.com/AmElmo/proofshot) | video (webm/mp4) | agent CLI, `proofshot pr` | console + server logs synced / ✗ / ✗ | step timeline | HTML viewer + PR comment | OSS (MIT), ~860★ | **4** |
| [Playwright screencast](https://playwright.dev/docs/release-notes) (1.59, Apr 2026) + [Playwright MCP](https://github.com/microsoft/playwright-mcp) `browser_video_chapter` | video | native | ✗ | **chapters, overlays, action labels** | file | OSS | **4** |
| [Playwright trace viewer](https://playwright.dev/docs/trace-viewer) + trace.playwright.dev | DOM snapshots per action + filmstrip | native | ✓ / ✓ (unverified in docs) / ✗ | `test.step` titles | trace.zip (MBs); static viewer, runs locally | OSS | **3.5** |
| [Cypress Test Replay](https://docs.cypress.io/cloud/features/test-replay) | DOM mutations | Cypress only | ✓ / partial / ✗ | command log | Cloud members only | free 500 results/mo; Team $67/mo | 3 |
| [playwright-recast](https://github.com/ThePatriczek/playwright-recast) | trace.zip → MP4 | PW; MCP | ✗ | **TTS voiceover, subtitles, zoom** | video | OSS, 61★, ~5.6k/wk, active | 3 |
| [dthinkr/playwright-demo-recorder](https://github.com/dthinkr/playwright-demo-recorder) | trace snapshots → click-through HTML | PW; pitched at agents | ✗ | hotspots | single HTML | OSS, 0★, Aug 2026 | 3 |
| [Jam.dev](https://jam.dev/docs/record-a-jam/instant-replay) | DOM replay (rrweb unconfirmed) | manual extension; [Jam MCP](https://jam.dev/docs/debug-a-jam/mcp) *reads* jams | ✓ / likely / ✗ | captions (Team plan) | hosted link | free 30 jams/mo; $14/creator | 4 (same artifact, human-recorded) |
| [OpenJam](https://github.com/lapnd/openjam) (fork) | rrweb | manual extension | ✓ / ✓ / ✗ | mic narration | **single HTML file** | OSS GPL-3, 0★ | 4 (format twin, no agent/PW) |
| [GN Tracing](https://github.com/gnasdev/gn-tracing) | video + DOM snapshots | manual extension; MCP | ✓ / ✓ / **✓** | annotated screenshots | hosted/Drive link | OSS GPL-3, 8★ | 4 (feature twin, video-based, tiny) |
| [AWS AgentCore Browser](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-session-recording.html) | DOM + CDP → your S3 | agent browser | ✓ / ✓ / ✗ | action markers | AWS console | AWS usage | 3 (closest panel set; locked to AWS) |

### Test / debug recording

| Tool | Notes | Close |
|---|---|---|
| [Replay.io](https://www.replay.io) | Time-travel browser. Test Suites shut down Aug 2024 ([pivot](https://www.replay.io/blog/a-new-direction)), then Nut.new, and now "Replay QA" + [Replay MCP](https://docs.replay.io/basics/replay-mcp/overview). Built for debugging; has changed direction often; current lineup **unverified**. $20/mo individual. | 2 |
| [Currents.dev](https://currents.dev/pricing) | Dashboard for PW/Cypress artifacts. From $49/mo. | 1 |
| [Checkly](https://www.checklyhq.com/pricing/) | Synthetic monitoring on PW; traces are an Enterprise add-on. | 1 |
| [Meticulous](https://www.meticulous.ai/how-it-works) | Records real user sessions and replays them per PR for visual diffs. Regression testing, not demos. Pricing sales-led (free-for-OSS claim unverified). | 2 |
| BrowserStack / Sauce / LambdaTest | Session video + logs; BrowserStack has public links. BrowserStack using rrweb is **unverified**. | 1 |
| QA Wolf / Momentic | Managed / AI test platforms, auth-gated artifacts. | 1 |
| Octomind | **Shut down in May–Jun 2026.** | 0 |

### Session replay (production RUM)

All are SDK-in-the-page tools for real-user analytics. None has a test or dev-session mode. All of them now have MCPs that let an agent **read** replays; none lets an agent **create** one.

| Tool | rrweb? | Console / bodies / storage | Sharing | Free tier | Close |
|---|---|---|---|---|---|
| [PostHog](https://posthog.com/docs/session-replay/sharing) | ✓ | opt-in / opt-in / ✗ | **public links + embed** | 5K rec/mo | 3 |
| [Sentry](https://docs.sentry.io/platforms/javascript/session-replay/configuration) | rrweb-derived (unverified) | ✓ / opt-in / ✗ | org-only | 50/mo | 2 |
| [LogRocket](https://logrocket.com/pricing) | own | ✓ / ✓ / ✗ | in-app | trial; $176/mo | 2 |
| [OpenReplay](https://github.com/openreplay/openreplay) (OSS, 12.9k★) | own | ✓ / ✓ / ✗ (+ Redux etc.) | self-host | free self-host | 2 (reference for player UX) |
| FullStory, [MS Clarity](https://github.com/microsoft/clarity-mcp-server), [Marker.io](https://marker.io/features/session-replay) | own | varies; Clarity has no console/net | in-app | — | 1–2 |
| Highlight.io | rrweb | — | **standalone product ended 2026-02-28**, folded into [LaunchDarkly](https://launchdarkly.com/blog/welcome-highlight-to-launchdarkly) | — | 1 |

### Cloud / agent browsers

| Vendor | Recording | Share | Narration |
|---|---|---|---|
| [Browserbase](https://www.browserbase.com/blog/session-recordings) | **dropped rrweb 2026-01-15** → CDP screencast (HLS/MP4) + network | not documented | ✗ |
| [Steel](https://steel.dev/blog/launch-week-v2-recap) | **dropped rrweb 2025-10** → MP4 + clickable agent-action log | — | action timeline |
| [Hyperbrowser](https://www.hyperbrowser.ai/docs/sessions/recordings) | rrweb (+ network) and MP4 | `recordingUrl` | ✗ |
| [Browser Use Cloud](https://docs.browser-use.com/cloud/api-v4/get-shared-session-recording) | MP4 | public share token | ✗ |
| [Kernel](https://www.kernel.sh/docs/changelog) | MP4 + separate console/net telemetry | hosted URL | **named markers → MP4 chapters** (2026-07-31) |
| [Cloudflare Browser Run](https://developers.cloudflare.com/browser-run/features/session-recording/) | rrweb + network API | dashboard / bring your own rrweb-player | ✗ |
| Anchor, Airtop | MP4 / video | API / live view only | ✗ |

Pricing mostly not checked. Browserbase: free, $20/mo, $99/mo.

### How coding agents show proof of work

| Agent | Artifact | Where |
|---|---|---|
| GitHub Copilot coding agent | Playwright MCP screenshots ([2025-07](https://github.blog/changelog/2025-07-02-copilot-coding-agent-now-has-its-own-web-browser/)) | PR description |
| OpenAI Codex cloud | screenshots (~2025-09; [image bug](https://github.com/openai/codex/issues/45731)) | task / PR |
| Google Jules | Playwright screenshots ([2025-08](https://jules.google/docs/changelog/2025-08-07/)) | chat / diff viewer |
| **Cursor cloud agents** | **video + screenshots** (RecordDemo tool, [2026-02](https://cursor.com/changelog/02-24-26)); **posted into PRs** from 2026-04 (opt-in); MP4s reported broken on the forum | web / Slack / PR |
| **Devin** | **annotated video**: chapters, idle cut, assertions ([docs](https://docs.devin.ai/work-with-devin/testing-and-recordings), 2026-05 rework) | app / Slack, not PR |
| Factory Droid Control | before/after videos, title cards ([docs](https://docs.factory.ai/cli/features/droid-control)) | PR / QA report |
| Replit Agent 3 | video replay with sections (date unverified) | in-app only |
| Claude Code | local: browser-pane screenshots, Claude in Chrome `gif_creator`; **cloud: no browser** ([closed not-planned](https://github.com/anthropics/claude-code/issues/75632)) | local / chat |
| Lovable | screenshots | chat |
| Amp | screenshots/videos (unverified) | thread |
| Bolt, v0 | nothing found | — |

Other demo MCPs and skills: [Pagecast](https://glama.ai/mcp/servers/mcpware/pagecast) (GIF/MP4, auto-zoom), Playwright MCP `--record-video` (reported broken, [#1506](https://github.com/microsoft/playwright-mcp/issues/1506)), [mozdowski](https://github.com/mozdowski/playwright-demo-recorder) / [kdjadeja21](https://github.com/kdjadeja21/product-demo-video-agent-plugin) / [product-video-skill](https://github.com/akmishra56/product-video-skill) (narrated MP4 from agent scripts, 0★ hobby projects), [simonw/showboat](https://github.com/simonw/showboat) + [rodney](https://github.com/simonw/rodney) (proof-of-work docs with screenshots, no replay).

**Pattern: in 2026 many small projects are making agent-scripted Playwright demo videos. None of them are DOM replays.**

### Interactive product demos (contrast only, not the target)

Arcade, Storylane, Navattic, Supademo, Walnut, Loom, Tango, Guidde, Scribe.
- Capture is done by a human with a browser extension (screenshots, video, or HTML on $500+/mo tiers).
- AI voiceover is common.
- Their MCPs (Arcade, Storylane, Navattic, Supademo) edit or manage existing demos; they don't capture from a script.
- Priced for sales and marketing. Loom (free–$24/user) is the default people will compare against.
- Sources: [Arcade](https://www.arcade.software/pricing), [Storylane](https://www.storylane.io/pricing), [Supademo MCP](https://docs.supademo.com/customize/mcp-server), [Loom](https://www.loom.com/pricing).

### PR visual tools

Chromatic, Percy, Argos, Lost Pixel and Happo show screenshot or DOM-archive **diffs** as PR checks, from 5k free snapshots, then $100–179/mo. Chromatic and Percy capture DOM archives from Playwright, which is technically close to rrweb, but they display static diffs.

The nearest to a replay is [Argos](https://argos-ci.com/docs/playwright): it hosts the Playwright trace, **only on failure**. Vercel comments have no recording. The [Netlify Drawer](https://docs.netlify.com/deploy/review-deploys/netlify-drawer-for-feedback/overview/) has recordings made by hand.

## Closest competitors (shortlist)

1. **Playwright (screencast chapters + trace viewer).** Free, native, and agents already use it via MCP. Covers narration (video) and devtools data (snapshots) as two separate artifacts. Has no continuous DOM replay, no storage timeline, and no small single file.
2. **tracelane.** Same technical approach (rrweb fixture → single HTML, console/network, MCP), but built for failure handoff, with no captions or storage, bodies off by default, and alpha and stalled. Read its code for tricks (re-injecting on navigation, flushing sessionStorage on pagehide); don't fork it.
3. **ProofShot.** Same audience and flow (agent → proof viewer → PR comment), but video-based, and no network bodies or storage.
4. **Cursor / Devin built-in videos.** Where users actually get demos today, locked into each platform.
5. **Jam.dev.** Same artifact (DOM + console + network link), recorded by a human; an agent can only read it.

## Gaps / whitespace

- **Storage timeline** (cookies + local/sessionStorage on the replay clock): nobody has it except GN Tracing, which is video-based.
- **Captions and step markers over a DOM replay** instead of video: nobody.
- **Network bodies on by default in a devtools-style panel inside one file:** tracelane has bodies off; the trace viewer needs its own viewer and is snapshot-based.
- **A small file (~40 KB) that plays anywhere** (PR, chat, Claude artifact) without an account: hosted players are auth-gated (Sentry, Cypress, Devin), and videos are MBs.
- **An agent that can inspect its own demo** (`summarize`, `frame`): session-replay MCPs read real-user replays, and nothing reads an agent's own demo.
- **A container format:** HAR (network) and the rrweb event schema exist, but there is no standard bundle of DOM + network + storage + markers. `.replay` would be new.
- **Claude Code cloud has no browser.** A self-contained artifact could fill that from local or CI.

## Headwinds

- **rrweb fragility on real sites** (iframes, shadow DOM, canvas, video) is why Browserbase and Steel moved to video. Counter: replay records *your own app under a script*, so those limits bite less. Document them, and keep an optional MP4 (via `screencast.showChapter`).
- **Video is what people already expect** as proof of work. A DOM replay has to be clearly better: inspectable, searchable, small.
- **Playwright could close the gap** by adding continuous replay or captions to traces.

## Verdict

**Yes, there's a real but narrow gap** for "agent-authored, narrated, shareable dev replay with devtools panels". No shipped tool combines all of it. The pieces exist separately:
- Playwright: narration as video, devtools data as snapshots
- tracelane: rrweb + single HTML
- ProofShot: an agent → PR flow

This fits Alex's framing: worth building for his own use, not a market bet. The space is crowded with video tools and unstable (Octomind died, Replay.io keeps pivoting, Highlight was absorbed), which argues for file-first OSS over hosted SaaS.

**Build vs contribute:**
1. Build on **rrweb 2.x** with its official record plugins: console, plus the new `@rrweb/rrweb-plugin-network-record` (Jun 2026, opt-in bodies). Contribute a **storage plugin** and body truncation/masking upstream.
2. Own the Playwright fixture, the `.replay` container, the devtools-panel player, and the agent CLI/skill (`summarize` / `frame`).
3. Interoperate with Playwright: optionally embed or import trace step data, export HAR, map `say()` → `screencast.showChapter` for an optional MP4.
4. Don't fork tracelane; credit it.

## Open follow-ups

- Verify the Playwright 1.61–1.63 details (step subtitles/params in reporting) against the release notes.
- Try tracelane and ProofShot hands-on (about 15 min each) to confirm the gaps.
- Check whether the rrweb network plugin works in the Playwright/`exposeBinding` setup the lab uses.

## Open-core models

Addendum 2026-09-25. Question: how do comparable tools split CLI / self-host / hosted, and what do they charge for? Sources are listed at the end of this section. Items marked unverified are flagged.

| Tool | Client / player | Server | Paid / hosted gates | Self-host footprint | Notes |
|---|---|---|---|---|---|
| **[asciinema](https://github.com/asciinema/asciinema-server)**: **closest analog** (recorder CLI + file format + player + public server) | player Apache-2.0; CLI GPLv3 | Apache-2.0 | none. asciinema.org is free, funded by donations | container + **Postgres required**. Single-user mode skips SMTP; login links go to the logs | CLI points at any server via `ASCIINEMA_SERVER_URL` |
| [Cap](https://github.com/capsoftware/cap) (OSS Loom) | desktop app | AGPLv3 (whole repo) | free = personal use, 5-min links. $29/yr commercial desktop; Pro $12/user/mo (storage, custom domain, teams); SAML +$199/mo | Next.js + Postgres + S3 + compose | nearest *paid* analog |
| [OpenReplay](https://openreplay.com/pricing/) | tracker OSS | AGPLv3 + proprietary EE | SSO/SCIM, audit, multi-tenant, unlimited sessions | compose/k8s; OSS self-host capped ~50K sessions/mo | cap on self-host |
| [PostHog](https://posthog.com/docs/self-host) | MIT | MIT except `ee/` | paid add-ons | "hobby" compose only; k8s support dropped; no guarantees | self-host effectively downgraded |
| [Sentry](https://develop.sentry.dev/self-hosted/) | SDKs (license unverified) | FSL, converts to Apache-2.0 after 2 years (since 2023) | cloud tiers; self-host = "Business plan without limits" | compose, 16 GB RAM min | FSL called "not open source" |
| [Highlight](https://github.com/highlight/highlight) | in repo | Apache-2.0 except `enterprise/` | enterprise self-host | Docker "hobby", 8 GB RAM | acquired by LaunchDarkly; OSS in maintenance only |
| [Plausible](https://plausible.io/blog/community-edition) | script | AGPLv3 (was MIT until 2020) | funnels, SSO, API are cloud-only | CE, 2 releases/yr | relicense accepted |
| [Excalidraw](https://plus.excalidraw.com/pricing) | MIT | collab server MIT | Excalidraw+ $6–7/user: persistence, rooms, history | static core | no backlash |
| Vaultwarden / Gitea / Forgejo | — | AGPL / MIT / GPLv3 | — | **single binary + SQLite** | the self-host experience to copy |
| [Cal.com](https://cal.com/blog/cal-com-goes-closed-source-why), [tldraw](https://tldraw.dev/community/license), Bitwarden SDK | — | relicensed: closed (Apr 2026) / custom license + watermark / non-free SDK clause, later fixed | — | — | backlash cases |
| rrweb Cloud | MIT lib | closed | hosted ingest/search | — | 30K sessions/mo free, then $1.60/1K |
| ProofShot, tracelane | MIT / Apache-2.0 | none | none (tracelane: GitHub Sponsors) | local only | — |

Name clash: a second **tracelane** exists (`tracelane/tracelane`, an "AI agent flight recorder", Apache-2.0).

**Copy:**
- **asciinema's shape:** a permissive format and player, one server codebase, a public instance, and the CLI pointed at any server via one env var (`REPLAY_SERVER`). Single-user login without SMTP.
- **One binary + SQLite** (Vaultwarden, Gitea). This is the main way to stand out against the compose sprawl of Sentry, PostHog, Cap and OpenReplay. It supports the Go single-binary idea.
- **Charge for what costs money to host, not for features:** private sharing, retention, storage, team seats (Cap, Excalidraw+). Self-host gets everything ("self-host = top tier without limits", as Sentry does it).
- **Free tier shaped like Jam's:** unlimited viewers; cap only uploads, length or retention.
- SSO only as a later add-on, if a team customer ever shows up.

**Avoid:**
- Crippling self-host (OpenReplay's cap, PostHog's "hobby").
- A proprietary `ee/` folder: solo maintenance burden, and it breaks "one codebase, 3 modes".
- A free tier limited to personal use (Cap).
- Custom licenses (tldraw).
- **Relicensing later** (Cal.com, tldraw, Gitea → Forgejo fork). Pick once.

**License recommendation:** **MIT on everything, server included.**
- The real risk that someone resells a tiny tool is close to zero.
- MIT gets the most adoption and embedding, which matters most for the format, player and recorder. It also fits Alex embedding the core in his own IDE/harness.
- The advantage is running the instance, not owning the code.
- Fallback if competing hosts ever worry him: **AGPL for the server only, MIT for the rest** (the Plausible/Vaultwarden split). It's OSI-approved, but some companies ban AGPL internally.
- **Skip FSL/BSL.** Not OSI-approved, and the time-delayed conversion only pays off at VC scale.

Unverified: Sentry SDK and Plausible script licenses, PostHog's container count, asciinema's CLI auth flow (believed to be install-ID token + `asciinema auth` URL), whether Highlight's hosted service still runs.

Sources: [asciinema self-hosting](https://docs.asciinema.org/manual/server/self-hosting/), [Sentry FSL](https://blog.sentry.io/introducing-the-functional-source-license-freedom-without-free-riding/), [PostHog helm sunset](https://posthog.com/blog/sunsetting-helm-support-posthog), [Plausible relicense (LWN)](https://lwn.net/Articles/834120/), [Cal.com AGPL/EE](https://cal.com/blog/changing-to-agplv3-and-introducing-enterprise-edition), [Forgejo GPL (LWN)](https://lwn.net/Articles/986998/), [Bitwarden SDK (Register)](https://www.theregister.com/2024/11/04/bitwarden_gpls_password_manager/), [Cap pricing](https://cap.so/pricing), [Jam pricing](https://jam.dev/pricing), [rrweb pricing](https://rrweb.com/pricing), [Highlight → LaunchDarkly](https://highlight.io/blog/joining-launchdarkly).
