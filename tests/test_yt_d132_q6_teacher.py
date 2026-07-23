import json

from cgauto.yt_d132_q6_teacher import (
    PILOT_SEED,
    build_specs,
    reconstruct_rows,
    write_reference_subset,
)


def test_pilot_spec_is_one_consumed_map_with_sixteen_threads():
    assert build_specs() == [
        {
            "shard_id": "pilot-00000",
            "start_seed": PILOT_SEED,
            "maps": 1,
            "threads": 16,
        }
    ]


def test_reconstruction_merges_shards_and_deduplicates_header(tmp_path):
    rows = []
    for shard, seed, value in (("b", 2, "two"), ("a", 1, "one")):
        rows.extend(
            [
                {"record_type": "arms", "shard_id": shard, "start_seed": seed, "row_index": 0, "line": "h"},
                {"record_type": "arms", "shard_id": shard, "start_seed": seed, "row_index": 1, "line": value},
                {"record_type": "baselines", "shard_id": shard, "start_seed": seed, "row_index": 0, "line": "b"},
                {"record_type": "baselines", "shard_id": shard, "start_seed": seed, "row_index": 1, "line": value},
            ]
        )
    rows.append(
        {
            "record_type": "metadata",
            "shard_id": "a",
            "start_seed": 1,
            "row_index": 0,
            "line": json.dumps({"elapsed_seconds": 1.0}),
        }
    )
    outputs, metadata = reconstruct_rows(rows, tmp_path)
    assert (tmp_path / "arms.tsv").read_text() == "h\none\ntwo\n"
    assert (tmp_path / "baselines.tsv").read_text() == "b\none\ntwo\n"
    assert outputs["arms"]["rows"] == 2
    assert metadata == [{"elapsed_seconds": 1.0}]


def test_reference_subset_preserves_header_and_seed_rows(tmp_path):
    source = tmp_path / "source.tsv"
    source.write_text("seed\tx\n1\ta\n2\tb\n1\tc\n")
    target = tmp_path / "target.tsv"
    summary = write_reference_subset(source, 1, target)
    assert target.read_text() == "seed\tx\n1\ta\n1\tc\n"
    assert summary["rows"] == 2
