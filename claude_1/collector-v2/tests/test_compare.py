"""Tests for the B5 comparison tool (task `20260811-s3-collector-v2`).

The failure that matters here is a FALSE PARITY: a comparison that reports no gaps because it
failed to read part of the bucket, or because it silently compared the wrong population. So
the tests pin rerun-manifest coverage, reference-format tolerance, and the refusal to call a
reference-less run a parity result.

Run: `uvx pytest claude_1/collector-v2/tests -q`
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import compare  # noqa: E402
from compare import bucket_ids, dates_in_range, parse_reference  # noqa: E402


class FakeS3:
    def __init__(self, manifests: dict[str, list[int]]):
        self.manifests = manifests

    def list_objects(self, prefix=""):
        return [{"key": key, "size": 1, "etag": "x"} for key in self.manifests
                if key.startswith(prefix)]

    def get_object(self, key):
        return "\n".join(
            json.dumps({"game_id": gid, "sha256": "d", "size": 1, "pack": "p"})
            for gid in self.manifests[key]).encode() + b"\n"


def test_rerun_manifests_are_included_not_ignored():
    """A day can span several objects; reading only the plain key invents missing ids."""
    s3 = FakeS3({
        "games/manifest/daily-2026-08-11.jsonl": [1, 2],
        "games/manifest/daily-2026-08-11.rerun-1.jsonl": [3, 4],
        "games/manifest/daily-2026-08-11.rerun-2.jsonl": [5],
    })
    per_date, problems = bucket_ids(s3, ["2026-08-11"])
    assert per_date["2026-08-11"]["ids"] == {1, 2, 3, 4, 5}
    assert [m["rerun"] for m in sorted(per_date["2026-08-11"]["manifests"],
                                       key=lambda m: m["rerun"])] == [0, 1, 2]
    assert problems == []


def test_manifests_outside_the_range_are_ignored():
    s3 = FakeS3({"games/manifest/daily-2026-08-11.jsonl": [1],
                 "games/manifest/daily-2026-08-12.jsonl": [2],
                 "games/manifest/backfill-000001.jsonl": [3]})
    per_date, _ = bucket_ids(s3, ["2026-08-11"])
    assert per_date["2026-08-11"]["ids"] == {1}


def test_reference_accepts_the_three_plausible_export_formats():
    assert parse_reference("1\n2\n3\n") == [1, 2, 3]
    assert parse_reference("[1, 2, 3]") == [1, 2, 3]
    assert parse_reference('{"game_id": 1}\n{"game_id": 2}\n') == [1, 2]
    assert parse_reference("  ") == []


def test_dates_in_range_is_inclusive_and_ordered():
    assert dates_in_range("2026-08-10", "2026-08-12") == [
        "2026-08-10", "2026-08-11", "2026-08-12"]
    assert dates_in_range("2026-08-10", "2026-08-10") == ["2026-08-10"]
    with pytest.raises(ValueError):
        dates_in_range("2026-08-12", "2026-08-10")


def run_main(tmp_path, monkeypatch, s3, extra=()):
    monkeypatch.setattr(compare, "S3Client", lambda *a, **k: s3)
    out = tmp_path / "result.json"
    code = compare.main(["--out", str(out), "--start", "2026-08-11", "--end", "2026-08-11",
                         *extra])
    return code, json.loads(out.read_text())


def test_missing_ids_are_reported_as_gaps(tmp_path, monkeypatch):
    reference = tmp_path / "ref.txt"
    reference.write_text("1\n2\n99\n")
    s3 = FakeS3({"games/manifest/daily-2026-08-11.jsonl": [1, 2]})
    code, report = run_main(tmp_path, monkeypatch, s3,
                            ["--reference", str(reference), "--reference-label", "test"])
    assert code == 1
    assert report["verdict"] == "GAPS"
    assert report["missing_from_day_manifests"] == [99]
    assert report["s3_wide_triage"]["absent_from_s3_entirely"] == [99], \
        "not held anywhere, so it is a real data gap"


def test_extra_ids_do_not_count_as_gaps(tmp_path, monkeypatch):
    """The two collectors run at different times over different cohorts; extra is expected."""
    reference = tmp_path / "ref.txt"
    reference.write_text("1\n")
    s3 = FakeS3({"games/manifest/daily-2026-08-11.jsonl": [1, 2, 3]})
    code, report = run_main(tmp_path, monkeypatch, s3,
                            ["--reference", str(reference), "--reference-label", "test"])
    assert code == 0
    assert report["verdict"] == "PARITY"
    assert report["extra_count"] == 2


def test_a_run_without_a_reference_refuses_to_claim_parity(tmp_path, monkeypatch):
    s3 = FakeS3({"games/manifest/daily-2026-08-11.jsonl": [1, 2]})
    _, report = run_main(tmp_path, monkeypatch, s3)
    assert report["verdict"] == "NO_REFERENCE"
    assert "must not be quoted" in report["note"]
    assert "missing_from_day_count" not in report


def test_an_unlabelled_reference_says_so(tmp_path, monkeypatch):
    """A figure that changes meaning at a boundary is this project's most expensive error."""
    reference = tmp_path / "ref.txt"
    reference.write_text("1\n")
    s3 = FakeS3({"games/manifest/daily-2026-08-11.jsonl": [1]})
    _, report = run_main(tmp_path, monkeypatch, s3, ["--reference", str(reference)])
    assert "UNLABELLED" in report["reference_label"]


def test_a_game_held_only_via_the_backfill_is_not_a_data_gap(tmp_path, monkeypatch):
    """The distinction 2026-08-11 turned on: 352 ids missing from the day's object, 0 absent
    from S3. Cut-over asks the first question; data safety asks the second."""
    reference = tmp_path / "ref.txt"
    reference.write_text("1\n2\n77\n")
    s3 = FakeS3({"games/manifest/daily-2026-08-11.jsonl": [1, 2],
                 "games/manifest/backfill-000000.jsonl": [77]})
    code, report = run_main(tmp_path, monkeypatch, s3,
                            ["--reference", str(reference), "--reference-label", "test"])
    assert code == 1 and report["verdict"] == "GAPS"
    assert report["missing_from_day_manifests"] == [77], "the VM did not collect it"
    assert report["s3_wide_triage"]["absent_from_s3_entirely"] == [], "but S3 holds it"
    assert report["s3_wide_triage"]["held_via_another_object_count"] == 1
