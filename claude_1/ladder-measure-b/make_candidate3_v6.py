#!/usr/bin/env python3
"""Build bot B of the L-1 ladder measurement: Candidate 3 in play, v6 telemetry on the wire.

Task `20260826-ladder-measure-cured-dancing-troll` (board row L-1). Bot B is the Candidate 3
**instrument** arm -- `KEEP_RULE_ENABLED = true`, `NARRATE_V6_ENABLED = true` -- the arm whose
`MSG`-stripped command stream was byte-identical to the candidate arm on all 240 panel games.
It is compacted exactly as bot A (row 0-3a) was, by the same compactor and the same round trip.

This script does NOT copy the gated arm. It regenerates it from the one source and the one flag
line, then REFUSES unless the bytes it produced are the bytes already gated. A generator that
agrees with the record is evidence; a copy is not.

Chain, each link checked and each failure fatal:

  1. `readable/door1-champion.rs`      sha256 ad1ae4ef...  the base of record
  2. compact(1) == `cgauto/submissions/candidate-door1-pure-deletion.rs` in canonical token
     stream                                                the base IS the ladder champion 547fa706...
  3. `claude_1/cure3/cure3-keep-v6.rs` sha256 01b61444...  the one source, regenerated from (1)
  4. (3) with the flag line rewritten to KEEP=true NARRATE=true -- the arm IS the source, so
     exactly ZERO lines differ (bot A's rule-off arm differs in exactly one)
  5. (4) == `claude_1/cure3/arm-instrument.rs` byte for byte  the parity-gated object
  6. (4) compiles (rustc --edition=2021 -O)
  7. compact(4) -> `cgauto/submissions/candidate-3-keep-v6-instrument.rs`, sha256 recorded,
     round trip re-checked from the written file, and the written file compiles
  8. the written file is NOT the same program as bot A's submission -- if B and A had the same
     token stream the measurement would be comparing a bot with itself

    python3 claude_1/ladder-measure-b/make_candidate3_v6.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "cgauto"))
sys.path.insert(0, str(REPO / "claude_1" / "cure3"))

import compact_rust_source as crs      # noqa: E402
import build_arms3 as ba               # noqa: E402

READABLE = REPO / "readable" / "door1-champion.rs"
READABLE_SHA = "ad1ae4eff70a5569e03e2149882bb22510746f4f8592907a5dfb936943ef0bfb"
CHAMPION_MIN = REPO / "cgauto" / "submissions" / "candidate-door1-pure-deletion.rs"
CHAMPION_MIN_SHA = "547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0"
SOURCE = REPO / "claude_1" / "cure3" / "cure3-keep-v6.rs"
SOURCE_SHA = "01b61444a109c1d190fba5b0a103c861c6f9e772596e97cf9042b9b2c516b3b3"
GATED_ARM = REPO / "claude_1" / "cure3" / "arm-instrument.rs"
GATED_ARM_SHA = "01b61444a109c1d190fba5b0a103c861c6f9e772596e97cf9042b9b2c516b3b3"
BOT_A_MIN = REPO / "cgauto" / "submissions" / "candidate-champion-v6-instrument.rs"

ARM = HERE / "candidate-3-keep-v6-instrument.rs"
SUBMISSION = REPO / "cgauto" / "submissions" / "candidate-3-keep-v6-instrument.rs"
REPORT = REPO / "readable" / "reports" / "candidate-3-keep-v6-instrument.round-trip.json"


class BuildError(Exception):
    """Fail closed: an arm that cannot prove its own lineage is not a ladder submission."""


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BuildError(message)


def token_stream(text: str) -> str:
    """The compactor's own canonical form -- the identity the round-trip report asserts."""
    return crs.compact(text)


def main() -> int:
    readable = READABLE.read_text()
    require(sha(readable) == READABLE_SHA,
            f"base is {sha(readable)}, expected {READABLE_SHA}")

    champ_min = CHAMPION_MIN.read_text()
    require(sha(champ_min) == CHAMPION_MIN_SHA,
            f"ladder champion is {sha(champ_min)}, expected {CHAMPION_MIN_SHA}")
    require(token_stream(readable) == token_stream(champ_min),
            "the readable base and the ladder champion are not the same program")

    source = SOURCE.read_text()
    require(sha(source) == SOURCE_SHA, f"source is {sha(source)}, expected {SOURCE_SHA}")

    lines = source.split("\n")
    marker = ba.flag_line(True, True)
    require(lines.count(marker) == 1,
            f"the flag line occurs {lines.count(marker)} times, expected 1")
    arm_text = "\n".join(marker if l == marker else l for l in lines)
    differing = [i + 1 for i, (a, b) in enumerate(zip(lines, arm_text.split("\n"))) if a != b]
    require(not differing,
            f"{len(differing)} lines differ from the source, expected 0 (B IS the source arm)")
    flag_line_number = lines.index(marker) + 1

    gated = GATED_ARM.read_text()
    require(sha(gated) == GATED_ARM_SHA,
            f"the gated instrument arm is {sha(gated)}, expected {GATED_ARM_SHA}")
    require(arm_text == gated,
            "the regenerated arm is NOT byte-identical to the gated instrument arm")

    ba.compile_check(arm_text, "candidate3_keep_v6_instrument")
    ARM.write_text(arm_text)
    (HERE / "candidate-3-keep-v6-instrument.rs.sha256").write_text(
        f"{sha(arm_text)}  candidate-3-keep-v6-instrument.rs\n")

    compacted = crs.compact(arm_text)
    if not compacted.endswith("\n"):
        compacted += "\n"
    SUBMISSION.write_text(compacted)
    written = SUBMISSION.read_text()
    require(written == compacted, "the written submission differs from what was compacted")
    require(token_stream(written) == token_stream(arm_text),
            "round trip FAILED: the compacted file is not the arm's token stream")
    ba.compile_check(written, "candidate3_keep_v6_instrument_min")
    (SUBMISSION.parent / (SUBMISSION.name + ".sha256")).write_text(
        f"{sha(written)}  {SUBMISSION.name}\n")

    bot_a = BOT_A_MIN.read_text()
    require(token_stream(written) != token_stream(bot_a),
            "bot B has the same token stream as bot A: the measurement would compare A with A")

    report = {
        "schema": "troll-farm-readable-source-v2",
        "task": "20260826-ladder-measure-cured-dancing-troll",
        "board_row": "L-1",
        "bot": "B",
        "arm": {"path": str(ARM.relative_to(REPO)), "sha256": sha(arm_text),
                "lines": arm_text.count("\n") + 1, "bytes": len(arm_text.encode())},
        "compacted": {"path": str(SUBMISSION.relative_to(REPO)), "sha256": sha(written),
                      "bytes": len(written.encode())},
        "base_readable": {"path": str(READABLE.relative_to(REPO)), "sha256": READABLE_SHA},
        "base_compacted": {"path": str(CHAMPION_MIN.relative_to(REPO)),
                           "sha256": CHAMPION_MIN_SHA},
        "source": {"path": str(SOURCE.relative_to(REPO)), "sha256": SOURCE_SHA},
        "keep_rule_enabled": True,
        "narrate_v6_enabled": True,
        "identical_to_gated_instrument_arm": True,
        "gated_instrument_arm": {"path": str(GATED_ARM.relative_to(REPO)),
                                 "sha256": GATED_ARM_SHA},
        "lines_differing_from_source": 0,
        "flag_line_number": flag_line_number,
        "base_readable_and_ladder_champion_same_token_stream": True,
        "canonical_token_stream_identical": True,
        "distinct_from_bot_a_submission": {
            "path": str(BOT_A_MIN.relative_to(REPO)), "sha256": sha(bot_a),
            "same_token_stream": False},
        "compiles": True,
        "verdict": "CANDIDATE_3_KEEP_V6_INSTRUMENT_ROUND_TRIP_EXACT",
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (HERE / "results" / "build.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"  arm         {sha(arm_text)[:16]}  {report['arm']['lines']} lines"
          f"  (flag line {flag_line_number}, 0 lines differ from source)")
    print(f"  compacted   {sha(written)[:16]}  {report['compacted']['bytes']} bytes"
          f"  -> {SUBMISSION.relative_to(REPO)}")
    print(f"  vs bot A    different token stream (A {sha(bot_a)[:16]})")
    print(f"  round trip  EXACT -> {REPORT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BuildError as exc:
        print(f"BUILD REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
