"""Tests for the cluster entrypoint's mid-run salvage.

The salvage is the only thing that survives a preemption, because a preempted operation restarts
its job **from scratch** rather than resuming. On 2026-09-01 the two entropy arms were preempted
five times between them; the salvage of the day kept only the newest checkpoint, so roughly twenty
job-hours yielded two late checkpoints at unrelated ages and no age-matched series — precisely
what the measurement needed. What is pinned here is that a preemption now leaves the *whole*
series recoverable:

1. every checkpoint is uploaded, each under its own name, and `mid-run-latest.pt` still holds the
   newest one;
2. a checkpoint already kept is not uploaded again on a later beat (the salvage must not grow
   with the square of the run's length);
3. one beat uploads at most `SALVAGE_PER_BEAT` new checkpoints, and the backlog drains on the
   beats that follow;
4. an upload that raises does not stop the heartbeat — a flaky cluster write must never kill a
   job that is training happily.
"""

from __future__ import annotations

import importlib.util
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NN_BOT = ROOT / "local_claude_1" / "nn-bot"


def load_entrypoint(work: Path):
    """Import the entrypoint with `work` as its working directory, so OUTPUTS points inside it."""

    previous = Path.cwd()
    import os

    os.chdir(work)
    try:
        spec = importlib.util.spec_from_file_location(
            "yt_ppo_entrypoint_under_test", NN_BOT / "yt_ppo_entrypoint.py"
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        os.chdir(previous)


class Beats:
    """A stop-event that lets the heartbeat run exactly `n` beats, then stops it."""

    def __init__(self, n: int) -> None:
        self.remaining = n
        self.event = threading.Event()

    def wait(self, _period: float) -> bool:
        if self.remaining <= 0:
            return True  # "stop is set" -> the loop exits
        self.remaining -= 1
        return False


@pytest.fixture()
def staged(tmp_path, monkeypatch):
    """An entrypoint module whose outputs directory is real and whose uploads are recorded."""

    work = tmp_path / "work"
    (work / "outputs").mkdir(parents=True)
    module = load_entrypoint(work)
    uploads: list[tuple[str, str]] = []

    def fake_upload(local_path: Path, remote_path: str) -> None:
        uploads.append((Path(local_path).name, remote_path))

    monkeypatch.setattr(module, "upload_file", fake_upload)
    monkeypatch.setenv("TROLL_FARM_YT_OUTPUT_FILE", "//runs/r/outputs/troll_farm_output.tar.gz")
    return module, work / "outputs", uploads


def write_checkpoints(outputs: Path, updates: list[int]) -> None:
    """Create checkpoint files with increasing modification times, as the trainer does."""

    import os
    import time

    for index, update in enumerate(updates):
        path = outputs / f"checkpoint-u{update:06d}.pt"
        path.write_bytes(b"x" * 16)
        stamp = time.time() + index  # strictly increasing, so "newest" is unambiguous
        os.utime(path, (stamp, stamp))


def salvaged_names(uploads: list[tuple[str, str]]) -> list[str]:
    return [remote.rsplit("/", 1)[-1] for _, remote in uploads]


def test_every_checkpoint_is_kept_not_only_the_newest(staged):
    module, outputs, uploads = staged
    write_checkpoints(outputs, [250, 500, 750])
    (outputs / "train.log").write_text('{"update": 750}\n')

    beats = Beats(6)  # the salvage runs on every sixth beat
    module.heartbeat_loop(beats, minutes=0.0, started=0.0)

    kept = salvaged_names(uploads)
    for update in (250, 500, 750):
        assert f"mid-run-checkpoint-u{update:06d}.pt" in kept, f"u{update} was not kept: {kept}"
    assert "mid-run-latest.pt" in kept
    assert "mid-run-train.log" in kept


def test_a_kept_checkpoint_is_not_uploaded_again(staged):
    module, outputs, uploads = staged
    write_checkpoints(outputs, [250, 500])
    (outputs / "train.log").write_text('{"update": 500}\n')

    beats = Beats(12)  # two salvage beats, with a new checkpoint appearing between them
    original_wait = beats.wait

    def wait_and_grow(period: float) -> bool:
        stop = original_wait(period)
        if beats.remaining == 5:  # after the first salvage beat
            write_checkpoints(outputs, [750])
        return stop

    beats.wait = wait_and_grow  # type: ignore[method-assign]
    module.heartbeat_loop(beats, minutes=0.0, started=0.0)

    kept = salvaged_names(uploads)
    assert kept.count("mid-run-checkpoint-u000250.pt") == 1
    assert kept.count("mid-run-checkpoint-u000500.pt") == 1
    assert kept.count("mid-run-checkpoint-u000750.pt") == 1


def test_one_beat_uploads_at_most_the_cap_and_the_backlog_drains(staged, monkeypatch):
    module, outputs, uploads = staged
    monkeypatch.setattr(module, "SALVAGE_PER_BEAT", 2)
    write_checkpoints(outputs, [250, 500, 750, 1000, 1250])
    (outputs / "train.log").write_text('{"update": 1250}\n')

    module.heartbeat_loop(Beats(6), minutes=0.0, started=0.0)
    after_one = [name for name in salvaged_names(uploads) if name.startswith("mid-run-checkpoint")]
    assert len(after_one) == 2, after_one
    # oldest first, so an interrupted run still holds a contiguous early series
    assert after_one == ["mid-run-checkpoint-u000250.pt", "mid-run-checkpoint-u000500.pt"]

    uploads.clear()
    module.heartbeat_loop(Beats(12), minutes=0.0, started=0.0)
    after_more = [name for name in salvaged_names(uploads) if name.startswith("mid-run-checkpoint")]
    # a fresh loop has a fresh memory, so it re-keeps from the start, still two per beat
    assert len(after_more) == 4, after_more


def test_a_failing_upload_does_not_kill_the_heartbeat(staged, monkeypatch):
    module, outputs, uploads = staged
    write_checkpoints(outputs, [250])
    (outputs / "train.log").write_text('{"update": 250}\n')

    def explode(local_path: Path, remote_path: str) -> None:
        raise RuntimeError("the cluster said no")

    monkeypatch.setattr(module, "upload_file", explode)
    module.heartbeat_loop(Beats(6), minutes=0.0, started=0.0)  # must return, not raise
