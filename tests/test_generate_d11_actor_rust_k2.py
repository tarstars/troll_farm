import json
import subprocess
from pathlib import Path

import torch

from cgauto.export_d11_actor import export_actor
from cgauto.generate_d11_actor_rust_k2 import generate_optimized_source
from cgauto.train_level1_ppo import SpatialActorCritic


def test_k2_is_deterministic_preallocated_and_compiles(tmp_path: Path) -> None:
    torch.manual_seed(41)
    checkpoint = tmp_path / "model.pt"
    torch.save({"model": SpatialActorCritic().state_dict()}, checkpoint)
    payload = tmp_path / "actor.bin"
    manifest = tmp_path / "manifest.json"
    export_actor(
        checkpoint,
        payload_path=payload,
        manifest_path=manifest,
        verification_checkpoint_path=tmp_path / "verification.pt",
    )
    metadata = json.loads(manifest.read_text(encoding="utf-8"))
    source_a, accounting_a = generate_optimized_source(metadata, payload.read_bytes())
    source_b, accounting_b = generate_optimized_source(metadata, payload.read_bytes())

    assert source_a == source_b
    assert accounting_a == accounting_b
    assert accounting_a["generated_source_bytes"] < 100_000
    assert "struct Workspace" in source_a
    assert "get_unchecked" in source_a
    assert "let mut input=vec!" not in source_a
    assert source_a.count("let mut actor=Actor::new();") == 2

    path = tmp_path / "actor-k2.rs"
    path.write_text(source_a, encoding="utf-8")
    completed = subprocess.run(
        ["rustc", "--edition=2021", "-O", str(path), "-o", str(tmp_path / "actor-k2")],
        capture_output=True,
        check=False,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
