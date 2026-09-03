"""Solve one panel map on one seat: a two-stage sweep.  Stage A: every plan (second-troll talents
the draw affords x seed programmes x reserve rule) once, deterministically.  Stage B: the best
`refine` plans again with `rollouts` randomized rollouts each.  Keep the earliest completion of
the third troll; tie-break the bank in points plus the standing wood of our own trees."""
from __future__ import annotations

import random
import time

import world
import solver
import enumerate as en

SEED_PROGRAMMES = [
    [],
    [("LEMON", "near")],
    [("LEMON", "water")],
    [("LEMON", "water"), ("LEMON", "water")],
    [("LEMON", "near"), ("LEMON", "near")],
    [("LEMON", "water"), ("PLUM", "water")],
    [("LEMON", "water"), ("LEMON", "water"), ("PLUM", "water")],
    [("LEMON", "water"), ("LEMON", "water"), ("LEMON", "water")],
    [("PLUM", "water"), ("LEMON", "water")],
    [("LEMON", "near"), ("PLUM", "near")],
    [("APPLE", "water"), ("LEMON", "water")],
]


def bank_points(s: world.State):
    """The bank in points plus the standing wood of the trees we planted (4 a size unit)."""
    own_wood = sum(p.size for p in s.plants.values() if p.own)
    return s.score + 4 * own_wood


def run_plan(s0, plan_args, rng, horizon):
    plan = solver.Plan(**plan_args)
    s = solver.rollout(s0, plan, rng, horizon=horizon)
    done = len(s.trains) >= (2 if plan_args["t2"] else 1)
    return s, (s.trains[-1][0] if done else None)


def solve_map(item, seat=0, t3=(2, 3, 0, 3), rollouts=12, temps=(0.2, 0.5), horizon=200,
              seed=1, refine=6, t2_list=None, programmes=None, wait_cds=(4,), t2_not_before=1,
              bottlenecks=(0.0, 1.0)):
    s0 = world.make_state(item, seat)
    draw = item["draw"]
    t2s = t2_list if t2_list is not None else sorted(set(en.t2_candidates(draw, s0.m.has_iron)) | set(en.T2_DELAYED))
    programmes = SEED_PROGRAMMES if programmes is None else programmes
    t0 = time.time()
    n = 0
    stage_a = []
    for t2 in t2s:
        for seeds in programmes:
            for reserve in ((True, True), (True, False), (False, False)) if seeds else ((True, True),):
                for wcd in wait_cds:
                  for bn in bottlenecks:
                    args = dict(t2=t2, t3=t3, seeds=list(seeds), temp=0.0, reserve_t2=reserve[0], reserve_t3=reserve[1],
                                wait_cd=wcd, t2_not_before=t2_not_before, bottleneck=bn)
                    s, t_done = run_plan(s0, args, random.Random(0), horizon)
                    n += 1
                    if t_done is not None:
                        stage_a.append(((t_done, -bank_points(s)), s, args))
    stage_a.sort(key=lambda x: x[0])
    best = stage_a[0] if stage_a else None
    for key, s, args in stage_a[:refine]:
        for temp in temps:
            for k in range(rollouts):
                rng = random.Random(seed * 100003 + n)
                n += 1
                a = dict(args, temp=temp)
                s2, t_done = run_plan(s0, a, rng, horizon)
                if t_done is None:
                    continue
                key2 = (t_done, -bank_points(s2))
                if best is None or key2 < best[0]:
                    best = (key2, s2, a)
    dt = time.time() - t0
    if best is None:
        return {"done": False, "rollouts": n, "seconds": dt}
    key, s, args = best
    return {"done": True, "turn": key[0], "bank": -key[1], "plan": args, "trains": s.trains,
            "log": s.log, "rollouts": n, "seconds": dt, "inv": s.inv, "state": s,
            "stage_a_best": stage_a[0][0][0] if stage_a else None}
