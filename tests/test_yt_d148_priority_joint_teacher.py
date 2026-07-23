import json

from cgauto import yt_d148_priority_joint_teacher as d148


def test_d148_uses_correct_root_fresh_panel_and_reserved_validation():
    assert d148.YT_ROOT == "//home/delivery_ml/research/tarstars/troll_farm"
    assert d148.START_SEED == 9_844_136
    assert d148.START_SEED + d148.MAPS == d148.VALIDATION_START_SEED
    assert d148.build_paths()["build"] == (
        f"{d148.YT_ROOT}/dataset_builds/{d148.BUILD_NAME}"
    )
    specs = d148.build_specs()
    assert len(specs) == 16
    assert [spec["shard_id"] for spec in specs[:8]] == [
        f"joint-{index:02d}" for index in range(8)
    ]
    assert [spec["shard_id"] for spec in specs[8:]] == [
        f"exact-{index:02d}" for index in range(8)
    ]
    assert {spec["threads"] for spec in specs} == {16}
    assert {spec["maps"] for spec in specs} == {8}
    assert {spec["search_budget"] for spec in specs[:8]} == {64}


def test_d148_reconstruction_merges_each_record_type_in_seed_order(tmp_path):
    specs = d148.build_specs()
    rows = []
    for spec in specs:
        record_types = (
            d148.JOINT_RECORD_TYPES
            if spec["kind"] == "joint"
            else d148.EXACT_RECORD_TYPES
        )
        counts = {}
        for record_type in record_types:
            lines = ["field\tvalue", f"{spec['shard_id']}\t{record_type}"]
            counts[record_type] = len(lines)
            for index, line in enumerate(lines):
                rows.append(
                    {
                        "record_type": record_type,
                        "shard_id": spec["shard_id"],
                        "start_seed": spec["start_seed"],
                        "row_index": index,
                        "line": line,
                    }
                )
        rows.append(
            {
                "record_type": "metadata",
                "shard_id": spec["shard_id"],
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
    outputs, metadata, table_rows = d148.reconstruct_stream(
        rows, tmp_path / "out", specs
    )
    assert set(outputs) == set(d148.JOINT_RECORD_TYPES + d148.EXACT_RECORD_TYPES)
    assert all(outputs[name]["rows"] == 8 for name in outputs)
    assert len(metadata) == 16
    assert table_rows == len(rows)
    population = (tmp_path / "out" / "d148a-population-9844136-9844199.tsv").read_text()
    assert population.index("joint-00") < population.index("joint-07")
    assert not (tmp_path / "out" / "parts").exists()
