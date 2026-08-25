#!/usr/bin/env python3
"""The charter's POISON ARM — and, after the ruling of 2026-08-25T09:42:00Z, the control for the
control.

The charter asks for "a poison arm that holds on **every** blocked step forever (must be caught by
the P4 gate)". The as-built round answered the second half in the negative and the coordinator
ruled on it: **P4 is BLIND for this family** (`fuzz_panel.progress_turns` is game-level, so one
parked troll beside a working teammate is invisible), its clause is VOID as a safety net, and the
replacement net is the per-troll idle-with-work share with a line at 1.5 % fixed before this arm's
numbers existed. Disposition 4(c): *the poison arm must be caught by it*.

So the poison arm is graded by `idle_share.py` now, and P4's number is recorded only as the
evidence that it stays blind — never as a pass.

Two poison variants, because the revision changed what "holds on every blocked step" can mean:

  P-A  `HOLD_WINDOW=255` **and** `TRANSIENT_ONLY=false`  — the charter's bot literally: it holds on
       every blocked step, transient or permanent, and the counter can never reach the bound. This
       is the graded poison.
  P-B  `HOLD_WINDOW=255` with `TRANSIENT_ONLY=true` — the revised arm's own scoping with the bound
       removed. It prices what R-A alone is worth: if the transient predicate bounds the standing
       by itself, this variant cannot park a troll even with W unbounded.

Neither is a candidate; neither is in `arm-manifest.json`; neither may ever be submitted.

    python3 claude_1/cure1/poison_arm.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
OUT = HERE / "results" / "poison-arm.json"
LINE = 1.5

W_ON = "            const HOLD_WINDOW:u8=2;"
W_OFF = "            const HOLD_WINDOW:u8=255;"
TRANSIENT_ON = "            const TRANSIENT_ONLY:bool=true;"
TRANSIENT_OFF = "            const TRANSIENT_ONLY:bool=false;"

VARIANTS = {
    "P-A": {"transient": False, "graded": True,
            "what": "the charter's poison: holds on EVERY blocked step forever (W=255, R-A off)"},
    "P-B": {"transient": True, "graded": False,
            "what": "W=255 with R-A still on: what the transient predicate is worth alone"},
}


def poison_text(arm: str, transient: bool) -> str:
    text = (HERE / f"arm-{arm}.rs").read_text()
    for anchor, replacement, apply in ((W_ON, W_OFF, True),
                                       (TRANSIENT_ON, TRANSIENT_OFF, not transient)):
        if text.count(anchor) != 1:
            raise SystemExit(f"REFUSED: {anchor!r} occurs {text.count(anchor)} times in arm-{arm}")
        if apply:
            text = text.replace(anchor, replacement)
    return text


def run_panel(tag: str, source: Path, sha: str, arm: str, games: str, what: str) -> dict:
    cfg = json.loads((HERE / f"cure1-{arm}-config.json").read_text())
    cfg["task"] = f"20260825-dance-cure-candidate-1-hold POISON {tag} ({arm}) — NOT a candidate"
    cfg["candidate"] = {"crate": f"cure1_poison_{tag.replace('-', '_').lower()}_{arm}",
                        "sha256": sha, "source": f"../../{source.relative_to(REPO)}"}
    cfg["games_dir"] = games
    cfg["notes"] = [f"POISON ARM {tag}: {what}. Never a candidate, never in arm-manifest.json, "
                    "never submitted.", cfg["notes"][1]]
    path = HERE / f"cure1-poison-{tag.lower()}-{arm}-config.json"
    path.write_text(json.dumps(cfg, indent=2, sort_keys=True) + "\n")
    done = subprocess.run(
        [sys.executable, str(REPO / "claude_1/pipeline/fuzz_panel.py"), "--config", str(path),
         "--report", str(HERE / "results" / f"panel-poison-{tag.lower()}-{arm}.md"),
         "--json", str(HERE / "results" / f"panel-poison-{tag.lower()}-{arm}.json")],
        capture_output=True, text=True, timeout=3600)
    print(f"    {tag} {arm}: " + (done.stdout.strip().split("\n")[-1] if done.stdout.strip()
                                  else done.stderr[-300:]))
    return json.loads((HERE / "results" / f"panel-poison-{tag.lower()}-{arm}.json").read_text())


def p4_violations(panel: dict) -> int:
    return sum(1 for g in panel["games"]
               if any(v["property"] == "P4" for v in g["violations"]))


def main() -> int:
    revised = json.loads((HERE / "results" / "idle-share.json").read_text())
    revised_share = revised["arms"]["candidate (rule-on)"]["idle_with_work_share_pct"]
    base_share = revised["arms"]["base (rule-off)"]["idle_with_work_share_pct"]
    base_p4 = p4_violations(json.loads((HERE / "results" / "panel-floor.json").read_text()))

    report = {
        "control": "poison arm — the control for the control (ruling 20260825T094200Z, "
                   "disposition 4c)",
        "graded_by": "per-troll idle-with-work share <= 1.5 % (idle_share.py). P4 is VOID for "
                     "this family and its number is recorded only as evidence that it stays blind.",
        "line_pct": LINE,
        "base_idle_share_pct": base_share,
        "revised_arm_idle_share_pct": revised_share,
        "base_p4_violations": base_p4,
        "variants": {},
    }
    for tag, spec in VARIANTS.items():
        entry = {"what": spec["what"], "graded": spec["graded"], "arms": {}}
        for arm in ("candidate", "instrument"):
            text = poison_text(arm, spec["transient"])
            sha = hashlib.sha256(text.encode()).hexdigest()
            path = HERE / f"poison-{tag.lower()}-{arm}.rs"
            path.write_text(text)
            games = f"/tmp/claude-1000/cure1/poison-{tag.lower()}-{arm}/games"
            panel = run_panel(tag, path, sha, arm, games, spec["what"])
            entry["arms"][arm] = {"source": str(path.relative_to(REPO)), "sha256": sha,
                                  "games_archive": f"{games}/games.jsonl.gz",
                                  "blocking_games": panel["stats"]["blocking_games"],
                                  "p4_violations": p4_violations(panel)}
        idle = subprocess.run(
            [sys.executable, str(HERE / "idle_share.py"),
             "--arm", f"poison {tag}=/tmp/claude-1000/cure1/poison-{tag.lower()}-instrument/"
                      "games/games.jsonl.gz",
             "--json", str(HERE / "results" / f"idle-share-poison-{tag.lower()}.json")],
            capture_output=True, text=True, timeout=1800)
        print("  " + (idle.stdout.strip().split("\n")[0] if idle.stdout.strip()
                      else idle.stderr[-300:]))
        row = json.loads((HERE / "results" / f"idle-share-poison-{tag.lower()}.json").read_text()
                         )["arms"][f"poison {tag}"]
        entry["idle_with_work_share_pct"] = row["idle_with_work_share_pct"]
        entry["hold_turns"] = row["branches"].get("H", 0)
        entry["longest_consecutive_hold_run"] = row["longest_consecutive_hold_run"]
        entry["worst_troll"] = row["worst_troll"]
        entry["caught_by_the_idle_clause"] = row["idle_with_work_share_pct"] > LINE
        entry["p4_still_blind"] = (
            entry["arms"]["candidate"]["p4_violations"] <= base_p4
            and row["longest_consecutive_hold_run"] >= 60)
        report["variants"][tag] = entry

    pa = report["variants"]["P-A"]
    caught = pa["caught_by_the_idle_clause"]
    report["caught"] = caught
    report["verdict"] = (
        "PASS — the charter's poison arm is CAUGHT by the clause that replaced P4: idle-with-work "
        "%.4f %% against the %.1f %% line, longest consecutive hold run %d turns."
        % (pa["idle_with_work_share_pct"], LINE, pa["longest_consecutive_hold_run"])
        if caught else
        "FAIL — the replacement safety net does not catch a bot designed to park a troll, so no "
        "green from it licenses the revised arm either.")
    report["p4_blindness_reconfirmed"] = pa["p4_still_blind"]
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"\n  {report['verdict']}")
    print(f"  P4 on the same poison run: {pa['arms']['candidate']['p4_violations']} against the "
          f"base's {base_p4} — blindness reconfirmed: {pa['p4_still_blind']}")
    print(f"  -> {OUT}")
    return 0 if caught else 1


if __name__ == "__main__":
    sys.exit(main())
