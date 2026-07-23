"""Tests for deterministic D64a Rust-model generation."""

from __future__ import annotations

from cgauto.generate_d64a_rust_model import load_model, render, rust_float


def test_rust_float_is_explicitly_floating() -> None:
    assert rust_float(1.0) == "1.0"
    assert rust_float(0.125) == "0.125"


def test_generated_model_is_deterministic_and_complete() -> None:
    model = load_model()
    first = render(model)
    second = render(model)

    assert first == second
    assert "pub const FEATURE_COUNT: usize = 44;" in first
    assert "pub const FEATURE_NAMES" in first
    assert "own_bank_iron" in first
    assert "pub const COEFFICIENTS" in first

