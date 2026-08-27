#!/usr/bin/env python3
"""Build "the floor": the champion of record with ONE change -- the second troll is never weaker
than speed 2, carry 2, chop 2 (harvest 0 as before). The owner's one-variable experiment of
2026-08-27 ("let's build the_floor"), born from the second-troll census
(`local_claude_1/second-troll-census/README.md`): the strong bots buy the same 2/2/0/2 troll we
do, later and never weaker; we field a weaker one in 37-45 % of games and lose those twice as
often within a batch.

THE RULE (owner, plain words). The bot waits until it can pay for a 2/2/0/2 troll (5 plums,
5 lemons, 1 apple, 5 iron); when a stronger one is fundable within its usual 15-turn horizon it
takes the stronger one, as before. From turn 35 (the existing deadline), if the wanted troll is
still unaffordable, it takes the strongest floored troll it can afford right now, and otherwise
keeps waiting for the basic 2/2/0/2 -- it never gives up training. Everything else is the champion.

WHAT THIS FILE IS. An INSTRUMENT for one hour on the ladder and a reading against the owner's
prediction; it promotes nothing and qualifies nothing. Identical in method to
`local_claude_1/apple-farm/make_apple_farm.py`: ONE base, the SAME edit applied to the
diagnostics arm and to the readable source, the same compactor, the same round trip -- except
that the edit is five REPLACEMENTS (anchor -> text), not pure insertions.

THE BASE is the champion of record (owner ruling 2026-08-27 09:05Z): its diagnostics arm
`local_claude_1/denial-ablation/champion-denial-off-v6-instrument.rs` (sha256 32172393...) whose
compacted form IS the ladder resident `41202036` (`cgauto/submissions/
candidate-champion-denial-off-v6-instrument.rs`, sha256 0e92f8fa...), and its readable form
`readable/denial-off-champion.rs` (sha256 4ce3d1e8...). The v6 diagnostic line is untouched.

THE EDIT, five replacements, each anchored on text that occurs exactly once in BOTH files:

  1. `opening_options`          -- the grid of candidate trolls starts at 2 for speed, carry and
                                   chop (2..3 each; the caps clamp to 2..3);
  2. `choose_second_troll`      -- the baseline when nothing is fundable within the horizon is
                                   the fallback troll (one definition instead of a second copy);
  3. `fallback_second_troll`    -- 1/1/0/1 -> 2/2/0/2;
  4. `enforce_training_deadline`-- the strongest affordable floored troll, else the fallback
                                   2/2/0/2 and keep waiting (the give-up branch is gone);
  5. the deadline block's comment says what it now does.

Chain, each link checked and each failure fatal:

  a. the three base files match their recorded sha256; compact(arm) == the ladder resident;
  b. every anchor occurs exactly once in the arm and exactly once in the readable source;
  c. the edited arm and the edited readable source both compile (rustc --edition=2021 -O);
  d. compact(edited arm) -> `cgauto/submissions/candidate-the-floor-v6-instrument.rs`, sha256
     sidecar, round trip re-checked from the written file, and the file compiles;
  e. the written file is a NEW program on the ladder: its token stream differs from the bare
     champion, bot A, bot B, the banana farm, the apple farm and the resident;
  f. `readable/diffs/the-floor.diff` = unified diff of the readable champion against the readable
     champion with the same replacements -- the diff the owner reads; its +/- counts equal the
     replacements' own counts.

    python3 local_claude_1/the-floor/make_the_floor.py
"""
from __future__ import annotations

import difflib
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "cgauto"))
sys.path.insert(0, str(REPO / "claude_1" / "cure3"))

import compact_rust_source as crs      # noqa: E402
import build_arms3 as ba               # noqa: E402

ARM_BASE = REPO / "local_claude_1" / "denial-ablation" / "champion-denial-off-v6-instrument.rs"
ARM_BASE_SHA = "321723933c2a0cfb6bfcd62c57e0d25b6783ffb8ddcfea37c05b053e2e46cd4f"
READABLE = REPO / "readable" / "denial-off-champion.rs"
READABLE_SHA = "4ce3d1e85e8962d84c0ecb1a071de46e844d24f7dbe5a31bd6ca0579db552143"
RESIDENT_MIN = REPO / "cgauto" / "submissions" / "candidate-champion-denial-off-v6-instrument.rs"
RESIDENT_MIN_SHA = "0e92f8fa1e9097dd3df81989e222be8810f3cebdcd3efc950f84353f0bd1d57c"

OTHERS = (
    ("bare champion (old)", REPO / "cgauto" / "submissions" / "candidate-door1-pure-deletion.rs"),
    ("bot A (old champion + diagnostics)",
     REPO / "cgauto" / "submissions" / "candidate-champion-v6-instrument.rs"),
    ("bot B (keep-your-goal)", REPO / "cgauto" / "submissions" / "candidate-3-keep-v6-instrument.rs"),
    ("banana farm", REPO / "cgauto" / "submissions" / "candidate-banana-farm-v8-instrument.rs"),
    ("apple farm", REPO / "cgauto" / "submissions" / "candidate-apple-farm-v6-instrument.rs"),
    ("the resident (champion of record)", RESIDENT_MIN),
)

ARM = HERE / "champion-the-floor-v6-instrument.rs"
READABLE_EDITED = HERE / "the-floor-readable.rs"
SUBMISSION = REPO / "cgauto" / "submissions" / "candidate-the-floor-v6-instrument.rs"
REPORT = REPO / "readable" / "reports" / "candidate-the-floor-v6-instrument.round-trip.json"
DIFF = REPO / "readable" / "diffs" / "the-floor.diff"

# --------------------------------------------------------------------------------------------
# The five replacements. `anchor` occurs exactly once in both files and is replaced by `text`.
# Indentation as it stands in both files (12 spaces = an `impl` item, 16 = a function body).
# --------------------------------------------------------------------------------------------

REPL_GRID = dict(
    name="opening_options: the grid starts at 2 for speed, carry and chop",
    anchor=(
        "                let max_carry_capacity = max_carry_capacity.clamp(1, 3);\n"
        "                let max_chop_power = max_chop_power.clamp(1, 3);\n"
        "                for movement_speed in 1..=3 {\n"
        "                    for carry_capacity in 1..=max_carry_capacity {\n"
        "                        for chop_power in 1..=max_chop_power {\n"
    ),
    text=(
        "                let max_carry_capacity = max_carry_capacity.clamp(2, 3);\n"
        "                let max_chop_power = max_chop_power.clamp(2, 3);\n"
        "                for movement_speed in 2..=3 {\n"
        "                    for carry_capacity in 2..=max_carry_capacity {\n"
        "                        for chop_power in 2..=max_chop_power {\n"
    ),
)

REPL_BASELINE = dict(
    name="choose_second_troll: the baseline is the fallback troll (one definition)",
    anchor=(
        "                    .unwrap_or_else(|| {\n"
        "                        Self::opening_objective(\n"
        "                            view,\n"
        "                            Stats {\n"
        "                                movement_speed: 1,\n"
        "                                carry_capacity: 1,\n"
        "                                harvest_power: 0,\n"
        "                                chop_power: 1,\n"
        "                            },\n"
        "                        )\n"
        "                    });\n"
    ),
    text=(
        "                    .unwrap_or_else(|| {\n"
        "                        Self::opening_objective(view, Self::fallback_second_troll())\n"
        "                    });\n"
    ),
)

REPL_FALLBACK = dict(
    name="fallback_second_troll: 1/1/0/1 -> 2/2/0/2",
    anchor=(
        "            fn fallback_second_troll() -> Stats {\n"
        "                Stats {\n"
        "                    movement_speed: 1,\n"
        "                    carry_capacity: 1,\n"
        "                    harvest_power: 0,\n"
        "                    chop_power: 1,\n"
        "                }\n"
        "            }\n"
    ),
    text=(
        "            fn fallback_second_troll() -> Stats {\n"
        "                Stats {\n"
        "                    movement_speed: 2,\n"
        "                    carry_capacity: 2,\n"
        "                    harvest_power: 0,\n"
        "                    chop_power: 2,\n"
        "                }\n"
        "            }\n"
    ),
)

REPL_DEADLINE = dict(
    name="enforce_training_deadline: strongest affordable floored troll, else wait for 2/2/0/2",
    anchor=(
        "                self.desired_second = Self::strongest_affordable(view, self.opening_policy);\n"
        "                if self.desired_second.is_none() {\n"
        "                    self.opening_abandoned = true;\n"
        "                }\n"
    ),
    text=(
        "                self.desired_second = Some(\n"
        "                    Self::strongest_affordable(view, self.opening_policy).unwrap_or_else(|| {\n"
        "                        Self::opening_objective(view, Self::fallback_second_troll())\n"
        "                    }),\n"
        "                );\n"
    ),
)

REPL_COMMENT = dict(
    name="the deadline block's comment",
    anchor=(
        "            // If the second worker has not been trained by a deadline turn, abandons the preferred\n"
        "            // build and trains the strongest currently affordable one instead.\n"
    ),
    text=(
        "            // If the second worker has not been trained by a deadline turn, trains the strongest\n"
        "            // currently affordable floored build instead, or waits for the basic 2/2/0/2 -- the\n"
        "            // second troll is never weaker than speed 2, carry 2, chop 2 (the floor, 2026-08-27).\n"
    ),
)

REPLACEMENTS = (REPL_GRID, REPL_BASELINE, REPL_FALLBACK, REPL_DEADLINE, REPL_COMMENT)


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


def apply_replacements(text: str, what: str) -> str:
    for rep in REPLACEMENTS:
        count = text.count(rep["anchor"])
        require(count == 1, f"anchor for '{rep['name']}' occurs {count} times in {what}, expected 1")
        text = text.replace(rep["anchor"], rep["text"], 1)
    return text


def plus_minus(a: str, b: str) -> tuple[int, int]:
    """(+added, -removed) lines of a unified diff of a against b."""
    lines = list(difflib.unified_diff(a.splitlines(keepends=True), b.splitlines(keepends=True), n=0))
    added = sum(1 for l in lines if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in lines if l.startswith("-") and not l.startswith("---"))
    return added, removed


def rustfmt_status(path: Path) -> str:
    exe = shutil.which("rustfmt")
    if exe is None:
        return "unavailable"
    proc = subprocess.run([exe, "--check", "--edition", "2021", str(path)],
                          capture_output=True, text=True)
    return "clean" if proc.returncode == 0 else "NOT clean"


def main() -> int:
    arm_base = ARM_BASE.read_text()
    require(sha(arm_base) == ARM_BASE_SHA, f"arm base is {sha(arm_base)}, expected {ARM_BASE_SHA}")
    readable = READABLE.read_text()
    require(sha(readable) == READABLE_SHA, f"readable base is {sha(readable)}, expected {READABLE_SHA}")
    resident = RESIDENT_MIN.read_text()
    require(sha(resident) == RESIDENT_MIN_SHA,
            f"the resident is {sha(resident)}, expected {RESIDENT_MIN_SHA}")
    require(token_stream(arm_base) == token_stream(resident),
            "the arm base and the ladder resident are not the same program")

    arm_text = apply_replacements(arm_base, "the arm")
    readable_edited = apply_replacements(readable, "the readable champion")
    expected_added = sum(plus_minus(r["anchor"], r["text"])[0] for r in REPLACEMENTS)
    expected_removed = sum(plus_minus(r["anchor"], r["text"])[1] for r in REPLACEMENTS)
    delta_arm = len(arm_text.split("\n")) - len(arm_base.split("\n"))
    delta_readable = len(readable_edited.split("\n")) - len(readable.split("\n"))
    require(delta_arm == delta_readable == expected_added - expected_removed,
            f"line delta: arm {delta_arm}, readable {delta_readable}, "
            f"expected {expected_added - expected_removed}")

    ba.compile_check(arm_text, "champion_the_floor_v6_instrument")
    ba.compile_check(readable_edited, "champion_the_floor_readable")
    ARM.write_text(arm_text)
    (HERE / (ARM.name + ".sha256")).write_text(f"{sha(arm_text)}  {ARM.name}\n")
    READABLE_EDITED.write_text(readable_edited)
    (HERE / (READABLE_EDITED.name + ".sha256")).write_text(
        f"{sha(readable_edited)}  {READABLE_EDITED.name}\n")
    # Printed only, never written to a tracked file: the answer depends on the machine (the VM has
    # no rustfmt), and a regeneration must leave the tracked files byte-identical everywhere
    # (codex_1's 0-6 blocker, 18:15Z). The base readable is not clean under the installed rustfmt
    # either, so the line is informational.
    fmt = rustfmt_status(READABLE_EDITED)

    compacted = crs.compact(arm_text)
    if not compacted.endswith("\n"):
        compacted += "\n"
    SUBMISSION.write_text(compacted)
    written = SUBMISSION.read_text()
    require(written == compacted, "the written submission differs from what was compacted")
    require(token_stream(written) == token_stream(arm_text),
            "round trip FAILED: the compacted file is not the arm's token stream")
    ba.compile_check(written, "champion_the_floor_v6_instrument_min")
    (SUBMISSION.parent / (SUBMISSION.name + ".sha256")).write_text(
        f"{sha(written)}  {SUBMISSION.name}\n")

    distinct = {}
    for label, path in OTHERS:
        other = path.read_text()
        require(token_stream(written) != token_stream(other),
                f"the submission has the same token stream as {label} ({path.name})")
        distinct[label] = {"path": str(path.relative_to(REPO)), "sha256": sha(other),
                           "same_token_stream": False}

    diff_lines = list(difflib.unified_diff(
        readable.splitlines(keepends=True), readable_edited.splitlines(keepends=True),
        fromfile="readable/denial-off-champion.rs",
        tofile="readable/denial-off-champion.rs (the floor)", n=3))
    DIFF.write_text("".join(diff_lines))
    removed = [l for l in diff_lines if l.startswith("-") and not l.startswith("---")]
    added = [l for l in diff_lines if l.startswith("+") and not l.startswith("+++")]
    require(len(removed) == expected_removed and len(added) == expected_added,
            f"the readable diff removes {len(removed)} and adds {len(added)}, "
            f"expected {expected_removed}/{expected_added}")

    report = {
        "schema": "troll-farm-readable-source-v2",
        "task": "the floor (owner's one-variable experiment, 2026-08-27: 'let's build the_floor')",
        "board_row": "ladder queue slot 4",
        "bot": "the champion of record; the second troll never weaker than 2/2/0/2",
        "arm": {"path": str(ARM.relative_to(REPO)), "sha256": sha(arm_text),
                "lines": len(arm_text.split("\n")), "bytes": len(arm_text.encode())},
        "compacted": {"path": str(SUBMISSION.relative_to(REPO)), "sha256": sha(written),
                      "bytes": len(written.encode())},
        "readable_edited": {"path": str(READABLE_EDITED.relative_to(REPO)),
                            "sha256": sha(readable_edited)},
        "base_arm": {"path": str(ARM_BASE.relative_to(REPO)), "sha256": ARM_BASE_SHA},
        "base_readable": {"path": str(READABLE.relative_to(REPO)), "sha256": READABLE_SHA},
        "base_resident": {"path": str(RESIDENT_MIN.relative_to(REPO)), "sha256": RESIDENT_MIN_SHA},
        "keep_rule_enabled": False,
        "narrate_v6_enabled": True,
        "edit": {"what": "five replacements: the floor",
                 "replacements": [{"name": r["name"],
                                   "added": plus_minus(r["anchor"], r["text"])[0],
                                   "removed": plus_minus(r["anchor"], r["text"])[1]}
                                  for r in REPLACEMENTS],
                 "lines_added": expected_added, "lines_removed": expected_removed},
        "readable_diff": {"path": str(DIFF.relative_to(REPO)), "added": expected_added,
                          "removed": expected_removed},
        "base_arm_and_resident_same_token_stream": True,
        "canonical_token_stream_identical": True,
        "distinct_from": distinct,
        "compiles": True,
        "verdict": "CHAMPION_THE_FLOOR_V6_INSTRUMENT_ROUND_TRIP_EXACT",
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "build.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"  base        arm {ARM_BASE_SHA[:16]} == resident {RESIDENT_MIN_SHA[:16]} (token stream)")
    print(f"  arm         {sha(arm_text)[:16]}  {report['arm']['lines']} lines"
          f"  (+{expected_added} / -{expected_removed})")
    print(f"  readable    {sha(readable_edited)[:16]}  rustfmt --check: {fmt}")
    print(f"  compacted   {sha(written)[:16]}  {report['compacted']['bytes']} bytes"
          f"  -> {SUBMISSION.relative_to(REPO)}")
    print(f"  distinct    from {', '.join(label for label, _ in OTHERS)}")
    print(f"  diff        {DIFF.relative_to(REPO)}  (+{expected_added} / -{expected_removed})")
    print(f"  round trip  EXACT -> {REPORT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BuildError as exc:
        print(f"BUILD REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
