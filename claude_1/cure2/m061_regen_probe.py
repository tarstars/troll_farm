#!/usr/bin/env python3
"""Run the two print-only regeneration probes on both `m061` seats and diff the clause inputs.

Gate G-A: each probe's stdout command stream must be byte-identical to its own (unprobed) arm's
on the same spec, or the probe is not print-only and nothing below means anything.

    python3 claude_1/cure2/m061_regen_probe.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in ("claude_1/t1", "claude_1/pipeline", "claude_1/banana-restoration-r2",
           "claude_1/narrate5"):
    sys.path.insert(0, str(REPO / _p))

import fuzz_panel as fp               # noqa: E402
import regression_tests as rt         # noqa: E402
import semantic_harness as sh         # noqa: E402

PANEL_CFG = HERE / "cure2-instrument-config.json"
OUT = HERE / "results" / "m061-regen-probe.json"
ARMS = {"instrument": (HERE / "arm-instrument.rs", HERE / "arm-instrument-regenprobe.rs"),
        "ruleoff": (HERE / "arm-ruleoff.rs", HERE / "arm-ruleoff-regenprobe.rs")}
RE_ROW = re.compile(r"^(REGEN|REGENBRANCH|TRAINNOW|CANDS) t=(\d+) (.*)$")


class GateError(Exception):
    pass


def run_capturing(binary, ref, turns):
    with tempfile.TemporaryFile(mode="w+") as err:
        fd = sys.stderr.fileno()
        saved = os.dup(fd)
        os.dup2(err.fileno(), fd)
        try:
            transcript, commands = rt.run_binary_custom(binary, ref, turns)
        finally:
            os.dup2(saved, fd)
            os.close(saved)
        err.seek(0)
        return transcript, commands, err.read()


def main() -> int:
    cfg = fp.load_config(PANEL_CFG)
    result = {"task": "20260825-dance-cure-candidate-2-swap", "gates": {}, "games": {}}
    with tempfile.TemporaryDirectory(prefix="cure2-regen-") as wd:
        wd = Path(wd)
        bins = {}
        for arm, (plain, probe) in ARMS.items():
            bins[arm] = (wd / f"{arm}.bin", wd / f"{arm}-probe.bin")
            sh.compile_text(plain.read_text(), bins[arm][0], crate=f"cure2_regen_{arm}")
            sh.compile_text(probe.read_text(), bins[arm][1], crate=f"cure2_regen_{arm}_probe")
        parent = wd / "parent.bin"
        parent_src = (PANEL_CFG.parent / cfg["parent"]["source"]).resolve()
        sh.compile_text(parent_src.read_text(), parent, crate="cure2_regen_parent")
        jobs = {f"{j['spec']['map_id']}:{j['spec']['seat']}": j
                for j in fp.build_jobs(cfg, bins["instrument"][0], parent)}
        for key in ("m061:0", "m061:1"):
            job = jobs[key]
            spec, turns = job["spec"], job["turns"]
            result["games"][key] = {}
            for arm in ARMS:
                _, plain_cmds = rt.run_binary_custom(bins[arm][0], fp.make_referee(spec), turns)
                _, probe_cmds, err = run_capturing(bins[arm][1], fp.make_referee(spec), turns)
                if plain_cmds != probe_cmds:
                    raise GateError(f"{key} {arm}: probe is NOT print-only")
                rows = []
                for line in err.splitlines():
                    m = RE_ROW.match(line)
                    if m and 96 <= int(m.group(2)) <= 104:
                        rows.append(line)
                result["games"][key][arm] = rows
                print(f"  {key} {arm}: parity OK, {len(rows)} probe rows in t90..112", flush=True)
        result["gates"]["G-A print-only"] = "PASS on both arms, both seats"
    OUT.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print("wrote", OUT.relative_to(REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
