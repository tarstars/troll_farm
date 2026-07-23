from cgauto.evaluate_d120a_policy_sealed_absolute_information import (
    absolute_information_gates,
)


def passing_information():
    return {
        "supported_tasks": 1_024,
        "minimum_supported_tasks_per_opponent": 128,
        "minimum_supported_tasks_per_seat": 512,
        "minimum_supported_tasks_per_fold": 512,
        "roots": 5_000,
        "minimum_roots_per_opponent": 500,
        "arms": 80_000,
        "minimum_arms_per_opponent": 8_000,
    }


def test_absolute_information_gates_accept_exact_boundaries():
    assert all(absolute_information_gates(passing_information()).values())


def test_absolute_information_gates_reject_each_shortfall():
    for field, boundary in passing_information().items():
        information = passing_information()
        information[field] = boundary - 1
        assert not all(absolute_information_gates(information).values()), field
