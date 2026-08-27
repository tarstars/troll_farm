#!/usr/bin/env python3
"""Build the apple-farm instrument: the champion of record plus ONE rule -- the owner's
one-variable experiment of 2026-08-27 ("let's do it"; design approved "1 c, 2 yes").

THE RULE (owner, plain words). If a grass cell touching our shack also touches water, the
starting troll plants an apple there on turns 1-3 (a water-side apple regrows a fruit every 2
turns), runs the normal opening (collects the training bill, trains the second troll), and once
the second troll exists returns to the cell and harvests it to the end of the game -- HARVEST
and DROP alternating without moving, half a point a turn. No own troll ever fells the farm tree.
The trained troll is unchanged (harvest power 0). Everything else is the champion.

WHAT THIS FILE IS. An INSTRUMENT for one hour on the ladder and a reading against the owner's
prediction; it promotes nothing and qualifies nothing (memory: the owner's loop is
"fix -> ladder -> one hour -> rating"). Identical in method to
`local_claude_1/denial-ablation/make_denial_off.py`: ONE base, the SAME edit applied to the
diagnostics arm and to the readable source, the same compactor, the same round trip.

THE BASE is the champion of record (owner ruling 2026-08-27 09:05Z): its diagnostics arm
`local_claude_1/denial-ablation/champion-denial-off-v6-instrument.rs` (sha256 32172393...) whose
compacted form IS the ladder resident `41202036` (`cgauto/submissions/
candidate-champion-denial-off-v6-instrument.rs`, sha256 0e92f8fa...), and its readable form
`readable/denial-off-champion.rs` (sha256 4ce3d1e8...). The v6 diagnostic line is untouched: it
already names every troll's chosen target each turn (TREE = harvest, BANK = drop, CELL = pick /
plant / move), so the hour's games come home annotated without a new decoder.

THE EDIT is four pure insertions (+N / -0), each anchored on text that occurs exactly once in
BOTH the arm and the readable source, so the diff the owner reads (`readable/diffs/
apple-farm.diff`) is the edit the ladder receives:

  1. `chop_candidates`   -- skip the farm cell's tree (no own troll ever fells the farm);
  2. `impl MoisanBot`    -- `farm_cell` (which door is the farm) and `farm_unit` (which troll);
  3. `impl YamoBot`      -- `farm_candidates` (the farm troll's turn: MOVE / PICK / PLANT /
                            HARVEST / DROP / WAIT);
  4. `commands`          -- the hook: when the farm owns a troll's turn, its candidate list is
                            the farm's.

Chain, each link checked and each failure fatal:

  a. the three base files match their recorded sha256; compact(arm) == the ladder resident;
  b. every anchor occurs exactly once in the arm and exactly once in the readable source;
  c. the edited arm and the edited readable source both compile (rustc --edition=2021 -O);
  d. compact(edited arm) -> `cgauto/submissions/candidate-apple-farm-v6-instrument.rs`, sha256
     sidecar, round trip re-checked from the written file, and the file compiles;
  e. the written file is a NEW program on the ladder: its token stream differs from the bare
     champion, bot A, bot B, the banana farm and the resident;
  f. `readable/diffs/apple-farm.diff` = unified diff of the readable champion against the readable
     champion with the same insertions -- the diff the owner reads; +N / -0 asserted.

    python3 local_claude_1/apple-farm/make_apple_farm.py
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
    ("the resident (champion of record)", RESIDENT_MIN),
)

ARM = HERE / "champion-apple-farm-v6-instrument.rs"
READABLE_EDITED = HERE / "apple-farm-readable.rs"
SUBMISSION = REPO / "cgauto" / "submissions" / "candidate-apple-farm-v6-instrument.rs"
REPORT = REPO / "readable" / "reports" / "candidate-apple-farm-v6-instrument.round-trip.json"
DIFF = REPO / "readable" / "diffs" / "apple-farm.diff"

# --------------------------------------------------------------------------------------------
# The four insertions. `anchor` occurs exactly once in both files; `text` is inserted BEFORE or
# AFTER it. Indentation as it stands in both files (12 spaces = an `impl` item, 16 = a function
# body, 20 = one level in).
# --------------------------------------------------------------------------------------------

INSERT_CHOP_SKIP = dict(
    name="chop_candidates skips the farm tree",
    where="after",
    anchor=(
        "                for plant in &view.plants {\n"
        "                    if plant.health <= 0 || !from_unit.contains_key(&plant.cell) {\n"
        "                        continue;\n"
        "                    }\n"
    ),
    text=(
        "                    if Self::farm_cell(view) == Some(plant.cell) {\n"
        "                        continue;\n"
        "                    }\n"
    ),
)

INSERT_HELPERS = dict(
    name="farm_cell + farm_unit (impl MoisanBot)",
    where="before",
    anchor="            fn wait() -> Candidate {\n",
    text=(
        "\n"
        "            // --------------------------------------------------------------------------\n"
        "            // Apple farm — indexed block `apple-farm` [feature]\n"
        "            //\n"
        "            // The owner's one-variable experiment of 2026-08-27 (\"let's do it\"; design 1c, 2 yes).\n"
        "            // If a grass cell touching our shack also touches water, the starting troll plants an\n"
        "            // apple there on turns 1-3 (a water-side apple regrows a fruit every 2 turns), runs the\n"
        "            // normal opening, and once the second troll exists returns to harvest it to the end\n"
        "            // of the game -- HARVEST and DROP alternating without moving, half a point a turn.\n"
        "            // No own troll ever fells the farm tree. Everything else is the champion.\n"
        "            //\n"
        "            // The farm cell: a door of our shack (walkable, touching water, never the shack's\n"
        "            // only door), preferring one that already holds an apple, else an empty one.\n"
        "            // --------------------------------------------------------------------------\n"
        "            fn farm_cell(view: &GameState) -> Option<Cell> {\n"
        "                let doors: Vec<Cell> = ortho_neighbors(view.shacks[0])\n"
        "                    .into_iter()\n"
        "                    .filter(|cell| view.walkable.contains(cell))\n"
        "                    .collect();\n"
        "                if doors.len() < 2 {\n"
        "                    return None;\n"
        "                }\n"
        "                let wet: Vec<Cell> = doors\n"
        "                    .into_iter()\n"
        "                    .filter(|cell| view.water.iter().any(|water| is_adjacent(*water, *cell)))\n"
        "                    .collect();\n"
        "                let holds_apple = |cell: &Cell| {\n"
        "                    view.plant_at(*cell).is_some_and(|index| {\n"
        "                        view.plants[index].kind == PlantKind::Apple && view.plants[index].health > 0\n"
        "                    })\n"
        "                };\n"
        "                wet.iter()\n"
        "                    .find(|cell| holds_apple(cell))\n"
        "                    .or_else(|| wet.iter().find(|cell| view.plant_at(**cell).is_none()))\n"
        "                    .copied()\n"
        "            }\n"
        "            // The farm troll: the starting troll -- the own unit with harvest power, lowest id.\n"
        "            fn farm_unit(view: &GameState) -> Option<i32> {\n"
        "                view.units\n"
        "                    .iter()\n"
        "                    .filter(|unit| unit.player == 0 && unit.stats.harvest_power > 0)\n"
        "                    .map(|unit| unit.id)\n"
        "                    .min()\n"
        "            }\n"
    ),
)

INSERT_FARM_TURN = dict(
    name="farm_candidates (impl YamoBot)",
    where="before",
    anchor="            fn endgame(view: &GameState) -> bool {\n",
    text=(
        "\n"
        "            // --------------------------------------------------------------------------\n"
        "            // Apple farm — indexed block `apple-farm` [feature]: the farm troll's turn\n"
        "            //\n"
        "            // Returns the farm troll's whole candidate list when the farm owns its turn: while\n"
        "            // the farm cell has no tree (plant it, in any phase -- turns 1-3 in the normal case),\n"
        "            // and from the second troll on (harvest it). While the tree grows during the opening\n"
        "            // the troll is the champion's. Stateless: if the opponent fells the tree, the same\n"
        "            // rule replants it.\n"
        "            // --------------------------------------------------------------------------\n"
        "            fn farm_candidates(\n"
        "                &mut self,\n"
        "                view: &GameState,\n"
        "                unit: &Unit,\n"
        "                train_now: bool,\n"
        "            ) -> Option<Vec<Candidate>> {\n"
        "                let farm = MoisanBot::farm_cell(view)?;\n"
        "                if MoisanBot::farm_unit(view) != Some(unit.id) {\n"
        "                    return None;\n"
        "                }\n"
        "                let tree = view.plant_at(farm).map(|index| &view.plants[index]);\n"
        "                let trolls = view.units.iter().filter(|unit| unit.player == 0).count();\n"
        "                let harvesting = trolls >= 2 || self.opening_abandoned;\n"
        "                if tree.is_some() && !harvesting {\n"
        "                    return None;\n"
        "                }\n"
        "                // A farm PICK is not a conversion commitment (pick -> plant anywhere -> chop).\n"
        "                self.regeneration_commitments.remove(&unit.id);\n"
        "                let farm_action = |command: String, target: Target| Candidate {\n"
        "                    command,\n"
        "                    score: 50_000.0,\n"
        "                    target,\n"
        "                };\n"
        "                let mut out = vec![MoisanBot::wait()];\n"
        "                if unit.cell != farm {\n"
        "                    out.push(farm_action(\n"
        "                        format!(\"MOVE {} {} {}\", unit.id, farm.0, farm.1),\n"
        "                        Target::Cell(farm),\n"
        "                    ));\n"
        "                    return Some(out);\n"
        "                }\n"
        "                // Before the second troll is paid for, one apple stays in the shack for its bill.\n"
        "                let apples_kept = if trolls >= 2 { 0 } else { 1 };\n"
        "                let apple = PlantKind::Apple.as_str();\n"
        "                let action = match tree {\n"
        "                    None if unit.carry[APPLE] > 0 => {\n"
        "                        Some((format!(\"PLANT {} {}\", unit.id, apple), Target::Cell(farm)))\n"
        "                    }\n"
        "                    None if unit.total_carried() > 0 => {\n"
        "                        Some((format!(\"DROP {}\", unit.id), Target::Bank(farm)))\n"
        "                    }\n"
        "                    None if !train_now\n"
        "                        && unit.free_capacity() > 0\n"
        "                        && view.inventories[0][APPLE] > apples_kept =>\n"
        "                    {\n"
        "                        Some((format!(\"PICK {} {}\", unit.id, apple), Target::Cell(farm)))\n"
        "                    }\n"
        "                    Some(_) if unit.total_carried() > 0 => {\n"
        "                        Some((format!(\"DROP {}\", unit.id), Target::Bank(farm)))\n"
        "                    }\n"
        "                    Some(plant) if plant.fruits > 0 && unit.free_capacity() > 0 => {\n"
        "                        Some((format!(\"HARVEST {}\", unit.id), Target::Tree(farm)))\n"
        "                    }\n"
        "                    _ => None,\n"
        "                };\n"
        "                if let Some((command, target)) = action {\n"
        "                    out.push(farm_action(command, target));\n"
        "                }\n"
        "                Some(out)\n"
        "            }\n"
    ),
)

INSERT_HOOK = dict(
    name="commands: the farm owns its troll's turn",
    where="before",
    anchor="                    by_id.insert(unit.id, candidates);\n",
    text=(
        "                    if let Some(farm) = self.farm_candidates(view, unit, train_now) {\n"
        "                        candidates = farm;\n"
        "                    }\n"
    ),
)

INSERTIONS = (INSERT_CHOP_SKIP, INSERT_HELPERS, INSERT_FARM_TURN, INSERT_HOOK)


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


def apply_insertions(text: str, what: str) -> str:
    for ins in INSERTIONS:
        count = text.count(ins["anchor"])
        require(count == 1, f"anchor for '{ins['name']}' occurs {count} times in {what}, expected 1")
        replacement = (ins["anchor"] + ins["text"]) if ins["where"] == "after" else (ins["text"] + ins["anchor"])
        text = text.replace(ins["anchor"], replacement, 1)
    return text


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

    arm_text = apply_insertions(arm_base, "the arm")
    readable_edited = apply_insertions(readable, "the readable champion")
    added_arm = len(arm_text.split("\n")) - len(arm_base.split("\n"))
    added_readable = len(readable_edited.split("\n")) - len(readable.split("\n"))
    expected_added = sum(ins["text"].count("\n") for ins in INSERTIONS)
    require(added_arm == added_readable == expected_added,
            f"lines added: arm {added_arm}, readable {added_readable}, expected {expected_added}")

    ba.compile_check(arm_text, "champion_apple_farm_v6_instrument")
    ba.compile_check(readable_edited, "champion_apple_farm_readable")
    ARM.write_text(arm_text)
    (HERE / (ARM.name + ".sha256")).write_text(f"{sha(arm_text)}  {ARM.name}\n")
    READABLE_EDITED.write_text(readable_edited)
    (HERE / (READABLE_EDITED.name + ".sha256")).write_text(
        f"{sha(readable_edited)}  {READABLE_EDITED.name}\n")

    compacted = crs.compact(arm_text)
    if not compacted.endswith("\n"):
        compacted += "\n"
    SUBMISSION.write_text(compacted)
    written = SUBMISSION.read_text()
    require(written == compacted, "the written submission differs from what was compacted")
    require(token_stream(written) == token_stream(arm_text),
            "round trip FAILED: the compacted file is not the arm's token stream")
    ba.compile_check(written, "champion_apple_farm_v6_instrument_min")
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
        tofile="readable/denial-off-champion.rs (apple farm)", n=3))
    DIFF.write_text("".join(diff_lines))
    removed = [l for l in diff_lines if l.startswith("-") and not l.startswith("---")]
    added = [l for l in diff_lines if l.startswith("+") and not l.startswith("+++")]
    require(len(removed) == 0 and len(added) == expected_added,
            f"the readable diff removes {len(removed)} and adds {len(added)}, expected 0/{expected_added}")

    report = {
        "schema": "troll-farm-readable-source-v2",
        "task": "apple-farm instrument (owner's one-variable experiment, 2026-08-27; design 1c/2yes)",
        "board_row": "ladder queue slot 3",
        "bot": "the champion of record plus the apple-farm rule",
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
        "edit": {"what": "four pure insertions: the apple-farm rule",
                 "insertions": [{"name": i["name"], "where": i["where"],
                                 "lines": i["text"].count("\n")} for i in INSERTIONS],
                 "lines_added": expected_added, "lines_removed": 0},
        "readable_diff": {"path": str(DIFF.relative_to(REPO)), "added": expected_added, "removed": 0},
        "base_arm_and_resident_same_token_stream": True,
        "canonical_token_stream_identical": True,
        "distinct_from": distinct,
        "compiles": True,
        "verdict": "CHAMPION_APPLE_FARM_V6_INSTRUMENT_ROUND_TRIP_EXACT",
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "build.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"  base        arm {ARM_BASE_SHA[:16]} == resident {RESIDENT_MIN_SHA[:16]} (token stream)")
    print(f"  arm         {sha(arm_text)[:16]}  {report['arm']['lines']} lines  (+{expected_added} / -0)")
    print(f"  compacted   {sha(written)[:16]}  {report['compacted']['bytes']} bytes"
          f"  -> {SUBMISSION.relative_to(REPO)}")
    print(f"  distinct    from {', '.join(label for label, _ in OTHERS)}")
    print(f"  diff        {DIFF.relative_to(REPO)}  (+{expected_added} / -0)")
    print(f"  round trip  EXACT -> {REPORT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BuildError as exc:
        print(f"BUILD REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
