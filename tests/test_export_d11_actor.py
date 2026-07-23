from pathlib import Path

import torch

from cgauto.export_d11_actor import ACTOR_LAYERS, export_actor, quantize_actor_state
from cgauto.train_level1_ppo import SpatialActorCritic


def test_quantization_has_frozen_layer_order_and_preserves_critic() -> None:
    torch.manual_seed(17)
    source = SpatialActorCritic().state_dict()
    converted, payload, layers = quantize_actor_state(source)

    assert [layer["name"] for layer in layers] == list(ACTOR_LAYERS)
    assert len(payload) == sum(
        layer["weight_bytes"] + layer["scale_bytes"] + layer["bias_bytes"]
        for layer in layers
    )
    assert sum(layer["weight_count"] for layer in layers) == 33_616
    assert all(layer["maximum_absolute_weight_error"] >= 0 for layer in layers)
    assert all(
        torch.equal(converted[name], tensor)
        for name, tensor in source.items()
        if name.startswith("critic.") or name.endswith(".bias")
    )
    assert any(
        not torch.equal(converted[f"{prefix}.weight"], source[f"{prefix}.weight"])
        for prefix in ACTOR_LAYERS
    )


def test_export_is_reproducible_and_verification_checkpoint_loads(tmp_path: Path) -> None:
    torch.manual_seed(23)
    source_path = tmp_path / "source.pt"
    torch.save({"model": SpatialActorCritic().state_dict()}, source_path)

    first = tmp_path / "first"
    second = tmp_path / "second"
    result_a = export_actor(
        source_path,
        payload_path=first / "actor.bin",
        manifest_path=first / "manifest.json",
        verification_checkpoint_path=first / "verification.pt",
    )
    result_b = export_actor(
        source_path,
        payload_path=second / "actor.bin",
        manifest_path=second / "manifest.json",
        verification_checkpoint_path=second / "verification.pt",
    )

    assert (first / "actor.bin").read_bytes() == (second / "actor.bin").read_bytes()
    assert (first / "manifest.json").read_bytes() == (second / "manifest.json").read_bytes()
    assert result_a["payload_sha256"] == result_b["payload_sha256"]
    assert result_a["dequantized_actor_tensor_sha256"] == result_b[
        "dequantized_actor_tensor_sha256"
    ]

    saved = torch.load(first / "verification.pt", map_location="cpu", weights_only=False)
    restored = SpatialActorCritic()
    restored.load_state_dict(saved["model"], strict=True)
    observations = torch.randint(0, 256, (2, 104, 11, 22), dtype=torch.uint8)
    logits, values = restored(observations)
    assert logits.shape == (2, 13 * 11 * 22)
    assert values.shape == (2,)
    assert torch.isfinite(logits).all()
    assert torch.isfinite(values).all()
