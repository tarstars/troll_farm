#!/usr/bin/env python3
"""Gate G-P for NARRATE **v3** — the instrument plays swap R-1's game, and its telemetry keeps
the distinction v2 lost.

Ruled by codex_1's construction ruling `20260823T113503Z`: v3 adds, per live own unit, the
unit-local best candidate taken from the candidate map BEFORE joint pairing consumes it, while
v2's chosen target keeps its name and meaning. The `available` field has THREE distinct states —
`ABSENT` (no/empty candidate vector), `NONE` (an explicit WAIT was locally best), and a concrete
target — and none of the three may serialize or decode like another.

A passing v2 buys v3 nothing, so every check is re-run here in full against the v3 instrument.

WHAT THIS GATE CANNOT PROVE, unchanged from v2 and repeated rather than footnoted: this harness
does not react to the command stream's length, ordering or content. The instrument emits a `MSG`
token on EVERY turn where the base emits one on turn 1 only. If the live referee reacts to that,
G-P passes and the ladder position is still not swap R-1's. That is the platform condition, it is
not mine to run, and a green result here does not discharge it.
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
INSTRUMENT = HERE / "instrument-swap-r1-narrate-v3.rs"
OUT = HERE / "results" / "gp3-parity-2026-08-23.json"

VERSION = "v3"
LINE_BUDGET = 2000

MSG_TOKEN = re.compile(r"^\s*MSG(\s|$)", re.IGNORECASE)

TARGET_RE = re.compile(
    r"^(NONE|SHACK|BANK\((-?\d+),(-?\d+)\)|CELL\((-?\d+),(-?\d+)\)|TREE\((-?\d+),(-?\d+)\))$")
# chosen is always a Target; available is a Target OR the distinct token ABSENT.
UNIT_RE = re.compile(r"^u(\d+)=([^/]+)/([^/]+)$")


class GateError(Exception):
    """Anything that would make a result mean something other than it says."""


def strip_msg(line: str) -> str:
    kept = [frag for frag in line.split(";") if not MSG_TOKEN.match(frag)]
    return ";".join(kept)


def msg_fragments(line: str) -> list[str]:
    return [frag for frag in line.split(";") if MSG_TOKEN.match(frag)]


def decode(payload: str):
    """Round-trip the wire syntax back to (turn, {id: (chosen, available)}). Raises off-grammar.

    `available` decodes to the string 'ABSENT' or to a Target spelling; the decoder never folds
    ABSENT into NONE, because that fold is exactly the v2 defect v3 exists to repair.
    """
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
    if len(tokens) < 2 or tokens[1] != VERSION:
        # A decoder that does not recognise the version REFUSES the game rather than guessing.
        raise GateError(f"unsupported NARRATE version {tokens[1] if len(tokens) > 1 else None!r}, "
                        f"this decoder reads {VERSION} only")
    if len(tokens) < 3 or not tokens[2].startswith("t="):
        raise GateError(f"no t= field: {payload!r}")
    turn = int(tokens[2][2:])
    units = {}
    order = []
    for tok in tokens[3:]:
        m = UNIT_RE.match(tok)
        if not m:
            raise GateError(f"off-grammar unit token {tok!r} in {payload!r}")
        uid, chosen, available = int(m.group(1)), m.group(2), m.group(3)
        if not TARGET_RE.match(chosen):
            raise GateError(f"off-grammar chosen target {chosen!r} in {payload!r}")
        if available != "ABSENT" and not TARGET_RE.match(available):
            raise GateError(f"off-grammar available target {available!r} in {payload!r}")
        if uid in units:
            raise GateError(f"unit {uid} appears twice in {payload!r}")
        units[uid] = (chosen, available)
        order.append(uid)
    return turn, units, order, bool(banner)


def check_telemetry(sid, tr, command_lines, census=None):
    """Grammar round-trip, one message per turn placed first, complete sorted roster, turn align,
    the three-state invariant, the line budget, and production tie parity on lone-unit turns."""
    errors = []
    for index, line in enumerate(command_lines, 1):
        frags = line.split(";")
        msgs = msg_fragments(line)
        if len(msgs) != 1:
            errors.append(f"turn {index}: {len(msgs)} MSG tokens, expected exactly 1")
            continue
        if not MSG_TOKEN.match(frags[0]):
            errors.append(f"turn {index}: the MSG token is not first in the command list")
        payload = msgs[0].strip()
        if len(payload) > LINE_BUDGET:
            errors.append(f"turn {index}: MSG payload {len(payload)} chars exceeds {LINE_BUDGET}")
        try:
            turn, units, order, banner = decode(payload)
        except GateError as exc:
            errors.append(f"turn {index}: {exc}")
            continue
        if census is not None:
            census["payload_max_chars"] = max(census["payload_max_chars"], len(payload))
            for uid, (chosen, available) in units.items():
                census["rows"] += 1
                census["available_states"][
                    "ABSENT" if available == "ABSENT"
                    else "NONE" if available == "NONE" else "CONCRETE"] += 1
                if chosen != available:
                    census["chosen_ne_available"] += 1
                    if chosen == "NONE" and available not in ("NONE", "ABSENT"):
                        census["discarded_want"] += 1
        if banner != (index == 1):
            errors.append(f"turn {index}: banner present={banner}, expected {index == 1}")
        if turn != index:
            errors.append(f"turn {index}: telemetry says t={turn} — turn misalignment")
        if order != sorted(order):
            errors.append(f"turn {index}: ids not ascending: {order}")
        # Production tie parity, on the wire: when exactly one own unit is live, select_recording
        # takes its ids.len()==1 branch, which IS the lone-unit max_by that `available` reuses.
        # So chosen and available must agree on that turn, ties included.
        if len(order) == 1:
            uid = order[0]
            chosen, available = units[uid]
            if census is not None:
                census["lone_unit_turns"] += 1
            if available != "ABSENT" and chosen != available:
                errors.append(f"turn {index}: lone-unit tie parity broken — "
                              f"chosen {chosen} != available {available}")
        if index <= tr.T:
            live = sorted(u.id for u in tr.state(index).own_units())
            if order != live:
                errors.append(f"turn {index}: roster {order} != live own units {live}")
    return errors


def new_census():
    return {"rows": 0, "chosen_ne_available": 0, "discarded_want": 0, "lone_unit_turns": 0,
            "payload_max_chars": 0,
            "available_states": {"ABSENT": 0, "NONE": 0, "CONCRETE": 0}}


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
    ap.add_argument("--instrument", default=str(INSTRUMENT))
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    instrument = Path(args.instrument)
    cfg = json.loads(fh.CONFIG.read_text())
    sits = fh.load_situations(args.only.split(",") if args.only else None)
    rows, telemetry_errors = [], []
    census = new_census()
    with tempfile.TemporaryDirectory(prefix="gp3-parity-") as wd:
        wd = Path(wd)
        base_bin, inst_bin = wd / "base.bin", wd / "inst.bin"
        sh.compile_text(BASE.read_text(), base_bin, crate="gp3_base")
        sh.compile_text(instrument.read_text(), inst_bin, crate="gp3_instrument")
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
            errs = check_telemetry(sid, tr_i, inst_lines, census)
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
        "gate": "G-P (NARRATE v3)",
        "task": "20260823-narrate-real-game-telemetry",
        "ruling": "codex_1 20260823T113503Z construction ruling; charter local_claude_1 "
                  "20260823T113300Z",
        "base": str(BASE.relative_to(REPO)),
        "instrument": str(instrument.relative_to(REPO)),
        "fixtures": len(rows),
        "byte_identical_without_msg": parity,
        "telemetry_error_count": len(telemetry_errors),
        "telemetry_errors": telemetry_errors[:40],
        "verdict": "PASS" if ok else "FAIL",
        "census": census,
        "census_note": "counts over the fixture corpus only. `discarded_want` is the class v2 "
                       "could not represent: chosen NONE with a concrete available. A zero here "
                       "means the fixtures never exercised it, NOT that the instrument cannot "
                       "record it.",
        "not_proven_here": "platform non-interference: this harness does not react to command "
                           "count, ordering or line length; the instrument emits a MSG token "
                           "every turn where the base emits one on turn 1 only",
        "rows": rows,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"\n  G-P v3: {parity}/{len(rows)} byte-identical without MSG, "
          f"{len(telemetry_errors)} telemetry errors -> {report['verdict']}")
    print(f"  census: rows {census['rows']}, chosen!=available {census['chosen_ne_available']}, "
          f"discarded-want {census['discarded_want']}, "
          f"lone-unit turns {census['lone_unit_turns']}, "
          f"longest payload {census['payload_max_chars']} chars")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
