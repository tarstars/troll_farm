from cgauto.per_opponent_continuation import analyze, build_examples
from cgauto.replay_conditioned_continuation import ACTION_VERBS, MAP_FEATURES, TARGET_FIELDS


def panel() -> dict:
    rows = []
    for agent_index in range(6):
        for game_index in range(24):
            signal = game_index % 4
            target_level = agent_index * 20 + signal * 3
            base = {field: 10 for field in TARGET_FIELDS}
            recent50 = {field: signal for field in TARGET_FIELDS}
            future50 = {field: target_level for field in TARGET_FIELDS}
            recent100 = {field: signal * 2 for field in TARGET_FIELDS}
            future100 = {field: target_level * 2 for field in TARGET_FIELDS}
            opening = {name: 1 for name in MAP_FEATURES}
            rows.append(
                {
                    "agent_name": f"agent-{agent_index}",
                    "agent_id": 100 + agent_index,
                    "game_id": 10_000 + agent_index * 100 + game_index,
                    "partition": "discovery" if game_index < 16 else "confirmation",
                    "has_iron": True,
                    "opening": opening,
                    "training_events": [
                        {"ordinal": 1, "turn": 1, "spec": [signal + 1, 2, 1, 1]}
                    ],
                    "snapshots": {"50": base, "100": base},
                    "intervals": [
                        {"start_turn": 1, "end_turn": 50, "increments": recent50},
                        {"start_turn": 51, "end_turn": 100, "increments": future50},
                        {"start_turn": 101, "end_turn": 150, "increments": future100},
                    ],
                    "scheduler": {
                        "phase_actions": {
                            "001-050": {verb: signal for verb in ACTION_VERBS},
                            "051-100": {verb: signal * 2 for verb in ACTION_VERBS},
                        }
                    },
                }
            )
    return {"rows": rows}


def test_identity_history_passes_predictive_fixture() -> None:
    report = analyze(panel())
    assert report["examples"] == 288
    assert report["passed"] is True
    assert all(report["gates"].values())


def test_panel_feature_integrity() -> None:
    examples = build_examples(panel())
    assert len(examples) == 288
    assert {len(row["features"]["history"]) for row in examples} == {27}
    assert {row["agent_id"] for row in examples} == set(range(100, 106))

