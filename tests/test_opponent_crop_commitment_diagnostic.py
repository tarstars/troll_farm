from cgauto.opponent_crop_commitment_diagnostic import command_target, summarize


def record(*, abandoned: bool, kind: str = "BANANA") -> dict:
    return {
        "abandoned": abandoned,
        "type": kind,
        "opponent_wood_collected": 1,
        "opponent_fruit_harvested": 2,
    }


def test_command_target_resolves_move_and_direct_tree_work() -> None:
    unit = {"x": 4, "y": 5}
    assert command_target("MOVE 7 8 9", unit) == (8, 9)
    assert command_target("CHOP 7", unit) == (4, 5)
    assert command_target("HARVEST 7", unit) == (4, 5)
    assert command_target("DROP 7", unit) is None
    assert command_target("MOVE 7 bad 9", unit) is None


def test_summarize_passes_only_material_distributed_abandonment() -> None:
    rows = []
    for index in range(20):
        selected = [record(abandoned=index < 10 and offset < 2) for offset in range(5)]
        rows.append(
            {
                "opponent": f"opponent-{index % 10}",
                "catastrophic": index < 10,
                "selected_crops": len(selected),
                "abandoned_crops": sum(item["abandoned"] for item in selected),
                "selected_records": selected,
            }
        )
    report = summarize(rows)
    assert report["selected_crops"] == 100
    assert report["abandoned_crops"] == 20
    assert report["abandonment_rate"] == 0.2
    assert report["abandoned_games"] == 10
    assert report["abandoned_opponents"] == 10
    assert report["abandoned_opponent_wood_share"] == 0.2
    assert report["catastrophic_abandoned_crops"] == 20
    assert report["gate_passed"] is True


def test_summarize_rejects_inert_diagnostic() -> None:
    report = summarize([])
    assert report["selected_crops"] == 0
    assert report["abandonment_rate"] == 0
    assert report["gate_passed"] is False
