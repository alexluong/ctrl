#!/bin/bash
set -e

echo "Starting Colima VM (arr)..."
colima start arr \
  --cpu 2 \
  --memory 2 \
  --disk 30 \
  --mount "/Volumes/Blue4/arr:w" \
  --mount "/Volumes/Red4/arr:w" \
  --mount-type virtiofs \
  --vm-type vz \
  --runtime docker

echo "VM ready. Use: docker --context colima-arr ..."
