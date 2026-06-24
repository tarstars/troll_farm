from bot.main import decide, State, Troll, Tree, PARAMS


def grid(w, h, blocked=()):
    return {(x, y) for x in range(w) for y in range(h)} - set(blocked)


def base(walkable, trees, my_trolls):
    return State(walkable=walkable, my_shack=(0, 0), opp_shack=(15, 7),
                 my_inventory=[0]*6, opp_inventory=[0]*6, trees=trees,
                 my_trolls=my_trolls, opp_trolls=[], turn=1)


def gather_only():
    p = dict(PARAMS)
    p["max_trolls"] = 0          # no training in this test
    p["plant_enabled"] = False
    return p


def test_two_trolls_do_not_target_the_same_tree():
    w = grid(8, 2, blocked=[(0, 0)])
    a = Troll(0, 4, 0, 1, 1, 1, [0]*6)
    b = Troll(1, 4, 1, 1, 1, 1, [0]*6)
    trees = [Tree("PLUM", 3, 0, 4, 4, 1, 5), Tree("PLUM", 5, 0, 4, 4, 1, 5)]
    cmds = decide(base(w, trees, [a, b]), gather_only())
    targets = {c.split()[-2] + "," + c.split()[-1] for c in cmds if c.startswith("MOVE")}
    assert targets == {"3,0", "5,0"}     # distinct trees, no double-booking


def test_empty_returns_wait():
    w = grid(4, 4, blocked=[(0, 0)])
    cmds = decide(base(w, [], []), gather_only())
    assert cmds == ["WAIT"]
