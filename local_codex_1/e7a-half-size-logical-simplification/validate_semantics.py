#!/usr/bin/env python3
"""Black-box semantic fixtures for the readable half-size E7a candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile


REPO = Path(__file__).resolve().parents[2]
CANDIDATE = REPO / "local_codex_1/e7a-half-size-logical-simplification/integrated-half-r32.rs"
CANDIDATE_SHA256 = "abb202db71040f8784b7d02cc114ced9f71d82e82d3c8a1cc975d87d3feeb4da"
SACRED = REPO / "rust/src/bin/yamo_orchard_live.rs"
SACRED_SHA256 = "fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f"
FOCUS_ANCHOR = "self.type_to_cut = Some(MoisanBot::focus_type(view));"

VALID_ARITIES = {
    "WAIT": 1,
    "MOVE": 4,
    "CHOP": 2,
    "HARVEST": 2,
    "DROP": 2,
    "PLANT": 3,
    "PICK": 3,
    "MINE": 2,
    "TRAIN": 5,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_text(source: str, output: Path, crate: str) -> None:
    completed = subprocess.run(
        [
            "rustc",
            "--edition=2021",
            "-O",
            "-Awarnings",
            "--crate-name",
            crate,
            "-",
            "-o",
            str(output),
        ],
        cwd=REPO,
        input=source,
        text=True,
        capture_output=True,
        timeout=120,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr[:4000])


def unit(
    unit_id: int,
    player: int,
    x: int,
    y: int,
    *,
    movement: int = 1,
    capacity: int = 2,
    harvest: int = 0,
    chop: int = 1,
    carry: tuple[int, int, int, int, int, int] = (0, 0, 0, 0, 0, 0),
) -> tuple[int, ...]:
    return (
        unit_id,
        player,
        x,
        y,
        movement,
        capacity,
        harvest,
        chop,
        *carry,
    )


def turn_text(
    *,
    inventory: tuple[int, int, int, int, int, int] = (0, 0, 0, 0, 0, 0),
    opponent_inventory: tuple[int, int, int, int, int, int] = (0, 0, 0, 0, 0, 0),
    plants: tuple[tuple[str, int, int, int, int, int, int], ...] = (),
    units: tuple[tuple[int, ...], ...] = (),
) -> str:
    lines = [
        " ".join(map(str, inventory)),
        " ".join(map(str, opponent_inventory)),
        str(len(plants)),
    ]
    lines.extend(" ".join(map(str, plant)) for plant in plants)
    lines.append(str(len(units)))
    lines.extend(" ".join(map(str, row)) for row in units)
    return "\n".join(lines) + "\n"


def transcript(rows: tuple[str, ...], turns: list[str]) -> str:
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("map rows have inconsistent widths")
    return f"{width} {len(rows)}\n" + "\n".join(rows) + "\n" + "".join(turns)


def commands(line: str) -> list[str]:
    return [
        command.strip()
        for command in re.split(r"[;\n]", line)
        if command.strip() and not command.strip().upper().startswith("MSG ")
    ]


def validate_command(command: str) -> None:
    parts = command.split()
    verb = parts[0].upper() if parts else ""
    if verb not in VALID_ARITIES or len(parts) != VALID_ARITIES[verb]:
        raise AssertionError(f"malformed command: {command!r}")
    integer_fields = {
        "MOVE": (1, 2, 3),
        "CHOP": (1,),
        "HARVEST": (1,),
        "DROP": (1,),
        "PLANT": (1,),
        "PICK": (1,),
        "MINE": (1,),
        "TRAIN": (1, 2, 3, 4),
    }.get(verb, ())
    for index in integer_fields:
        int(parts[index])


def run(binary: Path, payload: str) -> tuple[list[list[str]], str]:
    completed = subprocess.run(
        [str(binary)],
        cwd=REPO,
        input=payload,
        text=True,
        capture_output=True,
        timeout=10,
    )
    if completed.returncode:
        raise RuntimeError(
            f"candidate exited {completed.returncode}: {completed.stderr[:1000]}"
        )
    lines = completed.stdout.splitlines()
    parsed = [commands(line) for line in lines]
    for row in parsed:
        for command in row:
            validate_command(command)
    return parsed, completed.stderr


def focus_fixtures(probe: Path) -> list[dict]:
    rows = ("0..............1",)
    cases = [
        ("near_tie_below", 3, 10, "PLUM"),
        ("near_tie_boundary", 3, 11, "PLUM"),
        ("lemon_clear", 3, 12, "LEMON"),
        ("parent_plum", 12, 3, "PLUM"),
    ]
    output = []
    for name, lemon_x, plum_x, expected in cases:
        state = turn_text(
            plants=(
                ("LEMON", lemon_x, 0, 4, 12, 1, 0),
                ("PLUM", plum_x, 0, 4, 12, 1, 0),
            ),
            units=(unit(0, 0, 1, 0),),
        )
        _commands, stderr = run(probe, transcript(rows, [state]))
        matches = re.findall(r"^@FOCUS (LEMON|PLUM)$", stderr, re.MULTILINE)
        if matches != [expected]:
            raise AssertionError(f"{name}: focus={matches}, expected={expected}")
        output.append({"fixture": name, "expected": expected, "observed": matches[0]})
    return output


def training_bill_fixture(binary: Path) -> dict:
    rows = ("0..........1",)
    plants = (
        ("PLUM", 2, 0, 4, 12, 1, 0),
        ("LEMON", 5, 0, 4, 12, 1, 0),
    )
    first = turn_text(
        inventory=(2, 2, 2, 2, 2, 0),
        plants=plants,
        units=(unit(0, 0, 1, 0),),
    )
    second = turn_text(
        inventory=(10, 10, 10, 10, 10, 0),
        plants=plants,
        units=(unit(0, 0, 1, 0),),
    )
    rows_out, stderr = run(binary, transcript(rows, [first, second]))
    if stderr:
        raise AssertionError(f"training fixture stderr: {stderr!r}")
    if any(command.startswith(("TRAIN ", "CHOP ")) for command in rows_out[0]):
        raise AssertionError(f"turn one displaced bill collection: {rows_out[0]}")
    if not any(command.startswith("MOVE ") for command in rows_out[0]):
        raise AssertionError(f"turn one did not collect a bill resource: {rows_out[0]}")
    training = [command for command in rows_out[1] if command.startswith("TRAIN ")]
    if training != ["TRAIN 2 1 0 2"]:
        raise AssertionError(f"unexpected trained profile: {training}")
    return {"turn_one": rows_out[0], "turn_two": rows_out[1], "trained": training[0]}


def training_fallback_fixture(binary: Path) -> dict:
    rows = ("0....1",)
    state = turn_text(
        inventory=(2, 2, 2, 2, 2, 0),
        units=(unit(0, 0, 1, 0),),
    )
    rows_out, stderr = run(binary, transcript(rows, [state] * 35))
    if stderr:
        raise AssertionError(f"fallback fixture stderr: {stderr!r}")
    before = [command for row in rows_out[:34] for command in row if command.startswith("TRAIN ")]
    on_deadline = [command for command in rows_out[34] if command.startswith("TRAIN ")]
    if before or on_deadline != ["TRAIN 1 1 0 1"]:
        raise AssertionError(f"fallback training mismatch: before={before}, t35={on_deadline}")
    return {"turn": 35, "command": on_deadline[0]}


def banking_commitment_fixture(binary: Path) -> dict:
    rows = ("0......1",)
    states = [
        turn_text(units=(unit(0, 0, 5, 0, carry=(0, 0, 0, 0, 0, 1)),)),
        turn_text(units=(unit(0, 0, 3, 0, carry=(0, 0, 0, 0, 0, 1)),)),
        turn_text(units=(unit(0, 0, 1, 0, carry=(0, 0, 0, 0, 0, 1)),)),
    ]
    rows_out, stderr = run(binary, transcript(rows, states))
    if stderr:
        raise AssertionError(f"bank fixture stderr: {stderr!r}")
    expected = [["MOVE 0 4 0"], ["MOVE 0 2 0"], ["DROP 0"]]
    if rows_out != expected:
        raise AssertionError(f"wood commitment is not monotone: {rows_out}")
    return {"commands": rows_out, "door": [1, 0]}


def same_target_fixture(binary: Path) -> dict:
    rows = ("0.......1",)
    state = turn_text(
        plants=(("LEMON", 5, 0, 4, 12, 0, 4),),
        units=(unit(0, 0, 2, 0), unit(1, 0, 4, 0)),
    )
    rows_out, stderr = run(binary, transcript(rows, [state]))
    if stderr:
        raise AssertionError(f"same-target fixture stderr: {stderr!r}")
    active = [command for command in rows_out[0] if command != "WAIT"]
    if len(active) != 1:
        raise AssertionError(f"same tree assigned to more than one worker: {rows_out[0]}")
    return {"commands": rows_out[0], "active_workers": len(active)}


def landing_conflict_fixture(binary: Path) -> dict:
    rows = ("0.##1", "...##", "#.###")
    state = turn_text(
        plants=(
            ("LEMON", 2, 1, 4, 12, 0, 4),
            ("PLUM", 1, 2, 4, 12, 0, 4),
        ),
        units=(unit(0, 0, 0, 1), unit(1, 0, 1, 0)),
    )
    rows_out, stderr = run(binary, transcript(rows, [state]))
    if stderr:
        raise AssertionError(f"landing fixture stderr: {stderr!r}")
    moves = [command for command in rows_out[0] if command.startswith("MOVE ")]
    landings = [tuple(map(int, command.split()[2:4])) for command in moves]
    if len(landings) != len(set(landings)) or landings.count((1, 1)) > 1:
        raise AssertionError(f"duplicate landing survived guard: {rows_out[0]}")
    if len(moves) != 1 or "WAIT" not in rows_out[0]:
        raise AssertionError(f"expected one reserved landing and one wait: {rows_out[0]}")
    return {"commands": rows_out[0], "landings": landings}


def deadline_case(binary: Path, turn: int) -> list[str]:
    rows = ("0....1",)
    empty = turn_text(units=(unit(0, 0, 1, 0),))
    fruit = turn_text(
        inventory=(0, 0, 0, 1, 0, 0),
        units=(unit(0, 0, 1, 0),),
    )
    states = [empty] * (turn - 1) + [fruit]
    rows_out, stderr = run(binary, transcript(rows, states))
    if stderr:
        raise AssertionError(f"deadline fixture stderr: {stderr!r}")
    return rows_out[-1]


def endgame_deadline_fixture(binary: Path) -> dict:
    at_boundary = deadline_case(binary, 295)
    too_late = deadline_case(binary, 296)
    if not any(command == "PICK 0 BANANA" for command in at_boundary):
        raise AssertionError(f"feasible boundary conversion was skipped: {at_boundary}")
    if any(command.startswith("PICK ") for command in too_late):
        raise AssertionError(f"infeasible late conversion was started: {too_late}")
    return {"turn_295": at_boundary, "turn_296": too_late}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if sha256(CANDIDATE) != CANDIDATE_SHA256:
        raise RuntimeError("candidate hash mismatch")
    if sha256(SACRED) != SACRED_SHA256:
        raise RuntimeError("sacred source hash mismatch")
    source = CANDIDATE.read_text()
    if source.count(FOCUS_ANCHOR) != 1:
        raise RuntimeError("focus probe anchor is not unique")
    probe_source = source.replace(
        FOCUS_ANCHOR,
        "let focus=MoisanBot::focus_type(view);"
        'eprintln!("@FOCUS {}",focus.as_str());'
        "self.type_to_cut=Some(focus);",
        1,
    )
    with tempfile.TemporaryDirectory(prefix="e7a-half-size-semantics-") as directory:
        temp = Path(directory)
        binary = temp / "candidate"
        probe = temp / "focus-probe"
        compile_text(source, binary, "e7a_half_size_semantic_candidate")
        compile_text(probe_source, probe, "e7a_half_size_focus_probe")
        fixtures = {
            "focus": focus_fixtures(probe),
            "training_bill": training_bill_fixture(binary),
            "training_fallback": training_fallback_fixture(binary),
            "banking_commitment": banking_commitment_fixture(binary),
            "same_target": same_target_fixture(binary),
            "landing_conflict": landing_conflict_fixture(binary),
            "endgame_deadline": endgame_deadline_fixture(binary),
        }
    result = {
        "schema": "troll-farm-e7a-half-size-semantic-fixtures/1",
        "candidate": {
            "path": str(CANDIDATE.relative_to(REPO)),
            "bytes": CANDIDATE.stat().st_size,
            "sha256": CANDIDATE_SHA256,
        },
        "sacred_sha256": SACRED_SHA256,
        "verdict": "SEMANTIC_FIXTURES_PASS",
        "fixture_count": sum(
            len(value) if isinstance(value, list) else 1 for value in fixtures.values()
        ),
        "malformed_commands": 0,
        "unexpected_stderr_bytes": 0,
        "fixtures": fixtures,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": result["verdict"], "fixtures": result["fixture_count"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
