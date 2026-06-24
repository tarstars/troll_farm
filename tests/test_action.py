from bot.main import (gather_command, best_tree, State, Troll, Tree,
                      bfs_distances, _ortho_neighbors)


def grid(w, h, blocked=()):
    return {(x, y) for x in range(w) for y in range(h)} - set(blocked)


PARAMS = {"topup_radius": 0}  # default: never top up; bank when carrying


def fields(state, troll):
    shack_adj = [n for n in _ortho_neighbors(state.my_shack) if n in state.walkable]
    return bfs_distances(state.walkable, [troll.pos]), bfs_distances(state.walkable, shack_adj)


def make(walkable, shack, trees, troll):
    return State(walkable=walkable, my_shack=shack, opp_shack=(15, 7),
                 my_inventory=[0]*6, opp_inventory=[0]*6, trees=trees,
                 my_trolls=[troll], opp_trolls=[], turn=1)


def test_harvest_when_on_fruited_tree_with_capacity():
    w = grid(4, 4, blocked=[(0, 0)])
    tr = Troll(0, 2, 2, 1, 1, 1, [0]*6)
    st = make(w, (0, 0), [Tree("PLUM", 2, 2, 4, 4, 2, 5)], tr)
    dt, rd = fields(st, tr)
    assert gather_command(st, tr, set(), dt, rd, PARAMS) == ("HARVEST 0", (2, 2))


def test_full_troll_banks_via_move_then_drop():
    w = grid(4, 4, blocked=[(0, 0)])
    far = Troll(0, 3, 3, 1, 1, 1, [1, 0, 0, 0, 0, 0])    # full (cap 1)
    st = make(w, (0, 0), [], far)
    dt, rd = fields(st, far)
    assert gather_command(st, far, set(), dt, rd, PARAMS) == ("MOVE 0 0 0", None)
    near = Troll(0, 0, 1, 1, 1, 1, [1, 0, 0, 0, 0, 0])
    st2 = make(w, (0, 0), [], near)
    dt2, rd2 = fields(st2, near)
    assert gather_command(st2, near, set(), dt2, rd2, PARAMS) == ("DROP 0", None)


def test_empty_troll_moves_to_best_round_trip_tree():
    w = grid(8, 2, blocked=[(0, 0)])
    tr = Troll(0, 4, 0, 1, 1, 1, [0]*6)
    near = Tree("PLUM", 3, 0, 4, 4, 1, 5)
    far = Tree("PLUM", 5, 0, 4, 4, 1, 5)
    st = make(w, (0, 0), [near, far], tr)
    dt, rd = fields(st, tr)
    cmd, res = gather_command(st, tr, set(), dt, rd, PARAMS)
    assert cmd == "MOVE 0 3 0" and res == (3, 0)


def test_reserved_tree_is_skipped():
    w = grid(8, 2, blocked=[(0, 0)])
    tr = Troll(0, 4, 0, 1, 1, 1, [0]*6)
    near = Tree("PLUM", 3, 0, 4, 4, 1, 5)
    far = Tree("PLUM", 5, 0, 4, 4, 1, 5)
    st = make(w, (0, 0), [near, far], tr)
    dt, rd = fields(st, tr)
    cmd, res = gather_command(st, tr, {(3, 0)}, dt, rd, PARAMS)
    assert cmd == "MOVE 0 5 0" and res == (5, 0)


def test_spawn_on_shack_routes_out():
    w = grid(4, 1, blocked=[(0, 0)])
    tr = Troll(0, 0, 0, 1, 1, 1, [0]*6)        # on the shack
    st = make(w, (0, 0), [Tree("PLUM", 2, 0, 4, 4, 2, 5)], tr)
    dt, rd = fields(st, tr)
    cmd, _ = gather_command(st, tr, set(), dt, rd, PARAMS)
    assert cmd == "MOVE 0 2 0"


def test_tops_up_a_second_tree_when_radius_allows():
    w = grid(6, 1, blocked=[(0, 0)])
    tr = Troll(0, 2, 0, 1, 2, 1, [1, 0, 0, 0, 0, 0])   # cap 2, carrying 1
    st = make(w, (0, 0), [Tree("PLUM", 3, 0, 4, 4, 1, 5)], tr)
    dt, rd = fields(st, tr)
    cmd, res = gather_command(st, tr, set(), dt, rd, {"topup_radius": 5})
    assert cmd == "MOVE 0 3 0" and res == (3, 0)


def test_waits_when_no_reachable_tree():
    w = grid(4, 4, blocked=[(0, 0)])
    tr = Troll(0, 2, 2, 1, 1, 1, [0]*6)
    st = make(w, (0, 0), [], tr)
    dt, rd = fields(st, tr)
    assert gather_command(st, tr, set(), dt, rd, PARAMS) == ("WAIT", None)
