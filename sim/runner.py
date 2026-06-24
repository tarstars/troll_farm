"""Offline harness: play our bot vs the league-2 boss and measure win-rate.

FIDELITY WARNING — the win-rate here is NOT yet a trustworthy proxy for the real
CodinGame arena:
  * The boss port (sim/boss.py) omits the real boss's PLANT behaviour and uses
    Manhattan targeting with no ripeness prediction, so it is materially weaker
    than the arena boss and cannot punish our bot's mistakes.
  * next_cell breaks equidistant ties deterministically (smallest (x,y)) while the
    referee is random, so own-troll movement/blocking is only loosely validated
    here; the random-tie-break move "deadlock" seen in the arena cannot arise in
    this deterministic sim.
Strengthen the boss and add a seedable random tie-break mode before trusting the number.
"""

import argparse
from bot.main import decide, PARAMS
from sim.engine import step, recompute_scores
from sim.views import build_view
from sim.boss import boss_decide
from sim.mapgen import generate


def play_game(game, params, max_turns=300, log=None):
    for _ in range(max_turns):
        ours = decide(build_view(game, 0), params)
        theirs = boss_decide(game, 1)
        if log is not None:
            log.append((game.turn, [{"id": u.id, "pos": u.pos, "carry": list(u.carry)}
                                    for u in game.units if u.player == 0]))
        step(game, ours, theirs)
    recompute_scores(game)
    return game.scores[0], game.scores[1]


def win_rate(seeds, params=None):
    params = params or PARAMS
    seeds = list(seeds)
    wins = 0
    margin = 0
    for s in seeds:
        ours, boss = play_game(generate(s), params)
        margin += ours - boss
        if ours > boss:
            wins += 1
    n = len(seeds)
    return {"wins": wins, "games": n, "win_rate": wins / n if n else 0.0,
            "avg_margin": margin / n if n else 0.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    print(win_rate(range(args.seed, args.seed + args.games)))


if __name__ == "__main__":
    main()
