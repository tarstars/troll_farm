import pytest

from cgauto.make_policy_portfolio import make_portfolio


def source_fixture() -> str:
    return " ".join(
        [
            "use std::collections::{BTreeMap,BTreeSet};",
            "if safe_regeneration&&carried==0&&view.turn>=100",
            "fn initialize(&mut self,view:&GameState){self.initialized=true;self.starter_id=",
            "use crate::bot::moisan::SecureOrchardBot;",
            "while let Some(view)=read_turn(&mut reader,&map,turn){let commands=bot.commands(&view);",
        ]
    )


def test_portfolio_caches_turn_one_feature_and_gates_both_stack_components() -> None:
    result = make_portfolio(source_fixture())

    assert "pub static PORTFOLIO_STACK:AtomicBool=AtomicBool::new(false);" in result
    assert "PORTFOLIO_STACK.load(Ordering::Relaxed)&&safe_regeneration" in result
    assert "self.minimum_enemy_door_distance=14" in result
    assert "banana_fruits<=5" in result
    assert "{SecureOrchardBot,PORTFOLIO_STACK}" in result


def test_portfolio_refuses_ambiguous_replacement_site() -> None:
    source = source_fixture() + " use std::collections::{BTreeMap,BTreeSet};"

    with pytest.raises(RuntimeError, match="expected one portfolio replacement site"):
        make_portfolio(source)
