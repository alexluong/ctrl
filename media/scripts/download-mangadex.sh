#!/bin/bash

# Usage: ./download-mangadex.sh <mangadex-url> [start-volume] [end-volume]
# Example: ./download-mangadex.sh https://mangadex.org/title/7f30dfc3-0b80-4dcc-a3b9-0cd746fac005/detective-conan 2 2

URL="${1:?Usage: $0 <mangadex-url> [start-volume] [end-volume]}"
START_VOL="${2:-1}"
END_VOL="${3:-$START_VOL}"

docker --context colima-arr run --rm \
  -v /Volumes/Blue4/arr/media/books/downloads:/downloads \
  mansuf/mangadex-downloader:latest-optional \
  -lang en \
  --save-as cbz-volume \
  --start-volume "$START_VOL" \
  --end-volume "$END_VOL" \
  --ignore-missing-chapters \
  --no-track \
  "$URL"
