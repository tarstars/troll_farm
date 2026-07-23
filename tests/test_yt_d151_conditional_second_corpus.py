from cgauto import yt_d151_conditional_second_corpus as d151


def test_d151_uses_correct_root_and_exact_replicated_shards():
    assert d151.YT_ROOT == "//home/delivery_ml/research/tarstars/troll_farm"
    specs = d151.build_specs()
    assert len(specs) == 16
    assert {row["replica"] for row in specs} == {"a", "b"}
    assert all(row["maps"] == 8 and row["threads"] == 16 for row in specs)
    assert [row["start_seed"] for row in specs[:8]] == list(
        range(9_844_136, 9_844_200, 8)
    )


def test_build_paths_stays_under_project_suffix():
    paths = d151.build_paths()
    assert paths["build"].startswith(
        "//home/delivery_ml/research/tarstars/troll_farm/dataset_builds/"
    )
