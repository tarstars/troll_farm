"""Reproduce the page's ablation table (§4) from ablation.json alone -- NOT re-running ablate.py's
mp.Pool search. ablate.py's own summary print (lines 72-76) only gives median/mean/n; the page
additionally reports 'costs anything on N of 51' and 'worst', which are not printed by ablate.py,
so they are computed here directly from the same JSON."""
import json
import statistics

ABLATION = "/tmp/claude-1001/-home-tarstars-prj-troll-farm/ffb31f30-1b59-4b2c-a314-45d19f2fbb61/scratchpad/solver-verify/claude_1/opening-solver/ablation.json"


def pct(xs, q):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    return xs[min(len(xs) - 1, int(q * len(xs)))]


def main():
    rows = json.load(open(ABLATION))
    print(f"n rows (map-seats): {len(rows)}")

    for v in ("late_second", "no_water", "carry_one", "near_only"):
        costs = [r[v] - r["optimal"] for r in rows if r[v] is not None and r["optimal"] is not None]
        n_present = len(costs)
        n_positive = sum(1 for c in costs if c > 0)
        worst = max(costs) if costs else None
        med = statistics.median(costs) if costs else None
        mean = statistics.mean(costs) if costs else None
        print(f"{v:>12}: n_present {n_present}  median {med}  mean {mean:.2f}  "
              f"costs anything on {n_positive} of {n_present}  worst {worst}")

    # late_second restricted to the map-seats where orchard6 bought its second troll late
    # (i.e. not turn 1) -- the page's "0 overall; 7 on the 30 map-seats where orchard6 bought late"
    late_rows = [r for r in rows if r["orchard6_second"] != 1]
    turn1_rows = [r for r in rows if r["orchard6_second"] == 1]
    print(f"\norchard6_second == 1 on {len(turn1_rows)} of {len(rows)} map-seats "
          f"(bought late on the other {len(late_rows)})")
    late_costs = [r["late_second"] - r["optimal"] for r in late_rows
                  if r["late_second"] is not None and r["optimal"] is not None]
    print(f"late_second cost restricted to those {len(late_rows)} map-seats: "
          f"median {statistics.median(late_costs)}  mean {statistics.mean(late_costs):.2f}  n {len(late_costs)}")

    # sum of the four means, vs the mean gap orchard6_third - optimal
    means = {}
    for v in ("late_second", "no_water", "carry_one", "near_only"):
        costs = [r[v] - r["optimal"] for r in rows if r[v] is not None and r["optimal"] is not None]
        means[v] = statistics.mean(costs)
    total_mean = sum(means.values())
    print(f"\nfour means: {means}")
    print(f"sum of four means: {total_mean:.1f}")

    gaps = [r["orchard6_third"] - r["optimal"] for r in rows if r["optimal"] is not None]
    print(f"mean gap (orchard6_third - optimal): {statistics.mean(gaps):.1f}  "
          f"median {statistics.median(gaps)}  p25 {pct(gaps,0.25)} p75 {pct(gaps,0.75)}  n {len(gaps)}")


if __name__ == "__main__":
    main()
