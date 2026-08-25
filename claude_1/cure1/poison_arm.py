#!/usr/bin/env python3
"""The charter's POISON ARM: a fork that holds on every blocked step, forever.

The charter asks for "a poison arm that holds on **every** blocked step forever (must be caught by
the P4 gate)". A gate that never fails on a bot designed to stall is inert, and the candidate's
own green means nothing until this red is observed.

The fork is `arm-candidate.rs` with `HOLD_WINDOW` raised to `u8::MAX`, so the counter can never
reach the bound and the regressive detour is never taken. It is written to `poison-hold-forever.rs`
and excluded from `arm-manifest.json`. It is not a candidate and must never be submitted.

PASS means the poison arm is CAUGHT — it must block on more games than the candidate and its P4
violations must exceed the base's. A poison arm that sails through would mean the panel cannot see
a parked troll, and then the candidate's own result would have to be thrown away too.

**And a NOT-CAUGHT has two possible causes, which this control separates rather than conflating.**
Either the gate is blind to a parked troll, or the corpus never presents a block long enough to
park one — a troll that holds "forever" against a blocker that moves after two turns is not
parked at all. So a second poison variant is built from `arm-instrument.rs` (same W=255, plus v4
telemetry) and its longest CONSECUTIVE hold run per unit is read off the wire. A short longest run
means the corpus never sampled a permanent block, which is UNSAMPLED, not blind; a long run with
no P4 complaint would be blind.

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
SRC = HERE / "arm-candidate.rs"
POISON = HERE / "poison-hold-forever.rs"
CONFIG = HERE / "cure1-poison-config.json"
GAMES = "/tmp/claude-1000/cure1/cure1-poison/games"
OUT = HERE / "results" / "poison-arm.json"
OLD = "            const HOLD_WINDOW:u8=2;"
NEW = "            const HOLD_WINDOW:u8=255;"


def main() -> int:
    text = SRC.read_text()
    if text.count(OLD) != 1:
        print(f"REFUSED: the HOLD_WINDOW line occurs {text.count(OLD)} times")
        return 2
    poisoned = text.replace(OLD, NEW)
    POISON.write_text(poisoned)
    sha = hashlib.sha256(poisoned.encode()).hexdigest()
    print(f"  wrote {POISON.name}  sha256 {sha[:16]}  (W=255, POISON, never a candidate)")

    cfg = json.loads((HERE / "cure1-candidate-config.json").read_text())
    cfg["task"] = ("20260825-dance-cure-candidate-1-hold POISON ARM: holds on every blocked step "
                   "(W=255) vs the champion base 547fa706 — must be CAUGHT")
    cfg["candidate"] = {"crate": "cure1_poison_seat_a", "sha256": sha,
                        "source": "../../claude_1/cure1/poison-hold-forever.rs"}
    cfg["games_dir"] = GAMES
    cfg["notes"] = ["POISON ARM. The charter's live control on the P4 gate. Not chartered as a "
                    "candidate, not in arm-manifest.json, never to be submitted.", cfg["notes"][1]]
    CONFIG.write_text(json.dumps(cfg, indent=2, sort_keys=True) + "\n")

    done = subprocess.run(
        [sys.executable, str(REPO / "claude_1/pipeline/fuzz_panel.py"), "--config", str(CONFIG),
         "--report", str(HERE / "results" / "panel-poison.md"),
         "--json", str(HERE / "results" / "panel-poison.json")],
        capture_output=True, text=True, timeout=3600)
    print("  " + (done.stdout.strip().split("\n")[-1] if done.stdout.strip()
                  else done.stderr[-400:]))
    costs = subprocess.run(
        [sys.executable, str(HERE / "panel_costs.py"), "--candidate-games",
         f"{GAMES}/games.jsonl.gz", "--json",
         str(HERE / "results" / "panel-named-costs-poison.json")],
        capture_output=True, text=True, timeout=3600)
    print(costs.stdout or costs.stderr[-2000:])

    # --- the discriminator: how long does the poison arm actually hold? ---
    inst_text = (HERE / "arm-instrument.rs").read_text().replace(OLD, NEW)
    inst_path = HERE / "poison-hold-forever-instrument.rs"
    inst_path.write_text(inst_text)
    inst_sha = hashlib.sha256(inst_text.encode()).hexdigest()
    icfg = json.loads(CONFIG.read_text())
    icfg["task"] = icfg["task"] + " (telemetry variant, for the hold-run census)"
    icfg["candidate"] = {"crate": "cure1_poison_inst_seat_a", "sha256": inst_sha,
                         "source": "../../claude_1/cure1/poison-hold-forever-instrument.rs"}
    icfg["games_dir"] = GAMES + "-instrument"
    iconfig = HERE / "cure1-poison-instrument-config.json"
    iconfig.write_text(json.dumps(icfg, indent=2, sort_keys=True) + "\n")
    subprocess.run(
        [sys.executable, str(REPO / "claude_1/pipeline/fuzz_panel.py"), "--config", str(iconfig),
         "--report", str(HERE / "results" / "panel-poison-instrument.md"),
         "--json", str(HERE / "results" / "panel-poison-instrument.json")],
        capture_output=True, text=True, timeout=3600)
    sys.path.insert(0, str(REPO / "claude_1" / "narrate4"))
    import gzip                                            # noqa: E402
    import narrate4 as n4                                  # noqa: E402
    longest, hold_turns = 0, 0
    with gzip.open(f"{GAMES}-instrument/games.jsonl.gz", "rt", encoding="utf-8") as fh:
        for line in fh:
            game = json.loads(line)
            for cmdline in game["artifacts"]["candidate_commands"].rstrip("\n").split("\n"):
                frags = n4.msg_fragments(cmdline)
                if not frags:
                    continue
                _, units, _, _, _ = n4.decode(frags[0].strip())
                for _, _, branch, blocked in units.values():
                    if branch == "H":
                        hold_turns += 1
                        longest = max(longest, blocked)
    print(f"  poison telemetry: {hold_turns} hold turns, longest consecutive hold run "
          f"{longest} turns")

    poison = json.loads((HERE / "results" / "panel-named-costs-poison.json").read_text())
    cand = json.loads((HERE / "results" / "panel-named-costs.json").read_text())
    caught = (poison["blocking"]["candidate"] > cand["blocking"]["candidate"]
              and poison["p4_violations"]["candidate"] > poison["p4_violations"]["base"])
    # A hold run no longer than a couple of turns is not a parked troll, so a quiet gate on THIS
    # corpus is an unsampled state space, not a blind detector. The threshold is the P4 window.
    unsampled = longest < 60
    report = {
        "control": "poison arm — holds on every blocked step forever (W=255)",
        "task": "20260825-dance-cure-candidate-1-hold",
        "expected": "CAUGHT: more blocking games than the candidate arm, and P4 above the base",
        "observed": {
            "poison_blocking": poison["blocking"]["candidate"],
            "candidate_blocking": cand["blocking"]["candidate"],
            "base_blocking": cand["blocking"]["base"],
            "poison_p4": poison["p4_violations"]["candidate"],
            "base_p4": poison["p4_violations"]["base"],
            "poison_de_novo_blocks": len(poison["falsifiers"]["s7_3_de_novo_blocks"]),
            "poison_p4_worse_games": len(poison["falsifiers"]["s7_5_p4_worse_games"]),
            "poison_hold_turns": hold_turns,
            "longest_consecutive_hold_run": longest,
            "p4_liveness_window": 60,
        },
        "discriminator": (
            "longest consecutive hold run %d turns against the 60-turn P4 window: the corpus "
            "never presents a block long enough to park a troll, so the quiet gate is an "
            "UNSAMPLED state space, not a blind detector. A poison arm that cannot park cannot "
            "test the parking gate." % longest) if unsampled else
        ("longest consecutive hold run %d turns reaches the P4 window and P4 still did not fire: "
         "the gate is BLIND to a parked troll and no green on it can be read." % longest),
        "caught": caught,
        "verdict": ("PASS — the poison arm is caught" if caught else
                    "INCONCLUSIVE — the poison arm never parked a troll on this corpus, so the "
                    "P4 gate was never asked the question. NOT a pass: the charter's control is "
                    "UNSATISFIED and needs a corpus with a permanent block, which is a request "
                    "to the coordinator, not something I can quietly call green."
                    if unsampled else
                    "FAIL — the gate cannot see a parked troll, so the candidate's own green on "
                    "it means nothing"),
        "unsampled": unsampled,
        "sha256": sha,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"  poison arm {'CAUGHT' if caught else 'NOT CAUGHT'}: {report['observed']}")
    print(f"  verdict: {report['verdict']}")
    return 0 if caught else 1


if __name__ == "__main__":
    sys.exit(main())
