"""Independent check of the §3 verb-order-medians claims on the page, which report.py (as
extracted at this commit) does NOT print. Computed directly from the schedules/ JSON (free
variant, all 400 map-seats), the same source report.py itself reads."""
import glob
import json
import os
import statistics
from collections import Counter

SCHED_DIR = "/tmp/claude-1001/-home-tarstars-prj-troll-farm/ffb31f30-1b59-4b2c-a314-45d19f2fbb61/scratchpad/solver-verify/claude_1/opening-solver/schedules"
SUMMARY = "/tmp/claude-1001/-home-tarstars-prj-troll-farm/ffb31f30-1b59-4b2c-a314-45d19f2fbb61/scratchpad/solver-verify/claude_1/opening-solver/panel-summary.json"


def med(xs):
    return statistics.median(xs) if xs else None


def main():
    summ = json.load(open(SUMMARY))
    rows = summ["rows"]

    # -- "turn 1 TRAIN on 314 of 400 map-seats ... on the other 86 ... turns 14-38" --
    second_turns = [r["free_second_turn"] for r in rows if r.get("free_done")]
    n_turn1 = sum(1 for t in second_turns if t == 1)
    others = sorted(t for t in second_turns if t != 1)
    print(f"free_second_turn == 1: {n_turn1} of {len(second_turns)}")
    print(f"  the other {len(others)}: min {min(others)} max {max(others)}")

    # -- first-occurrence turn of PICK / PLANT / HARVEST / MINE, and counts per schedule,
    #    scanned directly from the free variant's raw commands (400 schedules) --
    first_pick, first_plant, first_harvest, first_mine = [], [], [], []
    n_pick_ever = n_plant_ever = n_harvest_ever = n_mine_ever = 0
    harvest_counts, mine_counts = [], []
    verb_totals = Counter()
    n_sched = 0
    files = sorted(glob.glob(os.path.join(SCHED_DIR, "*.json")))
    for fn in files:
        d = json.load(open(fn))
        if "free" not in d["solves"] or not d["solves"]["free"].get("done"):
            continue
        commands = d["solves"]["free"]["commands"]
        n_sched += 1
        fp = fpl = fh = fm = None
        h_count = m_count = 0
        for t, line in enumerate(commands, start=1):
            for c in line:
                verb = c.split()[0]
                verb_totals[verb] += 1
                if verb == "PICK" and fp is None:
                    fp = t
                if verb == "PLANT" and fpl is None:
                    fpl = t
                if verb == "HARVEST":
                    h_count += 1
                    if fh is None:
                        fh = t
                if verb == "MINE":
                    m_count += 1
                    if fm is None:
                        fm = t
        if fp is not None:
            first_pick.append(fp)
            n_pick_ever += 1
        if fpl is not None:
            first_plant.append(fpl)
            n_plant_ever += 1
        if fh is not None:
            first_harvest.append(fh)
            n_harvest_ever += 1
        if fm is not None:
            first_mine.append(fm)
            n_mine_ever += 1
        harvest_counts.append(h_count)
        mine_counts.append(m_count)

    print(f"\nscanned {n_sched} free schedules")
    print(f"first PICK: median {med(first_pick)} (present in {n_pick_ever}/{n_sched})")
    print(f"first PLANT: median {med(first_plant)} (present in {n_plant_ever}/{n_sched})")
    print(f"first HARVEST: median {med(first_harvest)} (present in {n_harvest_ever}/{n_sched})")
    print(f"first MINE: median {med(first_mine)} (present in {n_mine_ever}/{n_sched})")
    print(f"\nHARVEST count per schedule: median {med(harvest_counts)}")
    print(f"MINE count per schedule: median {med(mine_counts)}")
    tot = sum(verb_totals.values())
    print(f"\nverb totals over {n_sched} free schedules: " +
          ", ".join(f"{k} {100*v/tot:.0f}% ({v})" for k, v in verb_totals.most_common()))

    # cross-check against report.py's own verb-mix line (should match exactly -- same source)
    print(f"\n(cross-check) WAIT % = {100*verb_totals.get('WAIT',0)/tot:.1f}  MOVE % = {100*verb_totals.get('MOVE',0)/tot:.1f}")


if __name__ == "__main__":
    main()
