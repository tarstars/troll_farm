#!/usr/bin/env python3
"""Gate G-P — the instrument plays swap R-1's game, and its telemetry is well-formed.

Ruled by codex_1's construction r3 (`20260823T070405Z`): 34/34 per-fixture byte identity after
removing the COMPLETE `MSG` token, plus grammar round-trip, complete-roster, sorted-unique-id and
turn-alignment checks.

Both arms are re-run through the same `fuzz_panel` referee the fixture harness uses, from the same
frozen provenance, so the only difference between the two streams is the instrument's edit.

WHAT THIS GATE CANNOT PROVE, and it is written here rather than in a footnote: this harness does
not react to the command stream's length, ordering or content. The instrument emits a `MSG` token
on EVERY turn where the base emits one on turn 1 only. If the live referee reacts to that, G-P
passes and the ladder position is still not swap R-1's. That is the platform condition, it is not
mine to run, and a green result here does not discharge it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "t1"))
sys.path.insert(0, str(REPO / "claude_1" / "pipeline"))
sys.path.insert(0, str(REPO / "claude_1" / "banana-restoration-r2"))

import fixture_harness as fh        # noqa: E402
import fuzz_panel as fp             # noqa: E402
import regression_tests as rt       # noqa: E402
import semantic_harness as sh       # noqa: E402

BASE = REPO / "cgauto" / "submissions" / "candidate-swap-r1.rs"
INSTRUMENT = HERE / "instrument-swap-r1-narrate-v2.rs"
OUT = HERE / "results" / "gp-parity-2026-08-23.json"

# The COMPLETE MSG token, per the ruling: the whole `;`-delimited fragment, not a prefix of it.
MSG_TOKEN = re.compile(r"^\s*MSG(\s|$)", re.IGNORECASE)

TARGET_RE = re.compile(
    r"^(NONE|SHACK|BANK\((-?\d+),(-?\d+)\)|CELL\((-?\d+),(-?\d+)\)|TREE\((-?\d+),(-?\d+)\))$")
UNIT_RE = re.compile(r"^u(\d+)=(.+)$")


class GateError(Exception):
    """Anything that would make a result mean something other than it says."""


def strip_msg(line: str) -> str:
    kept = [frag for frag in line.split(";") if not MSG_TOKEN.match(frag)]
    return ";".join(kept)


def msg_fragments(line: str) -> list[str]:
    return [frag for frag in line.split(";") if MSG_TOKEN.match(frag)]


def decode(payload: str):
    """Round-trip the wire syntax back to (turn, {id: target}). Raises on anything off-grammar."""
    tokens = payload.split()
    if not tokens or tokens[0] != "MSG":
        raise GateError(f"fragment is not an MSG token: {payload!r}")
    tokens = tokens[1:]
    if "NARRATE" not in tokens:
        raise GateError(f"no NARRATE token: {payload!r}")
    start = tokens.index("NARRATE")
    banner = tokens[:start]
    if len(banner) > 1:
        raise GateError(f"more than one banner token before NARRATE: {banner!r}")
    tokens = tokens[start:]
    if len(tokens) < 2 or tokens[1] != "v2":
        raise GateError(f"version is not v2: {payload!r}")
    if len(tokens) < 3 or not tokens[2].startswith("t="):
        raise GateError(f"no t= field: {payload!r}")
    turn = int(tokens[2][2:])
    units = {}
    order = []
    for tok in tokens[3:]:
        m = UNIT_RE.match(tok)
        if not m:
            raise GateError(f"off-grammar unit token {tok!r} in {payload!r}")
        uid = int(m.group(1))
        if not TARGET_RE.match(m.group(2)):
            raise GateError(f"off-grammar target {m.group(2)!r} in {payload!r}")
        if uid in units:
            raise GateError(f"unit {uid} appears twice in {payload!r}")
        units[uid] = m.group(2)
        order.append(uid)
    return turn, units, order, bool(banner)


def check_telemetry(sid, tr, command_lines):
    """Grammar round-trip, one message per turn placed first, complete sorted roster, turn align."""
    errors = []
    for index, line in enumerate(command_lines, 1):
        frags = line.split(";")
        msgs = msg_fragments(line)
        if len(msgs) != 1:
            errors.append(f"turn {index}: {len(msgs)} MSG tokens, expected exactly 1")
            continue
        if not MSG_TOKEN.match(frags[0]):
            errors.append(f"turn {index}: the MSG token is not first in the command list")
        try:
            turn, units, order, banner = decode(msgs[0].strip())
        except GateError as exc:
            errors.append(f"turn {index}: {exc}")
            continue
        if banner != (index == 1):
            errors.append(f"turn {index}: banner present={banner}, expected {index == 1}")
        if turn != index:
            errors.append(f"turn {index}: telemetry says t={turn} — turn misalignment")
        if order != sorted(order):
            errors.append(f"turn {index}: ids not ascending: {order}")
        if index <= tr.T:
            live = sorted(u.id for u in tr.state(index).own_units())
            if order != live:
                errors.append(f"turn {index}: roster {order} != live own units {live}")
    return errors


def run_arm(sit, binary, cfg):
    spec = fh.spec_for(sit, cfg)
    ref = fp.make_referee(spec)
    transcript, commands = rt.run_binary_custom(Path(binary), ref, int(cfg["turns"]))
    import trace_detectors as td
    tr = td.build_trace(transcript, commands)
    return tr, commands.rstrip("\n").split("\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--only")
    args = ap.parse_args()

    cfg = json.loads(fh.CONFIG.read_text())
    sits = fh.load_situations(args.only.split(",") if args.only else None)
    rows, telemetry_errors = [], []
    with tempfile.TemporaryDirectory(prefix="gp-parity-") as wd:
        wd = Path(wd)
        base_bin, inst_bin = wd / "base.bin", wd / "inst.bin"
        sh.compile_text(BASE.read_text(), base_bin, crate="gp_base")
        sh.compile_text(INSTRUMENT.read_text(), inst_bin, crate="gp_instrument")
        for sit in sits:
            sid = sit["id"]
            _, base_lines = run_arm(sit, base_bin, cfg)
            tr_i, inst_lines = run_arm(sit, inst_bin, cfg)
            stripped = [strip_msg(line) for line in inst_lines]
            base_stripped = [strip_msg(line) for line in base_lines]
            identical = stripped == base_stripped
            first_diff = None
            if not identical:
                for i, (a, b) in enumerate(zip(base_stripped, stripped), 1):
                    if a != b:
                        first_diff = {"turn": i, "base": a, "instrument": b}
                        break
                if first_diff is None:
                    first_diff = {"turn": None,
                                  "base_turns": len(base_stripped),
                                  "instrument_turns": len(stripped)}
            errs = check_telemetry(sid, tr_i, inst_lines)
            telemetry_errors.extend(f"{sid}: {e}" for e in errs)
            rows.append({
                "id": sid, "turns": len(inst_lines),
                "byte_identical_without_msg": identical,
                "first_divergence": first_diff,
                "telemetry_errors": len(errs),
                "base_msg_tokens": sum(len(msg_fragments(l)) for l in base_lines),
                "instrument_msg_tokens": sum(len(msg_fragments(l)) for l in inst_lines),
            })
            mark = "PARITY" if identical and not errs else "FAILED"
            print(f"  {mark} {sid:<10} turns {len(inst_lines):>3}  "
                  f"telemetry errors {len(errs)}")

    parity = sum(1 for r in rows if r["byte_identical_without_msg"])
    ok = parity == len(rows) and not telemetry_errors
    report = {
        "gate": "G-P",
        "task": "20260823-narrate-real-game-telemetry",
        "ruling": "codex_1 20260823T070405Z construction r3",
        "base": str(BASE.relative_to(REPO)),
        "instrument": str(INSTRUMENT.relative_to(REPO)),
        "fixtures": len(rows),
        "byte_identical_without_msg": parity,
        "telemetry_error_count": len(telemetry_errors),
        "telemetry_errors": telemetry_errors[:40],
        "verdict": "PASS" if ok else "FAIL",
        "not_proven_here": "platform non-interference: this harness does not react to command "
                           "count, ordering or line length; the instrument emits a MSG token "
                           "every turn where the base emits one on turn 1 only",
        "rows": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"\n  G-P: {parity}/{len(rows)} byte-identical without MSG, "
          f"{len(telemetry_errors)} telemetry errors -> {report['verdict']}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
