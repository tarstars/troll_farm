from sim.state import from_ascii, SimUnit, SimPlant
from sim.boss import boss_decide


def test_boss_trains_second_troll():
    g = from_ascii(["10...."])           # player 0's shack at (0,0), player 1's shack at (1,0)
    g.units = [SimUnit(0, 1, 2, 0, 1, 1, 1, 0, [0]*6)]   # only one troll
    cmds = boss_decide(g, 1)
    assert "TRAIN 1 1 1 0" in cmds


def test_boss_harvests_tree_underfoot():
    g = from_ascii(["10...."])
    g.units = [SimUnit(0, 1, 2, 0, 1, 1, 1, 0, [0]*6),
               SimUnit(1, 1, 0, 0, 1, 1, 1, 0, [0]*6)]   # 2 trolls -> no train
    g.plants = [SimPlant("PLUM", 2, 0, 4, 4, 2, 5)]
    cmds = boss_decide(g, 1)
    assert "HARVEST 0" in cmds


def test_boss_returns_to_shack_when_full():
    g = from_ascii(["10...."])
    g.units = [SimUnit(0, 1, 3, 0, 1, 1, 1, 0, [1, 0, 0, 0, 0, 0]),
               SimUnit(1, 1, 5, 0, 1, 1, 1, 0, [0]*6)]
    cmds = boss_decide(g, 1)
    assert any(c.startswith("MOVE 0 0 0") or c == "DROP 0" for c in cmds)
