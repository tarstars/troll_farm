#!/usr/bin/env python3
"""Read a collected package of ladder games for the opening-solver question: when did our bot
actually buy its second and third troll against the real field, and did it pay?

The referee's own event tooltips carry every training with its turn ("$<seat> trained a unit"),
so the roster timeline needs no board reconstruction. Facts only, no verdict.

    python3 ladder_read_trolls.py <package.jsonl.gz> <our agent id> [label]
"""
import gzip, json, sys, statistics as st
from collections import Counter


def read(path, agent_id):
    games = []
    with gzip.open(path, "rt") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            seat = next((a["index"] for a in d["agents"] if a["agentId"] == agent_id), None)
            if seat is None:
                continue
            trains = sorted(
                t["turn"] for t in (json.loads(x) if isinstance(x, str) else x for x in d["tooltips"])
                if t.get("text", "").startswith(f"${seat} trained")
            )
            opp_seat = 1 - seat
            opp_trains = sorted(
                t["turn"] for t in (json.loads(x) if isinstance(x, str) else x for x in d["tooltips"])
                if t.get("text", "").startswith(f"${opp_seat} trained")
            )
            games.append({
                "seat": seat,
                "trains": trains,
                "opp_trains": opp_trains,
                "own_score": d["scores"][seat],
                "opp_score": d["scores"][opp_seat],
                "rank": d["ranks"][seat],
                "opponent": next(a["agentId"] for a in d["agents"] if a["index"] == opp_seat),
            })
    return games


def med(xs):
    return round(st.median(xs), 1) if xs else None


def main():
    path, agent_id = sys.argv[1], int(sys.argv[2])
    label = sys.argv[3] if len(sys.argv) > 3 else path
    g = read(path, agent_id)
    n = len(g)
    print(f"=== {label}   agent {agent_id}   {n} games")
    if not n:
        return

    wins = sum(1 for x in g if x["rank"] == 0)
    ties = sum(1 for x in g if x["own_score"] == x["opp_score"])
    print(f"  wins {wins}/{n} = {wins/n:.3f}   ties {ties}")
    print(f"  own score  median {med([x['own_score'] for x in g])}  mean {round(st.mean([x['own_score'] for x in g]),1)}")
    print(f"  opp score  median {med([x['opp_score'] for x in g])}  mean {round(st.mean([x['opp_score'] for x in g]),1)}")

    roster = Counter(len(x["trains"]) + 1 for x in g)      # we start with one troll
    print("  final roster size (trolls owned):",
          "  ".join(f"{k}:{v} ({v/n:.0%})" for k, v in sorted(roster.items())))

    second = [x["trains"][0] for x in g if len(x["trains"]) >= 1]
    third = [x["trains"][1] for x in g if len(x["trains"]) >= 2]
    print(f"  a SECOND troll in {len(second)}/{n} = {len(second)/n:.0%}   median turn {med(second)}"
          + (f"   quartiles {sorted(second)[len(second)//4]} / {med(second)} / {sorted(second)[3*len(second)//4]}" if second else ""))
    print(f"  a THIRD  troll in {len(third)}/{n} = {len(third)/n:.0%}   median turn {med(third)}"
          + (f"   quartiles {sorted(third)[len(third)//4]} / {med(third)} / {sorted(third)[3*len(third)//4]}" if third else ""))

    opp_third = [x["opp_trains"][1] for x in g if len(x["opp_trains"]) >= 2]
    print(f"  the OPPONENTS' third troll: in {len(opp_third)}/{n} = {len(opp_third)/n:.0%}   median turn {med(opp_third)}")

    if third:
        early = [x for x in g if len(x["trains"]) >= 2 and x["trains"][1] <= (med(third) or 0)]
        late = [x for x in g if len(x["trains"]) >= 2 and x["trains"][1] > (med(third) or 0)]
        for name, s in (("third troll at or before the median turn", early),
                        ("third troll after the median turn", late)):
            if s:
                w = sum(1 for x in s if x["rank"] == 0)
                print(f"    {name}: {len(s)} games, wins {w}/{len(s)} = {w/len(s):.3f}, "
                      f"own score mean {round(st.mean([x['own_score'] for x in s]),1)}")


if __name__ == "__main__":
    main()
