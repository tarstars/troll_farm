"""Evaluate a trained policy vs a scripted opponent on a fixed set of maps.

Reports win-rate / score margin / wood banked for the policy (greedy by default)
alongside a random-action baseline on the SAME maps, so the learning is
quantified head-to-head. Eval maps default to a HELD-OUT seed range (disjoint
from the default training pool 0..63) to check generalization.

    uv run python -m rl.evaluate --policy rl/runs/a2c_chopper/policy.npz \
        --opponent chopper --episodes 100
"""

import argparse
import os
import sys

import numpy as np

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from rl.env import TrollFarmEnv
from rl.policy import MLPPolicy


def run_episodes(env, seeds, policy=None, rng=None, greedy=True):
    out = []
    for s in seeds:
        env.seed_pool = [int(s)]
        obs = env.reset()
        while True:
            if policy is None:
                a = np.array([rng.randint(n) for n in env.action_nvec])
            else:
                a, _ = policy.act(obs, rng, greedy=greedy)
            obs, r, term, trunc, info = env.step(a)
            if term or trunc:
                break
        out.append(info)
    return out


def summarize(name, infos):
    margin = np.mean([i["margin"] for i in infos])
    win = np.mean([i["win"] for i in infos])
    myw = np.mean([i["my_wood"] for i in infos])
    oppw = np.mean([i["opp_wood"] for i in infos])
    mys = np.mean([i["my_score"] for i in infos])
    ops = np.mean([i["opp_score"] for i in infos])
    ntr = np.mean([i["n_trolls"] for i in infos])
    print(f"  {name:18s} win {win:5.2f} | margin {margin:7.1f} | "
          f"score {mys:6.1f} vs {ops:6.1f} | wood {myw:5.1f} vs {oppw:5.1f} | "
          f"trolls {ntr:.2f}")
    return dict(win=win, margin=margin, my_score=mys, opp_score=ops,
                my_wood=myw, opp_wood=oppw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", required=True)
    ap.add_argument("--opponent", default="chopper")
    ap.add_argument("--episodes", type=int, default=100)
    ap.add_argument("--eval-start", type=int, default=500,
                    help="first held-out map seed (train pool is 0..63)")
    ap.add_argument("--sampled", action="store_true",
                    help="sample actions instead of greedy argmax")
    ap.add_argument("--seed", type=int, default=123)
    args = ap.parse_args()

    seeds = list(range(args.eval_start, args.eval_start + args.episodes))
    env = TrollFarmEnv(opponent=args.opponent, seed_pool=[0], seed=args.seed)
    policy = MLPPolicy.load(args.policy)
    rng = np.random.RandomState(args.seed)

    print(f"[eval] policy={args.policy} opponent={args.opponent} "
          f"maps={seeds[0]}..{seeds[-1]} ({args.episodes}) "
          f"{'sampled' if args.sampled else 'greedy'}")
    rand_infos = run_episodes(env, seeds, policy=None, rng=rng)
    base = summarize("random baseline", rand_infos)
    pol_infos = run_episodes(env, seeds, policy=policy, rng=rng, greedy=not args.sampled)
    trained = summarize("trained policy", pol_infos)
    print(f"[eval] margin improvement: {base['margin']:.1f} -> {trained['margin']:.1f} "
          f"(+{trained['margin'] - base['margin']:.1f}); "
          f"win {base['win']:.2f} -> {trained['win']:.2f}")


if __name__ == "__main__":
    main()
