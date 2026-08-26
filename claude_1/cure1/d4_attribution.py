#!/usr/bin/env python3
"""Why D-4 grew from 10 episodes to 102 — attribution, before anybody calls it a surprise.

The named-cost table (`panel_costs.py`) reports one detector total that GREW: **D-4, 10 -> 102**,
against D-1 falling 27 -> 1. D-4 is `trace_detectors.detect_d4`, *Abandoned carried-wood return*:
inside a wood-committed interval, **two consecutive turns with no decrease of the unit's distance
to a bank door** and no cargo loss is an episode. Its own docstring says the threshold is two
turns because "1 turn of slack absorbs resolver displacement".

A hold is, by construction, a turn on which the unit does not move. So the first guess is that
`W = 2` spends exactly the slack D-4 does not have. That guess is CHECKED here rather than
asserted: every D-4 episode in the candidate arm is matched against the instrument arm's `r=H`
turns for the same unit (the two arms are proved to play the same game by `arm_equivalence.py`),
and the episode windows and their hold counts are histogrammed.

What the check says: every one of the 102 candidate episodes is exactly three turns long, and 96
of them contain exactly two hold turns for the episode's own unit. The growth is the hold rule's,
by the rule's own telemetry.

**And the obvious repair does not work.** `diagnostic_w1.py` prices `W = 1` on the same corpus:
D-4 goes to **132**, higher than `W = 2`'s 102, because a single hold followed by one
non-approaching turn trips the same two-turn threshold and shorter holds recur more often. So the
cost is not the size of `W`; it is that D-4 treats *standing still inside a wood-committed
interval* as abandoning the return, and the cure's whole idea is to stand still. Whether that
detector reading is right for a bot that may deliberately wait is a DESIGN question for the
coordinator and codex_1, not a repair for me to make inside a chartered build.

    python3 claude_1/cure1/d4_attribution.py
"""
from __future__ import annotations

import collections
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "narrate4"))
sys.path.insert(0, str(REPO / "claude_1" / "banana-restoration-r2"))
import narrate4 as n4               # noqa: E402
import trace_detectors as td        # noqa: E402

CAND = Path("/tmp/claude-1000/cure1/cure1-candidate/games/games.jsonl.gz")
INST = Path("/tmp/claude-1000/cure1/cure1-instrument/games/games.jsonl.gz")
FLOOR = Path("/tmp/claude-1000/cure1/cure1-floor/games/games.jsonl.gz")
OUT = HERE / "results" / "d4-attribution.json"


def load(path):
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return {(g["map_id"], g["seat"]): g for g in (json.loads(l) for l in fh)}


def d4_episodes(game, arm="candidate"):
    tr = td.build_trace(game["artifacts"][f"{arm}_transcript"],
                        game["artifacts"][f"{arm}_commands"])
    return td.detect_d4(tr)["episodes"]


def hold_turns(game):
    """{unit_id: {turn, ...}} taken from the instrument arm's own telemetry."""
    out = collections.defaultdict(set)
    for index, line in enumerate(game["artifacts"]["candidate_commands"].rstrip("\n").split("\n"),
                                 1):
        frags = n4.msg_fragments(line)
        if not frags:
            continue
        _, units, _, _, _ = n4.decode(frags[0].strip())
        for uid, (_, _, branch, _) in units.items():
            if branch == "H":
                out[uid].add(index)
    return out


def window(ep):
    """An episode's turn span. detect_d4 emits `unit`, `kind`, `turn_start`, `turn_end`; the keys
    are read explicitly and a missing one raises rather than defaulting to something plausible."""
    return int(ep["turn_start"]), int(ep["turn_end"])


def main() -> int:
    cand, inst, floor = load(CAND), load(INST), load(FLOOR)
    rows = []
    totals = collections.Counter()
    holds_in_window = collections.Counter()
    episode_lengths = collections.Counter()
    sample_ep = None
    for key in sorted(cand):
        base_eps = d4_episodes(floor[key])
        cand_eps = d4_episodes(cand[key])
        if not base_eps and not cand_eps:
            continue
        holds = hold_turns(inst[key])
        matched = 0
        for ep in cand_eps:
            if sample_ep is None:
                sample_ep = {"map_id": key[0], "seat": key[1], "episode": ep}
            uid = ep["unit"]
            a, b = window(ep)
            in_window = sum(1 for t in range(a, b + 1) if t in holds.get(uid, ()))
            holds_in_window[in_window] += 1
            episode_lengths[b - a + 1] += 1
            if in_window:
                matched += 1
        totals["base_episodes"] += len(base_eps)
        totals["candidate_episodes"] += len(cand_eps)
        totals["candidate_episodes_containing_a_hold"] += matched
        rows.append({"map_id": key[0], "seat": key[1],
                     "base_d4": len(base_eps), "candidate_d4": len(cand_eps),
                     "candidate_d4_containing_a_hold": matched,
                     "hold_turns_in_game": sum(len(v) for v in holds.values())})
    share = (totals["candidate_episodes_containing_a_hold"]
             / totals["candidate_episodes"]) if totals["candidate_episodes"] else 0.0
    report = {
        "question": "does the D-4 growth 10 -> 102 sit on the hold rule's own turns?",
        "task": "20260825-dance-cure-candidate-1-hold",
        "detector": "D-4 abandoned carried-wood return: 2 consecutive turns without decreasing "
                    "door distance inside a wood-committed interval "
                    "(trace_detectors.detect_d4; its slack is ONE turn)",
        "mechanism": "the growth is the hold rule's own turns: see holds_in_window and "
                     "episode_lengths. Lowering W does NOT relieve it -- the W=1 diagnostic "
                     "reports 132 D-4 episodes against W=2's 102 -- because a single hold plus "
                     "one non-approaching turn trips the same two-turn threshold. D-4 reads "
                     "standing still inside a wood-committed interval as abandoning the return.",
        "w1_diagnostic": "claude_1/cure1/results/panel-named-costs-diag-w1.json: D-4 10 -> 132, "
                         "blocking 43 -> 40, de-novo blocks 3, P3 new 1",
        "holds_in_window": dict(sorted(holds_in_window.items())),
        "episode_lengths": dict(sorted(episode_lengths.items())),
        "totals": dict(totals),
        "share_of_candidate_episodes_containing_a_hold": round(share, 4),
        "sample_episode": sample_ep,
        "arms_play_the_same_game": "claude_1/cure1/results/arm-equivalence.json (240/240)",
        "not_decided_here": "whether D-4's reading is right for a bot that may deliberately "
                            "wait, or whether the candidate is rejected on it. That is the "
                            "coordinator's and codex_1's, not the builder's. W = 1 is priced "
                            "above and is WORSE on this axis, so it is not a way out.",
        "rows": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"  D-4 episodes: base {totals['base_episodes']} -> candidate "
          f"{totals['candidate_episodes']}")
    print(f"  candidate episodes containing a hold turn for the same unit: "
          f"{totals['candidate_episodes_containing_a_hold']} ({share:.1%})")
    print(f"  -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
