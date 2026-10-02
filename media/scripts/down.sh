#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

STACKS=${1:-"all"}

cd "$PROJECT_DIR"

export DOCKER_CONTEXT="colima-arr"

case "$STACKS" in
  download)
    docker-compose -f compose/download.yaml --env-file .env down
    ;;
  arr)
    docker-compose -f compose/arr.yaml --env-file .env down
    ;;
  jellyfin)
    docker-compose -f compose/jellyfin.yaml --env-file .env down
    ;;
  calibre)
    docker-compose -f compose/calibre.yaml --env-file .env down
    ;;
  audiobookshelf)
    docker-compose -f compose/audiobookshelf.yaml --env-file .env down
    ;;
  private)
    docker-compose -f compose/private.yaml --env-file .env down
    ;;
  all)
    docker-compose -f compose/download.yaml -f compose/arr.yaml --env-file .env down
    ;;
  *)
    echo "Usage: down.sh [download|arr|jellyfin|calibre|audiobookshelf|private|all]"
    exit 1
    ;;
esac

echo "Stack '$STACKS' is down."
