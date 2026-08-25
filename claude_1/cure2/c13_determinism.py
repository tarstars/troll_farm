#!/usr/bin/env python3
"""C-13 — determinism: two runs, byte-identical outputs, over the whole corpus.

G-0 §9 pre-committed C-13 as "determinism: two runs with explicit `--label`/`--peer-label`,
byte-identical outputs -> identical". It is the cheapest remaining control and the one that
gates the credibility of every number already published: C-10's 66/66, C-11's 54,800/54,800,
the C-5 census and the named costs are all single-execution reads, and a single execution of a
nondeterministic bot measures nothing that can be reproduced.

The labels are EXPLICIT INPUTS, as `claude_1/geometry1/g1-reissue-2026-08-25.md` established
for K-4: a report that names its runs by their absolute temporary paths cannot be reproduced
byte-for-byte from a fresh archive by anyone else. `--label`/`--peer-label` are the only
presentation strings in the output, and gate D-3 refuses if any temporary path leaks into it.

Four layers, each a separate number rather than one word:

  D-0  generator determinism  -- `make_cure2_source.py`, `build_arms.py` and `make_c11_arm.py`
                                re-run in place must reproduce all six generated files
                                (`cure2-swap-v5.rs`, the three arms, `arm-c11.rs`, the manifest)
                                byte-identically. A generator that does not is a source that
                                cannot be re-derived from its pins.
  D-1  run-to-run             -- the SAME binary run twice on the same game must produce a
                                byte-identical command stream AND a byte-identical referee
                                transcript. The transcript is closed-loop, so it is a second,
                                coarser witness of the same behaviour.
  D-2  build-to-build         -- a SECOND, independent compilation of the identical source, in
                                a different directory, under a different crate name, run from a
                                different working directory, must produce the same two streams.
                                This is where path-, address- or hash-order-dependence would
                                show up; D-1 alone would not see it.
  D-3  label independence     -- the report's only presentation fields are the two labels, and
                                no temporary path appears anywhere in the JSON.

Population: all four published arms (`candidate`, `instrument`, `ruleoff`, `c11`) over 34
fixtures + 240 panel games = 274 games each, 1,096 game-arms, three executions apiece.

Two witnesses against a vacuous pass, because "two identical outputs" is trivially true of a bot
that never does anything (the all-WAIT-window failure mode this programme has met before):

  W-1  distinct command lines per game -- a game whose whole stream is one repeated line proves
       nothing about determinism. Reported as a count of games with < 2 distinct lines.
  W-2  arm separation -- the candidate and ruleoff streams must DIFFER on at least one game, or
       the comparator is returning "identical" for everything put in front of it. W-2b repeats
       it with every MSG fragment stripped, because the raw streams differ for a telemetry
       reason on every game (the candidate arm narrates nothing) and that would flatter it.

And two poisons, one per comparator, in the shape C-11's poison control established:

  P-13a  nondeterministic TELEMETRY: `pid={}` appended to the instrument arm's v5 payload. Must
         fire in the command-stream comparator on every game (pids differ between executions).
  P-13b  nondeterministic BEHAVIOUR: the candidate arm's end-of-turn `prev_cells` write gated on
         a wall-clock nanosecond parity bit. The candidate arm emits no MSG at all, so this
         fires only through the commands and the transcript -- exactly the channel that would
         carry a real nondeterminism. Its fire rate is ~50 % per game by construction and is
         reported as the measured number, not asserted.

    python3 claude_1/cure2/c13_determinism.py [--fixtures-only] [--label L] [--peer-label L]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
for _p in ("claude_1/t1", "claude_1/pipeline", "claude_1/banana-restoration-r2",
           "claude_1/narrate5"):
    sys.path.insert(0, str(REPO / _p))

import fixture_harness as fh          # noqa: E402
import fuzz_panel as fp               # noqa: E402
import regression_tests as rt         # noqa: E402
import semantic_harness as sh         # noqa: E402
import narrate5 as n5                # noqa: E402

PANEL_CFG = HERE / "cure2-instrument-config.json"
CENSUS = HERE / "results" / "panel-swap-census.json"
OUT = HERE / "results" / "c13-determinism.json"

ARMS = ["candidate", "instrument", "ruleoff", "c11"]

GENERATED = ["cure2-swap-v5.rs", "cure2-swap-v5.rs.sha256",
             "arm-candidate.rs", "arm-candidate.rs.sha256",
             "arm-instrument.rs", "arm-instrument.rs.sha256",
             "arm-ruleoff.rs", "arm-ruleoff.rs.sha256",
             "arm-c11.rs", "arm-c11.rs.sha256",
             "arm-manifest.json"]

GENERATORS = ["make_cure2_source.py", "build_arms.py", "make_c11_arm.py"]

# P-13a: one line, no line-count change, the instrument arm's payload only.
TELEMETRY_ANCHOR = '                tokens.push(format!("sf={}",meta.slot_fail));\n'
TELEMETRY_POISON = ('                tokens.push(format!("sf={} pid={}",meta.slot_fail,'
                    'std::process::id()));\n')

# P-13b: one line, no line-count change, the candidate arm's behaviour only.
BEHAVIOUR_ANCHOR = ("                    *prev_cells=view.units.iter().filter(|unit|unit.player==0)"
                    ".map(|unit|(unit.id,unit.cell)).collect();\n")
BEHAVIOUR_POISON = ("                    if std::time::SystemTime::now().duration_since"
                    "(std::time::UNIX_EPOCH).unwrap().subsec_nanos()%2==0{*prev_cells=view.units"
                    ".iter().filter(|unit|unit.player==0).map(|unit|(unit.id,unit.cell))"
                    ".collect();}\n")


class GateError(Exception):
    """Anything that would make the number below mean something other than it says."""


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def poison(source: str, anchor: str, replacement: str, what: str) -> str:
    if source.count(anchor) != 1:
        raise GateError(f"{what}: anchor matched {source.count(anchor)} times, refusing")
    out = source.replace(anchor, replacement)
    if len(out.splitlines()) != len(source.splitlines()):
        raise GateError(f"{what}: the poison edit changed the line count")
    return out


# ------------------------------------------------------------------ D-0 generator determinism

def d0_generators() -> dict:
    """Re-run every generator in place; all six generated files must come back byte-identical."""
    before = {name: sha((HERE / name).read_text()) for name in GENERATED}
    ran = []
    for script in GENERATORS:
        proc = subprocess.run([sys.executable, str(HERE / script)], cwd=str(REPO),
                              capture_output=True, text=True)
        if proc.returncode != 0:
            raise GateError(f"{script} exited {proc.returncode}: {proc.stderr.strip()[:400]}")
        ran.append(script)
    after = {name: sha((HERE / name).read_text()) for name in GENERATED}
    changed = sorted(n for n in GENERATED if before[n] != after[n])
    if changed:
        raise GateError(f"D-0: re-running the generators changed {changed} — the pinned sources "
                        f"are NOT re-derivable and the working tree is now dirty")
    return {"generators_re_run": ran, "files_compared": len(GENERATED),
            "files_differing": 0, "sha256": {n: after[n] for n in GENERATED},
            "result": "PASS — every generated file is byte-identical after a re-run"}


# --------------------------------------------------------------------------- the game corpus

def corpus(fixtures_only: bool):
    """(fixture jobs, all jobs) as (key, spec, turns); the panel half is the census population."""
    cfg = json.loads(fh.CONFIG.read_text())
    fixtures = []
    for sit in fh.load_situations(None):
        spec = fh.spec_for(sit, cfg)
        fixtures.append((sit["id"], spec, int(cfg["turns"])))
    jobs = list(fixtures)
    if not fixtures_only:
        pcfg = fp.load_config(PANEL_CFG)
        wanted = [r["game"] for r in json.loads(CENSUS.read_text())["rows"]]
        panel = {f"{j['spec']['map_id']}:{j['spec']['seat']}": j
                 for j in fp.build_jobs(pcfg, Path("unused-candidate"), Path("unused-parent"))}
        missing = [k for k in wanted if k not in panel]
        if missing:
            raise GateError(f"panel jobs missing {missing[:6]} — the population is not the "
                            f"census population")
        jobs.extend((key, panel[key]["spec"], panel[key]["turns"]) for key in wanted)
    return fixtures, jobs


def run(binary: Path, spec, turns: int, cwd: str | None = None):
    """One execution; returns (commands, transcript). cwd is honoured by chdir around the spawn."""
    if cwd is None:
        return _run(binary, spec, turns)
    saved = os.getcwd()
    os.chdir(cwd)
    try:
        return _run(binary, spec, turns)
    finally:
        os.chdir(saved)


def _run(binary: Path, spec, turns: int):
    """The arm's stderr is discarded here (the C-11 arm prints a PREVREAD line per turn): C-13
    compares the command stream and the referee transcript, and C-11 already owns the read."""
    fd = sys.stderr.fileno()
    saved = os.dup(fd)
    null = os.open(os.devnull, os.O_WRONLY)
    os.dup2(null, fd)
    try:
        transcript, commands = rt.run_binary_custom(binary, fp.make_referee(spec), turns)
    finally:
        os.dup2(saved, fd)
        os.close(saved)
        os.close(null)
    return commands, transcript


# ------------------------------------------------------- D-1 run-to-run and D-2 build-to-build

def compare_arm(name: str, source: str, jobs, wd: Path) -> dict:
    """Three executions per game: A and B from build 1, C from an independent build 2."""
    build1, build2 = wd / f"{name}-1" / "arm.bin", wd / f"{name}-2" / "arm.bin"
    other_cwd = wd / f"{name}-cwd"
    for path in (build1.parent, build2.parent, other_cwd):
        path.mkdir(parents=True, exist_ok=True)
    sh.compile_text(source, build1, crate=f"cure2_c13_{name}_one")
    sh.compile_text(source, build2, crate=f"cure2_c13_{name}_two")

    rows, d1_fail, d2_fail, thin, distinct_total = [], [], [], [], 0
    for key, spec, turns in jobs:
        cmd_a, tr_a = run(build1, spec, turns)
        cmd_b, tr_b = run(build1, spec, turns)
        cmd_c, tr_c = run(build2, spec, turns, cwd=str(other_cwd))
        distinct = len(set(cmd_a.rstrip("\n").split("\n")))
        distinct_total += distinct
        if distinct < 2:
            thin.append(key)
        if (cmd_a, tr_a) != (cmd_b, tr_b):
            d1_fail.append({"game": key, "commands_equal": cmd_a == cmd_b,
                            "transcript_equal": tr_a == tr_b})
        if (cmd_a, tr_a) != (cmd_c, tr_c):
            d2_fail.append({"game": key, "commands_equal": cmd_a == cmd_c,
                            "transcript_equal": tr_a == tr_c})
        stripped = "\n".join(n5.strip_msg(l) for l in cmd_a.rstrip("\n").split("\n"))
        rows.append({"game": key, "turns": turns, "commands_sha256": sha(cmd_a),
                     "commands_sha256_msg_stripped": sha(stripped),
                     "transcript_sha256": sha(tr_a), "distinct_command_lines": distinct})
    return {"arm": name, "source_sha256": sha(source), "games": len(rows),
            "D-1_run_to_run_mismatches": d1_fail, "D-2_build_to_build_mismatches": d2_fail,
            "W-1_games_with_fewer_than_two_distinct_command_lines": thin,
            "W-1_distinct_command_lines_total": distinct_total,
            "rows": rows}


# ------------------------------------------------------------------------------- the poisons

def poison_run(label: str, name: str, source: str, jobs, wd: Path, expect_channel: str) -> dict:
    """A nondeterministic arm run twice per game; the comparator must see it."""
    binary = wd / f"poison-{name}" / "arm.bin"
    binary.parent.mkdir(parents=True, exist_ok=True)
    sh.compile_text(source, binary, crate=f"cure2_c13_poison_{name}")
    fired_cmd, fired_tr, total = [], [], 0
    for key, spec, turns in jobs:
        total += 1
        cmd_a, tr_a = run(binary, spec, turns)
        cmd_b, tr_b = run(binary, spec, turns)
        if cmd_a != cmd_b:
            fired_cmd.append(key)
        if tr_a != tr_b:
            fired_tr.append(key)
    fired = fired_cmd if expect_channel == "commands" else fired_tr
    return {"poison": label, "arm": name, "poison_sha256": sha(source), "games": total,
            "fired_on_commands": len(fired_cmd), "fired_on_transcript": len(fired_tr),
            "games_where_it_fired": sorted(set(fired_cmd) | set(fired_tr))[:20],
            "verdict": ("PASS — the C-13 comparator detects it"
                        if fired else
                        "FAIL — C-13 IS INERT on this channel: a nondeterministic arm compared "
                        "identical")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="C-13 determinism control")
    ap.add_argument("--fixtures-only", action="store_true")
    ap.add_argument("--label", default="run A (first execution, build 1)",
                    help="presentation label for the first run — an explicit input so that the "
                         "report carries no absolute path")
    ap.add_argument("--peer-label",
                    default="run B (second execution; build 2 in a separate directory, "
                            "separate crate name, separate working directory)",
                    help="presentation label for the second run")
    args = ap.parse_args(argv)

    result = {"control": "C-13 — determinism over the whole corpus",
              "task": "20260825-dance-cure-candidate-2-swap",
              "run_a": args.label, "run_b": args.peer_label,
              "population": ("34 fixtures" if args.fixtures_only
                             else "34 fixtures + 240 panel games"),
              "executions_per_game_per_arm": 3,
              "gates": {}}

    result["D-0 generator determinism"] = d0_generators()
    fixtures, jobs = corpus(args.fixtures_only)

    arms, d1, d2 = [], 0, 0
    with tempfile.TemporaryDirectory(prefix="cure2-c13-") as tmp:
        wd = Path(tmp)
        for name in ARMS:
            source = (HERE / f"arm-{name}.rs").read_text()
            row = compare_arm(name, source, jobs, wd)
            d1 += len(row["D-1_run_to_run_mismatches"])
            d2 += len(row["D-2_build_to_build_mismatches"])
            arms.append(row)
            print(f"  {name:<11} {row['games']} games  D-1 {len(row['D-1_run_to_run_mismatches'])}"
                  f" mismatches  D-2 {len(row['D-2_build_to_build_mismatches'])} mismatches",
                  flush=True)

        instrument = (HERE / "arm-instrument.rs").read_text()
        candidate = (HERE / "arm-candidate.rs").read_text()
        p_a = poison_run("P-13a nondeterministic telemetry (pid in the v5 payload)", "telemetry",
                         poison(instrument, TELEMETRY_ANCHOR, TELEMETRY_POISON, "P-13a"),
                         fixtures, wd, "commands")
        print(f"  P-13a fired on {p_a['fired_on_commands']}/{p_a['games']} fixtures (commands)",
              flush=True)
        p_b = poison_run("P-13b nondeterministic behaviour (clock-gated prev_cells write)",
                         "behaviour",
                         poison(candidate, BEHAVIOUR_ANCHOR, BEHAVIOUR_POISON, "P-13b"),
                         fixtures, wd, "transcript")
        print(f"  P-13b fired on {p_b['fired_on_commands']}/{p_b['games']} fixtures (commands), "
              f"{p_b['fired_on_transcript']} (transcript)", flush=True)

    by_arm = {r["arm"]: {row["game"]: row["commands_sha256"] for row in r["rows"]} for r in arms}
    separated = [g for g in by_arm["candidate"]
                 if by_arm["candidate"][g] != by_arm["ruleoff"][g]]
    stripped = {r["arm"]: {row["game"]: row["commands_sha256_msg_stripped"] for row in r["rows"]}
                for r in arms}
    behavioural = [g for g in stripped["candidate"]
                   if stripped["candidate"][g] != stripped["ruleoff"][g]]
    thin = sorted({g for r in arms
                   for g in r["W-1_games_with_fewer_than_two_distinct_command_lines"]})

    result["arms"] = arms
    result["poisons"] = [p_a, p_b]
    result["witnesses"] = {
        "W-1 games with fewer than two distinct command lines (any arm)": len(thin),
        "W-1 games named": thin[:20],
        "W-1 distinct command lines summed over arms and games":
            sum(r["W-1_distinct_command_lines_total"] for r in arms),
        "W-2 games where the candidate and ruleoff streams differ": len(separated),
        "W-2b games where they differ with MSG STRIPPED (behaviour, not telemetry)":
            len(behavioural),
        "note": ("W-2 = 0 would mean the comparator returns 'identical' for two arms that are "
                 "known to differ, i.e. C-13 is inert regardless of the poisons. W-2 alone is "
                 "weak: the candidate arm carries no MSG and the ruleoff arm carries one every "
                 "turn, so their raw streams differ on every game for a telemetry reason. W-2b "
                 "strips every MSG fragment and is the behavioural half of the same witness."),
    }
    games = sum(r["games"] for r in arms)
    result["gates"]["D-1 run-to-run"] = (
        f"{'PASS' if not d1 else 'FAIL'} — {games - d1}/{games} game-arms byte-identical "
        f"on both the command stream and the referee transcript")
    result["gates"]["D-2 build-to-build"] = (
        f"{'PASS' if not d2 else 'FAIL'} — {games - d2}/{games} game-arms byte-identical "
        f"against an independent second build in another directory")
    blob = json.dumps(result)
    leaked = [frag for frag in ("cure2-c13-", "/tmp/", str(REPO)) if frag in blob]
    result["gates"]["D-3 label independence"] = (
        f"{'PASS' if not leaked else 'FAIL'} — the only presentation fields are run_a/run_b, "
        f"supplied as --label/--peer-label; leaked path fragments: {leaked}")

    ok = (not d1 and not d2 and not leaked and len(separated) > 0 and len(behavioural) > 0
          and p_a["fired_on_commands"] and p_b["fired_on_transcript"])
    result["verdict"] = (
        "PASS — identical" if ok else
        "FAIL — a run differed" if (d1 or d2) else
        "FAIL — a leak or an inert comparator; see the gates and the poisons")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    for gate, text in result["gates"].items():
        print(f"  {gate}: {text}")
    print("  W-2 candidate/ruleoff separation:", len(separated), "games;",
          len(behavioural), "with MSG stripped")
    print("verdict:", result["verdict"])
    print("wrote", OUT.relative_to(REPO))
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except GateError as exc:
        print(f"c13_determinism: GATE {exc}", file=sys.stderr)
        sys.exit(2)
