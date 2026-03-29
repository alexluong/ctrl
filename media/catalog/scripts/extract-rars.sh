#!/bin/bash
# Extract RAR files from nested episode folders
# Usage: ./extract-rars.sh "/path/to/show/folder"

if [ -z "$1" ]; then
  echo "Usage: $0 <folder_path>"
  echo "Example: $0 \"/Volumes/Blue4/arr/downloads/Review.with.Forrest.MacNeil.S01.1080p.WEB.h264-DiRT\""
  exit 1
fi

BASE_DIR="$1"

if [ ! -d "$BASE_DIR" ]; then
  echo "Error: Directory not found: $BASE_DIR"
  exit 1
fi

echo "Extracting RARs from: $BASE_DIR"
echo ""

# Find all .rar files (not .r00, .r01, etc - just the main .rar)
find "$BASE_DIR" -name "*.rar" -type f | while read -r rar_file; do
  dir=$(dirname "$rar_file")
  filename=$(basename "$rar_file")

  echo "=== Extracting: $filename ==="

  # Extract to the same directory as the RAR
  cd "$dir" && unar -q "$rar_file"

  if [ $? -eq 0 ]; then
    echo "Done: $filename"
  else
    echo "FAILED: $filename"
  fi
  echo ""
done

echo "=== Extraction complete ==="
