#!/usr/bin/env python3
"""Tests for the field aggregator (rung 1 of the port's selector).

    python3 -m pytest claude_1/h2h-panel/test_field.py -q

No compiled bot is needed: the runs are synthetic files in the shape `h2h.py` writes, plus the
committed validity runs under `results/` for one reading on real rows.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import field  # noqa: E402

RESULTS = HERE / "results"
PANEL = "panel-sha"
OPP = "opponent-sha"


def run_file(path: Path, rows, *, policy="cand", bot=OPP, panel=PANEL, faults=0) -> Path:
    payload = {
        "panel_sha256": panel, "bot_sha256": bot, "policy_sha256": policy,
        "illegal_commands_total": faults, "timeouts_total": 0, "referee_errors_total": 0,
        "rows": rows,
    }
    path.write_text(json.dumps(payload))
    return path


def row(map_hash, seat, own, theirs):
    return {"map_hash": map_hash, "policy_seat": seat, "policy_won": own > theirs,
            "tie": own == theirs, "policy_score": own, "bot_score": theirs}


def rows_from(scores):
    """scores: {map: {seat: (own, theirs)}}"""
    return [row(m, s, a, b) for m, seats in scores.items() for s, (a, b) in seats.items()]


def maps(n):
    return {f"m{i:02d}": {0: (100, 90), 1: (100, 90)} for i in range(n)}


def pair(tmp_path, name, cand_scores, champ_scores, expected=0, **kw):
    c = run_file(tmp_path / f"{name}-cand.json", rows_from(cand_scores), policy="cand", **kw)
    k = run_file(tmp_path / f"{name}-champ.json", rows_from(champ_scores), policy="champ", **kw)
    return field.Pair(name, c, k, expected)


def test_identical_runs_read_zero_with_a_zero_width_interval(tmp_path):
    p = pair(tmp_path, "a", maps(5), maps(5))
    report = field.compute([p], draws=200)
    o = report["per_opponent"][0]
    assert o["win_diff"]["mean"] == 0 and o["win_diff"]["interval_95"] == [0, 0]
    assert o["margin_diff"]["mean"] == 0 and o["margin_diff"]["interval_95"] == [0, 0]
    assert report["verdict"] == field.STRADDLES


def test_a_uniform_shift_is_read_exactly(tmp_path):
    cand = {m: {s: (own + 7, theirs) for s, (own, theirs) in seats.items()} for m, seats in maps(6).items()}
    p = pair(tmp_path, "a", cand, maps(6))
    report = field.compute([p], draws=200)
    o = report["per_opponent"][0]
    assert o["margin_diff"]["mean"] == 7 and o["margin_diff"]["interval_95"] == [7, 7]
    assert o["win_diff"]["mean"] == 0            # both already won every cell
    assert report["verdict"] == field.STRADDLES  # a margin-only shift does not move the verdict (ruling 09-02 09:23Z)


def test_the_verdict_reads_the_win_indicator_not_the_margin(tmp_path):
    # the champion loses every cell by 10; the candidate wins every cell by 1: the win indicator is +1
    # on every map (interval [1, 1]) while the margin moves by 11 -- ABOVE comes from the wins
    lost = {m: {0: (90, 100), 1: (90, 100)} for m in maps(6)}
    won = {m: {0: (101, 100), 1: (101, 100)} for m in maps(6)}
    report = field.compute([pair(tmp_path, "a", won, lost)], draws=200)
    f = report["field"]
    assert f["win_diff"]["mean"] == 1 and f["win_diff"]["interval_95"] == [1, 1]
    assert f["margin_diff"]["mean"] == 11
    assert report["verdict"] == field.ABOVE
    # the converse: the candidate loses every cell the champion won, by a hair -- BELOW on the wins
    # even though the margin difference is small
    barely_lost = {m: {0: (99, 100), 1: (99, 100)} for m in maps(6)}
    report = field.compute([pair(tmp_path, "b", barely_lost, maps(6))], draws=200)
    assert report["field"]["win_diff"]["interval_95"] == [-1, -1]
    assert report["field"]["margin_diff"]["mean"] == -11
    assert report["verdict"] == field.BELOW


def test_both_seats_of_a_map_travel_together(tmp_path):
    # seat 0 +10, seat 1 -10 on every map: per map the difference is exactly 0, so the interval is
    # [0, 0]; treating the seats as independent games would give a wide interval around 0.
    cand = {m: {0: (110, 90), 1: (90, 90)} for m in maps(8)}
    p = pair(tmp_path, "a", cand, maps(8))
    report = field.compute([p], draws=500)
    o = report["per_opponent"][0]
    assert o["margin_diff"]["mean"] == 0 and o["margin_diff"]["interval_95"] == [0, 0]
    assert o["win_diff"]["interval_95"] == [-0.5, -0.5]   # the seat-1 tie is a lost win, seat 0 was won already


def test_the_field_pools_every_opponent_per_map(tmp_path):
    base = maps(4)
    plus = {m: {s: (own + 4, theirs) for s, (own, theirs) in seats.items()} for m, seats in base.items()}
    minus = {m: {s: (own - 2, theirs) for s, (own, theirs) in seats.items()} for m, seats in base.items()}
    a = pair(tmp_path, "a", plus, base, bot="opp-a")
    b = pair(tmp_path, "b", minus, base, bot="opp-b")
    report = field.compute([a, b], draws=200)
    assert report["per_opponent"][0]["margin_diff"]["mean"] == 4
    assert report["per_opponent"][1]["margin_diff"]["mean"] == -2
    f = report["field"]
    assert f["margin_diff"]["mean"] == 1 and f["margin_diff"]["interval_95"] == [1, 1]
    assert f["margin_diff"]["maps"] == 4 and f["margin_diff"]["cells"] == 16
    assert f["win_diff"]["mean"] == 0             # every cell was already a win on both sides
    assert report["verdict"] == field.STRADDLES   # the verdict reads the win indicator


def test_a_pair_on_different_panels_or_opponents_or_cells_is_refused(tmp_path):
    with pytest.raises(ValueError, match="panel differs"):
        c = run_file(tmp_path / "c.json", rows_from(maps(3)), panel="p1")
        k = run_file(tmp_path / "k.json", rows_from(maps(3)), panel="p2")
        field.Pair("a", c, k, 0)
    with pytest.raises(ValueError, match="opponent differs"):
        c = run_file(tmp_path / "c2.json", rows_from(maps(3)), bot="o1")
        k = run_file(tmp_path / "k2.json", rows_from(maps(3)), bot="o2")
        field.Pair("a", c, k, 0)
    with pytest.raises(ValueError, match="cells differ"):
        c = run_file(tmp_path / "c3.json", rows_from(maps(3)))
        k = run_file(tmp_path / "k3.json", rows_from(maps(4)))
        field.Pair("a", c, k, 0)
    with pytest.raises(ValueError, match="expected 400 cells"):
        c = run_file(tmp_path / "c4.json", rows_from(maps(3)))
        k = run_file(tmp_path / "k4.json", rows_from(maps(3)))
        field.Pair("a", c, k, 400)


def test_faults_or_a_changing_candidate_make_the_reading_inconclusive(tmp_path):
    c = run_file(tmp_path / "c.json", rows_from(maps(3)), faults=2)
    k = run_file(tmp_path / "k.json", rows_from(maps(3)))
    report = field.compute([field.Pair("a", c, k, 0)], draws=100)
    assert report["clean"] is False and report["verdict"] == field.INCONCLUSIVE
    assert report["per_opponent"][0]["faults"]["candidate"] == {"illegal_commands": 2}

    a = pair(tmp_path, "a", maps(3), maps(3), bot="opp-a")
    c2 = run_file(tmp_path / "c2.json", rows_from(maps(3)), policy="other-cand", bot="opp-b")
    k2 = run_file(tmp_path / "k2.json", rows_from(maps(3)), policy="champ", bot="opp-b")
    report = field.compute([a, field.Pair("b", c2, k2, 0)], draws=100)
    assert report["verdict"] == field.INCONCLUSIVE
    assert any("candidate is not one file" in p for p in report["problems"])


def test_repeated_opponent_names_are_refused(tmp_path):
    a = pair(tmp_path, "a", maps(2), maps(2))
    with pytest.raises(ValueError, match="repeat"):
        field.compute([a, a], draws=10)


@pytest.mark.skipif(not (RESULTS / "orchard6-vs-champion.json").exists(), reason="validity runs absent")
def test_the_validity_runs_reproduce_the_p0_reading():
    # Against the opponent "champion": orchard 6 as the candidate, the champion as the champion
    # (its run against itself reads exactly zero), so the difference is orchard 6's P-0 reading.
    p = field.Pair("champion", RESULTS / "orchard6-vs-champion.json",
                   RESULTS / "champion-vs-champion.json", 400)
    report = field.compute([p])
    o = report["per_opponent"][0]
    assert o["margin_diff"]["mean"] == pytest.approx(-26.04, abs=0.01)
    assert o["margin_diff"]["interval_95"] == pytest.approx([-30.57, -21.55], abs=0.01)
    assert o["win_diff"]["mean"] == pytest.approx(0.1625 - 113 / 400, abs=1e-6)   # the champion vs itself wins 113 of 400 (174 ties)
    assert report["field"]["margin_diff"] == o["margin_diff"]
    assert report["verdict"] == field.BELOW
    text = field.render(report)
    assert "FIELD" in text and text.endswith("VERDICT: FIELD_BELOW_ZERO")


def test_the_command_line_writes_the_json(tmp_path, monkeypatch, capsys):
    c = run_file(tmp_path / "c.json", rows_from(maps(3)))
    k = run_file(tmp_path / "k.json", rows_from(maps(3)))
    out = tmp_path / "field.json"
    monkeypatch.setattr(sys, "argv", ["field.py", "--opponent", f"x={c},{k}", "--expected-cells", "6",
                                      "--bootstrap", "50", "--json-out", str(out)])
    assert field.main() == 0
    assert json.loads(out.read_text())["verdict"] == field.STRADDLES
    assert "VERDICT: FIELD_STRADDLES_ZERO" in capsys.readouterr().out
