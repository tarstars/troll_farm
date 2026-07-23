from cgauto.rich_opponent_scheduler_transition_study import partition_summary


def row() -> dict:
    final = {
        "successful_plants": 100,
        "wood": 100,
    }
    return {
        "opponent": "rich",
        "final_worker_count": 4,
        "third_worker_turn_or_301": 80,
        "training_events": [
            {"ordinal": 1, "turn": 1, "spec": [2, 2, 2, 1]},
            {"ordinal": 2, "turn": 80, "spec": [2, 3, 1, 2]},
            {"ordinal": 3, "turn": 100, "spec": [2, 3, 1, 2]},
        ],
        "trained_workers": 3,
        "hybrid_trained_workers": 3,
        "active_50_workers": 4,
        "multi_role_active_50_workers": 2,
        "later_training_events": 2,
        "coordinated_later_training_events": 2,
        "has_harvest_to_plant": True,
        "has_chop_to_drop": True,
        "snapshots": {
            "100": {"successful_plants": 40, "wood": 40},
            "300": final,
        },
        "turns": 300,
        "scheduler": {
            "phase_actions": {"001-050": {"HARVEST": 10}},
            "transitions": {"HARVEST->PLANT": 4, "CHOP->DROP": 4},
        },
    }


def test_partition_summary_passes_all_replicated_mechanisms() -> None:
    summary = partition_summary([row() for _ in range(5)])
    assert all(summary["mechanism_checks"].values())


def test_partition_summary_fails_missing_scale_and_transitions() -> None:
    value = row()
    value["final_worker_count"] = 2
    value["third_worker_turn_or_301"] = 301
    value["has_harvest_to_plant"] = False
    value["has_chop_to_drop"] = False
    summary = partition_summary([value])
    assert summary["mechanism_checks"]["front_loaded_scale"] is False
    assert summary["mechanism_checks"]["late_renewable_loop"] is False
