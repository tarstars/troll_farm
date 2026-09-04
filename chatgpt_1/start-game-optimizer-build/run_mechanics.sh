#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
DIR=chatgpt_1/start-game-optimizer-build
mkdir -p "$DIR/results"
python3 "$DIR/repair_generator.py"
python3 "$DIR/test_model.py" | tee "$DIR/results/model-tests.log"
python3 "$DIR/make_candidate.py" | tee "$DIR/results/build.log"
python3 local_claude_1/third-troll/fixtures_diff.py \
  --arm "$DIR/champion-start-game-optimizer-v6-instrument.rs" \
  --submission cgauto/submissions/candidate-start-game-optimizer-v6-instrument.rs \
  --out "$DIR/results/fixtures.json" | tee "$DIR/results/fixtures.log"
python3 local_claude_1/third-troll/fixtures_diff.py \
  --arm local_claude_1/denial-ablation/champion-denial-off-v6-instrument.rs \
  --submission cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs \
  --out "$DIR/results/control-fixtures.json" | tee "$DIR/results/control-fixtures.log"
python3 local_claude_1/third-troll/smoke.py \
  --records local_claude_1/third-troll/smoke-maps-seed0.jsonl \
  --arm "$DIR/champion-start-game-optimizer-v6-instrument.rs" \
  --out "$DIR/results/smoke.json" | tee "$DIR/results/smoke.log"
python3 local_claude_1/third-troll/smoke.py \
  --records local_claude_1/third-troll/smoke-maps-seed0.jsonl \
  --arm local_claude_1/denial-ablation/champion-denial-off-v6-instrument.rs \
  --out "$DIR/results/control-smoke.json" | tee "$DIR/results/control-smoke.log"
python3 - "$DIR/results/smoke.json" "$DIR/results/control-smoke.json" <<'PY'
import json, sys
candidate=json.load(open(sys.argv[1]))
control=json.load(open(sys.argv[2]))
assert candidate["status"] == "PASS" and candidate["all_mechanics_ok"] == 24, candidate["status"]
assert control["status"] == "PASS" and control["all_mechanics_ok"] == 24, control["status"]
print("MECHANICS PASS: candidate 24/24, control 24/24")
PY
python3 claude_1/h2h-panel/turn_time.py \
  --bot cgauto/submissions/candidate-start-game-optimizer-v6-instrument.rs \
  --maps 3 --json-out "$DIR/results/turn-time.json" | tee "$DIR/results/turn-time.log"
