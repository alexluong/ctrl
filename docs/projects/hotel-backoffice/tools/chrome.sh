#!/bin/sh
# visible Chrome with CDP debug port, isolated profile
cd "$(dirname "$0")"
exec "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9333 --user-data-dir="$PWD/.profile" \
  --no-first-run --no-default-browser-check about:blank
