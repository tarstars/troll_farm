"""Tests for the fixed-age bench driver.

The driver exists so that both arms of a paired experiment are benched with byte-identical flags;
the failure that matters is a silent difference between arms, not a crash. So the tests pin:

1. checkpoint discovery by exact age, including the salvaged `mid-run-` copies;
2. that an ambiguous directory raises instead of silently picking one checkpoint — two runs'
   outputs sharing a directory would otherwise mix arms;
3. the skip rule, so re-running as checkpoints land never repeats or overwrites work;
4. that the command is identical across arms apart from the checkpoint and the output path.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NN_BOT = ROOT / "local_claude_1" / "nn-bot"

spec = importlib.util.spec_from_file_location("bench_ages", NN_BOT / "bench_ages.py")
bench_ages = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = bench_ages
spec.loader.exec_module(bench_ages)


def touch(directory: Path, name: str) -> Path:
    path = directory / name
    path.write_bytes(b"checkpoint")
    return path


def test_finds_the_checkpoint_for_an_exact_age(tmp_path):
    touch(tmp_path, "ppo-yt-e00b-update000500.pt")
    touch(tmp_path, "ppo-yt-e00b-update002500.pt")
    touch(tmp_path, "ppo-yt-e00b-latest.pt")

    assert bench_ages.checkpoint_for_age(tmp_path, 500).name == "ppo-yt-e00b-update000500.pt"
    assert bench_ages.checkpoint_for_age(tmp_path, 2500).name == "ppo-yt-e00b-update002500.pt"
    assert bench_ages.checkpoint_for_age(tmp_path, 1500) is None


def test_a_salvaged_copy_resolves_too(tmp_path):
    touch(tmp_path, "mid-run-ppo-yt-e01b-update001500.pt")
    found = bench_ages.checkpoint_for_age(tmp_path, 1500)
    assert found is not None and found.name.startswith("mid-run-")


def test_two_runs_in_one_directory_raise_rather_than_guess(tmp_path):
    touch(tmp_path, "ppo-yt-e00b-update001500.pt")
    touch(tmp_path, "ppo-yt-e01b-update001500.pt")
    with pytest.raises(ValueError, match="2 checkpoints for update 1500"):
        bench_ages.checkpoint_for_age(tmp_path, 1500)


def test_age_500_is_not_matched_by_age_2500(tmp_path):
    """`*update000500.pt` must not be satisfied by `...update002500.pt`."""

    touch(tmp_path, "run-update002500.pt")
    assert bench_ages.checkpoint_for_age(tmp_path, 500) is None


def test_pending_splits_done_runnable_and_missing(tmp_path):
    checkpoints = tmp_path / "run"
    out = tmp_path / "out"
    checkpoints.mkdir()
    out.mkdir()
    touch(checkpoints, "r-update000500.pt")
    touch(checkpoints, "r-update001000.pt")
    (out / "bench-tag-u500.json").write_text("{}")

    to_run, done, missing = bench_ages.pending_ages(checkpoints, out, "tag", [500, 1000, 1500])
    assert done == [500]
    assert [age for age, _ in to_run] == [1000]
    assert missing == [1500]


def test_the_command_differs_between_arms_only_where_it_must(tmp_path):
    common = dict(
        panel="panel.jsonl",
        bot="bot.rs",
        library="lib.so",
        seed=0,
        train_p=0.02,
        threads=2,
        nice=19,
        python="python3",
        script="bench.py",
        replays=False,
    )
    left = bench_ages.bench_command(
        checkpoint=tmp_path / "e00b-update001500.pt",
        out_json=tmp_path / "bench-e00b-u1500.json",
        **common,
    )
    right = bench_ages.bench_command(
        checkpoint=tmp_path / "e01b-update001500.pt",
        out_json=tmp_path / "bench-e01b-u1500.json",
        **common,
    )
    differences = [(a, b) for a, b in zip(left, right) if a != b]
    assert len(left) == len(right)
    assert len(differences) == 2, differences  # the checkpoint and the output path, nothing else
    assert all("e00b" in a and "e01b" in b for a, b in differences)


def test_replays_are_requested_or_suppressed_explicitly(tmp_path):
    base = dict(
        checkpoint=tmp_path / "c.pt",
        out_json=tmp_path / "bench-tag-u500.json",
        panel="p", bot="b", library="l", seed=0, train_p=0.02,
        threads=2, nice=19, python="python3", script="bench.py",
    )
    with_replays = bench_ages.bench_command(replays=True, **base)
    without = bench_ages.bench_command(replays=False, **base)
    assert "--replays" in with_replays and "--no-replays" not in with_replays
    assert "--no-replays" in without and "--replays" not in without
