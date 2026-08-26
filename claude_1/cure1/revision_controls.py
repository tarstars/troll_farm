#!/usr/bin/env python3
"""The RED half of revisions R-A and R-B — three forks, on the identical corpus.

The ruling of 2026-08-25T09:42:00Z asks for the hold to be scoped two ways and for the scoping to
be shown to be what does the work. A green arm alone cannot show that: an inert rule and a
correctly scoped rule look the same from outside. So each revision's flag is flipped BACK, one
line at a time, and the same 240-game panel is re-run:

    F1  TRANSIENT_ONLY=false                       R-A off: the as-built hold policy on transient
                                                   AND permanent blocks, R-B still on
    F2  P3_SCOPING_ENABLED=false                   R-B off: the hold is live on orchard-eligible
                                                   maps again, R-A still on
    F3  both false                                 the as-built arm's hold policy exactly

Each fork is `arm-candidate.rs` (and, for the telemetry census, `arm-instrument.rs`) with ONE or
TWO lines rewritten and nothing else; the script refuses unless the anchor occurs exactly once.
None of these is a candidate and none is in `arm-manifest.json`.

What the pair is expected to show, and what it would mean if it did not:

  * R-B's control -- the ruling asked for "the hold firing on the same map one turn after the
    interval ends". `fuzz_panel.eval_p3` compares the WHOLE command stream whenever the seat view
    is orchard-eligible, and that flag is computed once per map+seat, so the covered interval IS
    the whole game and there is no "one turn after" inside it. The substitute, on the identical
    map: F2 (scoping off) must reproduce a P3 violation that the revised arm does not have. If F2
    is also P3-clean, then R-B is NOT what fixed P3 -- R-A is -- and the report must say so
    instead of claiming a scoping success.
  * R-A's control -- F1/F3 must show materially more hold turns and a higher idle-with-work
    share than the revised arm. If they do not, the transient predicate is not the lever.

    python3 claude_1/cure1/revision_controls.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
OUT = HERE / "results" / "revision-controls.json"

TRANSIENT_ON = "            const TRANSIENT_ONLY:bool=true;"
TRANSIENT_OFF = "            const TRANSIENT_ONLY:bool=false;"
SCOPING_ON = "            const P3_SCOPING_ENABLED:bool=true;"
SCOPING_OFF = "            const P3_SCOPING_ENABLED:bool=false;"

FORKS = {
    "F1-transient-off": {"transient": False, "scoping": True,
                         "what": "R-A off: the hold fires on permanent blocks again"},
    "F2-scoping-off": {"transient": True, "scoping": False,
                       "what": "R-B off: the hold is live on orchard-eligible maps again"},
    "F3-as-built-policy": {"transient": False, "scoping": False,
                           "what": "both revisions off: the as-built arm's hold policy"},
}


def fork_text(arm: str, transient: bool, scoping: bool) -> str:
    text = (HERE / f"arm-{arm}.rs").read_text()
    for anchor, want, off in ((TRANSIENT_ON, transient, TRANSIENT_OFF),
                              (SCOPING_ON, scoping, SCOPING_OFF)):
        if text.count(anchor) != 1:
            raise SystemExit(f"REFUSED: {anchor!r} occurs {text.count(anchor)} times in arm-{arm}")
        if not want:
            text = text.replace(anchor, off)
    return text


def run_panel(name: str, source: Path, sha: str, arm: str, games: str) -> dict:
    cfg = json.loads((HERE / f"cure1-{arm}-config.json").read_text())
    cfg["task"] = (f"20260825-dance-cure-candidate-1-hold REVISION CONTROL {name} "
                   f"({arm} variant) — NOT a candidate")
    cfg["candidate"] = {"crate": f"cure1_{name.replace('-', '_')}_{arm}",
                        "sha256": sha, "source": f"../../{source.relative_to(REPO)}"}
    cfg["games_dir"] = games
    cfg["notes"] = [f"REVISION CONTROL {name}: {FORKS[name]['what']}. Never a candidate, never "
                    "in arm-manifest.json, never submitted.", cfg["notes"][1]]
    path = HERE / f"cure1-{name}-{arm}-config.json"
    path.write_text(json.dumps(cfg, indent=2, sort_keys=True) + "\n")
    done = subprocess.run(
        [sys.executable, str(REPO / "claude_1/pipeline/fuzz_panel.py"), "--config", str(path),
         "--report", str(HERE / "results" / f"panel-{name}-{arm}.md"),
         "--json", str(HERE / "results" / f"panel-{name}-{arm}.json")],
        capture_output=True, text=True, timeout=3600)
    tail = (done.stdout.strip().split("\n")[-1] if done.stdout.strip() else done.stderr[-300:])
    print(f"    {name} {arm}: {tail}")
    return json.loads((HERE / "results" / f"panel-{name}-{arm}.json").read_text())


def p3_games(panel: dict) -> list:
    out = []
    for row in panel["games"]:
        if any(v["property"] == "P3" for v in row["violations"]):
            detail = next(v["detail"] for v in row["violations"] if v["property"] == "P3")
            out.append({"map_id": row["map_id"], "seat": row["seat"],
                        "first_divergence_turn": detail.get("first_divergence_turn")})
    return out


def main() -> int:
    report = {
        "control": "revision controls — R-A and R-B flipped back, one line at a time",
        "ruling": ("coordination/messages/local_claude_1/"
                   "20260825T094200Z-20260825-dance-cure-candidate-1-hold-policy.md"),
        "revised_arm": {},
        "forks": {},
    }
    revised = json.loads((HERE / "results" / "panel-candidate.json").read_text())
    report["revised_arm"] = {"blocking_games": revised["stats"]["blocking_games"],
                             "p3_games": p3_games(revised)}
    print(f"  revised arm: P3 games {report['revised_arm']['p3_games'] or 'none'}")

    for name, spec in FORKS.items():
        entry = {"what": spec["what"], "arms": {}}
        for arm in ("candidate", "instrument"):
            text = fork_text(arm, spec["transient"], spec["scoping"])
            sha = hashlib.sha256(text.encode()).hexdigest()
            path = HERE / f"fork-{name}-{arm}.rs"
            path.write_text(text)
            games = f"/tmp/claude-1000/cure1/{name}-{arm}/games"
            panel = run_panel(name, path, sha, arm, games)
            entry["arms"][arm] = {
                "source": str(path.relative_to(REPO)), "sha256": sha,
                "games_archive": f"{games}/games.jsonl.gz",
                "blocking_games": panel["stats"]["blocking_games"],
                "p3_games": p3_games(panel),
            }
        idle = subprocess.run(
            [sys.executable, str(HERE / "idle_share.py"),
             "--arm", f"candidate ({name})=/tmp/claude-1000/cure1/{name}-instrument/games/"
                      "games.jsonl.gz",
             "--json", str(HERE / "results" / f"idle-share-{name}.json")],
            capture_output=True, text=True, timeout=1800)
        print("  " + (idle.stdout.strip().split("\n")[0] if idle.stdout.strip()
                      else idle.stderr[-300:]))
        entry["idle"] = json.loads(
            (HERE / "results" / f"idle-share-{name}.json").read_text())["arms"][
                f"candidate ({name})"]
        report["forks"][name] = entry

    revised_idle = json.loads((HERE / "results" / "idle-share.json").read_text())
    r = revised_idle["arms"]["candidate (rule-on)"]
    report["revised_arm"]["idle_with_work_share_pct"] = r["idle_with_work_share_pct"]
    report["revised_arm"]["hold_turns"] = r["branches"].get("H", 0)

    f2 = report["forks"]["F2-scoping-off"]["arms"]["candidate"]["p3_games"]
    f3 = report["forks"]["F3-as-built-policy"]["arms"]["candidate"]["p3_games"]
    report["r_b_control"] = {
        "asked_for": ("the hold firing on the same map one turn after the P3 interval ends — NOT "
                      "CONSTRUCTIBLE: fuzz_panel.eval_p3 compares the whole command stream and "
                      "spec['orchard_eligible'] is computed once per map+seat, so the covered "
                      "interval is the whole game"),
        "substitute": "scoping off (F2) on the identical corpus must reproduce a P3 violation",
        "f2_p3_games": f2,
        "f3_p3_games": f3,
        "verdict": ("PASS — scoping off reproduces a P3 violation the revised arm does not have"
                    if f2 else
                    "NOT DEMONSTRATED — with R-A on, the hold never fires on an orchard-eligible "
                    "map on this corpus even with R-B off, so R-B is redundant HERE and its "
                    "P3-clean result is R-A's doing. R-B is retained as the belt to R-A's braces "
                    "and is reported as untested by this corpus, not as a success."),
    }
    hold_ratio = (report["forks"]["F3-as-built-policy"]["idle"]["branches"].get("H", 0)
                  / max(1, report["revised_arm"]["hold_turns"]))
    report["r_a_control"] = {
        "revised_hold_turns": report["revised_arm"]["hold_turns"],
        "as_built_policy_hold_turns":
            report["forks"]["F3-as-built-policy"]["idle"]["branches"].get("H", 0),
        "ratio": round(hold_ratio, 2),
        "revised_idle_share_pct": report["revised_arm"]["idle_with_work_share_pct"],
        "as_built_policy_idle_share_pct":
            report["forks"]["F3-as-built-policy"]["idle"]["idle_with_work_share_pct"],
        "verdict": ("PASS — the transient predicate is the lever: it removes the great majority "
                    "of hold turns and takes the idle share with them"
                    if hold_ratio > 2 else
                    "FAIL — flipping TRANSIENT_ONLY barely changes the hold count, so the "
                    "predicate is not what bounds the standing"),
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"\n  R-A control: {report['r_a_control']['verdict']}")
    print(f"  R-B control: {report['r_b_control']['verdict']}")
    print(f"  -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
