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
import packer  # noqa: E402
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
    """Records puts; `taken` keys raise PreconditionFailed as the live endpoint does.

    `held` seeds a backfill manifest, which is how the collector learns what is already in
    S3. It defaults to one id that no test discovers, so the known-id set is non-empty (an
    empty bucket listing is a hard error by design) without accidentally skipping anything.
    """

    def __init__(self, taken=(), held=(999_999_999,)):
        self.taken = set(taken)
        self.puts: list[str] = []
        self.objects: dict[str, bytes] = {}
        self.content_types: dict[str, str] = {}
        if held is not None:
            self.objects["games/manifest/backfill-000000.jsonl"] = b"\n".join(
                json.dumps({"game_id": gid, "sha256": "d", "size": 1,
                            "pack": "p"}).encode() for gid in held) + b"\n"

    def put_object(self, key, body, *, content_type="", if_none_match=False):
        self.puts.append(key)
        self.content_types[key] = content_type
        if if_none_match and key in self.taken:
            raise S3Error(412, "PreconditionFailed", "already exists")
        self.objects[key] = body
        return {"status": 200, "etag": '"fake"'}

    def get_object(self, key):
        return self.objects[key]

    def list_objects(self, prefix=""):
        return [{"key": key, "size": len(body), "etag": "x"}
                for key, body in sorted(self.objects.items()) if key.startswith(prefix)]


def make_pack(tmp_path):
    (tmp_path / "5.json").write_text("{}")
    return pack_day(DATE, [tmp_path / "5.json"])


def test_upload_uses_the_plain_key_when_free(tmp_path):
    pack = make_pack(tmp_path)
    result = upload_day(FakeS3(), pack, date=DATE, dry_run=False)
    assert result["rerun"] == 0
    assert result["pack_key"] == f"games/raw/daily/{DATE}{packer.PACK_EXTENSION}"


def test_upload_escalates_to_rerun_on_collision(tmp_path):
    """Append-only is this code's job: the grant permits overwriting (measured in B2)."""
    pack = make_pack(tmp_path)
    ext = packer.PACK_EXTENSION
    s3 = FakeS3(taken=[f"games/raw/daily/{DATE}{ext}",
                       f"games/raw/daily/{DATE}.rerun-1{ext}"])
    result = upload_day(s3, pack, date=DATE, dry_run=False)
    assert result["rerun"] == 2
    assert result["pack_key"] == f"games/raw/daily/{DATE}.rerun-2{ext}"


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
    ext = packer.PACK_EXTENSION
    every_key = {f"games/raw/daily/{DATE}{ext}"} | {
        f"games/raw/daily/{DATE}.rerun-{n}{ext}"
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


def test_permanently_gone_game_still_makes_the_run_nonzero(tmp_path, monkeypatch, capsys):
    """Replaces an earlier test that pinned exit 0 here — that pinned the wrong behaviour.

    Coordinator ruling `20260811T112547Z`: a same-day fetch failure is a real error in the
    end marker, not a soft skip. A 422 means the replay has left every participant's window,
    which is a permanent loss and the last thing that should read as a clean run. Raised by
    codex_1 in second review.
    """
    gone = urllib.error.HTTPError("u", 422, "err", {},
                                  io.BytesIO(b'{"id":548,"message":"Game not found"}'))
    platform = DiscoveringPlatform([1, 2], replay_replies={2: gone})
    code = run_main(tmp_path, monkeypatch, platform=platform, s3=FakeS3())
    output = capsys.readouterr().out
    assert code == 3
    assert "permanently_gone=1" in output, "the classification must survive, it just cannot excuse"
    assert "collector-v2 end exit=3" in output


def test_a_mixed_failure_day_is_nonzero_and_keeps_both_counts(tmp_path, monkeypatch, capsys):
    """The sharper half of the same defect: one permanent failure used to mask every
    transient one beside it, so a day that lost games two different ways exited 0."""
    gone = urllib.error.HTTPError("u", 422, "err", {},
                                  io.BytesIO(b'{"id":548,"message":"Game not found"}'))
    platform = DiscoveringPlatform([1, 2, 3, 4],
                                   replay_replies={2: gone, 3: TimeoutError("slow")})
    code = run_main(tmp_path, monkeypatch, platform=platform, s3=FakeS3())
    output = capsys.readouterr().out
    assert code == 3
    assert "failed=2" in output and "permanently_gone=1" in output
    cursor = json.loads((tmp_path / "state" / "collector-v2.json").read_text())
    run = cursor["runs"][0]
    assert len(run["fetch_failures"]) == 2
    assert sum(1 for f in run["fetch_failures"] if f.get("permanent")) == 1
    assert run["collected"] == 2, "the sweep still finished: one lost game must not cost the day"


def test_every_candidate_is_attempted_despite_a_failure(tmp_path, monkeypatch):
    """The other half of the ruling: do not abort the sweep on the first failure."""
    platform = DiscoveringPlatform([1, 2, 3], replay_replies={1: TimeoutError("slow")})
    run_main(tmp_path, monkeypatch, platform=platform, s3=FakeS3())
    attempted = sorted(body[0] for service, body in platform.calls
                       if service == "gameResult/findByGameId")
    assert attempted == [1, 2, 3]


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
            # Corrupt only what was just uploaded; manifests must still read, or the run
            # would fail on the known-id set instead of on the verification being tested.
            if key.startswith("games/manifest/backfill-"):
                return super().get_object(key)
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
            # Corrupt only what was just uploaded; manifests must still read, or the run
            # would fail on the known-id set instead of on the verification being tested.
            if key.startswith("games/manifest/backfill-"):
                return super().get_object(key)
            return b"not what was uploaded"

    code = run_main(tmp_path, monkeypatch, platform=DiscoveringPlatform([1]), s3=Corrupting(),
                    extra=["--prune-staging"])
    assert code == 2
    assert sorted((tmp_path / "state" / "staging" / DATE).glob("*.json"))


def test_staging_is_kept_by_default(tmp_path, monkeypatch):
    run_main(tmp_path, monkeypatch, platform=DiscoveringPlatform([1]), s3=FakeS3())
    assert sorted((tmp_path / "state" / "staging" / DATE).glob("*.json"))


# --- deduplication against S3 (task 20260811-collector-v2-dedupe) ---------------------


def test_a_game_already_in_s3_is_never_fetched(tmp_path, monkeypatch):
    """The acceptance check: known ids must not reach the fetch loop at all.

    Verified to fail against the pre-dedupe collector, which fetched all three.
    """
    platform = DiscoveringPlatform([1, 2, 3])
    s3 = FakeS3(held=[2])
    code = run_main(tmp_path, monkeypatch, platform=platform, s3=s3)
    assert code == 0
    fetched = [body[0] for service, body in platform.calls
               if service == "gameResult/findByGameId"]
    assert 2 not in fetched, "an already-held game must never be fetched"
    assert sorted(fetched) == [1, 3]


def test_known_ids_are_read_from_backfill_and_daily_manifests():
    s3 = FakeS3(held=[10])
    s3.objects["games/manifest/daily-2026-08-10.jsonl"] = (
        json.dumps({"game_id": 20, "sha256": "d", "size": 1, "pack": "p"}).encode() + b"\n")
    s3.objects["games/manifest/daily-2026-08-10.rerun-1.jsonl"] = (
        json.dumps({"game_id": 21, "sha256": "d", "size": 1, "pack": "p"}).encode() + b"\n")
    # a pack object under a different prefix must not be mistaken for a manifest
    s3.objects["games/raw/daily/2026-08-10.jsonl.gz"] = b"\x1f\x8b not json"
    known, stats = collector.known_ids_from_s3(s3)
    assert known == {10, 20, 21}
    assert stats["manifests"] == 3
    assert stats["new_ids_from_backfill"] == 1 and stats["new_ids_from_daily"] == 2


def test_dedupe_happens_before_the_cap_not_after(tmp_path, monkeypatch):
    """Binding design 3: the budget must be spent on the remainder, not consumed by
    already-held games that are then discarded."""
    platform = DiscoveringPlatform([1, 2, 3, 4, 5])
    s3 = FakeS3(held=[1, 2, 3])
    run_main(tmp_path, monkeypatch, platform=platform, s3=s3, extra=["--max-games", "2"])
    fetched = sorted(body[0] for service, body in platform.calls
                     if service == "gameResult/findByGameId")
    assert fetched == [4, 5], "the cap must apply to un-held games only"


def test_capped_remainder_takes_the_oldest_first(tmp_path, monkeypatch):
    """Binding design 5: games leave the window from the far end, so the oldest un-held
    candidate is nearest to expiry."""
    platform = DiscoveringPlatform([10, 20, 30, 40])
    run_main(tmp_path, monkeypatch, platform=platform, s3=FakeS3(),
             extra=["--max-games", "2"])
    fetched = sorted(body[0] for service, body in platform.calls
                     if service == "gameResult/findByGameId")
    assert fetched == [10, 20], "oldest-first, not newest-first"


def test_nothing_new_is_a_success_with_an_explicit_zero(tmp_path, monkeypatch, capsys):
    """Binding design 6: an empty remainder is exit 0, no pack object, and must be
    distinguishable in the log from a broken run."""
    s3 = FakeS3(held=[1, 2])
    code = run_main(tmp_path, monkeypatch, platform=DiscoveringPlatform([1, 2]), s3=s3)
    output = capsys.readouterr().out
    assert code == 0
    assert "fetched=0" in output
    assert "collector-v2 end exit=0" in output
    assert not [key for key in s3.puts if key.startswith("games/raw/")], \
        "no empty daily object may be written"


def test_a_failure_to_build_the_known_set_stops_the_run(tmp_path, monkeypatch, capsys):
    """Binding design 4: proceeding with an empty known-set re-fetches everything — today's
    defect wearing a different hat — so it must exit non-zero with its own marker."""

    class Unlistable(FakeS3):
        def list_objects(self, prefix=""):
            raise S3Error(403, "AccessDenied", "nope")

    platform = DiscoveringPlatform([1, 2])
    code = run_main(tmp_path, monkeypatch, platform=platform, s3=Unlistable())
    output = capsys.readouterr().out
    assert code == 4, "a distinct exit code, not a generic crash"
    assert "known_ids.failed" in output
    assert not [c for c in platform.calls if c[0] == "gameResult/findByGameId"], \
        "no game may be fetched when the known-id set is unavailable"


def test_an_empty_manifest_listing_is_an_error_not_an_empty_set(tmp_path, monkeypatch):
    """'The bucket lists nothing' and 'we hold nothing' are different claims."""
    with pytest.raises(collector.KnownIdsUnavailable):
        collector.known_ids_from_s3(FakeS3(held=None))


def test_an_unreadable_manifest_stops_the_run_rather_than_under_counting():
    class Unreadable(FakeS3):
        def get_object(self, key):
            raise S3Error(500, "InternalError", "boom")

    with pytest.raises(collector.KnownIdsUnavailable, match="could not read"):
        collector.known_ids_from_s3(Unreadable())


def test_known_set_is_rebuilt_every_run_not_cached_in_the_cursor(tmp_path, monkeypatch):
    """Binding design 2: a stale cache under-fetches silently."""
    s3 = FakeS3(held=[1])
    run_main(tmp_path, monkeypatch, platform=DiscoveringPlatform([1, 2]), s3=s3)
    cursor = json.loads((tmp_path / "state" / "collector-v2.json").read_text())
    assert "known_game_ids" not in cursor
    assert cursor["seen_game_ids"] == [2], "only what this run collected"


def test_a_nothing_new_run_is_recorded_exactly_once(tmp_path, monkeypatch):
    """The empty-remainder case flows through the ordinary path; a second early-exit branch
    used to record the run twice."""
    s3 = FakeS3(held=[1, 2])
    run_main(tmp_path, monkeypatch, platform=DiscoveringPlatform([1, 2]), s3=s3)
    cursor = json.loads((tmp_path / "state" / "collector-v2.json").read_text())
    assert len(cursor["runs"]) == 1
    assert cursor["runs"][0]["collected"] == 0
    assert cursor["runs"][0]["already_held"] == 2


def test_uploaded_pack_is_labelled_with_the_codec_actually_used(tmp_path, monkeypatch):
    """A pack uploaded as application/gzip when it is zstd tells every future reader a lie.

    Nothing asserted this until the content type was mutated back to a hard-coded
    "application/gzip" and the whole suite stayed green — the same hard-coding codex_1 found
    in review, surviving one layer up.
    """
    s3 = FakeS3()
    run_main(tmp_path, monkeypatch, platform=DiscoveringPlatform([1]), s3=s3)
    pack_keys = [key for key in s3.puts if key.startswith("games/raw/")]
    assert pack_keys, "the run must have uploaded a pack"
    for key in pack_keys:
        assert s3.content_types[key] == packer.CONTENT_TYPE
        assert key.endswith(packer.PACK_EXTENSION)


def test_unseen_returns_ids_in_ascending_order(tmp_path):
    """Pins the ORDERING ITSELF, not a slice of it (raised by local_claude_1, cross-review).

    Oldest-first was load-bearing on an upstream sort: `main` takes `wanted[:max_games]`, which
    only means "oldest" because `Cursor.unseen` happens to return sorted output. The existing
    slice test does catch an unsorted `unseen`, but only by luck — set iteration for its
    particular ids happens to come out non-ascending. With different ids it would pass while
    the ordering guarantee was gone.

    The id sets below are chosen so `list(set(...))` differs from `sorted(...)` in CPython,
    including real 9-digit game ids.
    """
    cursor = Cursor(tmp_path / "c.json")
    for candidates in ([10, 20, 30, 40],
                       [898550181, 898096416, 898058061, 891153730, 895033379],
                       list(reversed(range(100, 140)))):
        result = cursor.unseen(list(candidates))
        assert result == sorted(result), f"unseen must return ascending order for {candidates[:3]}…"
        assert result == sorted(set(candidates)), "and must be the full de-duplicated set"


def test_unseen_is_sorted_even_when_the_seen_set_removes_the_lowest(tmp_path):
    """Removal must not be allowed to reintroduce arbitrary order."""
    cursor = Cursor(tmp_path / "c.json")
    cursor.record(run={"finished_utc": "x"}, collected=[891153730, 895033379])
    result = cursor.unseen([898550181, 898096416, 898058061, 891153730, 895033379])
    assert result == [898058061, 898096416, 898550181]
