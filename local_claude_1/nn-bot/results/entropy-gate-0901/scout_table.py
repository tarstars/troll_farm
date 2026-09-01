#!/usr/bin/env python3
"""Print the scout curves of the two entropy arms as one table for the card.

Reads bench-<tag>-u<age>.json files written by bench_ages.py and prints, per age, each arm's
wins of 48 (by seat), mean scores, the paired per-cell win delta E00 − E01, and the faults.
Reviewer-facing: a scout is a ±5-win look, not a verdict (the gate is gate1.py)."""
import glob
import json
import os
import sys

BENCH_DIR = sys.argv[1] if len(sys.argv) > 1 else "/home/tarstars/nn-data/bench-0901"
OFF, ON = "e00b", "e01b"


def load(tag, age):
    path = os.path.join(BENCH_DIR, f"bench-{tag}-u{age}.json")
    if not os.path.exists(path):
        return None
    return json.load(open(path))


def cells(bench):
    return {(r["map_hash"], r["policy_seat"]): r for r in bench["rows"]}


def main():
    ages = sorted({int(os.path.basename(f).split("-u")[1].split(".")[0])
                   for f in glob.glob(os.path.join(BENCH_DIR, f"bench-{OFF}-u*.json"))})
    print("| update | E00 (entropy 0) wins/48 (seat 0 + seat 1) | E01 (entropy 0.01) wins/48 | paired E00 − E01 (cells won only by E00 − only by E01) | mean score E00 / E01 vs bot | faults |")
    print("|---|---|---|---|---|---|")
    for age in ages:
        a, b = load(OFF, age), load(ON, age)
        if a is None or b is None:
            print(f"| {age} | {'—' if a is None else a['policy_wins']} | {'—' if b is None else b['policy_wins']} | pending | | |")
            continue
        ca, cb = cells(a), cells(b)
        common = set(ca) & set(cb)
        only_a = sum(1 for c in common if ca[c]["policy_won"] and not cb[c]["policy_won"])
        only_b = sum(1 for c in common if cb[c]["policy_won"] and not ca[c]["policy_won"])
        faults = sum(x["illegal_commands_total"] + x["timeouts_total"] + x["referee_errors_total"] for x in (a, b))
        print(f"| {age} | {a['policy_wins']} ({a['policy_wins_by_seat'].get('0', 0)} + {a['policy_wins_by_seat'].get('1', 0)}) "
              f"| {b['policy_wins']} ({b['policy_wins_by_seat'].get('0', 0)} + {b['policy_wins_by_seat'].get('1', 0)}) "
              f"| {only_a - only_b:+d} ({only_a} − {only_b}) of {len(common)} cells "
              f"| {a['policy_score_mean']:.1f} / {b['policy_score_mean']:.1f} vs {a['bot_score_mean']:.1f} / {b['bot_score_mean']:.1f} | {faults} |")


if __name__ == "__main__":
    main()
