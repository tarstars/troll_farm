#!/usr/bin/env python3
"""Is the new joint `select` the old pair search at two trolls, choice for choice?

Builds the champion's diagnostics arm with ONLY the two `select` replacements of
`make_third_troll.py` (no third troll, no funding change) and plays it against the unchanged arm
on the 34 frozen situations and on the smoke's 24 real maps (both opponent profiles). The command
streams with the diagnostics `MSG` stripped must be identical on every game; the referee's end
state too. A single difference means the joint search is not the pair search, and the third-troll
build is not the one-variable experiment it claims to be.

    python3 local_claude_1/third-troll/select_equivalence.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
for _p in ("claude_1/t1", "claude_1/pipeline", "claude_1/banana-restoration-r2",
           "claude_1/narrate6", "claude_1/cure3"):
    sys.path.insert(0, str(REPO / _p))

import make_third_troll as mk       # noqa: E402
import containment as ct            # noqa: E402
import fixture_harness as fh        # noqa: E402
import semantic_harness as sh       # noqa: E402
import narrate6 as n6               # noqa: E402
import regression_tests as rt       # noqa: E402
import smoke                        # noqa: E402


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def main() -> int:
    base = mk.ARM_BASE.read_text()
    assert sha(base) == mk.ARM_BASE_SHA
    only_select = base
    for rep in (mk.REPL_SELECT, mk.REPL_SELECT_JOINT):
        assert only_select.count(rep["anchor"]) == 1
        only_select = only_select.replace(rep["anchor"], rep["text"], 1)
    cfg = json.loads(fh.CONFIG.read_text())
    sits = fh.load_situations(None)
    plan = []
    with open(HERE / "smoke-maps-seed0.jsonl") as fp:
        for line in fp:
            item = json.loads(line)
            plan.append((item["rec"], item["draw"], item["profile"]))
    rows, same = [], 0
    with tempfile.TemporaryDirectory(prefix="select-eq-") as wd:
        wd = Path(wd)
        base_bin, sel_bin = wd / "base.bin", wd / "sel.bin"
        sh.compile_text(base, base_bin, crate="select_eq_base")
        sh.compile_text(only_select, sel_bin, crate="select_eq_select_only")
        for sit in sits:
            a_lines, a_state, _ = ct.run_arm(sit, base_bin, cfg)
            b_lines, b_state, _ = ct.run_arm(sit, sel_bin, cfg)
            identical = [n6.strip_msg(l) for l in a_lines] == [n6.strip_msg(l) for l in b_lines] \
                and a_state == b_state
            same += identical
            rows.append({"game": sit["id"], "identical": identical, "turns": len(a_lines)})
            print(f"  {'SAME' if identical else 'DIFF'} fixture {sit['id']} ({len(a_lines)} turns)")
        for rec, draw, profile in plan:
            streams, states = [], []
            for binary in (base_bin, sel_bin):
                ref = smoke.make_referee(rec, draw, profile)
                _, commands = rt.run_binary_custom(binary, ref, 300)
                lines = commands.rstrip("\n").split("\n")
                streams.append([n6.strip_msg(l) for l in lines])
                states.append((list(ref.inv), list(ref.opp_inv),
                               sorted((uid, u["cell"], u["speed"], u["cap"], u["harvest"], u["chop"])
                                      for uid, u in ref.units.items())))
            identical = streams[0] == streams[1] and states[0] == states[1]
            same += identical
            rows.append({"game": rec["map_hash"], "profile": profile, "identical": identical,
                         "turns": len(streams[0])})
            print(f"  {'SAME' if identical else 'DIFF'} map {rec['map_hash']} {profile}")
    n = len(rows)
    report = {
        "what": "the champion's arm with only the joint-select replacements vs the unchanged arm",
        "base_arm_sha256": sha(base), "select_only_arm_sha256": sha(only_select),
        "games": n, "identical": same, "status": "PASS" if same == n else "FAIL", "rows": rows,
    }
    out = HERE / "results" / "select-equivalence.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"\n  {report['status']}  identical play on {same}/{n} games "
          f"(34 situations + {len(plan)} real maps)  -> {out}")
    return 0 if same == n else 1


if __name__ == "__main__":
    sys.exit(main())
