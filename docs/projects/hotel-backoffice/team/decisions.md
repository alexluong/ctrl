# Decisions

Format: `### D-n · title` → Status (Proposed / Accepted / Superseded), date, by, context, decision, consequences.

### D-1 · Go, no VM, Cloudflare hosting
Superseded by D-3 (Go dropped; no-VM + Cloudflare stand) · 2026-09-19 · Alex. Context: wants Go, wants to ship, won't run a VM. Consequence: WS1 spike = Go on Cloudflare Containers; fallback WASM.

### D-2 · Notes live in ctrl, one owner per file
Accepted · 2026-09-19 · architect. See `agents/README.md` protocol.

### D-3 · Plain Cloudflare Workers + TypeScript. No Go.
Accepted · 2026-09-19 · Alex. Context: Go-on-CF needs Containers (Workers Paid) or WASM (rough); Alex: "go simple Workers/TS, no need to worry about Golang." Consequences: free tier OK; Workers-native storage (D1 / DO / KV) in play; frontend naturally TS/React (helps collie-ui's React-vs-templ Q); the "Go-at-scale learning project" framing in `docs/stack.md` / `docs/ideas.md` no longer applies to SoLex. Spike scope shrinks to: Worker + D1 hello-world + dev loop + deploy.

### D-4 · Rebuild for data ownership; core subset + enhancements, not a clone
Accepted · 2026-09-19 · Alex (via solex-explore). Context: client already runs a PMS (the `:99` system); main driver for SoLex is owning their data. Decision: scope = core subset of what they use + enhancements (see `requirements.md`), explicitly *not* feature-parity. Consequences: WS2 maps the existing PMS (what's used, what data) before product commits scope; ~~migration/export becomes first-class~~ (amended by D-5: deferred); "what data do they need to own" is a discovery question.

### D-5 · Fresh start; migration deferred. Schema for the domain, not for an import.
Accepted · 2026-09-20 · Alex (via solex-explore). Context: existing PMS is ezFolio (ezCloud); its Excel export is broken (client-side data: URL truncates at `#`, exports are title-only), so no supported data-out path. Decision: rebuild starts empty; don't shape the model around importing ezFolio data. Consequences: product/dev model the domain cleanly; scraping stays a fallback; DB-export request to ezCloud parked in `team/questions.md`; "data ownership" now means *going forward*, not history.
