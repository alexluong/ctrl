#!/bin/bash
set -e

echo "Starting Colima VM (arr)..."
# Mac Mini M4 has 16 GB / 10 cores. This VM runs the whole media stack
# (download + private + calibre + audiobookshelf + jellyfin), so it gets a
# generous slice: 8 GB / 6 CPU. Leaves ~8 GB / 4 cores for macOS (+ the
# stopped 'hookdeck' work VM). 2 GB was starving qBittorrent/Jellyfin -> OOM.
colima start arr \
  --cpu 6 \
  --memory 8 \
  --disk 30 \
  --mount "/Volumes/Blue4/arr:w" \
  --mount "/Volumes/Red4/arr:w" \
  --mount-type virtiofs \
  --vm-type vz \
  --runtime docker

echo "VM ready. Use: docker --context colima-arr ..."
