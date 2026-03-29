#!/bin/bash
set -e

MODE=${1:-"status"}

case "$MODE" in
  on)
    echo "Enabling server mode..."
    sudo pmset -a sleep 0
    sudo pmset -a disksleep 0
    sudo pmset -a displaysleep 10
    sudo pmset -a powernap 0
    sudo pmset -a womp 1
    defaults write com.apple.screensaver askForPassword -int 0
    echo "Server mode enabled. Machine will stay awake, display sleeps after 10 mins, screen lock disabled."
    ;;
  off)
    echo "Disabling server mode (restoring defaults)..."
    sudo pmset -a sleep 1
    sudo pmset -a disksleep 10
    sudo pmset -a displaysleep 10
    sudo pmset -a powernap 1
    sudo pmset -a womp 1
    defaults write com.apple.screensaver askForPassword -int 1
    echo "Server mode disabled. Normal sleep behavior and screen lock restored."
    ;;
  status)
    echo "Current power settings:"
    pmset -g
    ;;
  *)
    echo "Usage: server-mode.sh [on|off|status]"
    exit 1
    ;;
esac
