from bot.main import decide, planting_commands, State, Troll, Tree, PARAMS


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


from bot.main import planting_commands


def plant_params(cells):
    p = dict(PARAMS)
    p["plant_enabled"] = True
    p["plant_type"] = "BANANA"
    p["orchard_cells"] = cells
    p["max_orchard"] = 4
    return p


def test_picks_a_seed_when_idle_at_shack_and_orchard_wanted():
    w = grid(4, 4, blocked=[(0, 0)])
    troll = Troll(0, 0, 1, 1, 1, 1, [0]*6)      # empty, adjacent to shack
    st = State(walkable=w, my_shack=(0, 0), opp_shack=(15, 7),
               my_inventory=[0, 0, 0, 5, 0, 0], opp_inventory=[0]*6,
               trees=[], my_trolls=[troll], opp_trolls=[], turn=1)
    cmds = planting_commands(st, plant_params([(1, 1)]), set())
    assert cmds == ["PICK 0 BANANA"]


def test_plants_seed_on_target_cell():
    w = grid(4, 4, blocked=[(0, 0)])
    troll = Troll(0, 1, 1, 1, 1, 1, [0, 0, 0, 1, 0, 0])   # carries a banana seed
    st = State(walkable=w, my_shack=(0, 0), opp_shack=(15, 7),
               my_inventory=[0]*6, opp_inventory=[0]*6, trees=[],
               my_trolls=[troll], opp_trolls=[], turn=1)
    cmds = planting_commands(st, plant_params([(1, 1)]), set())
    assert cmds == ["PLANT 0 BANANA"]


def test_planting_disabled_returns_nothing():
    w = grid(4, 4, blocked=[(0, 0)])
    troll = Troll(0, 0, 1, 1, 1, 1, [0]*6)
    st = State(walkable=w, my_shack=(0, 0), opp_shack=(15, 7),
               my_inventory=[0, 0, 0, 5, 0, 0], opp_inventory=[0]*6,
               trees=[], my_trolls=[troll], opp_trolls=[], turn=1)
    assert planting_commands(st, gather_only(), set()) == []
