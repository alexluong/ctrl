#!/bin/bash
# Manual check/repair of the VPN forwarded port <-> qBittorrent listening port.
#
# NOTE: This is now a BACKUP tool. Port sync happens automatically via gluetun's
# VPN_PORT_FORWARDING_UP_COMMAND hook (see compose/download.yaml), which fires on
# every (re)connect. Use this only to verify, or to force a re-sync by hand.
#
# Works credential-free because qBittorrent has WebUI\LocalHostAuth=false and we
# call the API from *inside* gluetun's network namespace (which qbit shares), so
# localhost:8080 is treated as a local, trusted client.
#
#   ./port-status.sh          # show VPN port vs qBittorrent port
#   ./port-status.sh --sync   # force qBittorrent to the current VPN port

DOCKER="docker --context colima-arr"
API="http://localhost:8080/api/v2"

echo "=== Port Status ==="

# Forwarded port from gluetun
VPN_PORT=$($DOCKER exec gluetun cat /tmp/gluetun/forwarded_port 2>/dev/null | tr -dc '0-9')
if [ -z "$VPN_PORT" ]; then
  echo "VPN Port: Not available (gluetun down or port forwarding disabled)"
  exit 1
fi
echo "VPN Port:         $VPN_PORT"

# qBittorrent's current listening port (creds-free, from inside the shared ns)
QB_PORT=$($DOCKER exec gluetun wget -qO- "$API/app/preferences" 2>/dev/null | grep -o '"listen_port":[0-9]*' | grep -o '[0-9]*')
if [ -z "$QB_PORT" ]; then
  echo "qBittorrent Port: Could not retrieve (qbit WebUI down?)"
  exit 1
fi
echo "qBittorrent Port: $QB_PORT"
echo ""

if [ "$VPN_PORT" = "$QB_PORT" ]; then
  echo "✓ Ports match - all good!"
else
  echo "✗ Ports mismatch!"
  if [ "$1" = "--sync" ]; then
    echo "Syncing qBittorrent to $VPN_PORT..."
    $DOCKER exec gluetun wget -qO- --post-data "json={\"listen_port\":$VPN_PORT}" "$API/setPreferences" >/dev/null 2>&1
    echo "Done. qBittorrent now listening on $VPN_PORT"
  else
    echo "Run with --sync to fix:  ./scripts/port-status.sh --sync"
  fi
fi
