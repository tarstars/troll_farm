import pytest

from cgauto.make_geometry_portfolio import make_geometry_portfolio


def source_fixture() -> str:
    return " ".join(
        [
            "use std::collections::{BTreeMap,BTreeSet};",
            "fn initialize(&mut self,view:&GameState){self.initialized=true;self.starter_id=",
            "use crate::bot::moisan::SecureOrchardBot;",
            "while let Some(view)=read_turn(&mut reader,&map,turn){let commands=bot.commands(&view);",
        ]
    )


def test_geometry_portfolio_caches_feature_and_restores_live_boundary() -> None:
    result = make_geometry_portfolio(source_fixture(), threshold=5)

    assert "PORTFOLIO_GEOMETRY:AtomicBool" in result
    assert "self.minimum_enemy_door_distance=14" in result
    assert "self.minimum_worker_speed=2" in result
    assert "banana_fruits<=5" in result
    assert "{SecureOrchardBot,PORTFOLIO_GEOMETRY}" in result


def test_geometry_portfolio_supports_a_frozen_alternate_threshold() -> None:
    assert "banana_fruits<=2" in make_geometry_portfolio(source_fixture(), threshold=2)


def test_geometry_portfolio_refuses_ambiguous_site() -> None:
    source = source_fixture() + " use std::collections::{BTreeMap,BTreeSet};"

    with pytest.raises(RuntimeError, match="expected one geometry-portfolio replacement site"):
        make_geometry_portfolio(source)
