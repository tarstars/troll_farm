//! B1: phase skeleton — Tempo meta must be phase-inert; Scale schedules Hoard→Factory.
use troll_farm::botmain::tactics::{phase_for, Meta, Phase, T_SWITCH};

#[test]
fn tempo_is_always_tempo() {
    for t in [1, 50, T_SWITCH, 299] {
        assert_eq!(phase_for(Meta::Tempo, t), Phase::Tempo);
    }
}

#[test]
fn scale_switches_at_t_switch() {
    assert_eq!(phase_for(Meta::Scale, 1), Phase::Hoard);
    assert_eq!(phase_for(Meta::Scale, T_SWITCH - 1), Phase::Hoard);
    assert_eq!(phase_for(Meta::Scale, T_SWITCH), Phase::Factory);
    assert_eq!(phase_for(Meta::Scale, 299), Phase::Factory);
}
