#!/usr/bin/env python3
"""Build the wood-aware three-troll optimized-start candidate and its control.

The candidate keeps stage 2A only for the cheap, real-field-proven second troll. Once two
workers stand, a bounded contested-resource assignment search chooses a complete third-troll
specification only when its forecast beats the wood those workers could bank instead. Resource
trips and ordinary chop trips then compete on one points-per-turn scale. The plan is rechecked
from the live board and abandoned to the champion when it ceases to pay.

The control is byte-identical except that third-troll planning is disabled. It isolates the
optimizer from the turn-2-second-troll change.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
STAGE2A = REPO / "claude_1" / "opening-solver" / "stage2a"
sys.path.insert(0, str(STAGE2A))
import make_opening_dispatcher as s2a  # noqa: E402

mk = s2a.mk
OPTIMIZER = (HERE / "optimizer.rs.in").read_text()
SOURCE_DISPATCHER = STAGE2A / "dispatcher.rs.in"
RESULTS = HERE / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

ARM = HERE / "champion-three-troll-optimized-v6-instrument.rs"
READABLE = HERE / "three-troll-optimized-readable.rs"
SUBMISSION = HERE / "candidate-three-troll-optimized-v6-instrument.rs"
REPORT = RESULTS / "build.json"
DIFF = HERE / "three-troll-optimized.diff"

CONTROL_ARM = HERE / "champion-turn2-second-control-v6-instrument.rs"
CONTROL_READABLE = HERE / "turn2-second-control-readable.rs"
CONTROL_SUBMISSION = HERE / "candidate-turn2-second-control-v6-instrument.rs"
CONTROL_REPORT = RESULTS / "control-build.json"
CONTROL_DIFF = HERE / "turn2-second-control.diff"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise mk.BuildError(message)


def replace_once(text: str, anchor: str, replacement: str, name: str) -> str:
    count = text.count(anchor)
    require(count == 1, f"{name}: anchor occurs {count} times, expected 1")
    return text.replace(anchor, replacement, 1)


def patched_dispatcher() -> str:
    text = SOURCE_DISPATCHER.read_text()

    opening_anchor = (
        "            // One turn of the opening: the TRAIN (if the pre-turn stock clears the bill) and\n"
        "            // one command per own troll; None once the opening is over (the champion plays).\n"
        "            fn opening_dispatch(&mut self, view: &GameState) -> Option<(Option<Stats>, BTreeMap<i32, Candidate>)> {\n"
    )
    text = replace_once(
        text,
        opening_anchor,
        OPTIMIZER + "\n" + opening_anchor,
        "insert contested dynamic program",
    )

    target_anchor = (
        "                let target = if n == 1 {\n"
        "                    Some(Self::opening_second_target(view))\n"
        "                } else {\n"
        "                    Self::third_troll_for(view)\n"
        "                };\n"
        "                let Some(target) = target else {\n"
        "                    self.opening_done = true;\n"
        "                    return None;\n"
        "                };\n"
    )
    target_replacement = (
        "                let target = if n == 1 {\n"
        "                    Some(Self::opening_second_target(view))\n"
        "                } else {\n"
        "                    if !Self::OPENING_ENABLE_THIRD {\n"
        "                        self.opening_done = true;\n"
        "                        return None;\n"
        "                    }\n"
        "                    if self.opening_third.is_none() {\n"
        "                        let Some((stats, deadline, shadows, net)) =\n"
        "                            Self::opening_optimize_third(view, &own)\n"
        "                        else {\n"
        "                            self.opening_done = true;\n"
        "                            return None;\n"
        "                        };\n"
        "                        self.opening_third = Some(stats);\n"
        "                        self.opening_third_deadline = deadline;\n"
        "                        self.opening_third_shadow = shadows;\n"
        "                        self.opening_third_net = net;\n"
        "                        self.opening_third_recheck = view.turn + Self::OPENING_THIRD_RECHECK;\n"
        "                    } else if view.turn >= self.opening_third_recheck {\n"
        "                        let stats = self.opening_third.unwrap();\n"
        "                        let Some((finish, shadows, net)) =\n"
        "                            Self::opening_score_third(view, &own, stats)\n"
        "                        else {\n"
        "                            self.opening_done = true;\n"
        "                            return None;\n"
        "                        };\n"
        "                        self.opening_third_deadline =\n"
        "                            (finish + 8).min(Self::OPENING_THIRD_LATEST);\n"
        "                        self.opening_third_shadow = shadows;\n"
        "                        self.opening_third_net = net;\n"
        "                        self.opening_third_recheck = view.turn + Self::OPENING_THIRD_RECHECK;\n"
        "                    }\n"
        "                    if view.turn > self.opening_third_deadline {\n"
        "                        self.opening_done = true;\n"
        "                        return None;\n"
        "                    }\n"
        "                    self.opening_third\n"
        "                };\n"
        "                let Some(target) = target else {\n"
        "                    self.opening_done = true;\n"
        "                    return None;\n"
        "                };\n"
    )
    text = replace_once(text, target_anchor, target_replacement, "replace third-troll target")

    text = replace_once(
        text,
        "                let sw = Self::OPENING_SURPLUS_WEIGHT;\n",
        "                let sw = if n == 2 { 1.0 } else { Self::OPENING_SURPLUS_WEIGHT };\n",
        "value surplus at face value while considering the third troll",
    )

    task_anchor = "                        let mut tasks: Vec<Task> = Vec::new();\n"
    task_replacement = (
        "                        if n == 2 {\n"
        "                            for item in pay.iter().copied() {\n"
        "                                if need[item] > 0 {\n"
        "                                    w[item] = self.opening_third_shadow[item].max(1.0);\n"
        "                                }\n"
        "                            }\n"
        "                        }\n"
        + task_anchor
    )
    text = replace_once(text, task_anchor, task_replacement, "apply dynamic-programming shadow prices")

    bank_anchor = (
        "                            let mut needed_carried = 0.0;\n"
        "                            let mut plain = 0;\n"
        "                            if needed_any {\n"
        "                                for item in 0..6 {\n"
        "                                    let k = unit.carry[item].min(need[item]);\n"
        "                                    needed_carried += k as f64 * w[item];\n"
        "                                    plain += k;\n"
        "                                }\n"
        "                            }\n"
        "                            let value = (needed_carried + (carrying - plain) as f64 * sw) / (d_home + 1) as f64\n"
        "                                + if free == 0 { 2.0 } else { 0.0 };\n"
    )
    bank_replacement = (
        "                            let mut carried_value = 0.0;\n"
        "                            for item in 0..6 {\n"
        "                                let needed = if needed_any {\n"
        "                                    unit.carry[item].min(need[item])\n"
        "                                } else {\n"
        "                                    0\n"
        "                                };\n"
        "                                carried_value += needed as f64 * w[item];\n"
        "                                let surplus = unit.carry[item] - needed;\n"
        "                                carried_value += surplus as f64\n"
        "                                    * if n == 2 {\n"
        "                                        if item == 5 { 4.0 } else { 1.0 }\n"
        "                                    } else {\n"
        "                                        sw\n"
        "                                    };\n"
        "                            }\n"
        "                            let value = carried_value / (d_home + 1) as f64\n"
        "                                + if free == 0 { 2.0 } else { 0.0 };\n"
    )
    text = replace_once(text, bank_anchor, bank_replacement, "price carried wood correctly")

    seed_comment = (
        "                            // A seed: only from stock the second troll's bill does not need,\n"
        "                            // never on a turn the TRAIN fires (R3), early in the game, with\n"
        "                            // empty hands; next to water when the detour is short (R4).\n"
    )
    chop_block = (
        "                            // Stage 2A suppressed the wood race until the third troll. Here\n"
        "                            // ordinary 4-point wood trips compete directly with the dynamic\n"
        "                            // program's shadow-priced training resources. A needed fruit tree\n"
        "                            // is discounted, not made immortal: if its wood is still the better\n"
        "                            // use, the live recheck may abandon the third-troll plan.\n"
        "                            if n == 2 {\n"
        "                                for candidate in MoisanBot::chop_candidates(view, unit, None) {\n"
        "                                    let target = match candidate.target {\n"
        "                                        Target::Tree(cell) | Target::Cell(cell) | Target::Bank(cell) => cell,\n"
        "                                        _ => continue,\n"
        "                                    };\n"
        "                                    let protected = view\n"
        "                                        .plant_at(target)\n"
        "                                        .map(|index| need[view.plants[index].kind.item_index()] > 0)\n"
        "                                        .unwrap_or(false);\n"
        "                                    tasks.push(Task {\n"
        "                                        value: candidate.score * 0.004\n"
        "                                            * if protected { 0.35 } else { 1.0 },\n"
        "                                        command: candidate.command,\n"
        "                                        target,\n"
        "                                        claim: None,\n"
        "                                        claim_cell: None,\n"
        "                                        seed: None,\n"
        "                                        needed: false,\n"
        "                                    });\n"
        "                                }\n"
        "                            }\n"
        + seed_comment
    )
    text = replace_once(text, seed_comment, chop_block, "restore the wood race")

    seed_condition = (
        "                            if seeds_now < Self::OPENING_SEEDS.len()\n"
        "                                && view.turn <= Self::OPENING_SEED_TURN_LIMIT\n"
    )
    seed_replacement = (
        "                            if seeds_now < Self::OPENING_SEEDS.len()\n"
        "                                && n <= 1\n"
        "                                && view.turn <= Self::OPENING_SEED_TURN_LIMIT\n"
    )
    text = replace_once(text, seed_condition, seed_replacement, "do not farm while funding the third troll")

    filter_anchor = (
        "                        if tasks.iter().any(|t| t.needed && t.claim.is_some()) {\n"
        "                            tasks.retain(|t| t.needed);\n"
        "                        }\n"
    )
    filter_replacement = (
        "                        if n <= 1 && tasks.iter().any(|t| t.needed && t.claim.is_some()) {\n"
        "                            tasks.retain(|t| t.needed);\n"
        "                        }\n"
    )
    text = replace_once(text, filter_anchor, filter_replacement, "let wood compete after the second troll")
    return text


def move_sidecar(path: Path) -> None:
    stray = mk.HERE / (path.name + ".sha256")
    if stray.exists():
        stray.replace(HERE / stray.name)


def build_control() -> dict:
    marker = "            const OPENING_ENABLE_THIRD: bool = true;\n"
    replacement = "            const OPENING_ENABLE_THIRD: bool = false;\n"
    arm = ARM.read_text()
    readable = READABLE.read_text()
    require(arm.count(marker) == 1 and readable.count(marker) == 1, "control marker is not unique")
    control_arm = arm.replace(marker, replacement, 1)
    control_readable = readable.replace(marker, replacement, 1)
    mk.ba.compile_check(control_arm, "turn2_second_control_v6_instrument")
    mk.ba.compile_check(control_readable, "turn2_second_control_readable")
    CONTROL_ARM.write_text(control_arm)
    CONTROL_READABLE.write_text(control_readable)
    (HERE / (CONTROL_ARM.name + ".sha256")).write_text(
        f"{mk.sha(control_arm)}  {CONTROL_ARM.name}\n"
    )
    (HERE / (CONTROL_READABLE.name + ".sha256")).write_text(
        f"{mk.sha(control_readable)}  {CONTROL_READABLE.name}\n"
    )
    compacted = mk.crs.compact(control_arm)
    if not compacted.endswith("\n"):
        compacted += "\n"
    CONTROL_SUBMISSION.write_text(compacted)
    require(mk.token_stream(compacted) == mk.token_stream(control_arm), "control round trip failed")
    mk.ba.compile_check(compacted, "turn2_second_control_v6_instrument_min")
    (HERE / (CONTROL_SUBMISSION.name + ".sha256")).write_text(
        f"{mk.sha(compacted)}  {CONTROL_SUBMISSION.name}\n"
    )
    base = mk.READABLE.read_text()
    import difflib

    CONTROL_DIFF.write_text(
        "".join(
            difflib.unified_diff(
                base.splitlines(keepends=True),
                control_readable.splitlines(keepends=True),
                fromfile="readable/denial-off-champion.rs",
                tofile="readable/denial-off-champion.rs (turn-2 second control)",
                n=3,
            )
        )
    )
    report = {
        "arm": {"path": str(CONTROL_ARM.relative_to(REPO)), "sha256": mk.sha(control_arm)},
        "readable": {
            "path": str(CONTROL_READABLE.relative_to(REPO)),
            "sha256": mk.sha(control_readable),
        },
        "submission": {
            "path": str(CONTROL_SUBMISSION.relative_to(REPO)),
            "sha256": mk.sha(compacted),
            "bytes": len(compacted.encode()),
            "utf16_units": len(compacted.encode("utf-16-le")) // 2,
        },
        "diff": str(CONTROL_DIFF.relative_to(REPO)),
        "round_trip_exact": True,
        "third_optimizer_enabled": False,
    }
    CONTROL_REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> int:
    dispatcher = patched_dispatcher()

    fields = dict(s2a.REPL_FIELDS)
    fields["text"] += (
        "            // Contested, wood-aware third-troll plan. None means not admitted yet.\n"
        "            opening_third: Option<Stats>,\n"
        "            opening_third_deadline: i32,\n"
        "            opening_third_shadow: [f64; 6],\n"
        "            opening_third_net: f64,\n"
        "            opening_third_recheck: i32,\n"
    )
    init = dict(s2a.REPL_INIT)
    init["text"] += (
        "                    opening_third: None,\n"
        "                    opening_third_deadline: 0,\n"
        "                    opening_third_shadow: [1.0; 6],\n"
        "                    opening_third_net: f64::NEG_INFINITY,\n"
        "                    opening_third_recheck: 0,\n"
    )
    dispatcher_replacement = dict(s2a.REPL_DISPATCHER)
    dispatcher_replacement["text"] = dispatcher + "            fn fallback_second_troll() -> Stats {\n"

    mk.REPLACEMENTS = (
        fields,
        init,
        dispatcher_replacement,
        s2a.REPL_TRAIN,
        s2a.REPL_FORCE,
        mk.REPL_SELECT,
        mk.REPL_SELECT_JOINT,
    )
    mk.STACKED = False
    mk.ARM = ARM
    mk.READABLE_EDITED = READABLE
    mk.SUBMISSION = SUBMISSION
    mk.REPORT = REPORT
    mk.DIFF = DIFF
    mk.OTHERS_LIST = list(mk.OTHERS)
    for label, path in (
        ("stage 2A opening dispatcher", REPO / "cgauto/submissions/candidate-opening-dispatcher-v6-instrument.rs"),
        ("three heroes", REPO / "cgauto/submissions/candidate-three-heroes-v6-instrument.rs"),
        ("orchard 6", REPO / "cgauto/submissions/candidate-orchard6-v6-instrument.rs"),
    ):
        if path.exists():
            mk.OTHERS_LIST.append((label, path))

    rc = mk.main()
    if rc != 0:
        return rc
    move_sidecar(ARM)
    move_sidecar(READABLE)
    stray = mk.HERE / "results" / "build-optimized.json"
    if stray.exists():
        stray.unlink()

    control = build_control()
    report = json.loads(REPORT.read_text())
    submission_text = SUBMISSION.read_text()
    report["task"] = "three-troll bot with a contested, wood-aware optimized start"
    report["board_row"] = "owner direct build 20260903-three-troll-optimized-start"
    report["bot"] = (
        "champion + turn-2 second troll; a contested-resource assignment dynamic program admits "
        "only wood-positive third-troll plans by turn 110; funding and chopping compete; live "
        "recheck abandons a plan that stops paying; joint selection after the third troll"
    )
    report["compacted"]["utf16_units"] = len(submission_text.encode("utf-16-le")) // 2
    report["control"] = control
    report["risk_budget"] = {
        "latest_third_turn": 110,
        "minimum_estimated_net_points": 8.0,
        "contested_first_fruit": "removed when an opponent harvester can arrive no later",
        "fallback": "champion immediately when no robust plan remains",
    }
    report["verdict"] = "THREE_TROLL_OPTIMIZED_START_BUILD_ROUND_TRIP_EXACT"
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    require(report["compacted"]["utf16_units"] < 100_000, "candidate exceeds platform source limit")
    require(control["submission"]["utf16_units"] < 100_000, "control exceeds platform source limit")
    print(json.dumps({
        "candidate_bytes": len(submission_text.encode()),
        "candidate_utf16_units": report["compacted"]["utf16_units"],
        "control_bytes": control["submission"]["bytes"],
        "control_utf16_units": control["submission"]["utf16_units"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except mk.BuildError as exc:
        print(f"BUILD REFUSED: {exc}", file=sys.stderr)
        raise SystemExit(2)
