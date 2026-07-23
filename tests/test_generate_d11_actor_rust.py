import base64
import hashlib
from pathlib import Path

import pytest

from cgauto.generate_d11_actor_rust import EXPECTED_FORMAT, generate_source


def fixture_export() -> tuple[dict, bytes]:
    payload = bytearray()
    layers = []
    names = [
        "stem.0",
        "tower.0.conv1",
        "tower.0.conv2",
        "tower.1.conv1",
        "tower.1.conv2",
        "tower.2.conv1",
        "tower.2.conv2",
        "tower.3.conv1",
        "tower.3.conv2",
        "actor",
    ]
    shapes = [(16, 104, 3, 3)] + [(16, 16, 3, 3)] * 8 + [(13, 16, 1, 1)]
    for index, (name, shape) in enumerate(zip(names, shapes)):
        output, inputs, height, width = shape
        weight_offset = len(payload)
        weights = bytes((position + index) % 255 for position in range(output * inputs * height * width))
        payload.extend(weights)
        scale_offset = len(payload)
        payload.extend(b"\0\0\x80?" * output)
        bias_offset = len(payload)
        payload.extend(b"\0\0\0\0" * output)
        layers.append(
            {
                "index": index,
                "name": name,
                "weight_shape": list(shape),
                "kernel": [height, width],
                "weight_offset": weight_offset,
                "weight_bytes": len(weights),
                "scale_offset": scale_offset,
                "scale_bytes": output * 4,
                "bias_offset": bias_offset,
                "bias_bytes": output * 4,
            }
        )
    frozen = bytes(payload)
    manifest = {
        "format": EXPECTED_FORMAT,
        "observation_shape": [104, 11, 22],
        "action_shape": [13, 11, 22],
        "payload_bytes": len(frozen),
        "payload_sha256": hashlib.sha256(frozen).hexdigest(),
        "layers": layers,
    }
    return manifest, frozen


def test_generated_source_is_reproducible_embeds_exact_payload_and_fits() -> None:
    manifest, payload = fixture_export()
    source_a, accounting_a = generate_source(manifest, payload)
    source_b, accounting_b = generate_source(manifest, payload)

    assert source_a == source_b
    assert accounting_a == accounting_b
    assert accounting_a["generated_source_bytes"] < 100_000
    assert accounting_a["payload_base64_bytes"] == len(base64.b64encode(payload))
    encoded = source_a.split('const PAYLOAD_B64:&str="', 1)[1].split('";', 1)[0]
    assert base64.b64decode(encoded) == payload
    assert "std::time::Instant" in source_a
    assert "fn masked_argmax" in source_a


def test_generator_rejects_payload_hash_mismatch() -> None:
    manifest, payload = fixture_export()
    manifest["payload_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="payload hash"):
        generate_source(manifest, payload)


def test_generated_source_compiles_directly_with_rustc(tmp_path: Path) -> None:
    manifest, payload = fixture_export()
    source, _ = generate_source(manifest, payload)
    path = tmp_path / "actor.rs"
    path.write_text(source, encoding="utf-8")

    import subprocess

    completed = subprocess.run(
        ["rustc", "--edition=2021", "-O", str(path), "-o", str(tmp_path / "actor")],
        capture_output=True,
        check=False,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
