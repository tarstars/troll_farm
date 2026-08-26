#!/usr/bin/env python3
r"""Phase 3b — gates G-a (trigger census) and G-c (partition and identity), on the 34 fixtures.

Built to the r2 design (`phase3b-design-proposal-r2-2026-08-22.md` @ `75085260…`) as accepted at
G-f, and to local_claude_1's build authorization `20260823T063300Z`, which says in terms: **no
fixture-only result promotes this change.** A pass here makes Phase 3b a candidate worth grading
and nothing more. It is not a cure, it claims no progress, and it addresses none of
OSC-004/017/034 or 032/033.

## What runs

Four binaries per subject, on each fixture, from the same frozen provenance through the same
`fuzz_panel` referee the fixture harness uses:

| arm | source | role |
|---|---|---|
| base plain | `claude_1/picker2/candidate-<s>-p1p2.rs` | the reference command stream |
| cand plain | `claude_1/picker3/candidate-<s>-p3b.rs` | the graded command stream |
| base probe | `claude_1/picker3/probe-<s>-base.rs` | census rows for the incumbent fallback |
| cand probe | `claude_1/picker3/probe-<s>-p3b.rs` | census rows for the ruled fallback |

## Gates, each fail-the-run

- **Probe parity** — each probe's command stream must be byte-identical to its own plain arm's.
  A probe that changes behaviour measures a different bot; this is the check that keeps the census
  rows attached to the graded stream.
- **Shipped-source inertness (design §5(a))** — `candidate-<s>-p3b.rs` must be byte-identical to
  the pinned P1+P2 source plus exactly the §1 hunk, re-derived here by re-running the builder's
  own comparison rather than trusting the earlier run. The probes carry recorders; the graded
  sources must not, and §5(b) holds because the graded arms above are built from the shipped
  sources and never from a probe.
- **G-a** — the five per-game counters of §4.1, reported, not thresholded. Plus the §4.1 runtime
  assertions: `delta_a_selected_ticks ⊆ delta_a_formed_ticks`, and Δ-A/Δ-B mutual exclusion for one
  unit on one tick. A violation fails the run and refutes §2.
- **G-c** — every game lands in exactly one class keyed on `first_delta_a_selected_tick`:
  NO-EFFECT (`null`) requires whole-game byte identity even where Δ-A was formed and never
  selected; EFFECT (`T`) requires identity strictly before `T`, and on `T` the changed command must
  be one of the specifically preserved Δ-A `PICK`s, with provenance recorded.

## What this does NOT do

G-b (Δ-B inertness by same-state fork, §5), G-d (panel with named costs) and G-e (the two-clause
progress bar) are separate and are not run here. Δ-B is *counted* here; counting is not the
inertness measurement, and this file does not claim it is.

**G-b is UNMEASURED on the fixture library** — local_claude_1's RULING 1 (`20260823T094600Z`).
Δ-B fires zero times across 34 fixtures × 2 subjects, so §5's "every naturally reached Δ-B state"
is empty here: not a pass, not a failure. Δ-B states are **not** to be synthesised to fill it;
G-b's proper subject is real games (the NARRATE corpus).

Run:  python3 claude_1/picker3/run_phase3b_gates.py [--subject cureC|door1|both] [--only IDS]
"""
from __future__ import annotations

import argparse, hashlib, json, re, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in ("claude_1/t1", "claude_1/pipeline", "claude_1/banana-restoration-r2"):
    sys.path.insert(0, str(REPO / p))
import fixture_harness as fh     # noqa: E402
import fuzz_panel as fp          # noqa: E402
import semantic_harness as sh    # noqa: E402

OUT = HERE / "results"

ARMS = {
    "cureC": {"base_plain": REPO / "claude_1/picker2/candidate-cureC-p1p2.rs",
              "cand_plain": HERE / "candidate-cureC-p3b.rs",
              "base_probe": HERE / "probe-cureC-base.rs",
              "cand_probe": HERE / "probe-cureC-p3b.rs"},
    "door1": {"base_plain": REPO / "claude_1/picker2/candidate-door1-p1p2.rs",
              "cand_plain": HERE / "candidate-door1-p3b.rs",
              "base_probe": HERE / "probe-door1-base.rs",
              "cand_probe": HERE / "probe-door1-p3b.rs"},
}

RE_FALL = re.compile(r"^P3BFALL arm=(\w+) turn=(\d+) unit=(-?\d+) carried=(\d+) items=(.*)$")
RE_RET = re.compile(r"^P3BRET arm=(\w+) turn=(\d+) unit=(-?\d+) items=(.*)$")
RE_PICK = re.compile(r"^PICK (-?\d+) (\w+)$")


class GateError(Exception):
    """Anything that would make a number below mean something other than it says."""


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def parse_items(blob: str) -> list[dict]:
    if not blob:
        return []
    items = []
    for chunk in blob.split("~"):
        command, score, target = chunk.rsplit("|", 2)
        items.append({"command": command, "score": float(score), "target": target})
    return items


def run_arm(sit, binary: Path, cfg, capture_stderr: bool):
    """Closed-loop run against the fixture's own referee; stderr to a file so it cannot deadlock."""
    spec = fh.spec_for(sit, cfg)
    ref = fp.make_referee(spec)
    turns = int(cfg["turns"])
    header = ref.map_header()
    lines, rows = [], []
    with tempfile.NamedTemporaryFile("w+", prefix="p3b-err-") as err:
        with subprocess.Popen([str(binary)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=err if capture_stderr else subprocess.DEVNULL,
                              text=True) as proc:
            proc.stdin.write(header)
            proc.stdin.flush()
            for _ in range(turns):
                proc.stdin.write(ref.turn_text())
                proc.stdin.flush()
                line = proc.stdout.readline()
                if not line:
                    raise GateError("candidate closed stdout early")
                line = line.rstrip("\n")
                lines.append(line)
                ref.apply(line)
                ref.grow()
            proc.stdin.close()
        if capture_stderr:
            err.seek(0)
            rows = err.read().splitlines()
    return lines, rows


def census(rows: list[str], arm: str):
    """Fallback state per (turn, unit): what `out` held on entry, and what was returned."""
    entered, returned = {}, {}
    for line in rows:
        m = RE_FALL.match(line)
        if m:
            if m.group(1) != arm:
                raise GateError(f"row from arm {m.group(1)} in the {arm} probe's stderr")
            entered[(int(m.group(2)), int(m.group(3)))] = {
                "carried": int(m.group(4)), "items": parse_items(m.group(5))}
            continue
        m = RE_RET.match(line)
        if m:
            returned[(int(m.group(2)), int(m.group(3)))] = parse_items(m.group(4))
    return entered, returned


def frags(line: str) -> list[str]:
    return [f.strip() for f in line.split(";")]


def grade_game(sid, base_lines, cand_lines, cand_entered, cand_returned, base_returned):
    """The §4.1 counters and the §4.2 class for one game, plus the two runtime assertions."""
    formed, selected, dup = [], [], []
    violations, preserved_by_tick = [], {}

    for (turn, unit), state in sorted(cand_entered.items()):
        # Δ-A: replant PICKs standing in `out` at fallback entry — kept by the candidate,
        # discarded by the incumbent, whose returned list is the base-side provenance.
        picks = [i for i in state["items"]
                 if RE_PICK.match(i["command"]) and i["target"].startswith("Cell(")]
        # Δ-B: bank candidates already in `out` that the fallback appends a second time.
        banks = [i for i in state["items"] if i["target"].startswith("Bank(")]
        delta_b = bool(banks) and state["carried"] > 0
        if picks:
            formed.append(turn)
            preserved_by_tick[(turn, unit)] = picks
        if delta_b:
            ret = cand_returned.get((turn, unit), [])
            seen, dupes = set(), []
            for item in ret:
                key = (item["command"], item["score"], item["target"])
                if key in seen and item["target"].startswith("Bank("):
                    dupes.append(key)
                seen.add(key)
            dup.append({"turn": turn, "unit": unit, "duplicate_bank_entries": len(dupes)})
        if picks and delta_b:
            violations.append(f"turn {turn} unit {unit}: Δ-A and Δ-B co-occur — §2 mutual "
                              f"exclusion refuted")
        if picks and state["carried"] != 0:
            violations.append(f"turn {turn} unit {unit}: a replant PICK stood in `out` with "
                              f"carried={state['carried']}")

    for (turn, unit), picks in sorted(preserved_by_tick.items()):
        if turn > len(cand_lines):
            continue
        emitted = frags(cand_lines[turn - 1])
        if any(p["command"] in emitted for p in picks):
            selected.append(turn)

    if not set(selected) <= set(formed):
        violations.append("delta_a_selected_ticks is not a subset of delta_a_formed_ticks")

    first = min(selected) if selected else None
    identical = cand_lines == base_lines
    first_diff = None
    for i, (a, b) in enumerate(zip(base_lines, cand_lines), 1):
        if a != b:
            first_diff = i
            break
    if first_diff is None and len(base_lines) != len(cand_lines):
        first_diff = min(len(base_lines), len(cand_lines)) + 1

    cls, why, provenance = None, None, None
    if first is None:
        cls = "NO-EFFECT"
        ok = identical
        why = "byte-identical" if ok else f"NO-EFFECT game diverged at turn {first_diff}"
    else:
        cls = "EFFECT"
        ok = first_diff is not None and first_diff >= first
        why = (f"identical before the first selected Δ-A tick {first}"
               if ok else
               f"diverged at turn {first_diff}, before the first selected Δ-A tick {first}")
        if ok:
            base_frags = frags(base_lines[first - 1]) if first <= len(base_lines) else []
            cand_frags = frags(cand_lines[first - 1]) if first <= len(cand_lines) else []
            changed = [f for f in cand_frags if f not in base_frags]
            picks = preserved_by_tick_at(preserved_by_tick, first)
            named = [c for c in changed if c in [p["command"] for p in picks]]
            if not changed or len(named) != len(changed):
                ok = False
                why = (f"on tick {first} the changed commands {changed} are not all preserved "
                       f"Δ-A PICKs {[p['command'] for p in picks]}")
            provenance = {
                "tick": first,
                "changed_commands": changed,
                "preserved_picks": [{k: p[k] for k in ("command", "score", "target")}
                                    for p in picks],
                "base_fallback_list": [
                    {k: i[k] for k in ("command", "score", "target")}
                    for (t, u), lst in sorted(base_returned.items()) if t == first for i in lst],
            }
    return {
        "id": sid,
        "delta_a_formed_ticks": len(formed), "delta_a_formed": formed[:40],
        "delta_a_selected_ticks": len(selected), "delta_a_selected": selected[:40],
        "first_delta_a_selected_tick": first,
        "delta_b_duplicate_ticks": len(dup), "delta_b_detail": dup[:20],
        "whole_game_identical": identical,
        "first_divergence_turn": first_diff,
        "class": cls, "class_ok": ok, "why": why, "provenance": provenance,
        "assertion_violations": violations,
    }


def preserved_by_tick_at(preserved, turn):
    out = []
    for (t, _u), picks in preserved.items():
        if t == turn:
            out.extend(picks)
    return out


def shipped_source_inertness(subject: str) -> dict:
    """Design §5(a): the graded source is the pinned source plus exactly the §1 hunk, re-derived."""
    sys.path.insert(0, str(HERE))
    import make_phase3b_candidate as mk
    src = mk.SUBJECTS[subject]["src"].read_text()
    want = mk.patch(subject, src)
    got = ARMS[subject]["cand_plain"].read_text()
    if got != want:
        raise GateError(f"{subject}: the graded source is NOT the pinned source plus the §1 hunk")
    return {"pinned": str(mk.SUBJECTS[subject]["src"].relative_to(REPO)),
            "pinned_sha256": sha256(src), "graded_sha256": sha256(got)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--subject", default="both", choices=["cureC", "door1", "both"])
    ap.add_argument("--only", help="comma-separated fixture ids")
    args = ap.parse_args()

    cfg = json.loads(fh.CONFIG.read_text())
    sits = fh.load_situations(args.only.split(",") if args.only else None)
    subjects = list(ARMS) if args.subject == "both" else [args.subject]

    report = {"gate": "G-a + G-c", "task": "20260820-pair-selector-anti-benching",
              "design": "claude_1/picker3/phase3b-design-proposal-r2-2026-08-22.md",
              "design_commit": "75085260b026750201061760804257f422c88a6b",
              "build_authorization": "local_claude_1 20260823T063300Z",
              "gb_status": "UNMEASURED on the fixture library",
              "gb_ruling": "local_claude_1 20260823T094600Z RULING 1: Δ-B fires zero times on 34 "
                           "fixtures × 2 subjects, so §5's 'every naturally reached Δ-B state' is "
                           "empty here. G-b is recorded UNMEASURED on the fixture library — not a "
                           "pass and not a failure. Δ-B states are NOT to be synthesised to fill "
                           "it; G-b's proper subject is real games (NARRATE corpus).",
              "not_proven_here": "G-b is UNMEASURED on the fixture library (see gb_ruling); G-d "
                                 "(panel with named costs) and G-e (progress bar) are not run "
                                 "here. Δ-B is counted, which is not the inertness measurement. "
                                 "No fixture-only result promotes this change.",
              "subjects": {}}
    failed = False

    for subject in subjects:
        print(f"\n=== subject {subject}")
        inert = shipped_source_inertness(subject)
        print(f"  shipped-source inertness (§5a): OK  graded {inert['graded_sha256'][:16]}…")
        rows, parity_failures = [], []
        with tempfile.TemporaryDirectory(prefix="p3b-") as wd:
            wd = Path(wd)
            bins = {}
            for arm, src in ARMS[subject].items():
                bins[arm] = wd / f"{arm}.bin"
                sh.compile_text(src.read_text(), bins[arm], crate=f"p3b_{arm}")
            for sit in sits:
                sid = sit["id"]
                base_lines, _ = run_arm(sit, bins["base_plain"], cfg, False)
                cand_lines, _ = run_arm(sit, bins["cand_plain"], cfg, False)
                bp_lines, bp_rows = run_arm(sit, bins["base_probe"], cfg, True)
                cp_lines, cp_rows = run_arm(sit, bins["cand_probe"], cfg, True)
                if bp_lines != base_lines:
                    parity_failures.append(f"{sid}: base probe stream != base plain stream")
                if cp_lines != cand_lines:
                    parity_failures.append(f"{sid}: cand probe stream != cand plain stream")
                _, base_returned = census(bp_rows, "BASE")
                cand_entered, cand_returned = census(cp_rows, "CAND")
                row = grade_game(sid, base_lines, cand_lines, cand_entered, cand_returned,
                                 base_returned)
                rows.append(row)
                mark = "OK  " if row["class_ok"] and not row["assertion_violations"] else "FAIL"
                print(f"  {mark} {sid:<10} {row['class']:<9} formed "
                      f"{row['delta_a_formed_ticks']:>3} selected "
                      f"{row['delta_a_selected_ticks']:>3} Δ-B {row['delta_b_duplicate_ticks']:>3} "
                      f"identical={row['whole_game_identical']}")

        violations = [f"{r['id']}: {v}" for r in rows for v in r["assertion_violations"]]
        bad = [r["id"] for r in rows if not r["class_ok"]]
        ok = not parity_failures and not violations and not bad
        failed = failed or not ok
        report["subjects"][subject] = {
            "shipped_source_inertness": inert,
            "probe_parity_failures": parity_failures,
            "assertion_violations": violations,
            "class_failures": bad,
            "games": len(rows),
            "no_effect_games": sum(1 for r in rows if r["class"] == "NO-EFFECT"),
            "effect_games": sum(1 for r in rows if r["class"] == "EFFECT"),
            "games_with_delta_a_formed": sum(1 for r in rows if r["delta_a_formed_ticks"]),
            "games_with_delta_b": sum(1 for r in rows if r["delta_b_duplicate_ticks"]),
            "panel_delta_a_formed_ticks": sum(r["delta_a_formed_ticks"] for r in rows),
            "panel_delta_a_selected_ticks": sum(r["delta_a_selected_ticks"] for r in rows),
            "panel_delta_b_duplicate_ticks": sum(r["delta_b_duplicate_ticks"] for r in rows),
            "verdict": "PASS" if ok else "FAIL",
            "rows": rows,
        }
        s = report["subjects"][subject]
        print(f"  {subject}: {s['effect_games']} EFFECT / {s['no_effect_games']} NO-EFFECT, "
              f"Δ-A formed {s['panel_delta_a_formed_ticks']} ticks, selected "
              f"{s['panel_delta_a_selected_ticks']}, Δ-B {s['panel_delta_b_duplicate_ticks']} "
              f"-> {s['verdict']}")

    report["verdict"] = "FAIL" if failed else "PASS"
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "phase3b-gac-2026-08-23.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"\n  G-a + G-c: {report['verdict']}")
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except GateError as exc:
        print(f"GATE FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
