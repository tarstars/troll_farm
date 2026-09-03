"""Read the panel run (panel-summary.json + schedules/) into the numbers the one page needs."""
from __future__ import annotations

import json
import os
import statistics
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def pct(xs, q):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    return xs[min(len(xs) - 1, int(q * len(xs)))]


def walk_stats(commands, trains):
    """Per-troll verb mix of a schedule and the items per trip (from DROP counts and HARVEST/MINE)."""
    verbs = Counter()
    for line in commands:
        for c in line:
            verbs[c.split()[0]] += 1
    return verbs


def main():
    summ = json.load(open(os.path.join(HERE, "panel-summary.json")))
    rows = summ["rows"]
    print(f"map-seats {len(rows)} (maps {summ['maps']}), wall {summ['wall_seconds']/60:.1f} min")
    # completion turns per variant
    for name in ("free", "chop2", "chop1", "same"):
        turns = [r.get(f"{name}_turn") for r in rows if r.get(f"{name}_done")]
        n_all = sum(1 for r in rows if f"{name}_done" in r)
        secs = [r.get(f"{name}_seconds") for r in rows if r.get(f"{name}_seconds")]
        print(f"{name:>6}: done {len(turns)}/{n_all}  third troll turn median {med(turns)}  p25 {pct(turns,0.25)} p75 {pct(turns,0.75)}  "
              f"seconds/map-seat median {med(secs):.1f}")
    o6 = [r["orchard6_third"] for r in rows if r["orchard6_third"]]
    print(f"orchard 6 on the same map-seats: third troll in {len(o6)}/{len(rows)}, median {med(o6)}")
    o6s = [r["orchard6_second"] for r in rows if r["orchard6_second"]]
    ch = [r["champion_second"] for r in rows if r["champion_second"]]
    print(f"orchard 6 second troll median {med(o6s)}; the champion's second troll median {med(ch)}; the solver's second troll median "
          f"{med([r.get('free_second_turn') for r in rows if r.get('free_done')])}")
    # the gap, same roster (the dead-on-paper test) and free
    for name in ("same", "free", "chop2", "chop1"):
        gaps = [r["orchard6_third"] - r[f"{name}_turn"] for r in rows if r.get(f"{name}_done") and r["orchard6_third"]]
        if gaps:
            print(f"gap orchard6 - solver ({name}): n {len(gaps)} median {med(gaps)} p25 {pct(gaps,0.25)} p75 {pct(gaps,0.75)}  "
                  f"solver earlier by >10 turns in {sum(1 for g in gaps if g > 10)} ({100*sum(1 for g in gaps if g > 10)/len(gaps):.0f} %), "
                  f"solver later in {sum(1 for g in gaps if g < 0)}")
    # the P curve
    print("\nthe time-versus-chop curve (third troll's chop 1 / 2 / 3), medians over map-seats solved for all three:")
    trip = [r for r in rows if all(r.get(f"{n}_done") for n in ("chop1", "chop2", "free"))]
    print(f"  n {len(trip)}: chop1 {med([r['chop1_turn'] for r in trip])}  chop2 {med([r['chop2_turn'] for r in trip])}  chop3 {med([r['free_turn'] for r in trip])}")
    print(f"  bank at completion (points + own standing wood): chop1 {med([r['chop1_bank'] for r in trip])} chop2 {med([r['chop2_bank'] for r in trip])} chop3 {med([r['free_bank'] for r in trip])}")
    # the second troll the solver picks
    t2 = Counter(tuple(r["free_second_talents"]) for r in rows if r.get("free_done"))
    print("\nthe solver's second troll (free, chop-3 roster):", t2.most_common(8))
    t2c = Counter(tuple(r["chop2_second_talents"]) for r in rows if r.get("chop2_done"))
    print("the solver's second troll (chop-2 roster):", t2c.most_common(8))
    # seeds and verbs from the schedules
    seeds = Counter()
    verbs = Counter()
    n_sched = 0
    first = {v: [] for v in ("PICK", "PLANT", "HARVEST", "MINE")}   # first turn each verb appears, per schedule
    per_sched = {v: [] for v in ("HARVEST", "MINE")}                # count of the verb per schedule
    for r in rows:
        if not r.get("free_done"):
            continue
        p = os.path.join(HERE, "schedules", f"{r['map_hash']}-s{r['seat']}.json")
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        sol = d["solves"]["free"]
        seeds[tuple((k, m) for k, m in sol["plan"]["seeds"])] += 1
        verbs.update(walk_stats(sol["commands"], sol["trains"]))
        n_sched += 1
        seen_first = {}
        counts = Counter()
        for t, line in enumerate(sol["commands"], start=1):
            for c in line:
                verb = c.split()[0]
                seen_first.setdefault(verb, t)
                counts[verb] += 1
        for v in first:
            if v in seen_first:
                first[v].append(seen_first[v])
        for v in per_sched:
            per_sched[v].append(counts[v])
    print("\nseed programmes chosen (free):", seeds.most_common(6))
    tot = sum(verbs.values())
    print(f"verb mix over {n_sched} free schedules (all trolls, turns to completion): " +
          ", ".join(f"{k} {100*v/tot:.0f}%" for k, v in verbs.most_common()))
    # the §3 verb-order table: the median first turn of each verb, and how many schedules use it at all
    second = [r["free_second_turn"] for r in rows if r.get("free_done")]
    others = sorted(t for t in second if t != 1)
    print(f"\nthe order of the opening (free, {n_sched} schedules):")
    print(f"  second troll TRAINed on turn 1 in {sum(1 for t in second if t == 1)} of {len(second)}; "
          f"the rest at turns {others[0] if others else '-'}–{others[-1] if others else '-'} "
          f"(middle half {pct(others, 0.25)}–{pct(others, 0.75)})")
    for v in ("PICK", "PLANT", "HARVEST", "MINE"):
        print(f"  first {v:<8} median turn {med(first[v])}  (appears in {len(first[v])} of {n_sched})")
    print(f"  per schedule: HARVEST median {med(per_sched['HARVEST'])}, MINE median {med(per_sched['MINE'])}")


if __name__ == "__main__":
    main()
