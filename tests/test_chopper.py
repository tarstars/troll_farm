from bot.main import (chop_command, _best_chop_target, training_command, decide,
                      bfs_distances, State, Troll, Tree, PARAMS)


def grid(w, h, blocked=()):
    return {(x, y) for x in range(w) for y in range(h)} - set(blocked)


def st(walkable, my_shack, opp_shack, trees, my_trolls, iron=frozenset(), inv=None):
    return State(walkable=walkable, my_shack=my_shack, opp_shack=opp_shack,
                 my_inventory=inv if inv is not None else [0]*6, opp_inventory=[0]*6,
                 trees=trees, my_trolls=my_trolls, opp_trolls=[], turn=5, iron_cells=iron)


def test_chopper_chops_tree_underfoot():
    w = grid(8, 1, blocked=[(0, 0)])
    ch = Troll(0, 3, 0, 1, 3, 0, [0]*6, chop_power=2)
    s = st(w, (0, 0), (7, 0), [Tree("PLUM", 3, 0, 4, 12, 0, 5)], [ch])
    assert chop_command(s, ch, set(), {(3, 0): 0}, PARAMS)[0] == "CHOP 0"


def test_chopper_targets_tree_nearest_enemy_camp():
    w = grid(8, 1, blocked=[(0, 0)])
    ch = Troll(0, 1, 0, 1, 3, 0, [0]*6, chop_power=2)
    trees = [Tree("PLUM", 2, 0, 4, 12, 0, 5), Tree("PLUM", 6, 0, 4, 12, 0, 5)]
    d = bfs_distances(w, [(1, 0)])
    assert _best_chop_target(st(w, (0, 0), (7, 0), trees, [ch]), ch, set(), d).pos == (6, 0)


def test_chopper_banks_wood_when_full():
    w = grid(8, 1, blocked=[(0, 0)])
    ch = Troll(0, 1, 0, 1, 2, 0, [0, 0, 0, 0, 0, 2], chop_power=2)  # carrying 2 wood, full
    d = bfs_distances(w, [(1, 0)])
    assert chop_command(st(w, (0, 0), (7, 0), [], [ch]), ch, set(), d, PARAMS)[0] == "DROP 0"


def test_chopper_mines_adjacent_iron():
    w = grid(8, 2, blocked=[(0, 0), (2, 1)])
    ch = Troll(0, 2, 0, 1, 3, 0, [0]*6, chop_power=2)
    s = st(w, (0, 0), (7, 1), [], [ch], iron=frozenset({(2, 1)}))
    assert chop_command(s, ch, set(), {(2, 0): 0}, PARAMS)[0] == "MINE 0"


def test_trains_a_chopper_first_in_bronze():
    troll = Troll(0, 1, 0, 1, 1, 1, [0]*6)
    s = st(grid(8, 2, blocked=[(0, 0)]), (0, 0), (7, 1), [], [troll],
           iron=frozenset({(3, 1)}), inv=[10, 10, 10, 10, 10, 0])
    cmd = training_command(s, PARAMS)
    assert cmd is not None and cmd.startswith("TRAIN") and cmd.split()[-1] != "0"


def test_no_chopper_training_without_iron_terrain():
    troll = Troll(0, 1, 0, 1, 1, 1, [0]*6)
    s = st(grid(8, 2, blocked=[(0, 0)]), (0, 0), (7, 1), [], [troll],
           inv=[10, 10, 10, 10, 0, 0])           # league-2: no iron terrain
    cmd = training_command(s, PARAMS)
    assert cmd is not None and cmd.endswith(" 0")  # only chop-0 specs


def test_decide_routes_chopper_to_chop():
    w = grid(8, 1, blocked=[(0, 0)])
    ch = Troll(0, 3, 0, 1, 3, 0, [0]*6, chop_power=2)
    s = st(w, (0, 0), (7, 0), [Tree("PLUM", 3, 0, 4, 12, 0, 5)], [ch],
           iron=frozenset({(5, 0)}))
    p = dict(PARAMS); p["plant_enabled"] = False
    assert "CHOP 0" in decide(s, p)


def test_chop1_starting_troll_does_not_block_real_chopper_training():
    # Bronze's starting troll has chopPower 1; it must NOT count as the chopper
    # (>=2), so we still train a real chopper instead of useless chop-1 trolls.
    starter = Troll(0, 1, 0, 1, 1, 1, [0]*6, chop_power=1)
    s = st(grid(8, 2, blocked=[(0, 0)]), (0, 0), (7, 1), [], [starter],
           iron=frozenset({(3, 1)}), inv=[10, 10, 10, 10, 10, 0])
    cmd = training_command(s, PARAMS)
    assert cmd is not None and cmd.split()[-1] != "0"   # trains chop>0


def test_chopper_stops_mining_once_iron_target_met():
    w = grid(8, 2, blocked=[(0, 0), (2, 1)])
    ch = Troll(0, 2, 0, 1, 3, 0, [0]*6, chop_power=2)
    s = st(w, (0, 0), (7, 1), [Tree("PLUM", 5, 0, 4, 12, 0, 5)], [ch],
           iron=frozenset({(2, 1)}), inv=[0, 0, 0, 0, 99, 0])   # iron already banked
    cmd, _ = chop_command(s, ch, set(), bfs_distances(w, [(2, 0)]), PARAMS)
    assert not cmd.startswith("MINE")    # enough iron -> go chop, don't keep mining
