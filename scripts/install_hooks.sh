#!/usr/bin/env bash
# Point this clone at the tracked hooks. Safe to re-run.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
chmod +x .githooks/* 2>/dev/null || true
git config core.hooksPath .githooks
echo "core.hooksPath -> .githooks ($(git rev-parse --show-toplevel))"
