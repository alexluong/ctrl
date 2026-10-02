---
name: build-as-board-task
description: In a discussion session, building that goes beyond a small fix becomes a board task with a spec, not work done inline
metadata:
  type: feedback
---

When Alex is thinking something through and a build falls out of it (a script change, a new mechanism), file it as a board task with a spec or handoff note under `ctrl-vault/work/task-N/` and keep discussing. Do not start building inside the discussion.

**Why:** 2026-10-02, mid-discussion about tunnels on the hookdeck VM, Claude started changing `bin/svc` and the menubar; Alex: "sorry i dont really know what we're trying to do yet, whatever building can you turn it into a dev task loop instead of doing it here". He had not agreed to a design yet, and the build pulled the session away from the question he was asking.

**How to apply:** explain the mechanism in plain steps first and get his "yes" on the design. Small fixes to something already agreed (a one-line bug, a doc correction) are fine inline. Work parked half-done goes on a branch with a handoff note, as with TASK-6. See also [[shared-checkouts-parallel-sessions]].
