#!/usr/bin/env python3
"""Read the generated gates and write one reproducible verdict page."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = HERE / "results"
ALLOWED = {
    "1 1 0 1",
    "1 2 0 1",
    "2 2 0 1",
    "2 2 0 2",
    "2 3 0 1",
    "2 3 0 2",
    "2 3 0 3",
}


def load(name: str):
    return json.loads((R / name).read_text())


def fixture_ok(report: dict) -> tuple[bool, list[str]]:
    problems: list[str] = []
    n = report["fixtures"]
    for key in ("plays_to_the_end", "deterministic_on_rerun", "compacted_binary_identical"):
        if report.get(key) != n:
            problems.append(f"{key}={report.get(key)} expected {n}")
    if report.get("telemetry_error_count"):
        problems.append(f"telemetry errors={report['telemetry_error_count']}")
    if report.get("arm_more_than_three_trolls"):
        problems.append(f"more than three trolls={report['arm_more_than_three_trolls']}")
    for row in report.get("rows", []):
        trains = row.get("train_arm", [])
        if len(trains) >= 2 and trains[1].get("spec") not in ALLOWED:
            problems.append(f"{row['id']}: unexpected third spec {trains[1].get('spec')}")
    return not problems, problems


def quantile(values: list[int], numerator: int, denominator: int):
    if not values:
        return None
    values = sorted(values)
    index = round((len(values) - 1) * numerator / denominator)
    return values[index]


def main() -> int:
    build = load("build.json")
    control_build = load("control-build.json")
    fixture = load("fixtures.json")
    control_fixture = load("control-fixtures.json")
    smoke = load("smoke.json")
    control_smoke = load("control-smoke.json")
    timing = load("turn-time.json")
    duel = load("candidate-vs-control.json")
    field = load("field.json")

    candidate_fixture_ok, candidate_fixture_problems = fixture_ok(fixture)
    control_fixture_ok, control_fixture_problems = fixture_ok(control_fixture)
    candidate_smoke_ok = smoke.get("all_mechanics_ok") == smoke.get("maps_played")
    control_smoke_ok = control_smoke.get("all_mechanics_ok") == control_smoke.get("maps_played")
    third_turns = [int(v) for v in smoke.get("third_troll_turns", [])]
    third_by_110 = [v for v in third_turns if v <= 110]
    specs = Counter(
        row["arm"]["third_troll"]["spec"]
        for row in smoke.get("rows", [])
        if row["arm"].get("third_troll")
    )
    warm_p99 = timing.get("warm_p99_ms")
    timing_ok = bool(timing.get("inside_platform_budget")) and warm_p99 is not None and warm_p99 < 40.0
    size = int(build["compacted"]["utf16_units"])
    control_size = int(control_build["submission"]["utf16_units"])
    size_ok = size < 100_000 and control_size < 100_000
    faults_ok = all(
        run.get(key, 0) == 0
        for run in (duel, load("candidate-vs-champion.json"), load("control-vs-champion.json"),
                    load("candidate-vs-orchard6.json"), load("control-vs-orchard6.json"))
        for key in ("illegal_commands_total", "referee_errors_total", "timeouts_total")
    )

    win = field["field"]["win_diff"]
    field_dead = win["mean"] < -0.05 and win["interval_95"][1] < -0.05
    mechanics_ok = (
        candidate_fixture_ok
        and control_fixture_ok
        and candidate_smoke_ok
        and control_smoke_ok
        and faults_ok
        and size_ok
    )
    viable = mechanics_ok and timing_ok and bool(third_by_110) and not field_dead
    verdict = "PASS_TO_REVIEW" if viable else "DEAD_AS_BOT"

    summary = {
        "verdict": verdict,
        "gates": {
            "candidate_fixture_ok": candidate_fixture_ok,
            "candidate_fixture_problems": candidate_fixture_problems,
            "control_fixture_ok": control_fixture_ok,
            "control_fixture_problems": control_fixture_problems,
            "candidate_smoke_ok": candidate_smoke_ok,
            "control_smoke_ok": control_smoke_ok,
            "third_trained_by_turn_110": len(third_by_110),
            "timing_ok_warm_p99_under_40ms": timing_ok,
            "source_size_ok": size_ok,
            "panel_faults_zero": faults_ok,
            "paired_dead_condition_triggered": field_dead,
        },
        "candidate": {
            "utf16_units": size,
            "third_troll_games": smoke.get("games_with_third_troll"),
            "maps": smoke.get("maps_played"),
            "third_turn_p25": quantile(third_turns, 1, 4),
            "third_turn_median": smoke.get("third_troll_turn_median"),
            "third_turn_p75": quantile(third_turns, 3, 4),
            "third_specs": dict(sorted(specs.items())),
            "fallback_or_no_third_games": smoke.get("maps_played", 0) - smoke.get("games_with_third_troll", 0),
            "smoke_score_minus_resident": smoke.get("own_score_sum_arm_minus_resident"),
            "warm_p99_ms": warm_p99,
            "first_turn_max_ms": timing.get("first_turn_max_ms"),
        },
        "control": {
            "utf16_units": control_size,
            "third_troll_games": control_smoke.get("games_with_third_troll"),
            "smoke_score_minus_resident": control_smoke.get("own_score_sum_arm_minus_resident"),
        },
        "paired_candidate_minus_control": {
            "opponents": field["field"]["opponents"],
            "win_diff": win,
            "margin_diff": field["field"]["margin_diff"],
        },
        "direct_candidate_vs_control": {
            "games": duel.get("games"),
            "candidate_wins": duel.get("policy_wins"),
            "reading": duel.get("reading"),
        },
        "scientific_boundary": (
            "The optimizer is a deterministic contested-resource assignment model and live policy gate. "
            "Its value estimate is not a proof of turn-300 game value; the paired panel is the value check."
        ),
    }
    (R / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    (R / "verdict.txt").write_text(verdict + "\n")

    lo, hi = win["interval_95"]
    lines = [
        "# Three-troll optimized start: executed result",
        "",
        f"**Verdict: `{verdict}`**",
        "",
        "## What was compared",
        "",
        "The candidate and control share the same turn-2-second-troll opening. Only the candidate "
        "enables the wood-aware third-troll optimizer. The paired result therefore measures that "
        "optimizer rather than the already-known early-second-troll change.",
        "",
        "## Validity and runtime",
        "",
        f"- candidate fixture bed: {'PASS' if candidate_fixture_ok else 'FAIL'}; control: "
        f"{'PASS' if control_fixture_ok else 'FAIL'}",
        f"- candidate smoke mechanics: {smoke.get('all_mechanics_ok')}/{smoke.get('maps_played')}; "
        f"control: {control_smoke.get('all_mechanics_ok')}/{control_smoke.get('maps_played')}",
        f"- source size: candidate {size:,} UTF-16 units; control {control_size:,}; limit 100,000",
        f"- timing: first-turn max {timing.get('first_turn_max_ms')} ms; warm p99 {warm_p99} ms",
        f"- panel execution faults zero: {faults_ok}",
        "",
        "## Third troll",
        "",
        f"- trained in {smoke.get('games_with_third_troll')}/{smoke.get('maps_played')} smoke games",
        f"- trained by turn 110 in {len(third_by_110)} games",
        f"- p25 / median / p75 turn: {summary['candidate']['third_turn_p25']} / "
        f"{summary['candidate']['third_turn_median']} / {summary['candidate']['third_turn_p75']}",
        f"- selected tuples: {dict(sorted(specs.items()))}",
        f"- fallback or no admitted/completed third-troll plan: "
        f"{summary['candidate']['fallback_or_no_third_games']} games",
        "",
        "## Candidate minus control on identical maps and opponents",
        "",
        f"- paired win difference: {win['mean']:+.4f} [{lo:+.4f}, {hi:+.4f}]",
        f"- paired margin difference: {field['field']['margin_diff']['mean']:+.2f} "
        f"{field['field']['margin_diff']['interval_95']}",
        f"- pre-registered death condition (below -0.05 with interval clear): {field_dead}",
        f"- direct duel: {duel.get('policy_wins')} candidate wins in {duel.get('games')} games; "
        f"paired reading {duel.get('reading')}",
        "",
        "## Boundary",
        "",
        summary["scientific_boundary"],
        "No ladder or platform action was taken.",
    ]
    (HERE / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
