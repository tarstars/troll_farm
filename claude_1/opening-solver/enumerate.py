"""Talent candidates: every second troll the draw affords on turn 1, and the third trolls of
the P sweep."""
from world import training_cost


def t2_candidates(draw, has_iron, ms_max=3, cc_max=4, hp_max=3, chop_max=3):
    out = []
    for ms in range(1, ms_max + 1):
        for cc in range(1, cc_max + 1):
            for hp in range(0, hp_max + 1):
                for chop in range(0, chop_max + 1):
                    t = (ms, cc, hp, chop)
                    cost = training_cost(1, t)
                    pay = (0, 1, 2, 4) if has_iron else (0, 1, 2)
                    if all(draw[i] >= cost[i] for i in pay):
                        out.append(t)
    return out


def t2_frontier(draw, has_iron, **kw):
    """Turn-1-affordable talents not dominated in every talent by another affordable one,
    plus the cheapest (1,1,0,0)/(1,1,1,1)-style floors the search may still want."""
    cands = t2_candidates(draw, has_iron, **kw)
    keep = []
    for t in cands:
        dominated = any(o != t and all(o[i] >= t[i] for i in range(4)) for o in cands)
        if not dominated:
            keep.append(t)
    return keep


T3_SWEEP = {
    "chop2": [(2, 3, 0, 2), (2, 3, 1, 2), (2, 2, 0, 2), (1, 3, 0, 2)],
    "chop3": [(2, 3, 0, 3), (2, 3, 1, 3), (2, 2, 0, 3), (1, 3, 0, 3)],
}
