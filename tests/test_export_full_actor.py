from __future__ import annotations

import gzip
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest


torch = pytest.importorskip("torch")

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "local_claude_1" / "nn-bot" / "export_full_actor.py"
SPEC = importlib.util.spec_from_file_location("export_full_actor", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
GENERATOR_PATH = ROOT / "local_claude_1" / "nn-bot" / "generate_full_bot.py"
GENERATOR_SPEC = importlib.util.spec_from_file_location("generate_full_bot", GENERATOR_PATH)
assert GENERATOR_SPEC and GENERATOR_SPEC.loader
GENERATOR = importlib.util.module_from_spec(GENERATOR_SPEC)
sys.modules[GENERATOR_SPEC.name] = GENERATOR
GENERATOR_SPEC.loader.exec_module(GENERATOR)
BED_PATH = ROOT / "local_claude_1" / "nn-bot" / "bed_full_bot.py"
BED_SPEC = importlib.util.spec_from_file_location("bed_full_bot", BED_PATH)
assert BED_SPEC and BED_SPEC.loader
BED = importlib.util.module_from_spec(BED_SPEC)
sys.modules[BED_SPEC.name] = BED
BED_SPEC.loader.exec_module(BED)

from cgauto.train_level1_ppo import PLAN_VOCAB_VERSION, SpatialActorCritic  # noqa: E402


def test_quantized_payload_covers_every_shipping_parameter() -> None:
    model = SpatialActorCritic(plan_head=True)
    converted, payload, layers, null = MODULE.quantize_full_actor_state(model.state_dict())
    shipping = sum(
        tensor.numel() for name, tensor in model.state_dict().items() if not name.startswith("critic.")
    )
    assert shipping == 34_799
    assert sum(layer["weight_count"] for layer in layers) + 1 == shipping - sum(
        layer["output_channels"] for layer in layers
    )
    assert null["offset"] + null["bytes"] == len(payload)
    assert len(payload) == 72_660
    assert {layer["effective_bits"] for layer in layers} == {16}
    assert {layer["quantization_group_size"] for layer in layers} == {64}
    assert set(converted) == set(model.state_dict())


def test_unicode20_payload_encoding_round_trips_every_byte_value() -> None:
    payload = bytes(range(256)) + b"tail"
    encoded = GENERATOR.unicode20(payload)
    decoded = bytearray()
    for first, second in zip(encoded[::2], encoded[1::2]):
        value = ((ord(first) - 0x10000) << 20) | (ord(second) - 0x10000)
        decoded.extend(value.to_bytes(5, "big"))
    assert bytes(decoded[: len(payload)]) == payload
    assert len(encoded) == 2 * ((len(payload) + 4) // 5)
    assert all(0x10000 <= ord(value) <= 0x10FFFF for value in encoded)


def test_source_size_counts_code_points_utf16_units_and_utf8_bytes() -> None:
    text = "a\U00010000"
    assert GENERATOR.source_size_counts(text) == {
        "unicode_code_points": 2,
        "utf16_code_units": 3,
        "utf8_bytes": 5,
    }
    assert BED.source_size_counts(text) == GENERATOR.source_size_counts(text)


def test_quantization_has_int8_base_packed_refinement_and_nearest_even() -> None:
    model = SpatialActorCritic(plan_head=True)
    state = model.state_dict()
    state["actor.weight"].copy_(torch.tensor([0.0] + [0.5] * 207).reshape(13, 16, 1, 1))
    converted, payload, layers, _ = MODULE.quantize_full_actor_state(state)
    layer = next(item for item in layers if item["name"] == "actor")
    scale = np.frombuffer(payload, dtype="<f4", count=1, offset=layer["scale_offset"])[0]
    coarse = np.frombuffer(payload, dtype=np.int8, count=208, offset=layer["weight_offset"])
    packed = np.frombuffer(
        payload, dtype=np.uint8, count=208, offset=layer["refinement_offset"]
    )
    refinement = packed
    assert scale == np.float32(0.5 / 32767.0)
    assert coarse[0] == 0 and refinement[0] == 0
    assert np.all(coarse[1:] == 127) and np.all(refinement[1:] == 255)
    expected = torch.from_numpy(
        ((coarse.astype(np.int32) * 256 + refinement).astype(np.float32) * scale).reshape(
            13, 16, 1, 1
        )
    )
    assert torch.equal(converted["actor.weight"], expected)


def test_export_rejects_foreign_plan_generation(tmp_path: Path) -> None:
    model = SpatialActorCritic(plan_head=True)
    checkpoint = tmp_path / "foreign.pt"
    torch.save(
        {
            "config": {"plan_vocab_version": "foreign"},
            "global_step": 0,
            "model": model.state_dict(),
            "optimizer": {},
        },
        checkpoint,
    )
    with pytest.raises(ValueError, match="plan vocabulary"):
        MODULE.export_full_actor(
            checkpoint,
            payload_path=tmp_path / "actor.bin",
            manifest_path=tmp_path / "manifest.json",
            verification_checkpoint_path=tmp_path / "verify.pt",
        )


def test_manifest_pins_sanitizer_and_argmax(tmp_path: Path) -> None:
    model = SpatialActorCritic(plan_head=True)
    checkpoint = tmp_path / "clone.pt"
    torch.save(
        {
            "config": {"plan_vocab_version": PLAN_VOCAB_VERSION},
            "global_step": 7,
            "model": model.state_dict(),
            "optimizer": {},
        },
        checkpoint,
    )
    result = MODULE.export_full_actor(
        checkpoint,
        payload_path=tmp_path / "actor.bin",
        manifest_path=tmp_path / "manifest.json",
        verification_checkpoint_path=tmp_path / "verify.pt",
    )
    assert result["plan_sanitizer"] == {"phase": "plan", "zero_planes": list(range(59, 72)) + [98]}
    assert result["decoding"] == {"plan": "masked_argmax", "command": "masked_argmax", "beam": False}
    assert result["shipping_parameter_count"] == 34_799
    assert result["critic_parameter_count_omitted"] == 1_153


def test_generated_runtime_recovers_and_caches_exact_turn1_seat() -> None:
    assert "ids!=[0,1]" in GENERATOR.RUNTIME
    assert "read_turn(&mut reader,&map,turn,absolute_seat)" in GENERATOR.RUNTIME
    assert "absolute_seat=Some(seat)" in GENERATOR.RUNTIME
    assert "cfg(tf_full_parity_probe)" in GENERATOR.RUNTIME


def test_generated_runtime_dispatch_and_forced_baseline_fallback(tmp_path: Path) -> None:
    assert 'is_x86_feature_detected!("avx2")' in GENERATOR.RUNTIME
    assert "cfg!(tf_nn_force_fallback)" in GENERATOR.RUNTIME
    assert GENERATOR.RUNTIME.count('#[target_feature(enable="avx2")]') == 1
    fallback = GENERATOR.RUNTIME.split("unsafe fn convolution_range_fallback", 1)[1].split(
        "unsafe fn convolution_range(", 1
    )[0]
    assert "_mm_mul_ps" in fallback and "_mm_add_ps" in fallback
    assert "_mm256" not in fallback and "target_feature" not in fallback

    rustc = shutil.which("rustc")
    if rustc is None:
        stable = (
            Path.home()
            / ".rustup"
            / "toolchains"
            / "stable-x86_64-unknown-linux-gnu"
            / "bin"
            / "rustc"
        )
        rustc = str(stable) if stable.is_file() else None
    if rustc is None:
        pytest.skip("rustc is required for the forced-fallback probe")
    candidate = ROOT / "cgauto" / "submissions" / "candidate-nn-clone.rs"
    binary = tmp_path / "forced-fallback-probe"
    subprocess.run(
        [
            rustc,
            "--edition=2021",
            "-O",
            "-Awarnings",
            "--cfg",
            "tf_nn_path_probe",
            "--cfg",
            "tf_nn_force_fallback",
            str(candidate),
            "-o",
            str(binary),
        ],
        check=True,
    )
    completed = subprocess.run([str(binary)], text=True, capture_output=True, check=True)
    assert completed.stdout.strip() == "baseline_fallback"


def test_three_run_timing_rule_is_frozen_and_context_sensitive() -> None:
    runs = [
        {"first_turn_max_ms": 10.0, "warm_turn_p99_ms": 14.0},
        {"first_turn_max_ms": 11.0, "warm_turn_p99_ms": 16.0},
        {"first_turn_max_ms": 12.0, "warm_turn_p99_ms": 14.5},
    ]
    information = BED.certify_timing(runs, "information")
    assert information["numerical_pass"]
    assert information["median_warm_turn_p99_ms"] == 14.5
    assert information["certified"] is None
    host = BED.certify_timing(runs, "host-of-record-quiet")
    assert host["certified"] is True
    too_slow = [dict(run) for run in runs]
    too_slow[1]["warm_turn_p99_ms"] = 20.001
    assert not BED.certify_timing(too_slow, "host-of-record-quiet")["numerical_pass"]
    with pytest.raises(ValueError, match="exactly three"):
        BED.certify_timing(runs[:2], "information")


def test_turn1_seat_corpus_checker_accepts_exact_ids_and_names_failures(tmp_path: Path) -> None:
    path = tmp_path / "states.jsonl.gz"
    rows = [
        {
            "game": 1,
            "turn": 1,
            "seat": 0,
            "state": {"units": [{"id": 0, "player": 0}, {"id": 1, "player": 1}]},
        },
        {
            "game": 2,
            "turn": 1,
            "seat": 0,
            "state": {"units": [{"id": 0, "player": 1}, {"id": 1, "player": 0}]},
        },
        {
            "game": 3,
            "turn": 1,
            "seat": 1,
            "state": {"units": [{"id": 0, "player": 0}, {"id": 1, "player": 1}]},
        },
    ]
    with gzip.open(path, "wt") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    result = BED.check_turn1_seat_corpus(path)
    assert result["seat0_turn1_games"] == 2
    assert not result["valid"]
    assert result["exceptions"] == [
        {"game": 2, "line": 2, "ids": [0, 1], "owners": {0: [1], 1: [0]}}
    ]
