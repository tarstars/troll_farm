from pathlib import Path

from cgauto.make_rollout_live_candidate import (
    DEFAULT_ENGINE,
    DEFAULT_MODEL,
    DEFAULT_PARENT,
    DEFAULT_STATE,
    compose,
    make_selectable_parent,
)


def test_selectable_parent_keeps_control_default_and_adds_one_option() -> None:
    source = DEFAULT_PARENT.read_text()
    result = make_selectable_parent(source)

    assert result.count("first_worker_max_bank_hp0:bool") == 1
    assert result.count("first_worker_max_bank_hp0:false") == 1
    assert result.count("pub fn max_bank_first_hp0()") == 1
    assert "first_worker_max_bank_hp0&&own_count==1" in result
    assert "harvest_power:0" in result


def test_composed_rollout_candidate_is_standalone_and_under_limit() -> None:
    result = compose(
        DEFAULT_PARENT.read_text(),
        DEFAULT_STATE.read_text(),
        DEFAULT_ENGINE.read_text(),
        DEFAULT_MODEL.read_text(),
    )

    assert len(result.encode()) < 100_000
    assert "mod rollout{" in result
    assert "std::thread::scope" in result
    assert "elapsed().as_millis()>=700" in result
    assert "option-control>30" in result
    assert "SecureOrchardBot::max_bank_first_hp0()" in result
    assert "fn from_ascii" not in result
    assert "pub fn apply_chop(" not in result
    assert "crate::game::engine" not in result
    assert "crate::game::state" not in result
