---
name: explain-infra-plainly
description: For infra/networking work Alex wants to understand each step - plain explanation before running, and a revisit-able explainer doc at his level
metadata:
  type: feedback
---

On infra and networking work (routers, Tailscale, firewalls, gateways), explain what a step does in plain terms before running it, with the real addresses, and answer "how does this actually work" questions concretely (where the packet goes, what runs it). Keep a plain-language explainer doc he can come back to, written for his level, next to the runbook: `ctrl-vault/docs/tailscale.md` is the model (cases, what each piece does, every setting it depends on, checks, "adding a device").

**Why:** Alex (TASK-9, 2026-10-04) wanted to tinker and understand, asked repeatedly how the pieces work, and asked for notes "accounting for my level of understanding" in case he revisits.

**How to apply:** step-by-step with a stop for his go-ahead when he asks for it; once he says "go ahead / get it done fully", execute the rest and report. Document anything that lives outside git (router settings, VPN exceptions) as carefully as code.
