import json

from cgauto import yt_d144_two_intervention_mc as d144


def test_d144_uses_correct_root_panel_and_four_fixed_jobs():
    assert d144.YT_ROOT == "//home/delivery_ml/research/tarstars/troll_farm"
    assert d144.build_paths()["build"] == (
        f"{d144.YT_ROOT}/dataset_builds/{d144.BUILD_NAME}"
    )
    specs = d144.build_specs()
    assert [spec["shard_id"] for spec in specs] == [
        "mc-a",
        "mc-b",
        "exact-00",
        "exact-01",
    ]
    assert [spec["kind"] for spec in specs] == ["mc", "mc", "exact", "exact"]
    assert {spec["threads"] for spec in specs} == {16}
    assert specs[0]["start_seed"] == d144.START_SEED
    assert specs[0]["maps"] == 8
    assert specs[0]["replicas"] == 128
    assert specs[0]["single_replicas"] == 16
    assert specs[-1]["start_seed"] == d144.START_SEED + 4


def test_d144_reconstruction_separates_repeats_and_merges_exact_shards(tmp_path):
    specs = d144.build_specs()
    rows = []
    for spec in specs:
        shard = spec["shard_id"]
        record_types = ("mc",) if spec["kind"] == "mc" else ("arms", "baselines")
        counts = {}
        for record_type in record_types:
            lines = ["field\tvalue", f"{shard}\t{record_type}"]
            counts[record_type] = len(lines)
            for index, line in enumerate(lines):
                rows.append(
                    {
                        "record_type": record_type,
                        "shard_id": shard,
                        "start_seed": spec["start_seed"],
                        "row_index": index,
                        "line": line,
                    }
                )
        rows.append(
            {
                "record_type": "metadata",
                "shard_id": shard,
                "start_seed": spec["start_seed"],
                "row_index": 0,
                "line": json.dumps(
                    {
                        "kind": spec["kind"],
                        "threads": spec["threads"],
                        "elapsed_seconds": 1.0,
                        "line_counts": counts,
                    }
                ),
            }
        )

    outputs, metadata, table_rows = d144.reconstruct_stream(
        rows, tmp_path / "out", specs
    )
    assert set(outputs) == {"mc-a", "mc-b", "arms", "baselines"}
    assert outputs["mc-a"]["rows"] == 1
    assert outputs["mc-b"]["rows"] == 1
    assert outputs["arms"]["rows"] == 2
    assert outputs["baselines"]["rows"] == 2
    assert len(metadata) == 4
    assert table_rows == len(rows)
    assert (tmp_path / "out" / "parts").exists() is False
    assert len((tmp_path / "out" / "d144a-exact-arms-9844128-9844135.tsv").read_text().splitlines()) == 3


def test_d144_incremental_oracle_uses_double_only_for_strict_margin_gain():
    task_a = (1, 0, "resident")
    task_b = (1, 1, "resident")
    baselines = {
        task_a: {
            "map_seed": "1",
            "seat": "0",
            "opponent": "resident",
            "own_score": "10",
            "opponent_score": "10",
            "own_created_crops": "1",
            "own_workers": "3",
        },
        task_b: {
            "map_seed": "1",
            "seat": "1",
            "opponent": "resident",
            "own_score": "20",
            "opponent_score": "20",
            "own_created_crops": "1",
            "own_workers": "3",
        },
    }
    arms = [
        {
            **baselines[task_a],
            "own_score": "15",
            "opponent_score": "10",
            "slot": "1",
        },
        {
            **baselines[task_b],
            "own_score": "24",
            "opponent_score": "20",
            "slot": "1",
        },
    ]
    doubles = [
        {
            **baselines[task_a],
            "mode": "double",
            "intervention_batches": "2",
            "own_score": "20",
            "opponent_score": "10",
            "replica": "17",
        },
        {
            **baselines[task_b],
            "mode": "double",
            "intervention_batches": "2",
            "own_score": "25",
            "opponent_score": "21",
            "replica": "17",
        },
    ]
    result = d144._incremental_oracle(doubles, arms, baselines)
    summary = result["summary"]
    assert summary["mean_one_use_oracle_gain"] == 4.5
    assert summary["mean_combined_oracle_gain"] == 7.0
    assert summary["mean_increment_beyond_one_use"] == 2.5
    assert summary["strict_increment_tasks"] == 1
    assert summary["new_crop_failures"] == 0
