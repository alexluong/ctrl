#!/usr/bin/env bash
# SwiftBar plugin: menubar front end to bin/svc. Services are listed under their group (workspace);
# click one to toggle it, submenu has open/log/restart.
# The 10s in the filename is the refresh interval (catches services that died on their own).
# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>

ROOT="$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)"
SVC="$ROOT/bin/svc"
LOGS="$HOME/Library/Logs/svc"

rows="$("$SVC" ls 2>&1)" || { echo "svc ⚠️"; echo "---"; echo "$rows"; exit 0; }
count="$(grep -c $'\trunning\t' <<< "$rows")"

if [ "$count" -gt 0 ]; then echo "$count | sfimage=bolt.fill"; else echo " | sfimage=bolt"; fi
echo "---"
group=''
while IFS=$'\t' read -r name state url host; do
  if [ "$name" = --- ]; then group="$state"; echo "---"; echo "$group | size=11"; continue; fi
  label="${name#"$group"-}"
  act="bash=$SVC param1=toggle param2=$name terminal=false refresh=true"
  case "$state" in
    running) echo "$label | checked=true $act" ;;
    failing) echo "$label ⚠️ | $act" ;;          # remote service in a restart loop; click stops it
    offline) echo "$label ($host offline)"; continue ;; # no action = greyed out
    *)       echo "$label | $act" ;;
  esac
  [ "$url" != - ] && [ "$state" = running ] && echo "-- Open $url | href=$url"
  [ "$state" = running ] && echo "-- Restart | bash=$SVC param1=restart param2=$name terminal=false refresh=true"
  if [ "$host" != - ]; then
    echo "-- Log | bash=$SVC param1=logs param2=$name param3=-f terminal=true"
  elif [ -f "$LOGS/$name.log" ]; then
    echo "-- Log | bash=/usr/bin/open param1=-a param2=Console param3=$LOGS/$name.log terminal=false"
  else
    echo "-- No log yet" # no action = greyed out
  fi
done <<< "$rows"
echo "---"
echo "Edit services.conf | bash=/usr/bin/open param1=-t param2=$ROOT/services.conf terminal=false"
echo "Logs folder | bash=/usr/bin/open param1=$LOGS terminal=false"
echo "Refresh | refresh=true"
