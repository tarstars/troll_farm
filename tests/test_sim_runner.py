from sim.mapgen import generate
from sim.runner import play_game, win_rate
from bot.main import PARAMS


def test_play_game_runs_and_returns_scores():
    log = []
    ours, boss = play_game(generate(1), PARAMS, max_turns=30, log=log)
    assert isinstance(ours, int) and isinstance(boss, int)
    assert len(log) == 30
    assert all("id" in u and "pos" in u for u in log[0][1])


def test_win_rate_summarises_multiple_games():
    r = win_rate(range(3), PARAMS)
    assert r["games"] == 3 and 0.0 <= r["win_rate"] <= 1.0
