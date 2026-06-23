"""Tests for tree ripeness prediction (mirrors referee Plant.tick, no water)."""
from bot.main import predict_fruits


def test_full_size_tree_produces_fruit_when_cooldown_hits_zero():
    # size 4, 2 fruits, cooldown 3 (PLUM base 8): after 3 ticks cd->0, produces 3rd fruit
    assert predict_fruits("PLUM", size=4, fruits=2, cooldown=3, ticks=3) == 3


def test_full_size_tree_holds_fruit_before_cooldown_elapses():
    # only 2 ticks: cooldown reaches 1, no production yet
    assert predict_fruits("PLUM", size=4, fruits=2, cooldown=3, ticks=2) == 2


def test_growing_tree_grows_size_before_producing_fruit():
    # size 2, no fruit, cd 1 (BANANA base 6): tick1 grows to size 3 (still 0 fruit)
    assert predict_fruits("BANANA", size=2, fruits=0, cooldown=1, ticks=1) == 0
    # needs to grow 2->3 (tick1) ->4 (tick7) then produce 1st fruit at tick13
    assert predict_fruits("BANANA", size=2, fruits=0, cooldown=1, ticks=12) == 0
    assert predict_fruits("BANANA", size=2, fruits=0, cooldown=1, ticks=13) == 1


def test_idle_full_tree_stays_capped_at_three():
    # size 4, 3 fruits, cd 0: nothing changes regardless of ticks
    assert predict_fruits("APPLE", size=4, fruits=3, cooldown=0, ticks=5) == 3


def test_cooldown_zero_produces_on_first_tick():
    # size 4, 1 fruit, cd 0: first tick immediately produces (cd-- skipped, cd already 0)
    assert predict_fruits("PLUM", size=4, fruits=1, cooldown=0, ticks=1) == 2
