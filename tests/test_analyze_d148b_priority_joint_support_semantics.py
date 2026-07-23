from cgauto import analyze_d148b_priority_joint_support_semantics as d148b


def mechanics(*, roots=300, support=False, integrity=True):
    return {
        "gates": {
            "complete_unique_arm_grid": integrity,
            "supported_tasks_at_least_90pct": support,
            "at_least_600_roots": roots >= 600,
            "zero_mechanical_failures": True,
        },
        "details": {"roots": roots, "arms": roots * 16},
    }


def test_scaled_root_repair_preserves_density_and_other_gates():
    repaired = d148b.exact_mechanics_with_scaled_root_gate(
        mechanics(roots=300), 8
    )
    assert repaired["pass"]
    assert not repaired["descriptive_support_gate"]
    assert not repaired["descriptive_unscaled_root_gate"]
    assert repaired["root_density"]["required_roots"] == 300

    assert not d148b.exact_mechanics_with_scaled_root_gate(
        mechanics(roots=299), 8
    )["pass"]
    assert not d148b.exact_mechanics_with_scaled_root_gate(
        mechanics(roots=300, integrity=False), 8
    )["pass"]


def test_root_coverage_keeps_shard_block_and_corpus_floors():
    blocks = [
        {"mechanics": {"details": {"roots": 600, "arms": 10_000}}}
        for _ in range(8)
    ]
    summary, gates = d148b.root_coverage_gates(blocks)
    assert all(gates.values())
    assert summary["total_roots"] == 4_800
    assert summary["roots_by_sixteen_map_block"] == {
        "0": 1_200,
        "1": 1_200,
        "2": 1_200,
        "3": 1_200,
    }

    blocks[0]["mechanics"]["details"]["roots"] = 299
    _, gates = d148b.root_coverage_gates(blocks)
    assert not gates["every_eight_map_shard_at_least_300_roots"]
