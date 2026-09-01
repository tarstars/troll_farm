#!/usr/bin/env python3
"""Finding 1 of the review: test CHAMPION-BEHAVIOUR.md section 4's substitute train rule
against the 160 recordings.

The rule as written: 'wait until the best affordable worker (harvest 0, largest
ms+cc+chop) has ms+cc+chop >= 5, then buy it; buy unconditionally by turn 35'.
Reports how often the rule buys on the champion's turn and bundle, and by how much
it is early or late when it does not.  Thresholds 4 and 6 are run for comparison.

Reviewer's instrument (local_claude_1, 2026-09-01); not part of the package.
"""
import collections
import itertools
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "cleanroom", "spec-work"))
import corpus  # noqa: E402

PLUM, LEMON, APPLE, BANANA, IRON, WOOD = range(6)


def affordable(inv, has_iron, ms, cc, chop, n=1):
    cost = (n + ms * ms, n + cc * cc, n + 0, n + chop * chop)
    if inv[PLUM] < cost[0] or inv[LEMON] < cost[1] or inv[APPLE] < cost[2]:
        return False
    return (not has_iron) or inv[IRON] >= cost[3]


def best_affordable(inv, has_iron):
    best = None
    for ms, cc, chop in itertools.product((1, 2, 3), repeat=3):
        if affordable(inv, has_iron, ms, cc, chop):
            key = (ms + cc + chop, ms, cc, chop)
            if best is None or key > best:
                best = key
    return best


def run(threshold, deadline, games):
    same_turn = both = 0
    turn_diff = collections.Counter()
    examples = []
    for g in games:
        seat = g["seat"]
        has_iron = any("+" in row for row in g["rows"])
        actual_turn = actual_bundle = None
        for t, cmds in enumerate(g["commands"]):
            for verb, args in cmds:
                if verb == "TRAIN":
                    actual_turn, actual_bundle = t + 1, tuple(args)
                    break
            if actual_turn:
                break
        rule_turn = rule_bundle = None
        for t in range(g["turns"]):
            inv = g["states"][t]["inventories"][seat]
            best = best_affordable(inv, has_iron)
            if best and (best[0] >= threshold or t + 1 >= deadline):
                rule_turn, rule_bundle = t + 1, (best[1], best[2], 0, best[3])
                break
        if rule_turn == actual_turn:
            same_turn += 1
            both += rule_bundle == actual_bundle
        turn_diff[(rule_turn or 0) - (actual_turn or 0)] += 1
        if rule_turn != actual_turn and len(examples) < 6:
            examples.append((g["game_id"], "champion", actual_turn, actual_bundle, "rule", rule_turn, rule_bundle))
    misses = sorted(d for d, n in turn_diff.items() if d != 0 for _ in range(n))
    print("threshold %d, deadline %d: same turn %d of %d (same bundle too: %d); when the rule misses, "
          "rule turn minus champion turn: median %s, min %s, max %s"
          % (threshold, deadline, same_turn, len(games), both,
             misses[len(misses) // 2] if misses else "-", min(misses) if misses else "-",
             max(misses) if misses else "-"))
    for e in examples:
        print("   ", e)


def main():
    games = list(corpus.games())
    for thr in (4, 5, 6):
        run(thr, 35, games)
    # the max-sum bundle is unique whenever it exists: each talent's price draws on its own resource
    ties = collections.Counter()
    for g in games:
        seat, has_iron = g["seat"], any("+" in r for r in g["rows"])
        for t, cmds in enumerate(g["commands"]):
            if any(v == "TRAIN" for v, _ in cmds):
                inv = g["states"][t]["inventories"][seat]
                aff = [z for z in itertools.product((1, 2, 3), repeat=3) if affordable(inv, has_iron, *z)]
                top = max(sum(z) for z in aff)
                ties[sum(1 for z in aff if sum(z) == top)] += 1
                break
    print("size of the max-sum tie set at the 160 purchases:", dict(ties))


if __name__ == "__main__":
    main()
