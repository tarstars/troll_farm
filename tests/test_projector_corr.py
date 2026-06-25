# tests/test_projector_corr.py
from bot.main import (project, estimate_rates, CHOPPER_SPECS, GATHERER_SPECS,
                      decide)
from sim.mapgen import generate_bronze
from sim.views import build_view
from sim.engine import step


POLICIES = [
    [],
    [GATHERER_SPECS[0]],
    [GATHERER_SPECS[0], GATHERER_SPECS[0]],
    [CHOPPER_SPECS[0]],
    [CHOPPER_SPECS[1], GATHERER_SPECS[0]],
    [CHOPPER_SPECS[2], GATHERER_SPECS[2], GATHERER_SPECS[2]],
]


def _spearman(xs, ys):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        rk = [0] * len(v)
        for pos, i in enumerate(order):
            rk[i] = pos
        return rk
    rx, ry = ranks(xs), ranks(ys)
    n = len(xs)
    mx = sum(rx) / n
    my = sum(ry) / n
    cov = sum((rx[i]-mx)*(ry[i]-my) for i in range(n))
    vx = sum((rx[i]-mx)**2 for i in range(n)) ** 0.5
    vy = sum((ry[i]-my)**2 for i in range(n)) ** 0.5
    return cov / (vx*vy) if vx and vy else 0.0


def _policy_decide(state, policy, params):
    # Train this policy's specs in order (earliest-affordable), otherwise act
    # exactly like the shipped bot. Implemented via forced_policy in params.
    p = dict(params)
    p["forced_policy"] = policy
    return decide(state, p)


def _sim_score(seed, policy):
    g = generate_bronze(seed)
    from bot.main import PARAMS
    opp = dict(PARAMS)
    opp["forced_policy"] = []          # fixed, non-expanding opponent (stable gate)
    for _ in range(300):
        cmds0 = _policy_decide(build_view(g, 0), policy, PARAMS)
        cmds1 = decide(build_view(g, 1), opp)
        step(g, cmds0, cmds1)
    return g.scores[0]


def test_projector_ranks_policies_like_the_sim():
    from sim.views import build_view as bv
    corrs = []
    for seed in range(6):
        g = generate_bronze(seed)
        st = bv(g, 0)
        r = estimate_rates(st)
        predicted = [project(st, pol, r) for pol in POLICIES]
        actual = [_sim_score(seed, pol) for pol in POLICIES]
        corrs.append(_spearman(predicted, actual))
    mean = sum(corrs) / len(corrs)
    assert mean >= 0.7, f"projector rank-correlation too low: {mean:.2f} ({corrs})"
