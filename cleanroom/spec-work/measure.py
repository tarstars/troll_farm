#!/usr/bin/env python3
"""Recompute every number cited in cleanroom/package/CHAMPION-BEHAVIOUR.md.

Writes cleanroom/spec-work/observations.json: one entry per claim, with the
measured counts and a handful of (game id, turn) citations.  The package
document quotes these; nothing in it may be written that is not produced here.

Also writes cleanroom/package/champion-purchases.json -- for each of the 160
matches, the shack's contents on every turn up to the purchase, whether the map
has iron, and what was bought on which turn -- the material the implementer
needs to fit a train rule of their own (section 4 of the behaviour document).

Run:  python3 cleanroom/spec-work/measure.py
"""
from __future__ import annotations

import collections
import itertools
import json
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus  # noqa: E402

WORK = {"CHOP", "HARVEST", "DROP", "PLANT", "PICK", "MINE"}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "observations.json")
PURCHASES = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "package", "champion-purchases.json")


def best_affordable(inventory, has_iron):
    """(ms, cc, chop) of the best harvest-0 worker affordable with one troll alive, or
    None. Each talent is capped by its own resource, so the best bundle is unique."""
    best = None
    for ms, cc, chop in itertools.product((1, 2, 3), repeat=3):
        if (inventory[0] >= 1 + ms * ms and inventory[1] >= 1 + cc * cc and inventory[2] >= 1
                and (not has_iron or inventory[4] >= 1 + chop * chop)):
            key = (ms + cc + chop, ms, cc, chop)
            if best is None or key > best:
                best = key
    return best


def substitute_rule(games, threshold, deadline=35):
    """How often 'buy the best affordable worker once ms+cc+chop >= threshold, and by
    turn `deadline` regardless' buys on the champion's own turn; and by how many turns
    it is early or late when it does not."""
    same_turn = 0
    misses = []
    for g in games:
        seat = g["seat"]
        has_iron = any("+" in row for row in g["rows"])
        actual = next((t + 1 for t, cmds in enumerate(g["commands"])
                       if any(v == "TRAIN" for v, _ in cmds)), None)
        rule = None
        for t in range(g["turns"]):
            best = best_affordable(g["states"][t]["inventories"][seat], has_iron)
            if best and (best[0] >= threshold or t + 1 >= deadline):
                rule = t + 1
                break
        if rule == actual:
            same_turn += 1
        else:
            misses.append((rule or 0) - (actual or 0))
    misses.sort()
    return {"threshold": threshold, "deadline": deadline, "same_turn": same_turn,
            "games": len(games),
            "when_it_misses_rule_turn_minus_champion_turn": {
                "median": misses[len(misses) // 2] if misses else None,
                "min": min(misses) if misses else None, "max": max(misses) if misses else None,
                "earlier": sum(1 for m in misses if m < 0),
                "later": sum(1 for m in misses if m > 0)}}


def main():
    obs = {}
    games = list(corpus.games())
    obs["corpus"] = {
        "games": len(games),
        "seat_0": sum(1 for g in games if g["seat"] == 0),
        "seat_1": sum(1 for g in games if g["seat"] == 1),
        "turn_lengths": {"min": min(g["turns"] for g in games),
                         "max": max(g["turns"] for g in games),
                         "full_300": sum(1 for g in games if g["turns"] == 300)},
        "map_heights": dict(collections.Counter(g["height"] for g in games)),
    }

    verbs = collections.Counter()
    verbs_by_band = collections.defaultdict(collections.Counter)
    move_step = collections.Counter()
    move_exact = collections.Counter()
    move_cites = []
    train = []
    train_rule_ok = 0
    train_first_affordable = 0
    drop_full = collections.Counter()
    drop_cites = []
    pick_priority = collections.Counter()
    plant_dist = collections.Counter()
    plant_cites = []
    chop_natural = collections.Counter()
    chop_planted = collections.Counter()
    first_pick = []
    mine_games = 0
    harvest_games = 0
    both_games = 0
    mine_turns = []
    harvest_turns = []
    wait_ctx = collections.Counter()
    final_inv = []
    journey_rank = collections.defaultdict(collections.Counter)
    journey_gap = collections.Counter()
    journey_cites = []
    train_cites = []
    pick_cites = []

    for g in games:
        seat = g["seat"]
        sh = corpus.shack(g, seat)
        walk = corpus.walkable_set(g)
        natural = {(p["x"], p["y"]) for p in g["states"][0]["plants"]}
        planted = {}
        acts = collections.defaultdict(list)
        trained_turn = None
        game_mine = game_harvest = 0
        first_pick_turn = None

        for t, cmds in enumerate(g["commands"], 1):
            state = g["states"][t - 1]
            band = min((t - 1) // 50, 5)
            for verb, args in cmds:
                verbs[verb] += 1
                verbs_by_band[band][verb] += 1

                if verb == "TRAIN":
                    inventory = state["inventories"][seat]
                    have = len(corpus.own_units(state, seat))
                    chosen = tuple(args)
                    train.append({"game": g["game_id"], "turn": t, "talents": chosen,
                                  "trolls_before": have})
                    affordable = [z for z in itertools.product(range(0, 7), repeat=4)
                                  if inventory[0] >= have + z[0] ** 2
                                  and inventory[1] >= have + z[1] ** 2
                                  and inventory[2] >= have + z[2] ** 2
                                  and inventory[4] >= have + z[3] ** 2]
                    if chosen in affordable:
                        best = sorted(affordable, key=lambda z: (z[2], -(z[0] + z[1] + z[3])))[0]
                        train_rule_ok += (best == chosen)
                    trained_turn = t
                    if len(train_cites) < 8:
                        train_cites.append({"game": g["game_id"], "turn": t,
                                            "talents": list(chosen),
                                            "shack": list(inventory)})
                    continue

                if verb == "WAIT":
                    units = corpus.own_units(state, seat)
                    on_tree = any(corpus.plant_at(state, u["x"], u["y"]) for u in units)
                    wait_ctx[("no trees left" if not state["plants"] else "trees remain",
                              "standing on a tree" if on_tree else "not on a tree")] += 1
                    continue

                unit = corpus.unit_by_id(state, args[0]) if args else None
                if unit is None:
                    continue
                cell = (unit["x"], unit["y"])

                if verb == "MOVE":
                    dist = corpus.bfs(walk, [cell]).get((args[1], args[2]))
                    move_step[dist if dist is not None and dist < 8 else "8+/unreachable"] += 1
                    move_exact[dist == unit["ms"]] += 1
                    if len(move_cites) < 6 and dist == unit["ms"]:
                        move_cites.append({"game": g["game_id"], "turn": t, "troll": args[0],
                                           "from": list(cell), "to": [args[1], args[2]],
                                           "speed": unit["ms"], "bfs_distance": dist})
                elif verb == "DROP":
                    drop_full[(sum(unit["carry"]), unit["cc"])] += 1
                    if len(drop_cites) < 6:
                        drop_cites.append({"game": g["game_id"], "turn": t, "troll": args[0],
                                           "carrying": sum(unit["carry"]), "capacity": unit["cc"]})
                elif verb == "PICK":
                    inventory = state["inventories"][seat]
                    present = tuple(n for i, n in enumerate(("PLUM", "LEMON", "APPLE", "BANANA"))
                                    if inventory[i] > 0)
                    pick_priority[(present, args[1])] += 1
                    if first_pick_turn is None:
                        first_pick_turn = t
                    if len(pick_cites) < 6:
                        pick_cites.append({"game": g["game_id"], "turn": t, "took": args[1],
                                           "shack_had": list(inventory[:4])})
                elif verb == "PLANT":
                    plant_dist[abs(cell[0] - sh[0]) + abs(cell[1] - sh[1])] += 1
                    planted[cell] = t
                    if len(plant_cites) < 6:
                        plant_cites.append({"game": g["game_id"], "turn": t, "troll": args[0],
                                            "cell": list(cell), "shack": list(sh),
                                            "species": args[1]})
                elif verb == "CHOP":
                    tree = corpus.plant_at(state, *cell)
                    size = tree["size"] if tree else None
                    if cell in planted:
                        chop_planted[size] += 1
                    elif cell in natural:
                        chop_natural[size] += 1
                elif verb == "MINE":
                    game_mine += 1
                    mine_turns.append(t)
                elif verb == "HARVEST":
                    game_harvest += 1
                    harvest_turns.append(t)

                if verb in WORK:
                    acts[args[0]].append((t, verb, cell))

        if trained_turn is not None:
            # did it fire on the first turn its own bundle was affordable?
            talents = train[-1]["talents"]
            need = talents[0] + talents[1] + talents[3]
            fired_early = False
            for t in range(1, trained_turn):
                state = g["states"][t - 1]
                if len(corpus.own_units(state, seat)) != 1:
                    break
                inventory = state["inventories"][seat]
                best = max((z[0] + z[1] + z[3] for z in itertools.product(range(0, 7), repeat=4)
                            if z[2] == 0
                            and inventory[0] >= 1 + z[0] ** 2 and inventory[1] >= 1 + z[1] ** 2
                            and inventory[2] >= 1 and inventory[4] >= 1 + z[3] ** 2), default=-1)
                if best >= need:
                    fired_early = True
                    break
            train_first_affordable += (not fired_early)

        if game_mine:
            mine_games += 1
        if game_harvest:
            harvest_games += 1
        if game_mine and game_harvest:
            both_games += 1
        if first_pick_turn is not None:
            first_pick.append({"game": g["game_id"], "turn": first_pick_turn,
                               "trees_alive": len(g["states"][first_pick_turn - 1]["plants"]),
                               "trees_at_start": len(g["states"][0]["plants"])})
        final_inv.append(list(g["states"][-1]["inventories"][seat]))

        # journeys: from the turn after one job to the turn a different tree is chopped
        for uid, seq in acts.items():
            for i in range(1, len(seq)):
                start = seq[i - 1][0] + 1
                end, verb, cell = seq[i]
                if verb != "CHOP" or cell == seq[i - 1][2] or end < start:
                    continue
                state = g["states"][start - 1]
                unit = corpus.unit_by_id(state, uid)
                if unit is None or unit["chop"] <= 0:
                    continue
                trees = {(p["x"], p["y"]): p for p in state["plants"]}
                if cell not in trees:
                    continue
                busy = {(o["x"], o["y"]) for o in corpus.own_units(state, seat) if o["id"] != uid}
                if cell in busy:
                    continue
                dist = corpus.bfs(walk, [(unit["x"], unit["y"])])
                if cell not in dist:
                    continue
                cands = [(c, p, math.ceil(dist[c] / max(unit["ms"], 1)),
                          math.ceil(p["health"] / unit["chop"]))
                         for c, p in trees.items() if c in dist and c not in busy]
                if len(cands) < 3:
                    continue

                def rank(key):
                    ordered = sorted(cands, key=key)
                    return next(i for i, z in enumerate(ordered) if z[0] == cell)

                journey_rank["nearest"][rank(lambda z: (z[2], z[0]))] += 1
                journey_rank["fewest turns to wood"][rank(lambda z: (z[2] + z[3], z[0]))] += 1
                journey_rank["most wood per turn"][
                    rank(lambda z: (-(4 * z[1]["size"] / (z[2] + z[3])), z[2], z[0]))] += 1
                journey_rank["biggest tree first"][
                    rank(lambda z: (-z[1]["size"], z[2], z[0]))] += 1
                nearest = min(z[2] for z in cands)
                mine_ = next(z for z in cands if z[0] == cell)
                journey_gap[min(mine_[2] - nearest, 8)] += 1
                if len(journey_cites) < 6 and mine_[2] == nearest:
                    journey_cites.append({"game": g["game_id"], "left_turn": start,
                                          "chopped_turn": end, "troll": uid,
                                          "tree": list(cell), "walk_turns": mine_[2],
                                          "chop_turns": mine_[3]})

    obs["verbs"] = dict(verbs)
    obs["verbs_by_50_turn_band"] = {"%d-%d" % (b * 50 + 1, b * 50 + 50): dict(c)
                                    for b, c in sorted(verbs_by_band.items())}
    obs["move_is_one_step"] = {
        "bfs_distance_to_move_target": {str(k): v for k, v in move_step.items()},
        "target_exactly_at_speed": move_exact[True],
        "target_short_of_speed": move_exact[False],
        "citations": move_cites,
    }
    unique_best = 0
    purchases = []
    for g in games:
        seat = g["seat"]
        has_iron = any("+" in row for row in g["rows"])
        bought = next(((t + 1, list(args)) for t, cmds in enumerate(g["commands"])
                       for v, args in cmds if v == "TRAIN"), None)
        if bought is None:
            continue
        turn, talents = bought
        inventory = g["states"][turn - 1]["inventories"][seat]
        best = best_affordable(inventory, has_iron)
        tied = [z for z in itertools.product((1, 2, 3), repeat=3)
                if best and z[0] + z[1] + z[2] == best[0]
                and inventory[0] >= 1 + z[0] ** 2 and inventory[1] >= 1 + z[1] ** 2
                and (not has_iron or inventory[4] >= 1 + z[2] ** 2)]
        unique_best += len(tied) == 1
        purchases.append({"game": g["game_id"], "seat": seat, "map": "%dx%d" % (g["width"], g["height"]),
                          "map_has_iron": has_iron, "bought": talents, "turn": turn,
                          "shack_by_turn": [list(g["states"][t]["inventories"][seat])
                                            for t in range(turn)]})
    obs["train"] = {
        "commands_total": len(train),
        "games": len(games),
        "turn": {"min": min(x["turn"] for x in train),
                 "median": statistics.median([x["turn"] for x in train]),
                 "max": max(x["turn"] for x in train)},
        "talents": {str(list(k)): v for k, v in
                    collections.Counter(x["talents"] for x in train).most_common()},
        "harvest_talent_always_zero": all(x["talents"][2] == 0 for x in train),
        "trolls_before_always_one": all(x["trolls_before"] == 1 for x in train),
        "matches_best_affordable_rule": train_rule_ok,
        "best_affordable_bundle_was_unique": unique_best,
        "fired_on_first_turn_its_bundle_was_affordable": train_first_affordable,
        "substitute_rule_agreement": [substitute_rule(games, thr) for thr in (4, 5, 6)],
        "citations": train_cites,
    }
    with open(os.path.abspath(PURCHASES), "w") as handle:
        json.dump({"what": "for each recorded match of the reference bot: the shack's contents "
                           "(plum, lemon, apple, banana, iron, wood) at the start of every turn "
                           "up to and including the turn it bought its second worker, whether "
                           "the map has iron cells (if not, the iron part of the price is waived), "
                           "and the worker it bought as [speed, carry, harvest, chop]",
                   "matches": purchases}, handle, indent=1)
    obs["drop"] = {
        "at_exactly_full_capacity": sum(v for (c, cap), v in drop_full.items() if c >= cap),
        "below_capacity": sum(v for (c, cap), v in drop_full.items() if c < cap),
        "carry_over_capacity": {"%d/%d" % k: v for k, v in drop_full.most_common(8)},
        "citations": drop_cites,
    }
    priority = {}
    for (present, took), count in pick_priority.items():
        priority.setdefault("+".join(present), {})[took] = count
    obs["pick"] = {"choice_given_what_the_shack_held": priority, "citations": pick_cites}
    obs["plant"] = {"manhattan_distance_from_own_shack": {str(k): v for k, v in
                                                          sorted(plant_dist.items())},
                    "citations": plant_cites}
    obs["chop"] = {
        "natural_trees_by_size": {str(k): v for k, v in sorted(chop_natural.items(),
                                                               key=lambda z: (z[0] is None, z[0]))},
        "self_planted_trees_by_size": {str(k): v for k, v in sorted(chop_planted.items(),
                                                                    key=lambda z: (z[0] is None, z[0]))},
    }
    early = [x for x in first_pick if x["turn"] < 251]
    late = [x for x in first_pick if x["turn"] >= 251]
    obs["seed_loop_trigger"] = {
        "games_with_a_pick": len(first_pick),
        "before_turn_251": {"games": len(early),
                            "trees_alive_max": max(x["trees_alive"] for x in early),
                            "trees_alive_median": statistics.median([x["trees_alive"] for x in early]),
                            "turn_median": statistics.median([x["turn"] for x in early]),
                            "turn_min": min(x["turn"] for x in early)},
        "from_turn_251": {"games": len(late),
                          "trees_alive_median": statistics.median([x["trees_alive"] for x in late]),
                          "trees_alive_max": max(x["trees_alive"] for x in late),
                          "turn_min": min(x["turn"] for x in late),
                          "turn_max": max(x["turn"] for x in late)},
        "citations": first_pick[:8],
    }
    obs["early_earning"] = {
        "games_with_any_mine": mine_games, "games_with_any_harvest": harvest_games,
        "games_with_both": both_games, "games_with_neither": len(games) - mine_games
                                                             - harvest_games + both_games,
        "mine_turn_max": max(mine_turns) if mine_turns else None,
        "harvest_turn_max": max(harvest_turns) if harvest_turns else None,
    }
    obs["wait"] = {" / ".join(k): v for k, v in wait_ctx.most_common()}
    columns = list(zip(*final_inv))
    scores = [sum(r[:4]) + 4 * r[5] for r in final_inv]
    obs["outcome"] = {
        "final_shack_mean": {n: round(sum(c) / len(c), 2) for n, c in zip(corpus.ITEMS, columns)},
        "score_mean": round(sum(scores) / len(scores), 1),
        "score_median": statistics.median(scores),
        "wood_share_of_score": round(4 * sum(r[5] for r in final_inv) / sum(scores), 3),
    }
    total = sum(journey_rank["nearest"].values())
    obs["target_choice"] = {
        "journeys": total,
        "top1_percent": {k: round(100 * v[0] / total, 1) for k, v in journey_rank.items()},
        "top3_percent": {k: round(100 * sum(v[i] for i in (0, 1, 2)) / total, 1)
                         for k, v in journey_rank.items()},
        "extra_walking_turns_over_the_nearest_tree":
            {str(k): v for k, v in sorted(journey_gap.items())},
        "citations": journey_cites,
    }

    with open(OUT, "w") as handle:
        json.dump(obs, handle, indent=1, sort_keys=True, default=str)
    print("wrote %s" % OUT)
    print(json.dumps({k: v for k, v in obs.items() if k in
                      ("corpus", "train", "seed_loop_trigger", "target_choice")},
                     indent=1, default=str)[:2500])


if __name__ == "__main__":
    main()
