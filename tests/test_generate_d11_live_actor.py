import json
import subprocess
from pathlib import Path

import torch

from cgauto.export_d11_actor import export_actor
from cgauto.generate_d11_live_actor import generate_live_source
from cgauto.train_level1_ppo import SpatialActorCritic


def test_live_source_is_reproducible_complete_small_and_compiles(tmp_path: Path) -> None:
    torch.manual_seed(43)
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
    source_a, accounting_a = generate_live_source(metadata, payload.read_bytes())
    source_b, accounting_b = generate_live_source(metadata, payload.read_bytes())
    assert source_a == source_b
    assert accounting_a == accounting_b
    assert accounting_a["under_100000_bytes"] is True
    assert "fn read_map" in source_a
    assert "fn observe" in source_a
    assert "TRAIN {} {} {} {}" in source_a
    assert "--audit" in source_a
    assert "INPUT_MAGIC" not in source_a

    source = tmp_path / "live.rs"
    binary = tmp_path / "live"
    source.write_text(source_a, encoding="utf-8")
    completed = subprocess.run(
        ["rustc", "--edition=2021", "-O", str(source), "-o", str(binary)],
        capture_output=True,
        check=False,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
