#!/usr/bin/env python3
"""Build "the third troll": the champion of record with ONE change -- after the second troll is
trained, the bot wants a third troll of speed 2, carry 3, no harvest power, chop 3 (2/3/0/3;
price with two trolls 6 plums, 11 lemons, 2 apples, 11 iron), both trolls collect that bill
together, and the turn it can be paid the bot trains it; from then on it chops like the second.
The owner's next one-variable experiment of 2026-08-28 ("set as next goal bot with the third
troll"), born from the reconstruction of the four top players (every one of them grows to three
or four trolls, bought the turn they become affordable; our losses are against 3+-troll bots).
Card: `coordination/tasks/20260828-third-troll.md`.

THE RULE (owner, plain words; design round 1 accepted "ok" x4, 2026-08-28 05:0xZ).
  1. Funding continues until the bill is paid, but the third troll is wanted only while at least
     100 turns remain (turn <= 200 of 300); the second troll's own deadline logic is untouched.
  2. Funding reuses the behaviour the champion already has for the second troll's bill (fruit and
     iron trips scored above chopping while an item is missing; carried wood banked first), now
     for both trolls: the starter (the only troll that can harvest) fetches the missing fruits,
     the trained troll mines the missing iron. A troll whose part of the bill is complete plays
     normally (chops) instead of idling.
  3. The talents are fixed at 2/3/0/3.
  4. The roster cap in `MoisanBot::can_train` goes from two to three.
  5. (the owner's fifth point: "the best troll selection machinery is optimized for two trolls --
     check what else should be tuned") The audit of every two-troll assumption in the champion
     found one piece of machinery that changes behaviour at three trolls: `MoisanBot::select`
     chooses the trolls' commands JOINTLY for exactly two (the best compatible pair) and fell back
     to a greedy id-order pass for three or more. It now searches the joint choice for any number
     of trolls (choice for choice the same at two). Everything else is per-troll or per-player and
     safe at three (roles, target de-confliction, move conflicts, regeneration commitments, the
     endgame, the diagnostics line); the second-troll opening machinery (`desired_second`,
     `strongest_affordable`, `enforce_training_deadline`, `training_affordable`) keeps its own
     "two trolls" guards on purpose -- it describes the SECOND troll only and must never overwrite
     it with a build for the third.

WHAT THIS FILE IS. An INSTRUMENT for one hour on the ladder and a reading against the owner's
prediction; it promotes nothing and qualifies nothing. Identical in method to
`local_claude_1/the-floor/make_the_floor.py`: ONE base, the SAME edit applied to the diagnostics
arm and to the readable source, the same compactor, the same round trip.

THE BASE is the champion of record (owner ruling 2026-08-27 09:05Z): its diagnostics arm
`local_claude_1/denial-ablation/champion-denial-off-v6-instrument.rs` (sha256 32172393...) whose
compacted form IS the ladder resident `41202036` (`cgauto/submissions/
candidate-champion-denial-off-v6-instrument.rs`, sha256 0e92f8fa...), and its readable form
`readable/denial-off-champion.rs` (sha256 4ce3d1e8...). The v6 diagnostic line is untouched (it
already names every own troll from the view, so a third troll appears in it by itself).

THE EDIT, seven edits carried by nine replacements, each anchored on text that occurs exactly once
in BOTH files:

  1. `can_train`            -- the roster cap 2 -> 3;
  2. the third troll's spec -- `THIRD_TROLL_HORIZON` (100 turns) and `third_troll()` = 2/3/0/3,
                               placed beside `fallback_second_troll`;
  3. `commands`: desired    -- with two trolls the wanted build is the fixed third troll, and it
                               is wanted only while the horizon holds; `train_now` follows;
  4. `commands`: early      -- the funding mode also runs while the third troll is wanted;
  5. `commands`: per troll  -- in the funding mode a troll with nothing of its part of the bill
                               left to fetch plays normally (`main_candidates`);
  6. `early_candidates`     -- the bill split by ability (fruit to the harvester, iron to the
                               non-harvester; with one troll it fetches everything, as before),
                               and the old chop fallback kept for the one-troll case only;
  7. `select`               -- the joint choice for any number of trolls (`select_joint`).

Chain, each link checked and each failure fatal (as the floor's):
  a. the three base files match their recorded sha256; compact(arm) == the ladder resident;
  b. every anchor occurs exactly once in the arm and exactly once in the readable source;
  c. the edited arm and the edited readable source both compile (rustc --edition=2021 -O);
  d. compact(edited arm) -> `cgauto/submissions/candidate-third-troll-v6-instrument.rs`, sha256
     sidecar, round trip re-checked from the written file, and the file compiles;
  e. the written file is a NEW program on the ladder: its token stream differs from the bare
     champion, bot A, bot B, the banana farm, the apple farm, the floor and the resident;
  f. `readable/diffs/third-troll.diff` = unified diff of the readable champion against the
     readable champion with the same replacements -- the diff the owner reads; its +/- counts
     equal the replacements' own counts.

    python3 local_claude_1/third-troll/make_third_troll.py
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
    ("the floor", REPO / "cgauto" / "submissions" / "candidate-the-floor-v6-instrument.rs"),
    ("the resident (champion of record)", RESIDENT_MIN),
)

ARM = HERE / "champion-third-troll-v6-instrument.rs"
READABLE_EDITED = HERE / "third-troll-readable.rs"
SUBMISSION = REPO / "cgauto" / "submissions" / "candidate-third-troll-v6-instrument.rs"
REPORT = REPO / "readable" / "reports" / "candidate-third-troll-v6-instrument.round-trip.json"
DIFF = REPO / "readable" / "diffs" / "third-troll.diff"

# --------------------------------------------------------------------------------------------
# The seven replacements. `anchor` occurs exactly once in both files and is replaced by `text`.
# Indentation as it stands in both files (12 spaces = an `impl` item, 16 = a function body,
# 20 = inside a block within a function body).
# --------------------------------------------------------------------------------------------

REPL_CAP = dict(
    name="can_train: the roster cap 2 -> 3",
    anchor=(
        "                if n >= 2 || TOTAL_TURNS - view.turn <= 20 {\n"
    ),
    text=(
        "                if n >= 3 || TOTAL_TURNS - view.turn <= 20 {\n"
    ),
)

REPL_SPEC = dict(
    name="the third troll's spec: THIRD_TROLL_HORIZON and third_troll() = 2/3/0/3",
    anchor=(
        "            fn fallback_second_troll() -> Stats {\n"
    ),
    text=(
        "            // The third troll (owner, 2026-08-28): a fixed lumberjack -- speed 2, carry 3, no\n"
        "            // harvest power, chop 3 -- wanted once the second troll exists and while at least\n"
        "            // THIRD_TROLL_HORIZON turns remain; both trolls collect its bill together.\n"
        "            const THIRD_TROLL_HORIZON: i32 = 100;\n"
        "            fn third_troll() -> Stats {\n"
        "                Stats {\n"
        "                    movement_speed: 2,\n"
        "                    carry_capacity: 3,\n"
        "                    harvest_power: 0,\n"
        "                    chop_power: 3,\n"
        "                }\n"
        "            }\n"
        "            fn fallback_second_troll() -> Stats {\n"
    ),
)

REPL_DESIRED = dict(
    name="commands: with two trolls the wanted build is the third troll, while the horizon holds",
    anchor=(
        "                let desired = self\n"
        "                    .desired_second\n"
        "                    .map(|objective| objective.stats)\n"
        "                    .unwrap_or_else(Self::fallback_second_troll);\n"
        "                let train_now = !self.opening_abandoned && MoisanBot::can_train(view, desired);\n"
    ),
    text=(
        "                let own_trolls = view.units.iter().filter(|unit| unit.player == 0).count();\n"
        "                let third_wanted =\n"
        "                    own_trolls == 2 && TOTAL_TURNS - view.turn >= Self::THIRD_TROLL_HORIZON;\n"
        "                let desired = if own_trolls >= 2 {\n"
        "                    Self::third_troll()\n"
        "                } else {\n"
        "                    self.desired_second\n"
        "                        .map(|objective| objective.stats)\n"
        "                        .unwrap_or_else(Self::fallback_second_troll)\n"
        "                };\n"
        "                let train_now = !self.opening_abandoned\n"
        "                    && (own_trolls < 2 || third_wanted)\n"
        "                    && MoisanBot::can_train(view, desired);\n"
    ),
)

REPL_EARLY = dict(
    name="commands: the funding mode also runs while the third troll is wanted",
    anchor=(
        "                let early = !self.opening_abandoned && my_units.len() < 2 && !train_now;\n"
    ),
    text=(
        "                let early =\n"
        "                    !self.opening_abandoned && (my_units.len() < 2 || third_wanted) && !train_now;\n"
    ),
)

REPL_PER_TROLL = dict(
    name="commands: a funding troll with nothing left to fetch plays normally",
    anchor=(
        "                    } else if early {\n"
        "                        MoisanBot::early_candidates(view, unit, desired)\n"
        "                    } else {\n"
    ),
    text=(
        "                    } else if early {\n"
        "                        // With two trolls, a troll whose part of the bill is complete gets\n"
        "                        // only the WAIT back from the funding list: it plays normally.\n"
        "                        let funding = MoisanBot::early_candidates(view, unit, desired);\n"
        "                        if own_trolls < 2 || funding.len() > 1 {\n"
        "                            funding\n"
        "                        } else {\n"
        "                            Self::main_candidates(\n"
        "                                view,\n"
        "                                unit,\n"
        "                                self.type_to_cut,\n"
        "                                self.idle_regeneration,\n"
        "                                self.persistent_regeneration,\n"
        "                                self.opponent_eta_penalty,\n"
        "                            )\n"
        "                        }\n"
        "                    } else {\n"
    ),
)

REPL_SPLIT = dict(
    name="early_candidates: the bill split by ability; the chop fallback for one troll only",
    anchor=(
        "                let n = view.units.iter().filter(|unit| unit.player == 0).count() as i32;\n"
        "                let cost = training_cost(n, desired.tuple());\n"
        "                for item in [PLUM, LEMON, APPLE, IRON] {\n"
        "                    if item == APPLE && cost[item] <= view.inventories[0][item] {\n"
        "                        continue;\n"
        "                    }\n"
        "                    if item != APPLE && cost[item] <= view.inventories[0][item] {\n"
        "                        continue;\n"
        "                    }\n"
        "                    if item == IRON {\n"
    ),
    text=(
        "                let n = view.units.iter().filter(|unit| unit.player == 0).count() as i32;\n"
        "                let cost = training_cost(n, desired.tuple());\n"
        "                // With two trolls the bill is split by ability: the troll that can harvest\n"
        "                // fetches the missing fruits, the one that cannot mines the missing iron. With\n"
        "                // one troll (the second troll's bill) it fetches everything, as before.\n"
        "                let fetches_fruit = unit.stats.harvest_power > 0;\n"
        "                let fetches_iron = n < 2 || unit.stats.harvest_power <= 0;\n"
        "                for item in [PLUM, LEMON, APPLE, IRON] {\n"
        "                    if cost[item] <= view.inventories[0][item] {\n"
        "                        continue;\n"
        "                    }\n"
        "                    if (item == IRON && !fetches_iron) || (item != IRON && !fetches_fruit) {\n"
        "                        continue;\n"
        "                    }\n"
        "                    if item == IRON {\n"
    ),
)

REPL_CHOP_FALLBACK = dict(
    name="early_candidates: the chop fallback for the one-troll case only",
    anchor=(
        "                if out.len() == 1 {\n"
        "                    out.extend(Self::chop_candidates(view, unit, None));\n"
    ),
    text=(
        "                if out.len() == 1 && n < 2 {\n"
        "                    out.extend(Self::chop_candidates(view, unit, None));\n"
    ),
)

REPL_SELECT = dict(
    name="select: the joint choice for any number of trolls (select_joint)",
    anchor=(
        "                if ids.len() == 2 {\n"
        "                    let mut best_score = f64::NEG_INFINITY;\n"
        "                    let mut best_pair = None;\n"
        "                    for a in &candidates_by_id[&ids[0]] {\n"
        "                        for b in &candidates_by_id[&ids[1]] {\n"
        "                            if !Self::compatible(a.target, b.target)\n"
        "                                || !Self::stock_compatible(a, b, inventory)\n"
        "                            {\n"
        "                                continue;\n"
        "                            }\n"
        "                            let score = a.score + b.score;\n"
        "                            if score > best_score {\n"
        "                                best_score = score;\n"
        "                                best_pair = Some((a.command.clone(), b.command.clone()));\n"
        "                            }\n"
        "                        }\n"
        "                    }\n"
        "                    if let Some((a, b)) = best_pair {\n"
        "                        return vec![a, b];\n"
        "                    }\n"
        "                }\n"
    ),
    text=(
        "                // The joint choice for every own troll at once (the third troll, 2026-08-28):\n"
        "                // a depth-first walk over the trolls in id order through every combination of\n"
        "                // one candidate per troll whose targets do not collide and whose PICKs do not\n"
        "                // overdraw the shack; the best sum of scores wins, the first found on a tie.\n"
        "                // With two trolls this is the pair search it replaces, choice for choice.\n"
        "                let lists: Vec<&Vec<Candidate>> =\n"
        "                    ids.iter().map(|id| &candidates_by_id[id]).collect();\n"
        "                let combinations = lists\n"
        "                    .iter()\n"
        "                    .fold(1usize, |n, list| n.saturating_mul(list.len()));\n"
        "                if combinations <= Self::JOINT_SELECT_LIMIT {\n"
        "                    let mut best_score = f64::NEG_INFINITY;\n"
        "                    let mut best_set = None;\n"
        "                    let mut chosen = Vec::new();\n"
        "                    Self::select_joint(\n"
        "                        &lists,\n"
        "                        inventory,\n"
        "                        &mut chosen,\n"
        "                        0.0,\n"
        "                        &mut best_score,\n"
        "                        &mut best_set,\n"
        "                    );\n"
        "                    if let Some(commands) = best_set {\n"
        "                        return commands;\n"
        "                    }\n"
        "                }\n"
    ),
)

REPL_SELECT_JOINT = dict(
    name="select_joint: the depth-first joint search, placed after select",
    anchor=(
        "            fn move_command(command: &str) -> Option<(i32, Cell)> {\n"
    ),
    text=(
        "            // Above this many combinations the greedy id-order pass below `select_joint`'s\n"
        "            // call is used instead (never reached with the champion's list sizes; a bound on\n"
        "            // the turn's time, not a behaviour).\n"
        "            const JOINT_SELECT_LIMIT: usize = 400_000;\n"
        "            fn select_joint<'a>(\n"
        "                lists: &[&'a Vec<Candidate>],\n"
        "                inventory: &[i32; 6],\n"
        "                chosen: &mut Vec<&'a Candidate>,\n"
        "                sum: f64,\n"
        "                best_score: &mut f64,\n"
        "                best_set: &mut Option<Vec<String>>,\n"
        "            ) {\n"
        "                let depth = chosen.len();\n"
        "                if depth == lists.len() {\n"
        "                    if sum > *best_score {\n"
        "                        *best_score = sum;\n"
        "                        *best_set = Some(chosen.iter().map(|c| c.command.clone()).collect());\n"
        "                    }\n"
        "                    return;\n"
        "                }\n"
        "                for candidate in lists[depth] {\n"
        "                    let targets_fit = chosen\n"
        "                        .iter()\n"
        "                        .all(|earlier| Self::compatible(earlier.target, candidate.target));\n"
        "                    let stock_fits = match Self::picked_item(&candidate.command) {\n"
        "                        Some(item) => {\n"
        "                            let taken = chosen\n"
        "                                .iter()\n"
        "                                .filter(|earlier| Self::picked_item(&earlier.command) == Some(item))\n"
        "                                .count() as i32;\n"
        "                            taken == 0 || inventory[item] >= taken + 1\n"
        "                        }\n"
        "                        None => true,\n"
        "                    };\n"
        "                    if !targets_fit || !stock_fits {\n"
        "                        continue;\n"
        "                    }\n"
        "                    chosen.push(candidate);\n"
        "                    Self::select_joint(\n"
        "                        lists,\n"
        "                        inventory,\n"
        "                        chosen,\n"
        "                        sum + candidate.score,\n"
        "                        best_score,\n"
        "                        best_set,\n"
        "                    );\n"
        "                    chosen.pop();\n"
        "                }\n"
        "            }\n"
        "            fn move_command(command: &str) -> Option<(i32, Cell)> {\n"
    ),
)

REPLACEMENTS = (REPL_CAP, REPL_SPEC, REPL_DESIRED, REPL_EARLY, REPL_PER_TROLL, REPL_SPLIT,
                REPL_CHOP_FALLBACK, REPL_SELECT, REPL_SELECT_JOINT)


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

    ba.compile_check(arm_text, "champion_third_troll_v6_instrument")
    ba.compile_check(readable_edited, "champion_third_troll_readable")
    ARM.write_text(arm_text)
    (HERE / (ARM.name + ".sha256")).write_text(f"{sha(arm_text)}  {ARM.name}\n")
    READABLE_EDITED.write_text(readable_edited)
    (HERE / (READABLE_EDITED.name + ".sha256")).write_text(
        f"{sha(readable_edited)}  {READABLE_EDITED.name}\n")
    # Printed only, never written to a tracked file (machine-dependent; see the floor's note).
    fmt = rustfmt_status(READABLE_EDITED)

    compacted = crs.compact(arm_text)
    if not compacted.endswith("\n"):
        compacted += "\n"
    SUBMISSION.write_text(compacted)
    written = SUBMISSION.read_text()
    require(written == compacted, "the written submission differs from what was compacted")
    require(token_stream(written) == token_stream(arm_text),
            "round trip FAILED: the compacted file is not the arm's token stream")
    ba.compile_check(written, "champion_third_troll_v6_instrument_min")
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
        tofile="readable/denial-off-champion.rs (the third troll)", n=3))
    DIFF.write_text("".join(diff_lines))
    removed = [l for l in diff_lines if l.startswith("-") and not l.startswith("---")]
    added = [l for l in diff_lines if l.startswith("+") and not l.startswith("+++")]
    require(len(removed) == expected_removed and len(added) == expected_added,
            f"the readable diff removes {len(removed)} and adds {len(added)}, "
            f"expected {expected_removed}/{expected_added}")

    report = {
        "schema": "troll-farm-readable-source-v2",
        "task": "the third troll (owner's one-variable experiment, 2026-08-28: "
                "'set as next goal bot with the third troll')",
        "board_row": "Track 3, row 3-1",
        "bot": "the champion of record; after the second troll both trolls fund a 2/3/0/3 "
               "lumberjack, trained the turn it is affordable (while >= 100 turns remain); "
               "select chooses jointly for any number of trolls",
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
        "edit": {"what": "nine replacements: the third troll",
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
        "verdict": "CHAMPION_THIRD_TROLL_V6_INSTRUMENT_ROUND_TRIP_EXACT",
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
