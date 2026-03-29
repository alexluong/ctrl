#!/bin/bash
# Verify media library integrity
# Usage: ./verify.sh

MEDIA_PATH="/Volumes/Blue4/arr/media"
DOWNLOADS_PATH="/Volumes/Blue4/arr/downloads"

echo "=== Media Verification ==="
echo "Date: $(date)"
echo ""

echo "=== Checking Hardlinks ==="
hardlink_count=0
copy_count=0

while IFS= read -r file; do
  links=$(stat -f %l "$file" 2>/dev/null)
  if [ "$links" -gt 1 ]; then
    ((hardlink_count++))
  else
    ((copy_count++))
    echo "COPY: $(basename "$(dirname "$file")")"
  fi
done < <(find "$MEDIA_PATH/movies" -type f \( -name "*.mkv" -o -name "*.mp4" \) 2>/dev/null)

echo ""
echo "Movies: $hardlink_count hardlinks, $copy_count copies"
echo ""

echo "=== Missing Episodes Check ==="
# Friends
echo "Friends:"
for ep in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24; do
  if ! ls "$MEDIA_PATH/tv/Friends/Season 2/"*S02E${ep}* &>/dev/null; then
    echo "  Missing: S02E${ep}"
  fi
done

# BBT S07
echo "The Big Bang Theory S07:"
for ep in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24; do
  if ! ls "$MEDIA_PATH/tv/The Big Bang Theory/Season 7/"*S07E${ep}* &>/dev/null; then
    echo "  Missing: S07E${ep}"
  fi
done

echo ""
echo "=== Done ==="
