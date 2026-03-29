#!/bin/bash
# Check and sync VPN forwarded port with qBittorrent

DOCKER="docker --context colima-arr"

# qBittorrent credentials (change if you updated the password)
QB_USER="${QB_USER:-admin}"
QB_PASS="${QB_PASS:-adminadmin}"

echo "=== Port Status ==="

# Get forwarded port from gluetun
VPN_PORT=$($DOCKER exec gluetun cat /tmp/gluetun/forwarded_port 2>/dev/null)
if [ -z "$VPN_PORT" ]; then
  echo "VPN Port: Not available (gluetun not running or port forwarding disabled)"
  exit 1
fi
echo "VPN Port: $VPN_PORT"

# Login to qBittorrent and get cookie
COOKIE=$($DOCKER exec qbittorrent curl -s -i "http://localhost:8080/api/v2/auth/login" \
  -d "username=$QB_USER&password=$QB_PASS" 2>/dev/null | grep -i 'set-cookie' | grep -o 'SID=[^;]*')

if [ -z "$COOKIE" ]; then
  echo "qBittorrent: Could not login (wrong password or not running?)"
  echo "  Set QB_PASS env var if you changed the password:"
  echo "  QB_PASS=yourpassword ./scripts/port-status.sh"
  exit 1
fi

# Get qBittorrent's current listening port via API
QB_PORT=$($DOCKER exec qbittorrent curl -s -b "$COOKIE" "http://localhost:8080/api/v2/app/preferences" 2>/dev/null | grep -o '"listen_port":[0-9]*' | grep -o '[0-9]*')
if [ -z "$QB_PORT" ]; then
  echo "qBittorrent Port: Could not retrieve"
  exit 1
fi
echo "qBittorrent Port: $QB_PORT"

# Compare
if [ "$VPN_PORT" = "$QB_PORT" ]; then
  echo ""
  echo "✓ Ports match - all good!"
else
  echo ""
  echo "✗ Ports mismatch!"
  echo ""

  if [ "$1" = "--sync" ]; then
    echo "Syncing qBittorrent to port $VPN_PORT..."
    $DOCKER exec qbittorrent curl -s -b "$COOKIE" "http://localhost:8080/api/v2/app/setPreferences" \
      -d "json={\"listen_port\":$VPN_PORT}" > /dev/null
    echo "Done. qBittorrent now listening on $VPN_PORT"
  else
    echo "Run with --sync to update qBittorrent:"
    echo "  ./scripts/port-status.sh --sync"
  fi
fi

# Show connection status
echo ""
echo "=== VPN Status ==="
$DOCKER exec gluetun wget -qO- http://localhost:8000/v1/openvpn/status 2>/dev/null || echo "Could not get VPN status"
