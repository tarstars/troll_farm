#!/usr/bin/env bash
# Canonical Banana R2 zero-oscillation gate entry point.
#
# Contract:
#   - exact candidate is built from build_candidate_v11.py;
#   - map generator/panel/detectors are pinned to b16f44d6;
#   - raw D-1 and D-4 counts must both be zero in every candidate game;
#   - no inherited/parent attribution exemption is permitted for D-1/D-4;
#   - result JSON binds all material inputs by SHA-256.
set +e
set -u
set -o pipefail

ROOT="${GITHUB_WORKSPACE:-$(git rev-parse --show-toplevel)}"
OUT="${ZERO_GATE_OUT:-$ROOT/chatgpt_1/banana-solve/ci/zero-oscillation-gate}"
CAND="$ROOT/chatgpt_1/banana-solve/candidate-banana-r2.min.rs"
CONTRACT="$ROOT/chatgpt_1/banana-solve/gate-contract-v1.json"
PINNED_COMMIT="b16f44d62caa9802253adaf255eb07b98273421b"
PINNED_TREE="${ZERO_GATE_PINNED_TREE:-/tmp/banana-zero-pinned}"
FAILED=0

mkdir -p "$OUT"
rm -rf "$OUT"/*

run_step() {
  local name="$1"
  shift
  echo "== $name ==" | tee -a "$OUT/run.log"
  "$@" >> "$OUT/run.log" 2>&1
  local code=$?
  echo "${name// /_}_exit=$code" | tee -a "$OUT/run.log"
  if [ "$code" -ne 0 ]; then
    FAILED=1
  fi
  return 0
}

{
  echo "candidate_ref=${GITHUB_REF_NAME:-$(git branch --show-current)}"
  echo "candidate_commit=${GITHUB_SHA:-$(git rev-parse HEAD)}"
  echo "workflow_ref=${GITHUB_WORKFLOW_REF:-local}"
  echo "pinned_panel_commit=$PINNED_COMMIT"
  echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "python=$(python3 --version 2>&1)"
  echo "rustc=$(rustc --version 2>&1)"
} > "$OUT/run.log"

run_step "candidate build" \
  python3 "$ROOT/chatgpt_1/banana-solve/build_candidate_v11.py"
run_step "candidate compile" \
  rustc --crate-name banana_candidate --edition=2021 -O \
    "$CAND" -o /tmp/banana-zero-candidate
run_step "trace detector tests" \
  python3 -m unittest discover \
    -s "$ROOT/claude_1/banana-restoration-r2" \
    -p test_trace_detectors.py
run_step "owner contract" \
  python3 "$ROOT/chatgpt_1/banana-solve/owner_contract_final_adapter.py" \
    --candidate "$CAND" \
    --output "$OUT/owner-contract"

# Materialize the exact reviewer-pinned panel. Worktree removal is idempotent.
git worktree remove --force "$PINNED_TREE" >> "$OUT/run.log" 2>&1 || true
rm -rf "$PINNED_TREE"
git fetch origin agent/claude_1 >> "$OUT/run.log" 2>&1
if [ "$?" -ne 0 ]; then
  FAILED=1
fi
git worktree add --detach "$PINNED_TREE" "$PINNED_COMMIT" \
  >> "$OUT/run.log" 2>&1
if [ "$?" -ne 0 ]; then
  FAILED=1
fi

PINNED_CFG="$OUT/pinned-config.json"
cp "$PINNED_TREE/claude_1/pipeline/fuzz-panel-config.json" "$PINNED_CFG"
if [ "$?" -ne 0 ]; then
  FAILED=1
fi

python3 - "$PINNED_CFG" "$CAND" \
  "$PINNED_TREE/cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs" <<'PY'
import hashlib
import json
import pathlib
import sys

config_path, candidate, parent = map(pathlib.Path, sys.argv[1:])
config = json.loads(config_path.read_text())
config["task"] = "20260802-banana-restoration-r2 zero-oscillation gate v1"
config["candidate"]["source"] = str(candidate.resolve())
config["candidate"]["sha256"] = hashlib.sha256(candidate.read_bytes()).hexdigest()
config["candidate"]["crate"] = "chatgpt_1_banana_zero_oscillation"
config["parent"]["source"] = str(parent.resolve())
config["parent"]["sha256"] = hashlib.sha256(parent.read_bytes()).hexdigest()
config["games_dir"] = "/tmp/banana-zero-oscillation/games"
config["bin_cache_dir"] = "/tmp/banana-zero-oscillation/bin"
config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
PY
if [ "$?" -ne 0 ]; then
  FAILED=1
fi

run_step "stable pinned gate" \
  python3 "$ROOT/chatgpt_1/banana-solve/run_stable_gate.py" \
    --panel-file "$PINNED_TREE/claude_1/pipeline/fuzz_panel.py" \
    --config "$PINNED_CFG" \
    --gate-contract "$CONTRACT" \
    --report "$OUT/stable-gate.md" \
    --json "$OUT/stable-gate.json" \
    --save-failures "$OUT/failures"

python3 - "$CAND" "$OUT" "$CONTRACT" "$0" <<'PY' >> "$OUT/run.log" 2>&1
import hashlib
import json
import os
import pathlib
import sys

candidate, out, contract, runner = map(pathlib.Path, sys.argv[1:])
summary = {
    "candidate_bytes": candidate.stat().st_size if candidate.exists() else None,
    "candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest()
    if candidate.exists()
    else None,
    "candidate_commit": os.environ.get("GITHUB_SHA"),
    "contract_sha256": hashlib.sha256(contract.read_bytes()).hexdigest(),
    "entrypoint_sha256": hashlib.sha256(runner.read_bytes()).hexdigest(),
}
for name, path in {
    "stable_gate": out / "stable-gate.json",
    "owner_contract": out / "owner-contract" / "owner-contract-results.json",
}.items():
    if not path.exists():
        continue
    payload = json.loads(path.read_text())
    summary[name] = payload.get("verdict")
    if name == "stable_gate":
        summary["hard_stability"] = payload.get("hard_stability")
        summary["sha_binding"] = payload.get("sha_binding")
(out / "summary.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n"
)
print(json.dumps(summary, indent=2, sort_keys=True))
PY
if [ "$?" -ne 0 ]; then
  FAILED=1
fi

exit "$FAILED"
