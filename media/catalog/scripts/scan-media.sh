#!/bin/bash
# Scan media directory and output summary
# Usage: ./scan-media.sh

MEDIA_PATH="/Volumes/Blue4/arr/media"

echo "=== Media Library Scan ==="
echo "Date: $(date)"
echo ""

echo "=== Movies ==="
movie_count=$(find "$MEDIA_PATH/movies" -maxdepth 1 -type d | wc -l)
echo "Total: $((movie_count - 1)) movies"
echo ""

echo "=== TV Shows ==="
for show in "$MEDIA_PATH/tv"/*; do
  if [ -d "$show" ]; then
    show_name=$(basename "$show")
    season_count=$(find "$show" -maxdepth 1 -type d -name "Season*" | wc -l)
    episode_count=$(find "$show" -type f \( -name "*.mkv" -o -name "*.mp4" \) | wc -l)
    echo "$show_name: $season_count seasons, $episode_count episodes"
  fi
done
echo ""

echo "=== Disk Usage ==="
du -sh "$MEDIA_PATH/movies" 2>/dev/null
du -sh "$MEDIA_PATH/tv" 2>/dev/null
