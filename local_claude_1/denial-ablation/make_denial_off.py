#!/usr/bin/env python3
"""Build the denial-ablation instrument: the diagnostics champion (bot A) with its plum/lemon
denial bonus removed -- the owner's one-variable experiment of 2026-08-27 08:05Z.

THE EXPERIMENT (owner, plain words): "we conducted a dirty experiment -- we changed several
variables in one turn. Take our champion with the simplest code and highest rating and turn this
plum-lemon denial logic at the beginning of the game off. I predict one hour exposition to arena
will show drastical rating drop." This file produces the bot for that hour and nothing else: it
is an INSTRUMENT (a measurement of one rule's worth on the ladder), not a candidate. It promotes
nothing and qualifies nothing.

THE ONE CHANGE. In the champion's chop scoring (`chop_candidates`) a chop on a tree of the
"focus" species -- plum or lemon, whichever stands nearer our shack (`focus_type`) -- earns a
bonus of 900 / (1 + Manhattan distance to the opponent's shack) while the opponent has at most
two trolls. That is the whole of the champion's targeted denial; every other chop is scored as
plain wood per turn. The four lines that grant the bonus are deleted. Nothing else changes.

The base is bot A -- the champion plus the v6 diagnostic line (`NARRATE_V6_ENABLED = true`,
`KEEP_RULE_ENABLED = false`), identical in play to the ladder champion `547fa706...` on 240/240
panel games and 34/34 fixtures -- so that the hour's games come home annotated.

Identical in method to `claude_1/ladder-measure-b/make_candidate3_v6.py` (bot B) and to the path
that produced bot A: ONE source, ONE flag line, ONE edit, the same compactor, the same round trip.

Chain, each link checked and each failure fatal:

  1. `readable/door1-champion.rs`               sha256 ad1ae4ef...  the base of record
  2. compact(1) == `cgauto/submissions/candidate-door1-pure-deletion.rs` in canonical token
     stream                                     the base IS the ladder champion 547fa706...
  3. `claude_1/cure3/cure3-keep-v6.rs`          sha256 01b61444...  the one source; with the flag
     line rewritten to KEEP=false NARRATE=true it must equal bot A's gated arm
     `claude_1/instrument6/champion-v6-instrument.rs` (sha256 0f75e7d6...) byte for byte, and
     exactly ONE line (the flag line) may differ from the source
  4. the ONE edit: the four-line bonus hunk occurs exactly once in the arm and exactly once in
     the readable base, and is removed from both (the readable diff is the same edit)
  5. the edited arm compiles (rustc --edition=2021 -O)
  6. compact(5) -> `cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs`, sha256 in
     a `.sha256` sidecar, round trip re-checked from the written file, and the file compiles
  7. the written file is a NEW program on the ladder: its token stream differs from the bare
     champion, from bot A, from bot B and from the farm
  8. `readable/diffs/denial-bonus-off.diff` = unified diff of the readable champion against the
     readable champion with the same hunk removed -- the diff the owner reads

    python3 local_claude_1/denial-ablation/make_denial_off.py
"""
from __future__ import annotations

import difflib
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
BOT_A_ARM = REPO / "claude_1" / "instrument6" / "champion-v6-instrument.rs"
BOT_A_ARM_SHA = "0f75e7d61c71d4881502aac2204faf6fb5035331857a9f400ea2647bccd94141"
BOT_A_MIN = REPO / "cgauto" / "submissions" / "candidate-champion-v6-instrument.rs"
BOT_A_MIN_SHA = "726731247910d846242fdabd0371c6f99ceb5c12de5e47d2b750d065b2b58c82"
BOT_B_MIN = REPO / "cgauto" / "submissions" / "candidate-3-keep-v6-instrument.rs"
FARM_MIN = REPO / "cgauto" / "submissions" / "candidate-banana-farm-v8-instrument.rs"

ARM = HERE / "champion-denial-off-v6-instrument.rs"
SUBMISSION = REPO / "cgauto" / "submissions" / "candidate-champion-denial-off-v6-instrument.rs"
REPORT = REPO / "readable" / "reports" / "candidate-champion-denial-off-v6-instrument.round-trip.json"
DIFF = REPO / "readable" / "diffs" / "denial-bonus-off.diff"

# The four lines that are the champion's targeted denial, verbatim (20-space indentation, as
# they stand in both the readable champion and the v6 source). The trailing newline is part of
# the hunk so that its removal leaves no blank line behind.
HUNK = (
    "                    if Some(plant.kind) == type_to_cut && opponent_trolls <= 2 {\n"
    "                        let opponent_distance = manhattan(plant.cell, view.shacks[1]);\n"
    "                        score += 900.0 / (1 + opponent_distance) as f64;\n"
    "                    }\n"
)


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


def remove_hunk(text: str, what: str) -> str:
    count = text.count(HUNK)
    require(count == 1, f"the bonus hunk occurs {count} times in {what}, expected exactly 1")
    return text.replace(HUNK, "", 1)


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

    # Bot A's arm: the source with the flag line set to KEEP=false NARRATE=true.
    lines = source.split("\n")
    marker_source = ba.flag_line(True, True)
    marker_arm = ba.flag_line(False, True)
    require(lines.count(marker_source) == 1,
            f"the source's flag line occurs {lines.count(marker_source)} times, expected 1")
    bot_a_text = "\n".join(marker_arm if l == marker_source else l for l in lines)
    differing = [i + 1 for i, (a, b) in enumerate(zip(lines, bot_a_text.split("\n"))) if a != b]
    require(differing == [lines.index(marker_source) + 1],
            f"lines differing from the source: {differing}, expected only the flag line")
    flag_line_number = differing[0]

    bot_a_gated = BOT_A_ARM.read_text()
    require(sha(bot_a_gated) == BOT_A_ARM_SHA,
            f"bot A's gated arm is {sha(bot_a_gated)}, expected {BOT_A_ARM_SHA}")
    require(bot_a_text == bot_a_gated,
            "the regenerated bot A arm is NOT byte-identical to the gated instrument arm")

    # The one edit, applied to bot A's arm and -- for the diff the owner reads -- to the
    # readable champion. Both must hold the hunk exactly once.
    arm_text = remove_hunk(bot_a_text, "bot A's arm")
    readable_off = remove_hunk(readable, "the readable champion")
    arm_lines = arm_text.split("\n")
    require(len(bot_a_text.split("\n")) - len(arm_lines) == 4,
            "the edit must remove exactly four lines")

    ba.compile_check(arm_text, "champion_denial_off_v6_instrument")
    ARM.write_text(arm_text)
    (HERE / "champion-denial-off-v6-instrument.rs.sha256").write_text(
        f"{sha(arm_text)}  champion-denial-off-v6-instrument.rs\n")

    compacted = crs.compact(arm_text)
    if not compacted.endswith("\n"):
        compacted += "\n"
    SUBMISSION.write_text(compacted)
    written = SUBMISSION.read_text()
    require(written == compacted, "the written submission differs from what was compacted")
    require(token_stream(written) == token_stream(arm_text),
            "round trip FAILED: the compacted file is not the arm's token stream")
    ba.compile_check(written, "champion_denial_off_v6_instrument_min")
    (SUBMISSION.parent / (SUBMISSION.name + ".sha256")).write_text(
        f"{sha(written)}  {SUBMISSION.name}\n")

    # A new program on the ladder, and not one that is already there.
    distinct = {}
    for label, path in (("bare champion", CHAMPION_MIN), ("bot A", BOT_A_MIN),
                        ("bot B", BOT_B_MIN), ("farm", FARM_MIN)):
        other = path.read_text()
        same = token_stream(written) == token_stream(other)
        require(not same, f"the submission has the same token stream as {label} ({path.name})")
        distinct[label] = {"path": str(path.relative_to(REPO)), "sha256": sha(other),
                           "same_token_stream": False}
    bot_a_min = BOT_A_MIN.read_text()
    require(sha(bot_a_min) == BOT_A_MIN_SHA,
            f"bot A's submission is {sha(bot_a_min)}, expected {BOT_A_MIN_SHA}")

    # The readable diff: the same four lines, removed from the readable champion.
    diff_lines = list(difflib.unified_diff(
        readable.splitlines(keepends=True), readable_off.splitlines(keepends=True),
        fromfile="readable/door1-champion.rs",
        tofile="readable/door1-champion.rs (plum/lemon denial bonus removed)", n=3))
    DIFF.write_text("".join(diff_lines))
    removed = [l for l in diff_lines if l.startswith("-") and not l.startswith("---")]
    added = [l for l in diff_lines if l.startswith("+") and not l.startswith("+++")]
    require(len(removed) == 4 and not added,
            f"the readable diff removes {len(removed)} lines and adds {len(added)}, expected 4/0")

    report = {
        "schema": "troll-farm-readable-source-v2",
        "task": "denial-ablation (owner's one-variable experiment, 2026-08-27 08:05Z)",
        "board_row": "ladder queue slot 2",
        "bot": "the diagnostics champion with the plum/lemon denial bonus removed",
        "arm": {"path": str(ARM.relative_to(REPO)), "sha256": sha(arm_text),
                "lines": len(arm_lines), "bytes": len(arm_text.encode())},
        "compacted": {"path": str(SUBMISSION.relative_to(REPO)), "sha256": sha(written),
                      "bytes": len(written.encode())},
        "base_readable": {"path": str(READABLE.relative_to(REPO)), "sha256": READABLE_SHA},
        "base_compacted": {"path": str(CHAMPION_MIN.relative_to(REPO)),
                           "sha256": CHAMPION_MIN_SHA},
        "source": {"path": str(SOURCE.relative_to(REPO)), "sha256": SOURCE_SHA},
        "bot_a_arm": {"path": str(BOT_A_ARM.relative_to(REPO)), "sha256": BOT_A_ARM_SHA,
                      "regenerated_byte_identical": True, "flag_line_number": flag_line_number},
        "keep_rule_enabled": False,
        "narrate_v6_enabled": True,
        "edit": {"what": "the four-line plum/lemon denial bonus in chop_candidates removed",
                 "hunk": HUNK, "lines_removed": 4, "lines_added": 0,
                 "occurrences_in_arm": 1, "occurrences_in_readable": 1},
        "readable_diff": {"path": str(DIFF.relative_to(REPO)), "removed": 4, "added": 0},
        "base_readable_and_ladder_champion_same_token_stream": True,
        "canonical_token_stream_identical": True,
        "distinct_from": distinct,
        "compiles": True,
        "verdict": "CHAMPION_DENIAL_OFF_V6_INSTRUMENT_ROUND_TRIP_EXACT",
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "build.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"  bot A arm   regenerated byte-identical (flag line {flag_line_number})")
    print(f"  arm         {sha(arm_text)[:16]}  {len(arm_lines)} lines  (4 lines removed)")
    print(f"  compacted   {sha(written)[:16]}  {report['compacted']['bytes']} bytes"
          f"  -> {SUBMISSION.relative_to(REPO)}")
    print(f"  distinct    from the bare champion, bot A, bot B and the farm")
    print(f"  diff        {DIFF.relative_to(REPO)}  (-4 / +0)")
    print(f"  round trip  EXACT -> {REPORT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BuildError as exc:
        print(f"BUILD REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
