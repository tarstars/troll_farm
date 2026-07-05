"""From-scratch A2C (advantage actor-critic) trainer for the Troll Farm env.

Pure numpy — no torch/sb3 — so it always runs. Trains player 0's factored
MultiDiscrete policy against a FIXED scripted opponent (default: the greedy
`chopper`, which actually banks wood, so learning is clearly visible).

Run (from the worktree root):
    uv run python -m rl.train --opponent chopper --iters 200

Outputs a learning curve to rl/runs/<tag>/curve.csv and the final policy to
rl/runs/<tag>/policy.npz. The honest metric is `margin` = my_score - opp_score
(mean over the iteration's sampled episodes); it should trend up over iters.
"""

import argparse
import csv
import os
import sys
import time

import numpy as np

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from rl.env import TrollFarmEnv
from rl.policy import MLPPolicy, softmax


# ── rollout collection ────────────────────────────────────────────────────────
def collect(env, policy, rng, n_episodes):
    obs_buf, act_buf, rew_buf, ep_lens = [], [], [], []
    infos = []
    for _ in range(n_episodes):
        obs = env.reset()
        L = 0
        while True:
            a, _v = policy.act(obs, rng)
            nobs, r, term, trunc, info = env.step(a)
            obs_buf.append(obs)
            act_buf.append(a)
            rew_buf.append(r)
            obs = nobs
            L += 1
            if term or trunc:
                infos.append(info)
                break
        ep_lens.append(L)
    X = np.asarray(obs_buf, dtype=np.float64)
    A = np.asarray(act_buf, dtype=np.int64)
    R = np.asarray(rew_buf, dtype=np.float64)
    return X, A, R, ep_lens, infos


# ── GAE ───────────────────────────────────────────────────────────────────────
def compute_gae(rewards, values, ep_lens, gamma, lam):
    N = len(rewards)
    adv = np.zeros(N)
    idx = 0
    for L in ep_lens:
        lastgae = 0.0
        for t in reversed(range(L)):
            i = idx + t
            nextval = 0.0 if t == L - 1 else values[i + 1]  # episode end = terminal
            delta = rewards[i] + gamma * nextval - values[i]
            lastgae = delta + gamma * lam * lastgae
            adv[i] = lastgae
        idx += L
    ret = adv + values
    return adv, ret


# ── one A2C update (hand-written backprop + Adam) ─────────────────────────────
def update(policy, X, A, rewards, ep_lens, gamma, lam, ent_coef, vf_coef, lr):
    h, logits, values = policy.forward(X)
    adv, ret = compute_gae(rewards, values, ep_lens, gamma, lam)
    adv_n = (adv - adv.mean()) / (adv.std() + 1e-8)
    N = X.shape[0]

    dlogits = np.zeros_like(logits)
    pg_loss = 0.0
    ent = 0.0
    off = 0
    ar = np.arange(N)
    for gi, n in enumerate(policy.nvec):
        z = logits[:, off:off + n]
        p = softmax(z, axis=1)
        a = A[:, gi]
        logp = np.log(p[ar, a] + 1e-9)
        pg_loss += -(logp * adv_n).mean()
        onehot = np.zeros((N, n))
        onehot[ar, a] = 1.0
        # d(-mean(logp*adv))/dz = adv*(p - onehot)/N
        dz = (adv_n[:, None] * (p - onehot)) / N
        Hrow = -(p * np.log(p + 1e-9)).sum(1)          # per-sample head entropy
        ent += Hrow.mean()
        # entropy bonus: minimise -ent_coef*H -> +ent_coef*p*(log p + H)/N
        dz += ent_coef * (p * (np.log(p + 1e-9) + Hrow[:, None])) / N
        dlogits[:, off:off + n] = dz
        off += n

    v_err = values - ret
    v_loss = 0.5 * (v_err ** 2).mean()
    dv = vf_coef * v_err / N

    # backprop into trunk
    dWp = h.T @ dlogits
    dbp = dlogits.sum(0)
    dWv = h.T @ dv[:, None]
    dbv = np.array([dv.sum()])
    dh = dlogits @ policy.Wp.T + dv[:, None] * policy.Wv.T
    dpre = dh * (1 - h ** 2)
    dW1 = X.T @ dpre
    db1 = dpre.sum(0)

    grads = {"W1": dW1, "b1": db1, "Wp": dWp, "bp": dbp, "Wv": dWv, "bv": dbv}
    gnorm = policy.adam_step(grads, lr=lr)
    return {"pg_loss": pg_loss, "v_loss": v_loss, "entropy": ent / len(policy.nvec),
            "grad_norm": gnorm, "adv_std": adv.std()}


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponent", default="chopper")
    ap.add_argument("--iters", type=int, default=200)
    ap.add_argument("--episodes-per-iter", type=int, default=6)
    ap.add_argument("--hidden", type=int, default=128)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--gamma", type=float, default=0.99)
    ap.add_argument("--lam", type=float, default=0.95)
    ap.add_argument("--ent-coef", type=float, default=0.01)
    ap.add_argument("--vf-coef", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seed-pool", type=int, default=64,
                    help="train on map seeds 0..N-1 (0 = a fresh random map each episode)")
    ap.add_argument("--carry-coef", type=float, default=0.5)
    ap.add_argument("--reward-scale", type=float, default=4.0)
    ap.add_argument("--init-policy", default=None,
                    help="warm-start from a saved policy.npz (e.g. curriculum boss->chopper)")
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()

    tag = args.tag or f"a2c_{args.opponent}"
    out_dir = os.path.join(_REPO_ROOT, "rl", "runs", tag)
    os.makedirs(out_dir, exist_ok=True)

    pool = range(args.seed_pool) if args.seed_pool > 0 else None
    env = TrollFarmEnv(opponent=args.opponent, seed_pool=pool, seed=args.seed,
                       carry_coef=args.carry_coef, reward_scale=args.reward_scale)
    if args.init_policy:
        policy = MLPPolicy.load(args.init_policy)
        assert policy.obs_dim == env.obs_dim and policy.nvec == env.action_nvec.tolist(), \
            "init policy shape mismatch"
        print(f"[train] warm-started from {args.init_policy}")
    else:
        policy = MLPPolicy(env.obs_dim, env.action_nvec, hidden=args.hidden, seed=args.seed)
    rng = np.random.RandomState(args.seed + 1)

    print(f"[train] opponent={args.opponent} obs_dim={env.obs_dim} "
          f"heads={env.action_nvec.tolist()} iters={args.iters} "
          f"eps/iter={args.episodes_per_iter} seed_pool={args.seed_pool}")
    print(f"[train] logging -> {out_dir}")

    curve_path = os.path.join(out_dir, "curve.csv")
    fcsv = open(curve_path, "w", newline="")
    writer = csv.writer(fcsv)
    writer.writerow(["iter", "env_steps", "margin", "win_rate", "my_wood",
                     "opp_wood", "ep_return", "n_trolls", "entropy", "v_loss",
                     "pg_loss", "grad_norm"])

    t0 = time.time()
    env_steps = 0
    best_margin = -1e9
    hist = []
    for it in range(1, args.iters + 1):
        X, A, R, ep_lens, infos = collect(env, policy, rng, args.episodes_per_iter)
        env_steps += len(R)
        stats = update(policy, X, A, R, ep_lens, args.gamma, args.lam,
                       args.ent_coef, args.vf_coef, args.lr)

        margin = float(np.mean([i["margin"] for i in infos]))
        win = float(np.mean([i["win"] for i in infos]))
        myw = float(np.mean([i["my_wood"] for i in infos]))
        oppw = float(np.mean([i["opp_wood"] for i in infos]))
        ntr = float(np.mean([i["n_trolls"] for i in infos]))
        # ep_return: sum of shaped rewards per episode
        ep_ret = float(R.sum() / args.episodes_per_iter)
        hist.append(margin)

        writer.writerow([it, env_steps, round(margin, 2), round(win, 3),
                         round(myw, 2), round(oppw, 2), round(ep_ret, 2),
                         round(ntr, 2), round(stats["entropy"], 3),
                         round(stats["v_loss"], 4), round(stats["pg_loss"], 4),
                         round(stats["grad_norm"], 3)])
        fcsv.flush()

        if it == 1 or it % 10 == 0 or it == args.iters:
            ma = np.mean(hist[-10:])
            sps = env_steps / (time.time() - t0)
            print(f"it {it:4d} | steps {env_steps:7d} | margin {margin:7.1f} "
                  f"(ma10 {ma:6.1f}) | win {win:4.2f} | wood {myw:4.1f}v{oppw:4.1f} "
                  f"| trolls {ntr:.1f} | ent {stats['entropy']:.2f} "
                  f"vL {stats['v_loss']:.3f} | {sps:.0f} st/s")

        if margin > best_margin:
            best_margin = margin
            policy.save(os.path.join(out_dir, "policy_best.npz"))

    policy.save(os.path.join(out_dir, "policy.npz"))
    fcsv.close()
    dt = time.time() - t0
    first = np.mean(hist[:10]) if len(hist) >= 10 else hist[0]
    last = np.mean(hist[-10:])
    print(f"\n[done] {args.iters} iters, {env_steps} env steps in {dt:.0f}s "
          f"({env_steps/dt:.0f} steps/s)")
    print(f"[result] mean margin: first10={first:.1f} -> last10={last:.1f} "
          f"(best iter margin {best_margin:.1f})")
    print(f"[out] curve: {curve_path}\n[out] policy: {out_dir}/policy.npz")


if __name__ == "__main__":
    main()
