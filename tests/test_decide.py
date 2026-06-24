from bot.main import decide, planting_commands, State, Troll, Tree, PARAMS, VERSION


def grid(w, h, blocked=()):
    return {(x, y) for x in range(w) for y in range(h)} - set(blocked)


def base(walkable, trees, my_trolls, turn=2):
    # default turn=2 so the turn-1 version MSG doesn't intrude on gather tests
    return State(walkable=walkable, my_shack=(0, 0), opp_shack=(15, 7),
                 my_inventory=[0]*6, opp_inventory=[0]*6, trees=trees,
                 my_trolls=my_trolls, opp_trolls=[], turn=turn)


def gather_only():
    p = dict(PARAMS)
    p["max_trolls"] = 0          # no training in this test
    p["plant_enabled"] = False
    return p


def _landings(cmds):
    return [(int(c.split()[2]), int(c.split()[3])) for c in cmds if c.startswith("MOVE")]


def test_two_trolls_move_to_distinct_cells_for_distinct_trees():
    w = grid(8, 2, blocked=[(0, 0)])
    a = Troll(0, 4, 0, 1, 1, 1, [0]*6)
    b = Troll(1, 4, 1, 1, 1, 1, [0]*6)
    trees = [Tree("PLUM", 3, 0, 4, 4, 1, 5), Tree("PLUM", 5, 0, 4, 4, 1, 5)]
    cmds = decide(base(w, trees, [a, b]), gather_only())
    landings = _landings(cmds)
    assert len(landings) == 2 and len(set(landings)) == 2   # both move, no collision


def test_banking_trolls_do_not_stack_on_one_cell():
    # both carry a fruit and head home from cells that would funnel onto one
    # shack-adjacent cell; collision resolution must split them.
    w = grid(4, 4, blocked=[(0, 0)])
    a = Troll(0, 2, 0, 1, 1, 1, [1, 0, 0, 0, 0, 0])
    b = Troll(1, 1, 1, 1, 1, 1, [1, 0, 0, 0, 0, 0])
    cmds = decide(base(w, [], [a, b]), gather_only())
    landings = _landings(cmds)
    assert len(landings) == 2 and len(set(landings)) == 2


def test_emits_version_message_on_first_turn_only():
    w = grid(4, 4, blocked=[(0, 0)])
    troll = Troll(0, 1, 0, 1, 1, 1, [0]*6)
    t1 = decide(base(w, [], [troll], turn=1), gather_only())
    assert t1[0] == f"MSG v{VERSION}"
    t2 = decide(base(w, [], [troll], turn=2), gather_only())
    assert not any(c.startswith("MSG") for c in t2)


def test_empty_returns_wait():
    w = grid(4, 4, blocked=[(0, 0)])
    cmds = decide(base(w, [], []), gather_only())
    assert cmds == ["WAIT"]


def test_decide_plants_when_enabled_and_troll_idle_at_shack():
    w = grid(6, 6, blocked=[(0, 0)])
    troll = Troll(0, 0, 1, 1, 1, 1, [0]*6)      # empty, adjacent to shack
    st = State(walkable=w, my_shack=(0, 0), opp_shack=(15, 7),
               my_inventory=[0, 0, 0, 5, 0, 0], opp_inventory=[0]*6,
               trees=[], my_trolls=[troll], opp_trolls=[], turn=2)
    p = dict(PARAMS)
    p["plant_enabled"] = True
    p["max_trolls"] = 0          # isolate planting from training
    assert "PICK 0 BANANA" in decide(st, p)


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
