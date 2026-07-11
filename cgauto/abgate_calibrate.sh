#!/bin/bash
# Calibration study for the abgate self-play gate (spec acceptance test):
# 5 candidate-vs-base pairs with KNOWN arena verdicts. usage: abgate_calibrate.sh [seeds] [jobs]
set -u
cd "$(dirname "$0")/.."
N=${1:-200}; J=${2:-4}
B=rust/target/abgate-bins; mkdir -p "$B" data/abgate

build() { # build <name> <min.rs>
  local W; W=$(mktemp -d); cp "$2" "$W/cc.rs"
  rustc --edition 2021 -O "$W/cc.rs" -o "$B/$1" 2>"$W/err" || { echo "BUILD FAILED: $1"; cat "$W/err" | head -5; exit 3; }
  echo "built $1"
}
build ringfarm    cgauto/submissions/v1.56.0-ringfarm.min.rs
build ringfix3    cgauto/submissions/v1.59.0-ringfix3.min.rs
build ringtune    cgauto/submissions/v1.57.0-ringtune.min.rs
build trainfruit  cgauto/submissions/v1.58.0-trainfruit.min.rs
build fellmission cgauto/submissions/v1.60.0-fellmission.min.rs
build chopharvest cgauto/submissions/v1.61.0-chopharvest.min.rs

G="uv run --no-sync python cgauto/abgate.py"
run() { # run <cand> <base> <arena_known>
  echo "=== $1 vs $2 (arena: $3) ==="
  $G "$B/$1" "$B/$2" --seeds "$N" --jobs "$J" --csv "data/abgate/cal_$1.csv" \
    | tee "data/abgate/cal_$1.txt" || true
}
run ringfix3    ringfarm  "+1.1 KEEP"
run ringtune    ringfarm  "-2.4 REVERT"
run trainfruit  ringfarm  "-3.2 REVERT"
run fellmission ringfix3  "-1.0 REVERT"
run chopharvest ringfix3  "-5.0 REVERT"
echo "calibration done — record the table in the spec + silver log"
