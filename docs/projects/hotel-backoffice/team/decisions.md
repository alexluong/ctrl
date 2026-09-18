# Decisions

Format: `### D-n · title` → Status (Proposed / Accepted / Superseded), date, by, context, decision, consequences.

### D-1 · Go, no VM, Cloudflare hosting
Accepted · 2026-09-19 · Alex. Context: wants Go, wants to ship, won't run a VM. Consequence: WS1 spike = Go on Cloudflare Containers; fallback WASM.

### D-2 · Notes live in ctrl, one owner per file
Accepted · 2026-09-19 · architect. See `agents/README.md` protocol.
