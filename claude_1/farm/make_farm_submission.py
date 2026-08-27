#!/usr/bin/env python3
"""Compact the banana farm's instrument arm into a ladder submission — task
`20260826-banana-farm-candidate` (board row F-2), owner ruling of 2026-08-27 06:06Z.

**What this is and is not.** The owner asked to *watch* the farm play on the platform: "I want to
see with my eyes how the current banana farm plays." The farm failed its validity gate (V1,
blocking games 52 to 96) and that verdict stands. This build promotes nothing and qualifies
nothing; it produces the file the coordinator submits so the farm's games come home, and the
telemetry arm is the one wanted because those games come home annotated (v8 on the wire).

Identical in method to `claude_1/ladder-measure-b/make_candidate3_v6.py`, which produced bot B,
and to the path that produced the champion instrument: ONE source, ONE flag line, the same
compactor, the same round trip. This script does NOT copy the gated arm. It regenerates it from
`farm-v8.rs` and the flag line, then REFUSES unless the bytes it produced are the bytes already
gated by the F-2 panel. A generator that agrees with the record is evidence; a copy is not.

Chain, each link checked and each failure fatal:

  1. `readable/door1-champion.rs`         sha256 ad1ae4ef...  the base of record
  2. compact(1) == `cgauto/submissions/candidate-door1-pure-deletion.rs` in canonical token
     stream                                the base IS the ladder champion 547fa706...
  3. `claude_1/farm/farm-v8.rs`           sha256 354d1302...  the one source
  4. (3) with the flag line rewritten to FARM=true NARRATE=true KEEP=false — the instrument arm
     IS the source, so exactly ZERO lines differ (the other two arms differ in exactly one)
  5. (4) == `claude_1/farm/arm-instrument.rs` byte for byte    the panel-gated object
  6. (4) compiles (rustc --edition=2021 -O)
  7. compact(4) -> `cgauto/submissions/candidate-banana-farm-v8-instrument.rs`, sha256 recorded
     in a `.sha256` sidecar, round trip re-checked from the written file, and the file compiles
  8. the written file is NOT the same program as the ladder champion it will replace, nor as
     bot A or bot B of the L-1 measurement — a submission that is a bot already on the ladder
     would show the owner nothing new

    python3 claude_1/farm/make_farm_submission.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "cgauto"))
sys.path.insert(0, str(HERE))

import compact_rust_source as crs      # noqa: E402
import build_arms_farm as ba           # noqa: E402

READABLE = REPO / "readable" / "door1-champion.rs"
READABLE_SHA = "ad1ae4eff70a5569e03e2149882bb22510746f4f8592907a5dfb936943ef0bfb"
CHAMPION_MIN = REPO / "cgauto" / "submissions" / "candidate-door1-pure-deletion.rs"
CHAMPION_MIN_SHA = "547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0"
SOURCE = HERE / "farm-v8.rs"
SOURCE_SHA = "354d1302f79ddc241ae49c5c0b1763ad045077bfb5f74d6e850bf43a43376b41"
GATED_ARM = HERE / "arm-instrument.rs"
GATED_ARM_SHA = "354d1302f79ddc241ae49c5c0b1763ad045077bfb5f74d6e850bf43a43376b41"

# Bots already on the ladder, by their submission files. The farm must not be any of them.
OTHER_LADDER_BOTS = {
    "ladder_champion": CHAMPION_MIN,
    "bot_a_champion_v6_instrument": REPO / "cgauto" / "submissions"
    / "candidate-champion-v6-instrument.rs",
    "bot_b_candidate_3_keep_v6_instrument": REPO / "cgauto" / "submissions"
    / "candidate-3-keep-v6-instrument.rs",
}

SUBMISSION = REPO / "cgauto" / "submissions" / "candidate-banana-farm-v8-instrument.rs"
REPORT = (REPO / "readable" / "reports"
          / "candidate-banana-farm-v8-instrument.round-trip.json")


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
    marker = ba.flag_line(True, True)          # FARM=true, NARRATE=true, KEEP=false
    require(lines.count(marker) == 1,
            f"the flag line occurs {lines.count(marker)} times, expected 1")
    arm_text = "\n".join(marker if l == marker else l for l in lines)
    differing = [i + 1 for i, (a, b) in enumerate(zip(lines, arm_text.split("\n"))) if a != b]
    require(not differing,
            f"{len(differing)} lines differ from the source, expected 0 "
            f"(the instrument arm IS the source)")
    flag_line_number = lines.index(marker) + 1

    gated = GATED_ARM.read_text()
    require(sha(gated) == GATED_ARM_SHA,
            f"the gated instrument arm is {sha(gated)}, expected {GATED_ARM_SHA}")
    require(arm_text == gated,
            "the regenerated arm is NOT byte-identical to the panel-gated instrument arm")

    ba.compile_check(arm_text, "banana_farm_v8_instrument")

    compacted = crs.compact(arm_text)
    if not compacted.endswith("\n"):
        compacted += "\n"
    SUBMISSION.write_text(compacted)
    written = SUBMISSION.read_text()
    require(written == compacted, "the written submission differs from what was compacted")
    require(token_stream(written) == token_stream(arm_text),
            "round trip FAILED: the compacted file is not the arm's token stream")
    ba.compile_check(written, "banana_farm_v8_instrument_min")
    (SUBMISSION.parent / (SUBMISSION.name + ".sha256")).write_text(
        f"{sha(written)}  {SUBMISSION.name}\n")

    distinct = {}
    for name, path in OTHER_LADDER_BOTS.items():
        other = path.read_text()
        same = token_stream(written) == token_stream(other)
        require(not same,
                f"the farm submission has the same token stream as {name} "
                f"({path.relative_to(REPO)}): submitting it would show the owner nothing new")
        distinct[name] = {"path": str(path.relative_to(REPO)), "sha256": sha(other),
                          "same_token_stream": False}

    report = {
        "schema": "troll-farm-readable-source-v2",
        "task": "20260826-banana-farm-candidate",
        "board_row": "F-2",
        "purpose": ("owner ruling 2026-08-27 06:06Z: the farm goes on the ladder to be WATCHED, "
                    "not promoted. The V1 validity failure stands; this build carries no verdict "
                    "about the farm's value and the champion of record remains the champion."),
        "arm": {"path": str(GATED_ARM.relative_to(REPO)), "sha256": sha(arm_text),
                "lines": arm_text.count("\n") + 1, "bytes": len(arm_text.encode())},
        "compacted": {"path": str(SUBMISSION.relative_to(REPO)), "sha256": sha(written),
                      "bytes": len(written.encode()),
                      "lines": written.count("\n") + 1},
        "base_readable": {"path": str(READABLE.relative_to(REPO)), "sha256": READABLE_SHA},
        "base_compacted": {"path": str(CHAMPION_MIN.relative_to(REPO)),
                           "sha256": CHAMPION_MIN_SHA},
        "source": {"path": str(SOURCE.relative_to(REPO)), "sha256": SOURCE_SHA},
        "generator_of_source": "claude_1/farm/make_farm_source.py",
        "keep_rule_enabled": False,
        "farm_enabled": True,
        "narrate_v8_enabled": True,
        "dialect": "v8 (claude_1/narrate8/narrate8.py)",
        "identical_to_gated_instrument_arm": True,
        "gated_instrument_arm": {"path": str(GATED_ARM.relative_to(REPO)),
                                 "sha256": GATED_ARM_SHA},
        "lines_differing_from_source": 0,
        "flag_line_number": flag_line_number,
        "base_readable_and_ladder_champion_same_token_stream": True,
        "canonical_token_stream_identical": True,
        "distinct_from_other_ladder_bots": distinct,
        "compiles": True,
        "verdict": "BANANA_FARM_V8_INSTRUMENT_ROUND_TRIP_EXACT",
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (HERE / "results" / "submission-build.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"  arm         {sha(arm_text)[:16]}  {report['arm']['lines']} lines"
          f"  (flag line {flag_line_number}, 0 lines differ from source)")
    print(f"  compacted   {sha(written)[:16]}  {report['compacted']['bytes']} bytes"
          f"  -> {SUBMISSION.relative_to(REPO)}")
    for name, info in distinct.items():
        print(f"  vs {name:<32} different token stream ({info['sha256'][:16]})")
    print(f"  round trip  EXACT -> {REPORT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BuildError as exc:
        print(f"BUILD REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
