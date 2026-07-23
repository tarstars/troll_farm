from cgauto.opening_activation_scan import summarize


def test_summarize_reports_sparse_seed_and_side_activation() -> None:
    rows = [
        {
            "seed": 4,
            "sides": [
                {
                    "seat": 0,
                    "diverged": True,
                    "candidate_commands": ["TRAIN 1 2 0 2", "MOVE 0 3 3"],
                },
                {
                    "seat": 1,
                    "diverged": True,
                    "candidate_commands": ["TRAIN 1 2 0 3"],
                },
            ],
        },
        {
            "seed": 5,
            "sides": [
                {"seat": 0, "diverged": False, "candidate_commands": ["MOVE 0 1 1"]},
                {"seat": 1, "diverged": False, "candidate_commands": ["WAIT"]},
            ],
        },
    ]

    result = summarize(rows)

    assert result["active_seed_count"] == 1
    assert result["active_side_count"] == 2
    assert result["active_seed_rate"] == 0.5
    assert result["active_seeds"] == [4]
    assert result["candidate_train_specs"] == {"1/2/0/2": 1, "1/2/0/3": 1}
