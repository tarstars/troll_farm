#!/usr/bin/env python3
"""Tests for the head-to-head panel driver and the panel maker.

    python3 -m pytest claude_1/h2h-panel/test_h2h.py -q      (or: python3 claude_1/h2h-panel/test_h2h.py)

The two games that need compiled bots (the mirrored game) compile the champion and orchard 6
once per session, about ten seconds.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import h2h                      # noqa: E402
import make_panel               # noqa: E402
import bench                    # noqa: E402
import gate1                    # noqa: E402
import semantic_harness as sh   # noqa: E402

REPO = HERE.parent.parent
CHAMPION = REPO / "cgauto" / "submissions" / "candidate-champion-denial-off-v6-instrument.rs"
ORCHARD6 = REPO / "cgauto" / "submissions" / "candidate-orchard6-v6-instrument.rs"
SLICE = REPO / "local_claude_1" / "nn-bot" / "maps-slice-1000.jsonl"

_BIN: dict[str, Path] = {}
_TMP = tempfile.TemporaryDirectory(prefix="test-h2h-")


def binary(src: Path) -> Path:
    if src.name not in _BIN:
        out = Path(_TMP.name) / (src.stem + ".bin")
        sh.compile_text(src.read_text(), out, crate="t_" + src.stem.replace("-", "_"))
        _BIN[src.name] = out
    return _BIN[src.name]


def first_panel_map():
    line = (HERE / "panel-200-seed1.jsonl").read_text().splitlines()[0]
    item = json.loads(line)
    return item["rec"], item["draw"]


# --------------------------------------------------------------------------- apply_pair

def test_apply_pair_counts_errors_on_both_seats_and_raises_on_neither():
    ref = bench.make_referee(bench._test_map(), [5, 5, 5, 5, 5, 0])
    assert h2h.apply_pair(ref, "WAIT", "BOGUS 1") == (0, 1)
    assert h2h.apply_pair(ref, "FLY 0", "WAIT") == (1, 0)
    assert sum(ref.error_counts.values()) == 1
    assert sum(ref.seat1_error_counts.values()) == 1
    assert ref.turn == 3


def test_apply_pair_executes_both_seats_moves():
    rec = bench._test_map()
    ref = bench.make_referee(rec, [5, 5, 5, 5, 5, 0])
    before = {uid: tuple(u["cell"]) for uid, u in ref.units.items()}
    # every unit is at its shack; a MOVE toward the other shack changes the cell of both
    p0, p1 = tuple(rec["shacks"]["p0"]), tuple(rec["shacks"]["p1"])
    h2h.apply_pair(ref, f"MOVE 0 {p1[0]} {p1[1]}", f"MOVE 1 {p0[0]} {p0[1]}")
    after = {uid: tuple(u["cell"]) for uid, u in ref.units.items()}
    assert after[0] != before[0] and after[1] != before[1]


# --------------------------------------------------------------------------- the game

def test_mirrored_game_swaps_the_scores():
    """orchard 6 on seat 0 against the champion IS the game champion-on-seat-1 against orchard 6:
    the same referee, the same commands, only the label of who is the policy changes."""
    rec, draw = first_panel_map()
    a = h2h.play(rec, draw, binary(ORCHARD6), binary(CHAMPION), policy_seat=0, turns=120)
    b = h2h.play(rec, draw, binary(CHAMPION), binary(ORCHARD6), policy_seat=1, turns=120)
    assert (a["policy_score"], a["bot_score"]) == (b["bot_score"], b["policy_score"])
    assert a["turns"] == b["turns"] and a["ended_reason"] == b["ended_reason"]
    assert a["policy_trains"] == b["bot_trains"]
    assert a["policy_command_errors"] == a["bot_command_errors"] == 0
    assert a["timeouts"] == 0


def test_seat_one_is_the_exchanged_game_for_one_bot():
    """The champion against itself: the seat-0 game and the seat-1 game are the same game."""
    rec, draw = first_panel_map()
    a = h2h.play(rec, draw, binary(CHAMPION), binary(CHAMPION), policy_seat=0, turns=80)
    b = h2h.play(rec, draw, binary(CHAMPION), binary(CHAMPION), policy_seat=1, turns=80)
    assert (a["policy_score"], a["bot_score"]) == (b["bot_score"], b["policy_score"])


def test_replay_keeps_both_lines_each_turn():
    rec, draw = first_panel_map()
    a = h2h.play(rec, draw, binary(CHAMPION), binary(ORCHARD6), policy_seat=0, turns=5,
                 keep_replay=True)
    assert len(a["replay"]) == 5
    assert all("MSG" in t["seat0"] and "MSG" in t["seat1"] for t in a["replay"])


# --------------------------------------------------------------------------- the report

def test_rows_read_by_gate1_bench(tmp_path):
    rec, draw = first_panel_map()
    panel = tmp_path / "panel.jsonl"
    panel.write_text(json.dumps({"rec": rec, "draw": draw, "profile": "h2h"}) + "\n")
    report = h2h.run_panel(ORCHARD6, CHAMPION, panel, jobs=1, turns=30)
    out = tmp_path / "r.json"
    out.write_text(json.dumps(report))
    b = gate1.Bench(out)
    assert set(b.cells) == {(rec["map_hash"], 0), (rec["map_hash"], 1)}
    assert b.execution_faults() == {}
    for key in b.cells:
        assert b.won(key) in (0, 1)
        assert isinstance(b.margin(key), float)
    assert report["reading"]["maps"] == 1 and report["reading"]["games"] == 2
    assert report["policy_sha256"] != report["bot_sha256"]


def test_paired_reading_carries_both_seats_of_a_map_together():
    # ten maps, the policy wins seat 0 and loses seat 1 on every map -> every map's value is 0.5,
    # so the bootstrap has nothing to spread: a zero-width interval at exactly one half
    rows = [{"map_hash": f"m{i}", "policy_seat": s, "policy_won": s == 0, "tie": False,
             "policy_score": 1 - s, "bot_score": s} for i in range(10) for s in (0, 1)]
    r = h2h.paired_reading(rows, draws=500)
    assert r["win_rate"] == 0.5 and r["win_rate_interval_95"] == [0.5, 0.5]
    assert r["maps_won_on_both_seats"] == 0 and r["maps_won_on_neither_seat"] == 0
    # the same rows read as 20 independent games would have spread; that is what pairing removes
    rows2 = [dict(r_, map_hash=f"m{i}") for i, r_ in enumerate(rows)]
    r2 = h2h.paired_reading(rows2, draws=500)
    assert r2["win_rate_interval_95"][0] < 0.5 < r2["win_rate_interval_95"][1]


# --------------------------------------------------------------------------- the panel

def test_make_panel_is_deterministic_and_distinct(tmp_path):
    records = [json.loads(l) for l in SLICE.read_text().splitlines()[:60]]
    a = make_panel.draw_panel(records, 20, 1)
    b = make_panel.draw_panel(records, 20, 1)
    c = make_panel.draw_panel(records, 20, 2)
    assert [x["rec"]["map_hash"] for x in a] == [x["rec"]["map_hash"] for x in b]
    assert [x["draw"] for x in a] == [x["draw"] for x in b]
    assert [x["rec"]["map_hash"] for x in a] != [x["rec"]["map_hash"] for x in c]
    assert len({x["rec"]["map_hash"] for x in a}) == 20
    assert all(2 <= v <= 10 for x in a for v in x["draw"][:5]) and all(x["draw"][5] == 0 for x in a)


def test_the_committed_panel_matches_its_sidecar_and_manifest():
    panel = HERE / "panel-200-seed1.jsonl"
    digest = make_panel.sha_file(panel)
    assert (HERE / "panel-200-seed1.jsonl.sha256").read_text().split()[0] == digest
    manifest = json.loads((HERE / "panel-200-seed1.manifest.json").read_text())
    assert manifest["panel_sha256"] == digest and manifest["count"] == 200 and manifest["seed"] == 1
    items = [json.loads(l) for l in panel.read_text().splitlines()]
    assert len(items) == 200 and len({i["rec"]["map_hash"] for i in items}) == 200


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
