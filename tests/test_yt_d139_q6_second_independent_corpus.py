from cgauto import yt_d133_q6_teacher_corpus as d133
from cgauto.yt_d139_q6_second_independent_corpus import (
    BUILD_NAME,
    START_SEED,
    YT_ROOT,
    configure_backend,
    restore_backend,
)


def test_d139_uses_correct_root_and_unused_seed_grid():
    try:
        configure_backend()
        assert d133.build_paths()["build"] == (
            f"{YT_ROOT}/dataset_builds/{BUILD_NAME}"
        )
        specs = d133.build_specs()
        assert len(specs) == 16
        assert specs[0]["start_seed"] == START_SEED
        assert specs[-1]["start_seed"] == START_SEED + 60
        assert {spec["threads"] for spec in specs} == {16}
    finally:
        restore_backend()
