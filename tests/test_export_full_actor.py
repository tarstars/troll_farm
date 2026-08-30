from __future__ import annotations

import importlib.util
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
