#!/usr/bin/env bash
# Cron wrapper for the daily wide-lens D61p collection driver (B0.4, authorized 2026-07-28).
# Installed as a user crontab entry marked `# troll-farm-wide-collect` (see `crontab -l`);
# remove by deleting that marked line via `crontab -e`.
#
# Read-only platform access only: the driver (data/scripts/collect_wide.py) never calls
# api_submit.py or anything that creates games, only the frozen collector's throttled
# PublicClient GET-equivalent JSON services.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
DRIVER="$REPO_ROOT/data/scripts/collect_wide.py"
LOG_FILE="$REPO_ROOT/data/raw/collect_wide.log"

cd "$REPO_ROOT" || exit 1
mkdir -p "$(dirname "$LOG_FILE")"

{
    echo "=== collect_wide_cron.sh start $(date -u +%FT%TZ) ==="
    timeout 3h "$PYTHON_BIN" "$DRIVER"
    status=$?
    echo "=== collect_wide_cron.sh end $(date -u +%FT%TZ) exit=$status ==="
    exit "$status"
} >>"$LOG_FILE" 2>&1
