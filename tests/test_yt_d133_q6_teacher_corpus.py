import json

import pytest

from cgauto.yt_d133_q6_teacher_corpus import (
    BLOCKS,
    MAPS_PER_BLOCK,
    MAPS_PER_SHARD,
    SHARDS_PER_BLOCK,
    START_SEED,
    YT_ROOT,
    build_paths,
    build_specs,
    combine_teachers,
    reconstruct_stream,
)


def test_specs_cover_four_independent_blocks_with_one_chunk_per_shard():
    specs = build_specs()
    assert len(specs) == BLOCKS * SHARDS_PER_BLOCK == 16
    assert [spec["start_seed"] for spec in specs] == list(
        range(START_SEED, START_SEED + BLOCKS * MAPS_PER_BLOCK, MAPS_PER_SHARD)
    )
    assert {spec["block_id"] for spec in specs} == set(range(BLOCKS))
    assert all(spec["maps"] == 4 and spec["threads"] == 16 for spec in specs)


def test_user_directed_yt_root_is_the_only_build_base():
    paths = build_paths(build_name="unit")
    assert YT_ROOT == "//home/delivery_ml/research/tarstars/troll_farm"
    assert paths["build"] == f"{YT_ROOT}/dataset_builds/unit"


def _tiny_specs():
    specs = build_specs()
    return specs


def test_stream_reconstruction_routes_out_of_order_shards_and_deduplicates_headers(
    tmp_path,
):
    specs = _tiny_specs()
    rows = []
    for spec in reversed(specs):
        shard = spec["shard_id"]
        start = spec["start_seed"]
        for record_type, header in (("arms", "ah"), ("baselines", "bh")):
            rows.extend(
                [
                    {
                        "record_type": record_type,
                        "shard_id": shard,
                        "start_seed": start,
                        "row_index": 0,
                        "line": header,
                    },
                    {
                        "record_type": record_type,
                        "shard_id": shard,
                        "start_seed": start,
                        "row_index": 1,
                        "line": f"{start}\t{record_type}",
                    },
                ]
            )
        rows.append(
            {
                "record_type": "metadata",
                "shard_id": shard,
                "start_seed": start,
                "row_index": 0,
                "line": json.dumps(
                    {
                        "elapsed_seconds": 1.0,
                        "arm_lines": 2,
                        "baseline_lines": 2,
                        "threads": 16,
                    }
                ),
            }
        )
    outputs, metadata, table_rows = reconstruct_stream(rows, tmp_path, specs)
    assert table_rows == 16 * 5
    assert len(metadata) == 16
    first_block = outputs["0"]
    assert first_block["arms"]["rows"] == 4
    assert first_block["baselines"]["rows"] == 4
    arms = (tmp_path / first_block["arms"]["path"]).read_text()
    assert arms.count("ah\n") == 1
    assert [line.split("\t")[0] for line in arms.splitlines()[1:]] == [
        str(START_SEED + offset) for offset in (0, 4, 8, 12)
    ]


def test_stream_reconstruction_rejects_a_row_gap(tmp_path):
    specs = _tiny_specs()
    spec = specs[0]
    rows = [
        {
            "record_type": "arms",
            "shard_id": spec["shard_id"],
            "start_seed": spec["start_seed"],
            "row_index": 1,
            "line": "gap",
        }
    ]
    with pytest.raises(RuntimeError, match="noncontiguous"):
        reconstruct_stream(rows, tmp_path, specs)


def _teacher(mean, std, crop=1.0):
    tasks = 256
    roots = 1000
    arms = 20_000
    oracle = {
        "tasks": tasks,
        "supported_tasks": 250,
        "mean_margin_gain": mean,
        "strict_improvement_rate": 0.8,
        "mean_own_score_gain": 1.0,
        "mean_opponent_score_delta": -mean + 1.0,
        "family_mean_margin_gain": {name: mean for name in (
            "resident", "compact_gold", "gold_adaptive", "silver_boss",
            "legend_balanced", "norx_native_three", "script_boss", "mybot"
        )},
        "positive_families": 8,
        "worst_family": mean,
        "intervention_rate": 0.8,
        "mean_selected_boundary": 2.0,
        "selected_kind_counts": {1: 100, 2: 50, 3: 55, 0: 51},
        "first_boundary_oracle_mean_gain": mean - 2.0,
        "later_boundary_increment": 2.0,
        "crop_rate": crop,
        "worker_three_rate": 0.8,
        "control_worker_three_rate": 0.8,
    }
    dp = {
        "roots": roots,
        "arms": arms,
        "act_now_roots": 200,
        "wait_roots": 800,
        "act_now_root_rate": 0.2,
        "positive_arm_advantages": 4000,
        "negative_arm_advantages": 12_000,
        "zero_arm_advantages": 4000,
        "positive_arm_advantage_rate": 0.2,
        "negative_arm_advantage_rate": 0.6,
        "target_mean": -2.0,
        "target_standard_deviation": std,
        "target_minimum": -50.0,
        "target_maximum": 50.0,
        "best_now_mean": 5.0,
    }
    return {"oracle": oracle, "backward_dp": dp}


def test_teacher_aggregation_uses_pooled_counts_and_moments():
    combined = combine_teachers(
        [_teacher(20.0, 5.0), _teacher(22.0, 7.0), _teacher(24.0, 9.0), _teacher(26.0, 11.0)]
    )
    assert combined["oracle"]["tasks"] == 1024
    assert combined["oracle"]["mean_margin_gain"] == 23.0
    assert combined["backward_dp"]["arms"] == 80_000
    assert combined["backward_dp"]["target_standard_deviation"] > 5.0
    assert combined["signal_pass"]
    assert combined["safety_pass"]
