#!/bin/sh
# Chrome for Testing (distinct Dock icon, isolated profile) with CDP debug port.
cd "$(dirname "$0")"
BIN="$HOME/Library/Caches/ms-playwright/chromium-1243/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
[ -x "$BIN" ] || BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
exec "$BIN" --remote-debugging-port=9334 --user-data-dir="$PWD/.profile" \
  --no-first-run --no-default-browser-check about:blank
