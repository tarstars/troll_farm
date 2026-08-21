#!/usr/bin/env python3
r"""Which generator branch the unrouted turns actually took — measured, not inferred.

Task `20260821-osc032-033-no-goal-instrument`, G-1 revision.

codex_1's G-1 refusal turned on 20 employed OSC-033 turns that the five Phase-3 anchors could
not name. Reading `commands()` gives an obvious candidate — it selects its generator from five
branches and the anchors tapped only `main_candidates` and `endgame_candidates`, leaving
`early_candidates` untapped — but "the structural explanation agrees with the count" is
exactly how I have published a right finding for a wrong reason before. So this measures it.

It rebuilds the PRE-REVISION five-anchor probe, finds every `PS3FINAL` row with no matching
`PS3ROUTE`, and reports the branch flags `PS3FINAL` already carries (`early`, `endgame`,
`committed`, `train_now`) for each. If the untapped-`early` explanation is right, every
unrouted turn is `early=true` with the other three false and NO other combination appears; a
second combination would mean more than one hole and the two-anchor repair would be
incomplete.

Observed 2026-08-21, on both fixtures: 34 unrouted turns each, all on turns 1-34, all
`early=true endgame=false committed=false train_now=false`, no other combination. OSC-033's
34 split 20 employed / 14 idle, matching the census exactly.

Restores every artifact it touches and verifies the restoration by digest.

Run:  python3 claude_1/nogoal/unrouted_cause.py
"""
import collections
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in ("claude_1/t1", "claude_1/hstarve1", "claude_1/banana-restoration-r2",
          "claude_1/pipeline", "claude_1/picker2"):
    sys.path.insert(0, str(REPO / p))
import coverage as C            # noqa: E402
import fixture_harness as H     # noqa: E402
import route_census as RC       # noqa: E402

BUILDER = REPO / "claude_1/picker2/make_route_probe.py"
MANIFEST = HERE / "route-probe-manifest-2026-08-21.json"
LIVE = "EXTRA_EDITS = {\"door1-champion\": EARLY_EDITS}"
STUB = "EXTRA_EDITS = {}  # PRE-REVISION five-anchor probe, for the cause diagnostic"
FIXTURES = ["OSC-032", "OSC-033"]
OUT = HERE / "unrouted-cause-2026-08-21.json"


def flags_of(final_line):
    d = dict(tok.split("=", 1) for tok in final_line.split() if "=" in tok)
    return (f"early={d['early']} endgame={d['endgame']} "
            f"committed={d['committed']} train_now={d['train_now']}")


def measure(rman):
    cfg = json.loads(H.CONFIG.read_text())
    sits = {s["id"]: s for s in H.load_situations(FIXTURES)}
    rows = []
    with tempfile.TemporaryDirectory(prefix="cause-") as wd:
        wd = Path(wd)
        (wd / "p").mkdir()
        (wd / "r").mkdir()
        plain = H.compile_candidate(REPO / rman["source"], wd / "p")
        rprobe = H.compile_candidate(REPO / rman["probe"], wd / "r")
        for sid in FIXTURES:
            rerr = C.check_parity(sits[sid], cfg, plain, rprobe)
            finals, routed = {}, set()
            for line in rerr.splitlines():
                m = RC.RE_FINAL.match(line)
                if m:
                    finals[(int(m.group(1)), int(m.group(2)))] = line.strip()
                    continue
                m = RC.RE_ROUTE.match(line)
                if m:
                    routed.add((int(m.group(1)), int(m.group(2))))
            unrouted = {k: v for k, v in finals.items() if k not in routed}
            flags = collections.Counter(flags_of(v) for v in unrouted.values())
            employed = sum(1 for v in unrouted.values()
                           if int(dict(t.split("=", 1) for t in v.split() if "=" in t)["n"]) != 1)
            turns = sorted(t for _, t in unrouted)
            rows.append({"id": sid, "final_rows": len(finals), "unrouted": len(unrouted),
                         "unrouted_employed": employed,
                         "unrouted_idle": len(unrouted) - employed,
                         "unrouted_turn_range": [turns[0], turns[-1]] if turns else None,
                         "branch_flags": dict(flags)})
            print(f"  {sid}: {len(finals)} PS3FINAL, {len(unrouted)} unrouted "
                  f"({employed} employed / {len(unrouted) - employed} idle), "
                  f"turns {turns[0] if turns else '-'}..{turns[-1] if turns else '-'}")
            for k, c in flags.most_common():
                print(f"      x{c:<4d} {k}")
    return rows


def main() -> int:
    builder_src = BUILDER.read_text()
    manifest_src = MANIFEST.read_text()
    probe_path = REPO / json.loads(manifest_src)["door1-champion"]["probe"]
    probe_src = probe_path.read_text()
    if builder_src.count(LIVE) != 1:
        print(f"refusing to run: {LIVE!r} not found exactly once in the builder.",
              file=sys.stderr)
        return 2
    try:
        BUILDER.write_text(builder_src.replace(LIVE, STUB))
        subprocess.run([sys.executable, str(BUILDER), "--subject", "door1-champion",
                        "--manifest", str(MANIFEST)], check=True, cwd=REPO)
        BUILDER.write_text(builder_src)
        rman = json.loads(MANIFEST.read_text())["door1-champion"]
        if len(rman["anchors"]) != 5:
            print(f"built {len(rman['anchors'])} anchors, expected 5", file=sys.stderr)
            return 2
        print(f"pre-revision probe: {len(rman['anchors'])} anchors, {rman['probe_sha256'][:12]}")
        rows = measure(rman)
    finally:
        BUILDER.write_text(builder_src)
        MANIFEST.write_text(manifest_src)
        probe_path.write_text(probe_src)
        man = json.loads(MANIFEST.read_text())["door1-champion"]
        got = hashlib.sha256(probe_path.read_bytes()).hexdigest()
        if got != man["probe_sha256"] or len(man["anchors"]) != 7:
            print(f"RESTORATION FAILED: manifest {man['probe_sha256'][:12]} vs disk {got[:12]}, "
                  f"{len(man['anchors'])} anchors.", file=sys.stderr)
            return 2
        print(f"restored: {len(man['anchors'])} anchors, probe {got[:12]}")
    # The claim under test: ONE branch accounts for every unrouted turn, in both fixtures.
    all_flags = {k for r in rows for k in r["branch_flags"]}
    expected = "early=true endgame=false committed=false train_now=false"
    if all_flags != {expected}:
        print(f"\nDIAGNOSIS REFUTED: unrouted turns take {len(all_flags)} branch combinations, "
              f"not one: {sorted(all_flags)}. The two-anchor repair does not close every hole "
              f"and must not be presented as if it did.", file=sys.stderr)
        return 1
    OUT.write_text(json.dumps(
        {"task": "20260821-osc032-033-no-goal-instrument",
         "claim": "every turn the five-anchor Phase-3 probe left unrouted took the 'early' "
                  "branch of commands(), i.e. early_candidates, which those anchors do not tap",
         "verdict": "CONFIRMED — one branch combination accounts for every unrouted turn in "
                    "both fixtures",
         "branch_flags_observed": sorted(all_flags),
         "probe": "the PRE-REVISION five-anchor build, rebuilt by this script and restored",
         "fixtures": rows}, indent=2, sort_keys=True) + "\n")
    print(f"\nDIAGNOSIS CONFIRMED: every unrouted turn in both fixtures is {expected!r}, "
          f"and no other combination appears.")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
