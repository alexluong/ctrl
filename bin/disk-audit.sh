#!/usr/bin/env bash
# Disk usage audit — measures the same buckets every run so snapshots are comparable.
# MacBook Pro only (460G volume). See docs/machine-disk.md.
#
# Usage: bin/disk-audit.sh [--row]
#   (no args)  human-readable report + drill-down
#   --row      single markdown table row, to append to docs/machine-disk.md
#
# Buckets are defined once, here. If you change a bucket's paths, past snapshots
# stop being comparable — note it in docs/machine-disk.md when you do.

set -uo pipefail
VOL="/System/Volumes/Data"

# --- budgets (GB) -------------------------------------------------------------
# Derived from measured baseline + headroom, NOT invented targets. Over budget
# means "this grew past its normal range, go look" — not "this is wasteful".
# Budgets are independent tripwires, not a partition of the disk: they're allowed
# to sum past capacity because the buckets don't all peak at once. FREE_FLOOR is
# the actual act-now signal. Rationale and revisions: docs/machine-disk.md.
BUDGET_DOCKER=120   # deliberately generous — primary dev runtime, baseline is post-prune
BUDGET_REPOS=90     # baseline 70.6 + headroom
BUDGET_CACHES=22    # baseline ~17 + headroom
BUDGET_SYSTEM=36    # baseline ~29 + headroom
FREE_FLOOR=50       # free space below this = act now, regardless of buckets

# --- bucket definitions -------------------------------------------------------
# Volatile = regrows on its own; this is where regressions almost always are.
docker_paths=(
  "$HOME/Library/Containers/com.docker.docker"
)
repos_paths=(
  "$HOME/git"
  "$HOME/code"
)
# Transient only: things with a real prune command that we'd actually run.
caches_paths=(
  "$HOME/Library/pnpm"
  "$HOME/Library/Caches"
  "$HOME/.cache"
  "$HOME/.npm"
)
# Platform state: installed runtimes, module caches, and tool VMs. Technically
# deletable, but they refill to the same size the moment you use the tool, so
# pruning them is churn rather than cleanup. Sized by baseline, not trimmed.
system_paths=(
  "$HOME/go"                                              # module cache; no prune-unreferenced exists
  "$HOME/Library/Application Support/Claude/vm_bundles"   # Claude desktop sandbox VM image
  "$HOME/.local/share/mise"
  "$HOME/.bun"
  "$HOME/.asdf"
  "$HOME/.pyenv"
  "$HOME/.cargo"
  "$HOME/.local/share/claude"
  "$HOME/.local/share/opencode"
  "$HOME/.claude"
)
# Stable = set once, shouldn't drift. If these move, something unusual happened.
apps_paths=(
  "/Applications"
  "/opt/homebrew"
)
personal_paths=(
  "$HOME/Library/Messages"
  "$HOME/Pictures"
  "$HOME/Documents"
  "$HOME/Downloads"
  "$HOME/Music"
  "$HOME/Library/Mobile Documents"
  "$HOME/Library/Group Containers/3L68KQB4HG.group.com.readdle.smartemail"
)

# --- helpers ------------------------------------------------------------------
# Sum of paths in MB. Missing paths count as 0 so the script survives uninstalls.
sum_mb() {
  local total=0 mb
  for p in "$@"; do
    [ -e "$p" ] || continue
    mb=$(du -sm "$p" 2>/dev/null | awk '{print $1}')
    [ -n "${mb:-}" ] && total=$((total + mb))
  done
  echo "$total"
}

gb() { awk -v m="$1" 'BEGIN{printf "%.1f", m/1024}'; }

# Largest children of a path, for the drill-down section.
top_children() {
  local path="$1" n="${2:-5}"
  [ -d "$path" ] || return 0
  du -sh "$path"/* 2>/dev/null | sort -rh | head -"$n" | sed 's/^/    /'
}

# --- measure ------------------------------------------------------------------
used_mb=$(df -m "$VOL" | awk 'NR==2{print $3}')
free_mb=$(df -m "$VOL" | awk 'NR==2{print $4}')
size_mb=$(df -m "$VOL" | awk 'NR==2{print $2}')

docker_mb=$(sum_mb "${docker_paths[@]}")
repos_mb=$(sum_mb "${repos_paths[@]}")
caches_mb=$(sum_mb "${caches_paths[@]}")
system_mb=$(sum_mb "${system_paths[@]}")
apps_mb=$(sum_mb "${apps_paths[@]}")
personal_mb=$(sum_mb "${personal_paths[@]}")

accounted=$((docker_mb + repos_mb + caches_mb + system_mb + apps_mb + personal_mb))
other_mb=$((used_mb - accounted))
[ "$other_mb" -lt 0 ] && other_mb=0

volatile_mb=$((docker_mb + repos_mb + caches_mb))
stable_mb=$((system_mb + apps_mb + personal_mb))

today=$(date +%Y-%m-%d)

# --- --row mode ---------------------------------------------------------------
if [ "${1:-}" = "--row" ]; then
  printf '| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |\n' \
    "$today" "$(gb $used_mb)" "$(gb $free_mb)" "$(gb $docker_mb)" "$(gb $repos_mb)" \
    "$(gb $caches_mb)" "$(gb $system_mb)" "$(gb $apps_mb)" "$(gb $personal_mb)" "$(gb $other_mb)"
  exit 0
fi

# --- report -------------------------------------------------------------------
pct() { awk -v a="$1" -v b="$used_mb" 'BEGIN{printf "%d", (a*100)/b}'; }

# Budget verdict: OVER by Ng (prune) / ok (Ng headroom).
verdict() {
  local mb="$1" budget_gb="$2"
  [ "$budget_gb" = "-" ] && { echo "-"; return; }
  local budget_mb=$((budget_gb * 1024))
  if [ "$mb" -gt "$budget_mb" ]; then
    echo "OVER by $(gb $((mb - budget_mb)))G"
  else
    echo "ok ($(gb $((budget_mb - mb)))G left)"
  fi
}

echo "DISK AUDIT — $today — MacBook Pro"
echo "Volume: $(gb $used_mb)G used / $(gb $size_mb)G  •  $(gb $free_mb)G free"
if [ "$free_mb" -lt $((FREE_FLOOR * 1024)) ]; then
  echo "  !! below ${FREE_FLOOR}G free floor — act now"
fi
echo
printf '%-10s %8s %6s  %-9s %7s  %s\n' "BUCKET" "SIZE" "%USED" "KIND" "BUDGET" "VERDICT"
printf '%-10s %8s %6s  %-9s %7s  %s\n' "------" "----" "-----" "----" "------" "-------"
printf '%-10s %7sG %5s%%  %-9s %6sG  %s\n' "docker"   "$(gb $docker_mb)"   "$(pct $docker_mb)"   "prunable" "$BUDGET_DOCKER" "$(verdict $docker_mb $BUDGET_DOCKER)"
printf '%-10s %7sG %5s%%  %-9s %6sG  %s\n' "repos"    "$(gb $repos_mb)"    "$(pct $repos_mb)"    "prunable" "$BUDGET_REPOS"  "$(verdict $repos_mb $BUDGET_REPOS)"
printf '%-10s %7sG %5s%%  %-9s %6sG  %s\n' "caches"   "$(gb $caches_mb)"   "$(pct $caches_mb)"   "prunable" "$BUDGET_CACHES" "$(verdict $caches_mb $BUDGET_CACHES)"
printf '%-10s %7sG %5s%%  %-9s %6sG  %s\n' "system"   "$(gb $system_mb)"   "$(pct $system_mb)"   "baseline" "$BUDGET_SYSTEM" "$(verdict $system_mb $BUDGET_SYSTEM)"
printf '%-10s %7sG %5s%%  %-9s %7s  %s\n' "apps"     "$(gb $apps_mb)"     "$(pct $apps_mb)"     "stable"   "-" "-"
printf '%-10s %7sG %5s%%  %-9s %7s  %s\n' "personal" "$(gb $personal_mb)" "$(pct $personal_mb)" "stable"   "-" "-"
printf '%-10s %7sG %5s%%  %-9s %7s  %s\n' "other"    "$(gb $other_mb)"    "$(pct $other_mb)"    "-"        "-" "-"
echo
echo "prunable: $(gb $volatile_mb)G   •   baseline+stable: $(gb $stable_mb)G"

echo
echo "--- docker ---"
if docker info >/dev/null 2>&1; then
  docker system df 2>/dev/null | sed 's/^/    /'
else
  echo "    (daemon not running — Docker.raw on disk: $(gb $docker_mb)G)"
fi
raw="$HOME/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw"
[ -f "$raw" ] && echo "    Docker.raw apparent: $(ls -lh "$raw" | awk '{print $5}')  actual: $(gb $docker_mb)G"

echo
echo "--- repos ---"
nm=$(find "$HOME/git" "$HOME/code" -type d -name node_modules -prune 2>/dev/null \
     | xargs -I{} du -sm {} 2>/dev/null | awk '{s+=$1} END {print s+0}')
echo "    node_modules total: $(gb $nm)G"
echo "    largest trees:"
du -sh "$HOME"/git/hub/*/ 2>/dev/null | sort -rh | head -5 | sed 's/^/      /'

echo
echo "--- caches (largest) ---"
for p in "${caches_paths[@]}"; do
  [ -e "$p" ] && du -sh "$p" 2>/dev/null
done | sort -rh | head -6 | sed 's/^/    /'

echo
echo "--- system (largest) ---"
for p in "${system_paths[@]}"; do
  [ -e "$p" ] && du -sh "$p" 2>/dev/null
done | sort -rh | head -6 | sed 's/^/    /'

echo
echo "--- apps (largest) ---"
top_children /Applications 6

echo
echo "--- personal (largest) ---"
for p in "${personal_paths[@]}"; do
  [ -e "$p" ] && du -sh "$p" 2>/dev/null
done | sort -rh | head -5 | sed 's/^/    /'

echo
echo "Snapshot row for docs/machine-disk.md:"
"$0" --row
