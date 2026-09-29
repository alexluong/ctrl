#!/bin/bash
# SessionStart: export the workspace mise env into Claude's shell (mise's cd hook never runs there).
# Then put mise's tool dirs first: the login PATH has global installs (~/Library/pnpm) ahead of them.
[ -n "${CLAUDE_ENV_FILE:-}" ] || exit 0
cd "${CLAUDE_PROJECT_DIR:-$PWD}" || exit 0
mise env -s bash >> "$CLAUDE_ENV_FILE" 2>/dev/null
echo "export PATH=\"$(mise bin-paths 2>/dev/null | paste -sd: -):\$PATH\"" >> "$CLAUDE_ENV_FILE"
exit 0
