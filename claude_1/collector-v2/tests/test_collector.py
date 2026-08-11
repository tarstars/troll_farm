"""Tests for the B4 collector service (task `20260811-s3-collector-v2`).

These pin the behaviours that only show up when something goes wrong, because that is when an
unattended 05:47 service is least observable:

  - the cursor is written atomically and survives a crash mid-write (self-review finding F8)
  - the cursor is NOT advanced when the upload failed, so a failed day is retried, not lost
  - an upload collision escalates to `.rerun-N` instead of overwriting or giving up
  - a permanently-gone game (HTTP 422) is distinguished from a transient failure
  - every run emits an `exit=N` end marker, including the crash path

No network and no bucket: the platform client and the S3 client are both stubbed.

Run: `uvx pytest claude_1/collector-v2/tests -q`
"""

from __future__ import annotations

import io
import json
import sys
import urllib.error
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import collector  # noqa: E402
from collector import Cursor, atomic_write_json, fetch, upload_day  # noqa: E402
from packer import pack_day  # noqa: E402
from s3client import S3Error  # noqa: E402

DATE = "2026-08-11"


class FakePlatform:
    """Stands in for `PublicClient`. `replies` maps game_id -> payload or an Exception."""

    def __init__(self, replies: dict):
        self.replies = replies
        self.calls: list[tuple[str, object]] = []

    def post(self, service, body):
        self.calls.append((service, body))
        reply = self.replies[body[0]]
        if isinstance(reply, Exception):
            raise reply

        class Response:
            payload = reply
            raw = json.dumps(reply).encode()

        return Response()


def valid_replay(game_id: int) -> dict:
    return {"gameId": game_id, "frames": [{"n": 0}], "scores": [1, 0],
            "agents": [{"agentId": 1}, {"agentId": 2}]}


# --- cursor durability ---------------------------------------------------------------


def test_atomic_write_leaves_no_partial_file(tmp_path):
    target = tmp_path / "cursor.json"
    atomic_write_json(target, {"a": 1})
    assert json.loads(target.read_text()) == {"a": 1}
    assert list(tmp_path.glob("*.tmp-*")) == [], "temp file must not survive"


def test_cursor_survives_a_crash_during_write(tmp_path, monkeypatch):
    """F8 was a torn state file wedging every later run. The old content must remain intact."""
    target = tmp_path / "cursor.json"
    atomic_write_json(target, {"generation": 1, "seen_game_ids": [1, 2, 3]})
    original = target.read_bytes()

    def explode(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(collector.os, "replace", explode)
    with pytest.raises(OSError):
        atomic_write_json(target, {"generation": 2, "seen_game_ids": [9]})

    assert target.read_bytes() == original, "a failed write must not damage the old cursor"
    assert json.loads(target.read_text())["generation"] == 1


def test_cursor_reports_unseen_only(tmp_path):
    cursor = Cursor(tmp_path / "c.json")
    cursor.record(run={"finished_utc": "x"}, collected=[10, 11])
    assert cursor.unseen([10, 11, 12]) == [12]

    reloaded = Cursor(tmp_path / "c.json")
    assert reloaded.unseen([10, 11, 12]) == [12], "seen set must survive a restart"


def test_cursor_trim_is_reported_not_silent(tmp_path):
    """A cap that nobody is told about reads as full coverage. This one returns its count."""
    cursor = Cursor(tmp_path / "c.json", capacity=5)
    dropped = cursor.record(run={"finished_utc": "x"}, collected=list(range(100, 110)))
    assert dropped == 5
    assert cursor.data["seen_game_ids"] == [105, 106, 107, 108, 109], "keeps the highest ids"


# --- fetch classification ------------------------------------------------------------


def test_fetch_marks_422_as_permanently_gone(tmp_path):
    """B1: a 422 means the replay left every participant's window — it is gone, not delayed."""
    gone = urllib.error.HTTPError("u", 422, "err", {},
                                  io.BytesIO(b'{"id":548,"message":"Game not found"}'))
    platform = FakePlatform({1: valid_replay(1), 2: gone})
    collected, failures = fetch(platform, [1, 2], tmp_path)
    assert collected == [1]
    assert len(failures) == 1
    assert failures[0]["permanent"] is True
    assert failures[0]["game_id"] == 2


def test_fetch_keeps_going_after_one_failure(tmp_path):
    platform = FakePlatform({1: valid_replay(1), 2: TimeoutError("slow"), 3: valid_replay(3)})
    collected, failures = fetch(platform, [1, 2, 3], tmp_path)
    assert collected == [1, 3]
    assert len(failures) == 1 and failures[0].get("permanent") is None


def test_fetch_rejects_a_malformed_replay(tmp_path):
    platform = FakePlatform({1: {"gameId": 1}})  # no frames -> replay_shape invalid
    collected, failures = fetch(platform, [1], tmp_path)
    assert collected == []
    assert "shape" in failures[0]["error"].lower() or "invalid" in failures[0]["error"].lower()
    assert not list(tmp_path.glob("*.json")), "an invalid replay must not be staged"


# --- upload behaviour ----------------------------------------------------------------


class FakeS3:
    """Records puts; `taken` keys raise PreconditionFailed as the live endpoint does."""

    def __init__(self, taken=()):
        self.taken = set(taken)
        self.puts: list[str] = []
        self.objects: dict[str, bytes] = {}

    def put_object(self, key, body, *, content_type="", if_none_match=False):
        self.puts.append(key)
        if if_none_match and key in self.taken:
            raise S3Error(412, "PreconditionFailed", "already exists")
        self.objects[key] = body
        return {"status": 200, "etag": '"fake"'}

    def get_object(self, key):
        return self.objects[key]


def make_pack(tmp_path):
    (tmp_path / "5.json").write_text("{}")
    return pack_day(DATE, [tmp_path / "5.json"])


def test_upload_uses_the_plain_key_when_free(tmp_path):
    pack = make_pack(tmp_path)
    result = upload_day(FakeS3(), pack, date=DATE, dry_run=False)
    assert result["rerun"] == 0
    assert result["pack_key"] == f"games/raw/daily/{DATE}.jsonl.gz"


def test_upload_escalates_to_rerun_on_collision(tmp_path):
    """Append-only is this code's job: the grant permits overwriting (measured in B2)."""
    pack = make_pack(tmp_path)
    s3 = FakeS3(taken=[f"games/raw/daily/{DATE}.jsonl.gz",
                       f"games/raw/daily/{DATE}.rerun-1.jsonl.gz"])
    result = upload_day(s3, pack, date=DATE, dry_run=False)
    assert result["rerun"] == 2
    assert result["pack_key"] == f"games/raw/daily/{DATE}.rerun-2.jsonl.gz"


def test_upload_always_sets_if_none_match(tmp_path, monkeypatch):
    pack = make_pack(tmp_path)
    seen = []

    class Recorder(FakeS3):
        def put_object(self, key, body, *, content_type="", if_none_match=False):
            seen.append(if_none_match)
            return super().put_object(key, body, content_type=content_type,
                                      if_none_match=if_none_match)

    upload_day(Recorder(), pack, date=DATE, dry_run=False)
    assert seen and all(seen), "an unconditional PUT can silently clobber a day"


def test_upload_gives_up_rather_than_guessing_forever(tmp_path):
    pack = make_pack(tmp_path)
    every_key = {f"games/raw/daily/{DATE}.jsonl.gz"} | {
        f"games/raw/daily/{DATE}.rerun-{n}.jsonl.gz"
        for n in range(1, collector.MAX_RERUN + 1)}
    with pytest.raises(RuntimeError, match="refusing to guess"):
        upload_day(FakeS3(taken=every_key), pack, date=DATE, dry_run=False)


def test_upload_error_that_is_not_a_collision_propagates(tmp_path):
    pack = make_pack(tmp_path)

    class Denied(FakeS3):
        def put_object(self, key, body, *, content_type="", if_none_match=False):
            raise S3Error(403, "AccessDenied", "nope")

    with pytest.raises(S3Error):
        upload_day(Denied(), pack, date=DATE, dry_run=False)


# --- end-to-end run behaviour --------------------------------------------------------


def run_main(tmp_path, monkeypatch, *, platform, s3=None, extra=()):
    monkeypatch.setattr(collector, "PublicClient", lambda *a, **k: platform)
    if s3 is not None:
        monkeypatch.setattr(collector, "S3Client", lambda *a, **k: s3)
    argv = ["--state-dir", str(tmp_path / "state"), "--date", DATE, *extra]
    return collector.main(argv)


class DiscoveringPlatform(FakePlatform):
    """Answers the leaderboard and battle-list calls, then replays."""

    def __init__(self, game_ids, replay_replies=None):
        self.game_ids = game_ids
        self.replay_replies = replay_replies or {}
        self.calls = []

    def post(self, service, body):
        self.calls.append((service, body))

        class Response:
            pass

        response = Response()
        if service.startswith("Leaderboards"):
            response.payload = {"users": [{"agentId": 7}]}
        elif service.startswith("gamesPlayersRanking"):
            response.payload = [{"gameId": gid, "done": True} for gid in self.game_ids]
        else:
            game_id = body[0]
            reply = self.replay_replies.get(game_id, valid_replay(game_id))
            if isinstance(reply, Exception):
                raise reply
            response.payload = reply
        response.raw = json.dumps(response.payload).encode()
        return response


def test_successful_run_advances_the_cursor(tmp_path, monkeypatch, capsys):
    s3 = FakeS3()
    code = run_main(tmp_path, monkeypatch, platform=DiscoveringPlatform([1, 2]), s3=s3)
    assert code == 0
    cursor = json.loads((tmp_path / "state" / "collector-v2.json").read_text())
    assert cursor["seen_game_ids"] == [1, 2]
    assert "collector-v2 end exit=0" in capsys.readouterr().out


def test_cursor_is_not_advanced_when_the_upload_fails(tmp_path, monkeypatch, capsys):
    """Otherwise a failed day's games look collected forever and are never retried."""

    class Denied(FakeS3):
        def put_object(self, key, body, *, content_type="", if_none_match=False):
            raise S3Error(403, "AccessDenied", "nope")

    code = run_main(tmp_path, monkeypatch, platform=DiscoveringPlatform([1, 2]), s3=Denied())
    assert code == 2, "a failed upload is its own exit code, not a generic crash"
    assert not (tmp_path / "state" / "collector-v2.json").exists()
    output = capsys.readouterr().out
    assert "collector-v2 end exit=2" in output, "the end marker must survive the failure path"


def test_transient_fetch_failure_reports_exit_3(tmp_path, monkeypatch):
    platform = DiscoveringPlatform([1, 2], replay_replies={2: TimeoutError("slow")})
    code = run_main(tmp_path, monkeypatch, platform=platform, s3=FakeS3())
    assert code == 3, "an incomplete day must not look like a clean run"


def test_permanently_gone_game_does_not_fail_the_run(tmp_path, monkeypatch):
    gone = urllib.error.HTTPError("u", 422, "err", {},
                                  io.BytesIO(b'{"id":548,"message":"Game not found"}'))
    platform = DiscoveringPlatform([1, 2], replay_replies={2: gone})
    assert run_main(tmp_path, monkeypatch, platform=platform, s3=FakeS3()) == 0


def test_end_marker_is_emitted_even_when_discovery_explodes(tmp_path, monkeypatch, capsys):
    class Broken(DiscoveringPlatform):
        def post(self, service, body):
            raise RuntimeError("platform down")

    code = run_main(tmp_path, monkeypatch, platform=Broken([]), s3=FakeS3())
    assert code == 1
    assert "collector-v2 end exit=1" in capsys.readouterr().out


def test_uploaded_pack_is_verified_by_download(tmp_path, monkeypatch):
    """A corrupted upload must fail the run rather than be recorded as collected."""

    class Corrupting(FakeS3):
        def get_object(self, key):
            return b"not what was uploaded"

    code = run_main(tmp_path, monkeypatch, platform=DiscoveringPlatform([1]), s3=Corrupting())
    assert code == 2
    assert not (tmp_path / "state" / "collector-v2.json").exists()


# --- staging retention ---------------------------------------------------------------


def test_staging_is_pruned_only_after_a_verified_upload(tmp_path, monkeypatch):
    """The VM's disk is 94% full; unpruned staging fills it in a fortnight. But bytes may
    only leave this disk once they are provably in the bucket."""
    run_main(tmp_path, monkeypatch, platform=DiscoveringPlatform([1, 2]), s3=FakeS3(),
             extra=["--prune-staging"])
    staged = tmp_path / "state" / "staging" / DATE
    assert not staged.exists() or not list(staged.glob("*.json"))


def test_staging_survives_a_failed_upload(tmp_path, monkeypatch):
    """If the upload failed, the staged replays are the only copy — they must not be deleted."""

    class Denied(FakeS3):
        def put_object(self, key, body, *, content_type="", if_none_match=False):
            raise S3Error(403, "AccessDenied", "nope")

    code = run_main(tmp_path, monkeypatch, platform=DiscoveringPlatform([1, 2]), s3=Denied(),
                    extra=["--prune-staging"])
    assert code == 2
    staged = sorted((tmp_path / "state" / "staging" / DATE).glob("*.json"))
    assert [p.stem for p in staged] == ["1", "2"], "staged replays are the only copy left"


def test_staging_survives_a_failed_verification(tmp_path, monkeypatch):
    class Corrupting(FakeS3):
        def get_object(self, key):
            return b"not what was uploaded"

    code = run_main(tmp_path, monkeypatch, platform=DiscoveringPlatform([1]), s3=Corrupting(),
                    extra=["--prune-staging"])
    assert code == 2
    assert sorted((tmp_path / "state" / "staging" / DATE).glob("*.json"))


def test_staging_is_kept_by_default(tmp_path, monkeypatch):
    run_main(tmp_path, monkeypatch, platform=DiscoveringPlatform([1]), s3=FakeS3())
    assert sorted((tmp_path / "state" / "staging" / DATE).glob("*.json"))
