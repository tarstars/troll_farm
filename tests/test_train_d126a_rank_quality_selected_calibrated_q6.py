from cgauto.train_d126a_rank_quality_selected_calibrated_q6 import rank_quality_key


def test_rank_quality_key_prioritizes_regret_then_coverage_then_seed():
    candidates = [{"seed": 1}, {"seed": 2}, {"seed": 3}]
    summaries = {
        1: {"train_mean_proposal_regret": 17.0, "train_within_10_rate": 0.50},
        2: {"train_mean_proposal_regret": 16.0, "train_within_10_rate": 0.40},
        3: {"train_mean_proposal_regret": 16.0, "train_within_10_rate": 0.45},
    }
    selected = min(candidates, key=lambda item: rank_quality_key(item, summaries))
    assert selected["seed"] == 3


def test_rank_quality_key_has_fixed_seed_tie_break():
    candidates = [{"seed": 4}, {"seed": 2}]
    summaries = {
        seed: {"train_mean_proposal_regret": 16.0, "train_within_10_rate": 0.45}
        for seed in (2, 4)
    }
    selected = min(candidates, key=lambda item: rank_quality_key(item, summaries))
    assert selected["seed"] == 2
