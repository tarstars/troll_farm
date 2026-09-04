#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
DIR=chatgpt_1/champion-prefix-orchard
mkdir -p "$DIR/results"
python3 "$DIR/test_oracle.py" | tee "$DIR/results/tests.log"
python3 "$DIR/oracle.py" \
  --champion local_claude_1/denial-ablation/champion-denial-off-v6-instrument.rs \
  --records local_claude_1/third-troll/smoke-maps-seed0.jsonl \
  --policies "$DIR/policies.json" \
  --out "$DIR/results/result.json" \
  --report "$DIR/RESULTS.md" \
  2>&1 | tee "$DIR/results/run.log"
